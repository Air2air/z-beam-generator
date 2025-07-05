"""
Enhanced content generation service with word budget management and API efficiency.
"""

import os
from typing import Dict, List
from generator.core.services.content_service import ContentGenerationService
from generator.core.services.word_budget_manager import (
    WordBudgetManager,
    ContentMetrics,
)
from generator.core.interfaces.services import (
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

logger = get_logger("efficient_content_service")

# Enhanced logging colors and symbols for better visual awareness
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
UNDERLINE = "\033[4m"

# Colors
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_BLUE = "\033[94m"
BRIGHT_MAGENTA = "\033[95m"
BRIGHT_CYAN = "\033[96m"

# Progress symbols
GEAR = "⚙️"
TARGET = "🎯"
CHART = "📊"
MAGNIFY = "🔍"
CYCLE = "🔄"
CHECK = "✅"
CROSS = "❌"
ARROW_UP = "↗️"
ARROW_DOWN = "↘️"
STOPWATCH = "⏱️"
LIGHTBULB = "💡"


class EfficientContentGenerationService(ContentGenerationService):
    """Enhanced content service with word budget management and reduced API usage."""

    def __init__(
        self,
        api_client: IAPIClient,
        detection_service: IDetectionService,
        prompt_repository: IPromptRepository,
        max_article_words: int = 1200,
    ):
        super().__init__(api_client, detection_service, prompt_repository)
        self.word_budget_manager = WordBudgetManager(max_article_words)
        self.logger = logger

    def generate_article_sections(
        self,
        request: GenerationRequest,
        section_configs: List[SectionConfig],
        context: GenerationContext,
    ) -> Dict[str, GenerationResult]:
        """Generate all sections with coordinated word budget management."""

        # Allocate word budgets across all sections
        section_names = [config.name for config in section_configs]
        self.word_budget_manager.allocate_budgets(section_names)

        # Log budget summary
        budget_summary = self.word_budget_manager.get_budget_summary()
        self.logger.info(
            f"📊 Word Budget Summary: {budget_summary['total_article_words']} words across {len(section_names)} sections"
        )

        for section_name, budget_info in budget_summary["sections"].items():
            self.logger.info(
                f"   {section_name}: {budget_info['target_words']} words ({budget_info['percentage']})"
            )

        # Generate sections with budget constraints
        results = {}
        total_api_calls = 0

        for config in section_configs:
            self.logger.info(
                f"\n{GEAR} {BOLD}Generating section:{RESET} {BRIGHT_CYAN}{config.name}{RESET}"
            )

            # Enhance request with budget-aware settings
            budget_aware_request = self._create_budget_aware_request(
                request, config.name
            )

            # Generate section with enhanced efficiency
            result = self.generate_section_efficiently(
                budget_aware_request, config, context
            )

            # Track metrics
            metrics = self.word_budget_manager.analyze_content(
                result.content, config.name
            )
            total_api_calls += self._estimate_api_calls(result)

            results[config.name] = result

            # Enhanced completion summary
            utilization_color = (
                GREEN
                if 0.8 <= metrics.utilization <= 1.2
                else YELLOW
                if metrics.utilization < 0.8
                else RED
            )
            self.logger.info(
                f"{CHECK} {BOLD}Section '{config.name}' complete:{RESET} "
                f"{utilization_color}{metrics.word_count} words{RESET} "
                f"({utilization_color}{metrics.utilization:.1%}{RESET} of target), "
                f"{BRIGHT_BLUE}{result.iterations_completed} iterations{RESET}"
            )

        # Enhanced final summary with visual formatting
        total_words = sum(len(result.content.split()) for result in results.values())
        budget_utilization = total_words / self.word_budget_manager.total_article_words
        budget_color = (
            GREEN
            if 0.9 <= budget_utilization <= 1.1
            else YELLOW
            if budget_utilization < 0.9
            else RED
        )

        self.logger.info(f"\n{TARGET} {BOLD}Article Generation Complete:{RESET}")
        self.logger.info(
            f"   {CHART} Total words: {budget_color}{total_words}{RESET}/{self.word_budget_manager.total_article_words} "
            f"({budget_color}{budget_utilization:.1%}{RESET})"
        )
        self.logger.info(f"   {STOPWATCH} Total API calls: ~{total_api_calls}")
        self.logger.info(
            f"   {CHECK} Sections completed: {len(results)}/{len(section_configs)}"
        )

        return results

    def generate_section_efficiently(
        self,
        request: GenerationRequest,
        section_config: SectionConfig,
        context: GenerationContext,
    ) -> GenerationResult:
        """Generate a section with enhanced efficiency and budget awareness."""

        # Get section budget
        budget = self.word_budget_manager.get_section_budget(section_config.name)
        if budget:
            self.logger.info(
                f"{CHART} {BOLD}Section budget:{RESET} {BRIGHT_CYAN}{budget.target_words} words{RESET} "
                f"({BRIGHT_CYAN}{budget.percentage:.1%}{RESET} of total article)"
            )

        # Get the prompt template with budget constraints
        prompt_template = self._prompt_repository.get_prompt(
            section_config.prompt_file.replace(".txt", ""), "sections"
        )
        if not prompt_template:
            raise ContentGenerationError(
                f"Prompt template not found: {section_config.prompt_file}",
                section=section_config.name,
            )

        # Enhance prompt with word budget
        enhanced_prompt = self.word_budget_manager.adjust_prompt_for_budget(
            prompt_template.content, section_config.name
        )

        # Generate initial content with budget-aware max_tokens
        initial_content = self._generate_budget_aware_content(
            request, section_config, context, enhanced_prompt
        )

        # Check if content meets budget requirements
        metrics = self.word_budget_manager.analyze_content(
            initial_content, section_config.name
        )

        # If no AI detection required or content is way off budget, return early
        if not section_config.ai_detect:
            self.logger.info(
                f"{DIM}Section {section_config.name} skipping detection (ai_detect=false){RESET}"
            )
            return GenerationResult(
                content=initial_content, threshold_met=True, iterations_completed=1
            )

        if not metrics.within_budget and metrics.utilization > 1.5:
            self.logger.warning(
                f"Content significantly over budget ({metrics.utilization:.1%}), "
                "skipping detection to focus on length reduction"
            )
            # Try to generate shorter content
            shorter_content = self._generate_shorter_content(
                request, section_config, context, enhanced_prompt, metrics
            )
            return GenerationResult(
                content=shorter_content, threshold_met=False, iterations_completed=2
            )

        # Run efficient detection iterations
        return self._generate_with_efficient_detection(
            request, section_config, context, initial_content
        )

    def _create_budget_aware_request(
        self, request: GenerationRequest, section_name: str
    ) -> GenerationRequest:
        """Create a request with budget-aware max_tokens."""
        budget_max_tokens = self.word_budget_manager.calculate_max_tokens(section_name)

        return GenerationRequest(
            material=request.material,
            sections=request.sections,
            provider=request.provider,
            model=request.model,
            ai_detection_threshold=request.ai_detection_threshold,
            human_detection_threshold=request.human_detection_threshold,
            iterations_per_section=request.iterations_per_section,
            temperature=request.temperature,
            max_tokens=min(
                request.max_tokens, budget_max_tokens
            ),  # Use budget constraint
            force_regenerate=request.force_regenerate,
        )

    def _generate_budget_aware_content(
        self,
        request: GenerationRequest,
        section_config: SectionConfig,
        context: GenerationContext,
        prompt_template: str,
    ) -> str:
        """Generate content with budget awareness."""
        try:
            # Format the prompt with context variables
            formatted_prompt = prompt_template.format(**context.variables)

            # Call the API with budget-aware max_tokens
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
                max_tokens=request.max_tokens,  # Already budget-aware from _create_budget_aware_request
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
                f"Failed to generate budget-aware content: {str(e)}",
                section=section_config.name,
            ) from e

    def _generate_shorter_content(
        self,
        request: GenerationRequest,
        section_config: SectionConfig,
        context: GenerationContext,
        prompt_template: str,
        metrics: ContentMetrics,
    ) -> str:
        """Generate shorter content when initial content is too long."""

        budget = self.word_budget_manager.get_section_budget(section_config.name)
        if not budget:
            return ""  # Can't shorten without budget info

        # Create a more restrictive prompt
        length_instruction = f"\n\nCRITICAL: This response MUST be exactly {budget.target_words} words or less. The previous attempt was {metrics.word_count} words which is too long. Be concise and focused."

        restrictive_prompt = prompt_template + length_instruction
        formatted_prompt = restrictive_prompt.format(**context.variables)

        # Use even more restrictive max_tokens
        restrictive_max_tokens = int(budget.target_words * 1.0)  # No buffer

        try:
            # Use temperature_config.content_temp if available, otherwise fallback to legacy temperature
            content_temp = (
                request.temperature_config.content_temp
                if request.temperature_config
                else request.temperature
            )
            content = self._api_client.call_api(
                prompt=formatted_prompt,
                model=request.model,
                temperature=content_temp,  # Use temperature_config instead of legacy field
                max_tokens=restrictive_max_tokens,
                timeout=request.api_timeout,
            )

            return (
                self._clean_and_validate_content(content, section_config.name)
                if content
                else ""
            )

        except Exception as e:
            self.logger.error(
                f"Failed to generate shorter content for {section_config.name}: {e}"
            )
            return ""

    def _generate_with_efficient_detection(
        self,
        request: GenerationRequest,
        section_config: SectionConfig,
        context: GenerationContext,
        initial_content: str,
    ) -> GenerationResult:
        """Generate content with efficient detection - fewer API calls."""

        current_content = initial_content
        ai_score = None
        human_score = None

        # Efficient detection strategy:
        # 1. Only run detection on iterations 1 and final
        # 2. Skip detection if content is way over budget
        # 3. Use configured iterations for detection optimization

        max_efficient_iterations = request.iterations_per_section

        for iteration in range(1, max_efficient_iterations + 1):
            # Get content metrics for detailed logging
            metrics = self.word_budget_manager.analyze_content(
                current_content, section_config.name
            )

            # Enhanced iteration logging with visual formatting
            iteration_color = (
                BRIGHT_BLUE
                if iteration == 1
                else BRIGHT_MAGENTA
                if iteration == max_efficient_iterations
                else CYAN
            )
            self.logger.info(
                f"{CYCLE} {BOLD}Efficient iteration {iteration_color}{iteration}{RESET}{BOLD}/{iteration_color}{max_efficient_iterations}{RESET} "
                f"for {BOLD}{section_config.name}{RESET}"
            )

            # Content analysis with color coding
            budget = self.word_budget_manager.get_section_budget(section_config.name)
            if budget:
                utilization_color = (
                    GREEN
                    if 0.8 <= metrics.utilization <= 1.2
                    else YELLOW
                    if metrics.utilization < 0.8
                    else RED
                )
                self.logger.info(
                    f"{CHART} Content: {utilization_color}{metrics.word_count} words{RESET} "
                    f"(target: {budget.target_words}) - {utilization_color}{metrics.utilization:.1%} utilization{RESET} "
                    f"{'✅' if 0.8 <= metrics.utilization <= 1.2 else '⚠️' if metrics.utilization < 0.8 else '🔴'}"
                )

            # Check if we should skip detection for efficiency
            if self.word_budget_manager.should_skip_detection(
                current_content, section_config.name, iteration
            ):
                self.logger.info(
                    f"Skipping detection for iteration {iteration} (efficiency optimization)"
                )

                # Create dummy scores to continue
                ai_score = AIScore(
                    score=25,
                    feedback="Skipped for efficiency",
                    iteration=iteration,
                    detection_type="ai",
                )
                human_score = AIScore(
                    score=25,
                    feedback="Skipped for efficiency",
                    iteration=iteration,
                    detection_type="human",
                )

                # If this isn't the last iteration, try to improve content
                if iteration < max_efficient_iterations:
                    current_content = self._improve_content_efficiently(
                        current_content, context, request, section_config.name
                    )
                continue

            # Run detection only when necessary
            if iteration == 1 or iteration == max_efficient_iterations:
                self.logger.info(f"🔍 Running detection for iteration {iteration}")

                # Run AI detection
                ai_score = self._detection_service.detect_ai_likelihood(
                    current_content,
                    context,
                    iteration,
                    request.detection_temperature,  # Legacy parameter kept for backward compatibility
                    request.api_timeout,
                    temperature_config=request.temperature_config,  # Pass the temperature_config
                )

                # Run human detection
                human_score = self._detection_service.detect_human_likelihood(
                    current_content,
                    context,
                    iteration,
                    request.detection_temperature,  # Legacy parameter kept for backward compatibility
                    request.api_timeout,
                    temperature_config=request.temperature_config,  # Pass the temperature_config
                )

                # Enhanced detection results logging with visual formatting
                ai_color = (
                    GREEN if ai_score.score <= request.ai_detection_threshold else RED
                )
                human_color = (
                    GREEN
                    if human_score.score <= request.human_detection_threshold
                    else RED
                )
                ai_status = (
                    f"{GREEN}✅ PASS{RESET}"
                    if ai_score.score <= request.ai_detection_threshold
                    else f"{RED}❌ FAIL{RESET}"
                )
                human_status = (
                    f"{GREEN}✅ PASS{RESET}"
                    if human_score.score <= request.human_detection_threshold
                    else f"{RED}❌ FAIL{RESET}"
                )

                self.logger.info(
                    f"{MAGNIFY} {BOLD}Detection Results{RESET} - "
                    f"AI: {ai_color}{ai_score.score}%{RESET} {ai_status} | "
                    f"Human: {human_color}{human_score.score}%{RESET} {human_status}"
                )

                # Check if thresholds are met
                ai_threshold_met = ai_score.score <= request.ai_detection_threshold
                human_threshold_met = (
                    human_score.score <= request.human_detection_threshold
                )

                if ai_threshold_met and human_threshold_met:
                    self.logger.info(f"✅ Thresholds met in iteration {iteration}")
                    return GenerationResult(
                        content=current_content,
                        ai_score=ai_score,
                        human_score=human_score,
                        threshold_met=True,
                        iterations_completed=iteration,
                    )

            # Improve content for next iteration (but only if not the last)
            if iteration < max_efficient_iterations:
                old_word_count = len(current_content.split()) if current_content else 0
                self.logger.info(
                    f"{GEAR} {BOLD}Improving content for iteration {BRIGHT_BLUE}{iteration + 1}{RESET}"
                )

                current_content = self._improve_content_efficiently(
                    current_content, context, request, section_config.name
                )

                new_word_count = len(current_content.split()) if current_content else 0
                word_change = new_word_count - old_word_count
                change_color = (
                    GREEN if word_change > 0 else RED if word_change < 0 else YELLOW
                )
                change_indicator = (
                    ARROW_UP
                    if word_change > 0
                    else ARROW_DOWN
                    if word_change < 0
                    else "→"
                )

                self.logger.info(
                    f"{LIGHTBULB} {BOLD}Content improved:{RESET} {old_word_count} → {new_word_count} words "
                    f"({change_color}{change_indicator}{abs(word_change)}{RESET})"
                )

        # Return final result
        return GenerationResult(
            content=current_content,
            ai_score=ai_score or AIScore(score=50, feedback="Not tested"),
            human_score=human_score or AIScore(score=50, feedback="Not tested"),
            threshold_met=False,
            iterations_completed=max_efficient_iterations,
        )

    def _improve_content_efficiently(
        self,
        content: str,
        context: GenerationContext,
        request: GenerationRequest,
        section_name: str,
    ) -> str:
        """Improve content efficiently with budget awareness."""

        try:
            budget = self.word_budget_manager.get_section_budget(section_name)

            # Load enhanced improvement prompt
            improvement_variables = {
                **context.variables,
                "content": content,
                "target_words": budget.target_words if budget else 200,
                "section_name": section_name,
            }

            # Try to load the enhanced humanization prompt
            try:
                improvement_prompt_path = os.path.join(
                    os.path.dirname(__file__),
                    "../../prompts/improvement/humanize_content.txt",
                )
                if os.path.exists(improvement_prompt_path):
                    with open(improvement_prompt_path, "r") as f:
                        improvement_prompt_template = f.read()
                    improvement_prompt = improvement_prompt_template.format(
                        **improvement_variables
                    )
                else:
                    # Fallback to enhanced inline prompt
                    improvement_prompt = f"""Please rewrite this {section_name} content to sound completely human-written while maintaining exactly {improvement_variables["target_words"]} words:

ORIGINAL CONTENT:
{content}

HUMANIZATION REQUIREMENTS:
- Vary sentence lengths and use contractions naturally
- Replace generic statements with specific examples  
- Use conversational tone as if explaining to a colleague
- Include practical context and real-world applications
- Avoid formulaic language and overly structured formatting
- Add natural qualifiers (often, typically, sometimes)
- Must be exactly {improvement_variables["target_words"]} words

Write as an experienced professional sharing knowledge informally."""
            except Exception as e:
                self.logger.warning(f"Could not load improvement prompt: {e}")
                # Simple fallback
                improvement_prompt = f"""Please improve this {section_name} content to be more human-like and exactly {improvement_variables["target_words"]} words:

{content}

Make it sound more natural, reduce AI-like phrases, and ensure it's exactly {improvement_variables["target_words"]} words."""

            # Generate improved content with budget constraint
            max_tokens = self.word_budget_manager.calculate_max_tokens(section_name)

            # Use temperature_config.improvement_temp if available, otherwise fallback to content_temp or legacy temperature
            improvement_temp = request.temperature
            if request.temperature_config:
                improvement_temp = (
                    request.temperature_config.improvement_temp
                    or request.temperature_config.content_temp
                )

            improved_content = self._api_client.call_api(
                prompt=improvement_prompt,
                model=request.model,
                temperature=improvement_temp,  # Use temperature_config.improvement_temp if available
                max_tokens=max_tokens,
                timeout=request.api_timeout,
            )

            return improved_content.strip() if improved_content else content

        except Exception as e:
            self.logger.error(
                f"Failed to improve content efficiently for {section_name}: {e}"
            )
            return content

    def _estimate_api_calls(self, result: GenerationResult) -> int:
        """Estimate number of API calls used for this section."""
        # Rough estimate based on iterations and detection
        base_calls = result.iterations_completed  # Content generation calls

        if result.ai_score and result.ai_score.score != 50:  # Detection was run
            detection_calls = 2  # AI + Human detection
        else:
            detection_calls = 0

        improvement_calls = max(0, result.iterations_completed - 1)  # Improvement calls

        return base_calls + detection_calls + improvement_calls
