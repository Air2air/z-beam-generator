"""
Enhanced content generation service with proper interface implementation.
"""

import json
import re
from typing import Optional
from generator.core.interfaces.services import (
    IContentGenerator,
    IAPIClient,
    IDetectionService,
    IPromptRepository,
)
from generator.core.domain.models import (
    GenerationRequest,
    GenerationContext,
    SectionConfig,
    GenerationResult,
    AIScore,
    TemperatureConfig,
)
from generator.core.exceptions import ContentGenerationError
from generator.modules.logger import get_logger

logger = get_logger("content_service")


class ContentGenerationService(IContentGenerator):
    """Service for generating content with AI/human detection."""

    def __init__(
        self,
        api_client: IAPIClient,
        detection_service: IDetectionService,
        prompt_repository: IPromptRepository,
    ):
        self._api_client = api_client
        self._detection_service = detection_service
        self._prompt_repository = prompt_repository

    def generate_section(
        self,
        request: GenerationRequest,
        section_config: SectionConfig,
        context: GenerationContext,
    ) -> GenerationResult:
        """Generate content for a single section with optional detection."""
        logger.info(
            f"Generating section: {section_config.name} (ai_detect: {section_config.ai_detect})"
        )

        # Get the prompt template
        prompt_template = self._prompt_repository.get_prompt(
            section_config.prompt_file.replace(".txt", ""), "sections"
        )
        if not prompt_template:
            raise ContentGenerationError(
                f"Prompt template not found: {section_config.prompt_file}",
                section=section_config.name,
            )

        # Generate initial content
        initial_content = self._generate_initial_content(
            request, section_config, context, prompt_template.content
        )

        # If no AI detection required, return immediately
        if not section_config.ai_detect:
            logger.info(
                f"Section {section_config.name} skipping detection (ai_detect=false)"
            )
            return GenerationResult(
                content=initial_content, threshold_met=True, iterations_completed=1
            )

        # Run through detection iterations
        return self._generate_with_detection_iterations(
            request, section_config, context, initial_content
        )

    def _generate_initial_content(
        self,
        request: GenerationRequest,
        section_config: SectionConfig,
        context: GenerationContext,
        prompt_template: str,
    ) -> str:
        """Generate the initial content for a section."""
        try:
            # Format the prompt with context variables
            formatted_prompt = prompt_template.format(**context.variables)

            # Call the API
            # Use temperature_config.content_temp if available, otherwise fallback to legacy temperature
            content_temp = (
                request.temperature_config.content_temp
                if request.temperature_config
                else request.temperature
            )
            content = self._api_client.call_api(
                prompt=formatted_prompt,
                model=request.model,
                temperature=content_temp,
                max_tokens=request.max_tokens,
                timeout=request.api_timeout,
            )

            if not content or not content.strip():
                raise ContentGenerationError(
                    "Empty content returned from API", section=section_config.name
                )

            # Clean and validate the content
            cleaned_content = self._clean_and_validate_content(
                content, section_config.name
            )
            return cleaned_content

        except Exception as e:
            raise ContentGenerationError(
                f"Failed to generate initial content: {str(e)}",
                section=section_config.name,
            ) from e

    def _generate_with_detection_iterations(
        self,
        request: GenerationRequest,
        section_config: SectionConfig,
        context: GenerationContext,
        initial_content: str,
    ) -> GenerationResult:
        """Generate content with detection iterations."""
        current_content = initial_content
        ai_score = None
        human_score = None
        previous_ai_score = None
        previous_human_score = None

        # Display iteration start banner
        self._display_iteration_banner(section_config.name, request)

        for iteration in range(1, request.iterations_per_section + 1):
            logger.info(
                f"Detection iteration {iteration}/{request.iterations_per_section} for {section_config.name}"
            )

            # Run comprehensive detection using new unified system
            detection_results = self._detection_service.run_comprehensive_detection(
                current_content,
                context,
                request.ai_detection_threshold,
                request.human_detection_threshold,
                iteration,
                temperature_config=request.temperature_config,
            )
            
            # Extract individual scores for compatibility with existing logic
            ai_score = detection_results["ai_detection"]["raw_result"]
            human_score = detection_results["natural_voice_detection"]["raw_result"]

            # Display iteration results
            self._display_iteration_results(
                iteration,
                request.iterations_per_section,
                ai_score,
                human_score,
                previous_ai_score,
                previous_human_score,
                request.ai_detection_threshold,
                request.human_detection_threshold,
                section_config.name,
                current_content,  # Pass current content for word count analysis
            )

            # Check if thresholds are met
            ai_threshold_met = ai_score.score <= request.ai_detection_threshold
            human_threshold_met = human_score.score <= request.human_detection_threshold

            if ai_threshold_met and human_threshold_met:
                self._display_success_banner(
                    section_config.name, iteration, ai_score, human_score
                )

                # Track the successful improvement cycle
                if iteration > 1:  # Only track if improvements were actually made
                    self._track_complete_improvement_cycle(
                        section_name=section_config.name,
                        initial_ai_score=previous_ai_score or ai_score,
                        initial_human_score=previous_human_score or human_score,
                        final_ai_score=ai_score,
                        final_human_score=human_score,
                        iterations=iteration,
                        threshold_met=True,
                    )

                return GenerationResult(
                    content=current_content,
                    ai_score=ai_score,
                    human_score=human_score,
                    threshold_met=True,
                    iterations_completed=iteration,
                )

            # If not the last iteration, improve the content
            if iteration < request.iterations_per_section:
                current_content = self._improve_content(
                    current_content, ai_score, human_score, context, request
                )

            # Store scores for next iteration comparison
            previous_ai_score = ai_score
            previous_human_score = human_score

        # Return final result even if thresholds not met
        self._display_final_banner(
            section_config.name,
            request.iterations_per_section,
            ai_score,
            human_score,
            request,
        )

        # Track the unsuccessful improvement cycle
        if request.iterations_per_section > 1:
            self._track_complete_improvement_cycle(
                section_name=section_config.name,
                initial_ai_score=previous_ai_score or ai_score,
                initial_human_score=previous_human_score or human_score,
                final_ai_score=ai_score,
                final_human_score=human_score,
                iterations=request.iterations_per_section,
                threshold_met=False,
            )

        return GenerationResult(
            content=current_content,
            ai_score=ai_score,
            human_score=human_score,
            threshold_met=False,
            iterations_completed=request.iterations_per_section,
        )

    def _improve_content(
        self,
        content: str,
        ai_score: AIScore,
        human_score: AIScore,
        context: GenerationContext,
        request: GenerationRequest,
    ) -> str:
        """Improve content based on detection feedback using adaptive strategies."""
        try:
            # Select improvement prompt based on detection patterns
            improvement_prompt_name = self._select_adaptive_improvement_strategy(
                ai_score, human_score
            )

            # Get the selected improvement prompt
            improvement_prompt = self._prompt_repository.get_prompt(
                improvement_prompt_name, "detection"
            )

            if not improvement_prompt:
                logger.warning(
                    f"No improvement prompt found for {improvement_prompt_name}, using default"
                )
                improvement_prompt = self._prompt_repository.get_prompt(
                    "initial_prompt", "detection"
                )

                if not improvement_prompt:
                    return content

            # Create targeted feedback based on detection scores
            targeted_feedback = self._create_targeted_feedback(ai_score, human_score)

            # Format improvement prompt with adaptive guidance
            improvement_variables = {
                **context.variables,
                "previous_version": content,
                "feedback": targeted_feedback,
                "ai_score": ai_score.score,
                "human_score": human_score.score,
                "strategy": self._get_improvement_strategy_guidance(
                    ai_score, human_score
                ),
            }

            formatted_prompt = improvement_prompt.content.format(
                **improvement_variables
            )

            # Generate improved content
            # Use temperature_config.improvement_temp if available, otherwise fallback to content_temp or legacy temperature
            improvement_temp = request.temperature
            if request.temperature_config:
                improvement_temp = (
                    request.temperature_config.improvement_temp
                    or request.temperature_config.content_temp
                )

            improved_content = self._api_client.call_api(
                prompt=formatted_prompt,
                model=request.model,
                temperature=improvement_temp,
                max_tokens=8192,  # Increase max_tokens for improvement step
                timeout=request.api_timeout,
            )

            # Track the success of the improvement strategy
            self._track_improvement_success(
                strategy=improvement_prompt_name,
                initial_ai_score=ai_score.score,
                initial_human_score=human_score.score,
                final_ai_score=ai_score.score,  # Final scores after improvement
                final_human_score=human_score.score,
                section_name=context.content_type
                or "unknown",  # Pass the content type for tracking
            )

            return improved_content.strip() if improved_content else content

        except Exception as e:
            logger.error(f"Failed to improve content: {str(e)}")
            return content  # Return original content if improvement fails

    def _clean_and_validate_content(self, content: str, section_name: str) -> str:
        """Clean and validate content, handling common JSON truncation issues."""
        try:
            # Remove any leading/trailing whitespace
            cleaned_content = content.strip()

            # Skip JSON validation for chart sections that contain JavaScript/HTML
            if (
                section_name == "chart"
                or "<script>" in cleaned_content
                or "</script>" in cleaned_content
            ):
                logger.debug(
                    f"Skipping JSON validation for chart/script content in {section_name}"
                )
                return cleaned_content

            # If the content looks like JSON but might be truncated, try to fix it
            if cleaned_content.startswith("{") and not cleaned_content.endswith("}"):
                logger.warning(
                    f"Detected potentially truncated JSON response for {section_name}"
                )
                # Try to close JSON if it looks incomplete
                if cleaned_content.count("{") > cleaned_content.count("}"):
                    cleaned_content += "}"
                    logger.info(f"Attempted to fix truncated JSON for {section_name}")

            # For JSON responses, validate they parse correctly
            if cleaned_content.startswith("{") and cleaned_content.endswith("}"):
                try:
                    json.loads(cleaned_content)  # Validate JSON structure
                    logger.debug(f"Valid JSON content validated for {section_name}")
                except json.JSONDecodeError as e:
                    logger.error(
                        f"Invalid JSON in response for {section_name}: {str(e)}"
                    )
                    # If JSON is invalid, we might still want to use the content as-is
                    # depending on the use case

            return cleaned_content

        except Exception as e:
            logger.warning(f"Content cleaning failed for {section_name}: {str(e)}")
            return content  # Return original if cleaning fails

    def _display_iteration_banner(
        self, section_name: str, request: GenerationRequest
    ) -> None:
        """Display iteration start banner - simplified."""
        CYAN = "\033[96m"
        BOLD = "\033[1m"
        RESET = "\033[0m"

        print(f"\n{CYAN}{BOLD}▶ SECTION: {section_name.upper()}{RESET}")
        print(
            f"{CYAN}Target: AI ≤{request.ai_detection_threshold}% | Human ≤{request.human_detection_threshold}%{RESET}"
        )

    def _display_iteration_results(
        self,
        iteration: int,
        max_iterations: int,
        ai_score,
        human_score,
        previous_ai_score,
        previous_human_score,
        ai_threshold: int,
        human_threshold: int,
        section_name: str,
        content: str = "",
        word_budget_manager=None,
    ) -> None:
        """Display streamlined iteration results with score tracking."""
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        RED = "\033[91m"
        BOLD = "\033[1m"
        RESET = "\033[0m"

        # Calculate score changes
        ai_change = ""
        human_change = ""
        if previous_ai_score:
            ai_diff = ai_score.score - previous_ai_score.score
            if ai_diff > 0:
                ai_change = f" {RED}↑{ai_diff}{RESET}"
            elif ai_diff < 0:
                ai_change = f" {GREEN}↓{abs(ai_diff)}{RESET}"
            else:
                ai_change = f" {YELLOW}→{RESET}"

        if previous_human_score:
            human_diff = human_score.score - previous_human_score.score
            if human_diff > 0:
                human_change = f" {RED}↑{human_diff}{RESET}"
            elif human_diff < 0:
                human_change = f" {GREEN}↓{abs(human_diff)}{RESET}"
            else:
                human_change = f" {YELLOW}→{RESET}"

        # Calculate word count
        word_count = len(content.split()) if content else 0

        # Determine threshold status icons
        ai_icon = "✅" if ai_score.score <= ai_threshold else "❌"
        human_icon = "✅" if human_score.score <= human_threshold else "❌"

        # Create progress bars
        ai_bar = "█" * (ai_score.score // 5) + "░" * (20 - (ai_score.score // 5))
        human_bar = "█" * (human_score.score // 5) + "░" * (
            20 - (human_score.score // 5)
        )

        print(
            f"\n{BOLD}Iteration {iteration}/{max_iterations} [{section_name.upper()}] - Words: {word_count}{RESET}"
        )
        print(f"AI Score:    {ai_icon} {ai_score.score}%{ai_change} [{ai_bar}]")
        print(
            f"Human Score: {human_icon} {human_score.score}%{human_change} [{human_bar}]"
        )

        # Show action for next iteration
        if iteration < max_iterations:
            both_pass = (
                ai_score.score <= ai_threshold and human_score.score <= human_threshold
            )
            if not both_pass:
                print(
                    f"{YELLOW}➤ Generating improved content for iteration {iteration + 1}...{RESET}"
                )

    def _display_success_banner(
        self, section_name: str, iteration: int, ai_score, human_score
    ) -> None:
        """Display streamlined success banner when thresholds are met."""
        GREEN = "\033[92m"
        BOLD = "\033[1m"
        RESET = "\033[0m"

        print(f"\n{GREEN}{BOLD}✓ {section_name.upper()} COMPLETE {RESET}")
        print(
            f"{GREEN}Iterations: {iteration} | AI: {ai_score.score}% | Human: {human_score.score}% | SUCCESS!{RESET}"
        )

    def _display_final_banner(
        self, section_name: str, iterations: int, ai_score, human_score, request
    ) -> None:
        """Display streamlined final banner when max iterations reached."""
        YELLOW = "\033[93m"
        RED = "\033[91m"
        BOLD = "\033[1m"
        RESET = "\033[0m"

        ai_met = ai_score.score <= request.ai_detection_threshold
        human_met = human_score.score <= request.human_detection_threshold

        if ai_met and human_met:
            color = YELLOW
            status = "PARTIAL SUCCESS"
        else:
            color = RED
            status = "FAILED"

        print(f"\n{color}{BOLD}! {section_name.upper()} {status}{RESET}")
        print(
            f"{color}Iterations: {iterations}/{iterations} | AI: {ai_score.score}% | Human: {human_score.score}%{RESET}"
        )

    def _select_adaptive_improvement_strategy(
        self, ai_score: AIScore, human_score: AIScore
    ) -> str:
        """
        Select the most appropriate improvement strategy based on detection scores.

        Returns the name of the improvement prompt to use.
        """
        # Default strategy
        strategy = "initial_prompt"

        # If AI score is high but human score is low - focus on reducing AI patterns
        if ai_score.score > 50 and human_score.score <= 30:
            strategy = "reduce_ai_patterns"

        # If human score is high but AI score is low - focus on improving human-like qualities
        elif human_score.score > 50 and ai_score.score <= 30:
            strategy = "increase_human_qualities"

        # If both scores are high - try a balanced approach
        elif ai_score.score > 40 and human_score.score > 40:
            strategy = "balanced_improvement"

        # If both scores are already good, use light touch improvements
        elif ai_score.score <= 30 and human_score.score <= 30:
            strategy = "light_refinement"

        # Fall back to default if the selected strategy doesn't exist
        if not self._prompt_repository.get_prompt(strategy, "detection"):
            strategy = "initial_prompt"

        return strategy

    def _create_targeted_feedback(self, ai_score: AIScore, human_score: AIScore) -> str:
        """
        Create targeted feedback based on detection scores to guide improvement.
        """
        feedback_parts = []

        # Add AI detection feedback with priority weighting
        if ai_score.score > 50:
            feedback_parts.append(
                f"CRITICAL - AI Detection Feedback: {ai_score.feedback}"
            )
        else:
            feedback_parts.append(f"AI Detection Feedback: {ai_score.feedback}")

        # Add human detection feedback with priority weighting
        if human_score.score > 50:
            feedback_parts.append(
                f"CRITICAL - Human Detection Feedback: {human_score.feedback}"
            )
        else:
            feedback_parts.append(f"Human Detection Feedback: {human_score.feedback}")

        # Add specific improvement focus based on score patterns
        if ai_score.score > human_score.score:
            feedback_parts.append(
                "FOCUS: Reduce patterns commonly associated with AI generation while preserving content quality."
            )
        else:
            feedback_parts.append(
                "FOCUS: Increase human-like writing qualities while maintaining information accuracy."
            )

        return "\n\n".join(feedback_parts)

    def _get_improvement_strategy_guidance(
        self, ai_score: AIScore, human_score: AIScore
    ) -> str:
        """
        Generate specific guidance for the selected improvement strategy.
        """
        # Base guidance
        guidance = "Make targeted improvements to the content."

        # Adaptive guidance based on score patterns
        if ai_score.score > 70:
            guidance = (
                "The content appears highly AI-generated. Break up repetitive structures, "
                "vary sentence patterns significantly, add more informal language, and "
                "incorporate practical insights that feel like personal experience."
            )
        elif ai_score.score > 40:
            guidance = (
                "The content has some AI-like patterns. Add more natural transitions, "
                "vary your phrasing, and include a few colloquial expressions or industry jargon "
                "that would come from practical experience."
            )
        elif human_score.score > 70:
            guidance = (
                "The content lacks human-like qualities. Add some personal perspective, "
                "use more varied vocabulary, include an occasional conversational aside, "
                "and vary your sentence structures more naturally."
            )
        elif human_score.score > 40:
            guidance = (
                "The content needs more human-like attributes. Include some informal language, "
                "add a few professional insights, and vary your writing rhythm with some "
                "shorter sentences mixed with longer explanations."
            )
        elif ai_score.score <= 30 and human_score.score <= 30:
            guidance = (
                "The content is already quite good. Make minor refinements to further "
                "enhance readability and natural flow, but preserve the overall structure "
                "and approach that's working well."
            )

        return guidance

    def _track_improvement_success(
        self,
        strategy: str,
        initial_ai_score: int,
        initial_human_score: int,
        final_ai_score: int,
        final_human_score: int,
        section_name: str,
    ) -> None:
        """
        Track the success of improvement strategies to build a knowledge base for adaptive improvements.
        """
        try:
            # Calculate improvement delta
            ai_delta = initial_ai_score - final_ai_score
            human_delta = initial_human_score - final_human_score

            # Calculate overall success score (positive is good)
            success_score = ai_delta + human_delta

            # Log the results for future analysis
            logger.debug(
                f"Strategy '{strategy}' for {section_name}: "
                f"AI score delta: {ai_delta}, Human score delta: {human_delta}, "
                f"Success score: {success_score}"
            )

            # TODO: Store this data in a persistent store for long-term learning
            # This could be implemented with the existing prompt performance repository
            # or with a new specialized repository for improvement strategies

        except Exception as e:
            logger.error(f"Failed to track improvement success: {str(e)}")

    def _track_complete_improvement_cycle(
        self,
        section_name: str,
        initial_ai_score: AIScore,
        initial_human_score: AIScore,
        final_ai_score: AIScore,
        final_human_score: AIScore,
        iterations: int,
        threshold_met: bool,
    ) -> None:
        """
        Track the complete improvement cycle results to analyze which strategies work best.
        """
        try:
            # Calculate overall improvement
            ai_improvement = initial_ai_score.score - final_ai_score.score
            human_improvement = initial_human_score.score - final_human_score.score

            # Log the results
            logger.debug(
                f"Improvement cycle for {section_name}: "
                f"AI score delta: {ai_improvement}, Human score delta: {human_improvement}, "
                f"Iterations: {iterations}, Success: {threshold_met}"
            )

            # TODO: Store these results in a persistent repository for analysis
            # This data can be used to refine the adaptive strategies

        except Exception as e:
            logger.error(f"Failed to track improvement cycle: {str(e)}")

    def generate_section_content(
        self,
        section_name: str,
        material: str,
        generation_context: dict,
        api_client,
        prompt_manager,
        ai_detection_threshold: int,
        human_detection_threshold: int,
        iterations_per_section: int = None,
        temperature: float = None,
        timeout: int = None,
        temperature_config: Optional[TemperatureConfig] = None,
    ) -> dict:
        """Generate content for a specific section (interface compatibility method)."""
        # Set defaults from config if not provided
        if iterations_per_section is None:
            from config.global_config import get_config
            iterations_per_section = get_config().get_iterations_per_section()
        if temperature is None:
            from config.global_config import get_config
            temperature = get_config().get_content_temperature()
        if timeout is None:
            from config.global_config import get_config
            timeout = get_config().get_api_timeout()
            
        # This is a legacy interface method - redirect to the main generation flow
        from generator.core.domain.models import GenerationRequest, GenerationContext

        # Create proper request and context objects
        request = GenerationRequest(
            material=material,
            section_configs={
                section_name: SectionConfig(
                    name=section_name, ai_detect=True, prompt_file=f"{section_name}.txt"
                )
            },
            ai_detection_threshold=ai_detection_threshold,
            human_detection_threshold=human_detection_threshold,
            iterations_per_section=iterations_per_section,
            temperature_config=temperature_config or TemperatureConfig(),
        )

        context = GenerationContext(
            material=material, content_type=section_name, variables=generation_context
        )

        # Generate the content using the main method
        result = self.generate_content(request, context)

        # Return in the legacy format
        if result.sections and section_name in result.sections:
            section_result = result.sections[section_name]
            return {
                "content": section_result.content,
                "ai_score": section_result.ai_score,
                "human_score": section_result.human_score,
                "iterations": section_result.iterations,
                "word_count": len(section_result.content.split()),
            }
        else:
            # Return empty result if generation failed
            return {
                "content": "",
                "ai_score": AIScore(
                    score=100, feedback="Generation failed", iteration=0
                ),
                "human_score": AIScore(
                    score=100, feedback="Generation failed", iteration=0
                ),
                "iterations": 0,
                "word_count": 0,
            }
