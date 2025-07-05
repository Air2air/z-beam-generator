"""
Natural Voice Detection Service - Detecting AUTHENTIC Professional Voice

This service focuses on detecting genuine, professional expertise voice patterns that:
1. Show natural rhythm and flow without forced casualness
2. Demonstrate real industry knowledge and experience  
3. Use authentic technical language without oversimplification
4. Maintain professional credibility without robotic formality
5. AVOID exaggerated "humanization" tricks (excessive casual language, forced colloquialisms)

CRITICAL: Natural Voice ≠ Forced Humanization
- GOOD Natural Voice: Professional expertise with natural flow
- BAD Forced Humanization: Excessive casual language, trying too hard to sound human
"""

from generator.core.domain.models import AIScore, GenerationContext, TemperatureConfig
from generator.core.interfaces.services import IAPIClient, IPromptRepository
from generator.core.exceptions import DetectionError
from generator.core.services.prompt_optimizer_compatible import PromptOptimizerCompatible
from generator.modules.logger import get_logger
from typing import Optional
import time

logger = get_logger("natural_voice_detection_service")


class NaturalVoiceDetectionService:
    """Service focused exclusively on detecting Natural Voice authenticity."""

    def __init__(self, api_client: IAPIClient, prompt_repository: IPromptRepository):
        self._api_client = api_client
        self._prompt_repository = prompt_repository
        self.logger = get_logger("natural_voice_detection_service")

        # Get the model from the api_client provider (no hardcoded defaults)
        provider = getattr(api_client, "_provider", None)
        
        # Natural Voice specific prompt variations focused on AUTHENTIC professional voice
        self._natural_voice_prompt_variations = [
            "natural_voice_enhanced",
            "natural_voice_professional", 
            "natural_voice_v1",
            "natural_voice_v2",
            "natural_voice_v3",
            "natural_voice_rhythm",
            "natural_voice_expertise",
        ]

        # Initialize Natural Voice specific optimizer
        self._optimizer = PromptOptimizerCompatible()

        # Set model for API calls
        try:
            import os
            import importlib.util
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

    def detect_natural_voice_authenticity(
        self,
        content: str,
        context: GenerationContext,
        iteration: int = 1,
        temperature: float = None,
        timeout: int = None,
        temperature_config: Optional[TemperatureConfig] = None,
    ) -> AIScore:
        """
        Detect Natural Voice authenticity in content.
        
        Returns AIScore where:
        - Low score (15-25%) = Good (authentic professional voice)
        - High score (75-100%) = Poor (exaggerated humanization or artificial voice)
        """
        # Set defaults from config if not provided
        if temperature is None:
            from config.global_config import get_config
            temperature = get_config().get_detection_temperature()
        if timeout is None:
            from config.global_config import get_config
            timeout = get_config().get_api_timeout()
            
        section_name = context.get_variable("section_name", "Unknown")
        
        # Get optimal Natural Voice detection prompt for this iteration and section
        optimal_prompt = self._optimizer.get_optimal_prompt(
            "natural_voice", iteration, section_name, self._natural_voice_prompt_variations
        )
        
        logger.info(f"👤 Natural Voice - Using prompt: {optimal_prompt} (iteration {iteration})")

        # Use Natural Voice specific temperature from config
        detection_temp = (
            temperature_config.detection_temp if temperature_config else temperature
        )

        return self._run_natural_voice_detection(
            content, context, iteration, optimal_prompt, section_name, detection_temp, timeout
        )

    def _run_natural_voice_detection(
        self,
        content: str,
        context: GenerationContext,
        iteration: int,
        prompt_name: str,
        section_name: str,
        temperature: float,
        timeout: int,
    ) -> AIScore:
        """Run Natural Voice detection with specific prompt and track performance."""
        try:
            # Get the Natural Voice detection prompt
            prompt_template = self._prompt_repository.get_prompt(prompt_name, "detection")
            if not prompt_template:
                raise DetectionError(f"Natural Voice detection prompt not found: {prompt_name}")

            formatted_prompt = prompt_template.content.format(content=content)

            # Make API call for Natural Voice detection
            start_time = time.time()
            try:
                response = self._api_client.call_api(
                    prompt=formatted_prompt,
                    model=self._model,
                    temperature=temperature,
                    max_tokens=4000,
                    timeout=timeout,
                )
                duration = time.time() - start_time

                if duration > 20:
                    self.logger.warning(f"⚠️ Slow Natural Voice detection response: {duration:.2f}s")

            except Exception as e:
                duration = time.time() - start_time
                self.logger.error(f"❌ Natural Voice detection API call failed after {duration:.2f}s: {str(e)}")
                return AIScore(
                    score=50,  # Neutral score on failure
                    feedback=f"Natural Voice detection failed due to API error: {str(e)}",
                    iteration=iteration,
                    detection_type="natural_voice",
                )

            # Parse Natural Voice detection response
            score, feedback = self._parse_natural_voice_response(response)

            # Track Natural Voice detection performance
            # Success for Natural Voice = score in optimal range (15-25%)
            success = 15 <= score <= 25
            self._optimizer.track_performance(
                prompt_name, "natural_voice", score, iteration, success, section_name
            )

            # Display Natural Voice detection results
            self._display_natural_voice_results(section_name, score, feedback, iteration, prompt_name)

            return AIScore(
                score=score,
                feedback=feedback,
                iteration=iteration,
                detection_type="natural_voice",
            )

        except Exception as e:
            logger.error(f"Natural Voice detection failed: {str(e)}")
            raise DetectionError(f"Failed to run Natural Voice detection: {str(e)}", "natural_voice", len(content)) from e

    def _parse_natural_voice_response(self, response: str) -> tuple[int, str]:
        """Parse Natural Voice detection response and extract score."""
        import re
        
        # Look for confidence patterns specific to Natural Voice detection
        patterns = [
            r"NATURAL VOICE CONFIDENCE:\s*(\d+)%",
            r"NATURAL VOICE:\s*(\d+)%",
            r"VOICE CONFIDENCE:\s*(\d+)%",
            r"AUTHENTICITY:\s*(\d+)%",
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
        logger.warning(f"Could not parse Natural Voice score from: {response[:100]}")
        return 50, response[:200]  # Neutral score with truncated response

    def _display_natural_voice_results(self, section_name: str, score: int, feedback: str, iteration: int, prompt_name: str):
        """Display Natural Voice detection results with appropriate formatting."""
        # Visual progress bar for Natural Voice detection
        progress_blocks = "■" * (score // 10) + "□" * (10 - score // 10)
        
        # Natural Voice scoring logic: 15-25% is optimal range
        if 15 <= score <= 25:
            status = "✅ EXCELLENT"
            color = "🟢"
        elif 10 <= score <= 30:
            status = "✅ GOOD"
            color = "🟡"
        elif score < 10:
            status = "⚠️ TOO ARTIFICIAL"
            color = "🔵"
        else:
            status = "❌ OVER-HUMANIZED"
            color = "🔴"
        
        print(f"👤 Natural Voice: {score}% [{progress_blocks}] {color} {status}")
        if 15 <= score <= 25:
            print(f"   🎯 Perfect authenticity range!")
        if iteration > 1:
            print(f"   Prompt: {prompt_name} | Iteration: {iteration}")
        
        logger.debug(f"Natural Voice Details - Section: {section_name}, Score: {score}%, Feedback: {feedback[:100]}")

    def get_natural_voice_performance(self) -> dict:
        """Get performance statistics for Natural Voice detection prompts."""
        return self._optimizer.get_performance_stats("natural_voice")

    def is_score_in_optimal_range(self, score: int) -> bool:
        """Check if the Natural Voice score is in the optimal authenticity range."""
        return 15 <= score <= 25

    def get_score_interpretation(self, score: int) -> str:
        """Get human-readable interpretation of Natural Voice score."""
        if score < 10:
            return "Too artificial - lacks authentic professional voice"
        elif 10 <= score < 15:
            return "Good authenticity but could be more natural"
        elif 15 <= score <= 25:
            return "Excellent authentic professional voice"
        elif 25 < score <= 35:
            return "Good but slightly over-emphasized"
        else:
            return "Over-humanized with exaggerated characteristics"
