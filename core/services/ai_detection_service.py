"""
Separate AI Detection Service - focused solely on detecting AI-generated patterns.
"""

from core.domain.models import AIScore, GenerationContext, TemperatureConfig
from core.interfaces.services import IAPIClient, IPromptRepository
from core.exceptions import DetectionError
from core.services.prompt_optimizer_compatible import PromptOptimizerCompatible
from modules.logger import get_logger
from config.global_config import get_config, requires_config
from typing import Optional
import time

logger = get_logger("ai_detection_service")


class AIDetectionService:
    """Service focused exclusively on detecting AI-generated content patterns."""

    def __init__(self, api_client: IAPIClient, prompt_repository: IPromptRepository):
        self._api_client = api_client
        self._prompt_repository = prompt_repository
        self.logger = get_logger("ai_detection_service")

        # Get the model from the api_client provider (no hardcoded defaults)
        provider = getattr(api_client, "_provider", None)
        
        # AI-specific prompt variations
        self._ai_prompt_variations = [
            "ai_detection_enhanced",
            "ai_detection_prompt_minimal", 
            "ai_detection_v1",
            "ai_detection_v2",
            "ai_detection_v3",
            "ai_detection_v4",
        ]

        # Initialize AI-specific optimizer
        self._optimizer = PromptOptimizerCompatible()

        # Set model for API calls
        try:
            import sys, os, importlib.util
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            run_path = os.path.join(project_root, "run.py")
            spec = importlib.util.spec_from_file_location("run_module", run_path)
            run_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(run_module)
            provider_models = getattr(run_module, "PROVIDER_MODELS", {})
            self._model = provider_models.get(provider, {}).get("model") if provider else None
        except Exception as e:
            logger.warning(f"Could not load model from run.py: {e}")
            self._model = None

    @requires_config
    def detect_ai_patterns(
        self,
        content: str,
        context: GenerationContext,
        iteration: int = 1,
        temperature: float = None,  # Will use config default if None
        timeout: int = None,        # Will use config default if None
        temperature_config: Optional[TemperatureConfig] = None,
    ) -> AIScore:
        """
        Detect AI-generated patterns in content.
        
        Returns AIScore where:
        - Low score (0-25%) = Good (minimal AI patterns detected)
        - High score (75-100%) = Poor (heavy AI patterns detected)
        """
        config = get_config()
        
        # Use config values instead of hardcoded defaults
        if temperature is None:
            temperature = config.get_detection_temperature()
        if timeout is None:
            timeout = config.get_api_timeout()
            
        section_name = context.get_variable("section_name", "Unknown")
        
        # Get optimal AI detection prompt for this iteration and section
        optimal_prompt = self._optimizer.get_optimal_prompt(
            "ai", iteration, section_name, self._ai_prompt_variations
        )
        
        logger.info(f"🤖 AI Detection - Using prompt: {optimal_prompt} (iteration {iteration})")

        # Use config-specific temperature from temperature_config, or fall back to parameter
        detection_temp = (
            temperature_config.detection_temp if temperature_config 
            else temperature
        )

        return self._run_ai_detection(
            content, context, iteration, optimal_prompt, section_name, detection_temp, timeout
        )

    def _run_ai_detection(
        self,
        content: str,
        context: GenerationContext,
        iteration: int,
        prompt_name: str,
        section_name: str,
        temperature: float,
        timeout: int,
    ) -> AIScore:
        """Run AI detection with specific prompt and track performance."""
        try:
            # Get the AI detection prompt
            prompt_template = self._prompt_repository.get_prompt(prompt_name, "detection")
            if not prompt_template:
                raise DetectionError(f"AI detection prompt not found: {prompt_name}")

            formatted_prompt = prompt_template.content.format(content=content)

            # Make API call for AI detection
            start_time = time.time()
            try:
                response = self._api_client.call_api(
                    prompt=formatted_prompt,
                    model=self._model,
                    temperature=temperature,
                    max_tokens=get_config().get_max_large_response_tokens(),
                    timeout=timeout,
                )
                duration = time.time() - start_time

                if duration > 20:
                    self.logger.warning(f"⚠️ Slow AI detection response: {duration:.2f}s")

            except Exception as e:
                duration = time.time() - start_time
                self.logger.error(f"❌ AI detection API call failed after {duration:.2f}s: {str(e)}")
                return AIScore(
                    score=50,  # Neutral score on failure
                    feedback=f"AI detection failed due to API error: {str(e)}",
                    iteration=iteration,
                    detection_type="ai",
                )

            # Parse AI detection response
            score, feedback = self._parse_ai_detection_response(response)

            # Track AI detection performance
            config = get_config()
            success_threshold = config.get_ai_detection_threshold()
            success = score <= success_threshold  # Success = score below threshold
            self._optimizer.track_performance(
                prompt_name, "ai", score, iteration, success, section_name
            )

            # Display AI detection results
            self._display_ai_detection_results(section_name, score, feedback, iteration, prompt_name)

            return AIScore(
                score=score,
                feedback=feedback,
                iteration=iteration,
                detection_type="ai",
            )

        except Exception as e:
            logger.error(f"AI detection failed: {str(e)}")
            raise DetectionError(f"Failed to run AI detection: {str(e)}", "ai", len(content)) from e

    def _parse_ai_detection_response(self, response: str) -> tuple[int, str]:
        """Parse AI detection response and extract score."""
        import re
        
        # Look for confidence patterns specific to AI detection
        patterns = [
            r"AI DETECTION CONFIDENCE:\s*(\d+)%",
            r"AI CONFIDENCE:\s*(\d+)%", 
            r"CONFIDENCE:\s*(\d+)%",
            r"(\d+)%",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                score = int(match.group(1))
                # Extract feedback (everything before the confidence line)
                feedback_match = re.split(pattern, response, flags=re.IGNORECASE)
                feedback = feedback_match[0].strip() if feedback_match else response[:200]
                return score, feedback
        
        # Fallback if no pattern matches
        logger.warning(f"Could not parse AI detection score from: {response[:100]}")
        return 50, response[:200]  # Neutral score with truncated response

    def _display_ai_detection_results(self, section_name: str, score: int, feedback: str, iteration: int, prompt_name: str):
        """Display AI detection results with appropriate formatting."""
        # Visual progress bar for AI detection
        progress_blocks = "■" * (score // 10) + "□" * (10 - score // 10)
        status = "✅ PASS" if score <= 25 else "❌ FAIL"
        
        print(f"🤖 AI Detection: {score}% [{progress_blocks}] {status}")
        if iteration > 1:
            print(f"   Prompt: {prompt_name} | Iteration: {iteration}")
        
        logger.debug(f"AI Detection Details - Section: {section_name}, Score: {score}%, Feedback: {feedback[:100]}")

    def get_ai_prompt_performance(self) -> dict:
        """Get performance statistics for AI detection prompts."""
        return self._optimizer.get_performance_stats("ai")
