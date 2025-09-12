"""
AI Detection Configuration Optimizer - Core Module

Main optimization class providing configuration analysis and updates
based on Winston AI detection results using DeepSeek recommendations.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml
from api.client_manager import create_api_client

from .prompt_optimizer import PromptOptimizer
from .validation import ConfigValidator
from .utils import AnalysisUtils

# Import centralized AI detection configuration
try:
    from run import AI_DETECTION_CONFIG
except ImportError:
    # Fallback if run.py is not available
    AI_DETECTION_CONFIG = {
        "target_score": 70.0,
        "winston_ai_range": (0, 30),
        "winston_unclear_range": (30, 70),
        "winston_human_range": (70, 100),
    }

logger = logging.getLogger(__name__)


class AIDetectionConfigOptimizer:
    """Optimizes AI detection configuration using DeepSeek analysis of Winston results."""

    def __init__(self, config_path: str = "config/ai_detection.yaml"):
        self.config_path = Path(config_path)
        # Initialize DeepSeek client when needed
        self._deepseek_client = None

        # OPTIMIZATION: Enhanced flag set for higher AI detection scores
        self.optimization_flags = [
            # Core foundational enhancements
            "conversational_style",  # Core: Natural flow
            "natural_language_patterns",  # Core: Address manipulation detection
            "sentence_variability",  # Core: Break uniform patterns
            "cultural_adaptation",  # Core: Author authenticity
            "emotional_depth",  # Core: Human nuance
            "paragraph_structure",  # Core: Break regimented paragraphs
            "lexical_diversity",  # Core: Vary vocabulary
            # Advanced linguistic patterns for high scores
            "syntactic_complexity_variation",  # Advanced: Vary sentence structure complexity
            "discourse_marker_diversity",  # Advanced: Use varied transition words
            "pragmatic_context_markers",  # Advanced: Add contextual cues
            "information_structure_variation",  # Advanced: Vary information presentation
            "register_shifting",  # Advanced: Mix formal/informal language
            "hedging_and_qualification",  # Advanced: Add uncertainty markers
            "epistemic_markers",  # Advanced: Show knowledge limitations
            # Cognitive authenticity markers
            "mid_thought_interruptions",  # Cognitive: Simulate thinking pauses
            "cognitive_dissonance_indicators",  # Cognitive: Show internal conflict
            "uncertainty_expressions",  # Cognitive: Express doubt naturally
            "subjective_evaluation_markers",  # Cognitive: Add personal opinions
            "personal_reflection_indicators",  # Cognitive: Show introspection
            "contextual_memory_references",  # Cognitive: Reference prior knowledge
            # Advanced structural variations
            "paragraph_rhythm_variation",  # Structural: Vary paragraph pacing
            "thematic_progression_markers",  # Structural: Show topic development
            "coherence_breaking_devices",  # Structural: Natural topic shifts
            "narrative_digression_patterns",  # Structural: Allow tangents
            "perspective_shifting",  # Structural: Change viewpoints
            "temporal_reference_diversity",  # Structural: Vary time references
            # Contextual and cultural adaptation
            "domain_specific_jargon_variation",  # Contextual: Mix technical terms
            "cultural_reference_integration",  # Cultural: Add relevant references
            "situational_context_markers",  # Contextual: Show awareness of context
            "professional_experience_indicators",  # Professional: Show expertise
            "expertise_level_markers",  # Professional: Demonstrate knowledge depth
            # Rhetorical and stylistic devices
            "metaphorical_language_usage",  # Rhetorical: Use metaphors naturally
            "rhetorical_question_patterns",  # Rhetorical: Ask questions for emphasis
            "contrastive_construction_usage",  # Rhetorical: Use contrast for effect
            "emphasis_and_intensification",  # Stylistic: Add emphasis markers
            "politeness_strategies",  # Social: Use polite language appropriately
            "persuasive_language_markers",  # Persuasive: Natural persuasion techniques
        ]

        # Track previous configurations for rollback
        self.previous_configs = []

        # Learning mechanism for successful configurations
        self.successful_configs = []

        # OPTIMIZATION: Enhanced state management
        self.baseline_configs = []  # Preserve high-performing configurations
        self.baseline_score_threshold = 50.0  # Score threshold for baseline preservation
        self.rollback_threshold = 15.0  # Score drop that triggers rollback

        # Initialize helper components
        self.prompt_optimizer = PromptOptimizer(self.optimization_flags)
        self.validator = ConfigValidator(self.config_path)
        self.utils = AnalysisUtils()

    @property
    def deepseek_client(self):
        """Lazy initialization of DeepSeek client."""
        if self._deepseek_client is None:
            self._deepseek_client = create_api_client("deepseek")
        return self._deepseek_client

    def _load_current_config(self) -> Dict[str, Any]:
        """Load the current configuration from file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, "r") as f:
                    return yaml.safe_load(f) or {}
            else:
                logger.warning(f"Configuration file not found: {self.config_path}")
                return {}
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return {}

    def optimize_config(
        self,
        winston_result: Dict[str, Any],
        content: str,
        current_config: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], Optional[str]]:
        """
        Optimize the AI detection configuration based on Winston results.

        Args:
            winston_result: Winston AI detection analysis results
            content: The generated content that was analyzed
            current_config: Current ai_detection.yaml configuration

        Returns:
            Tuple of (updated configuration dictionary, deepseek response text)
        """
        try:
            # Store winston_result for validation method access
            self._current_winston_result = winston_result

            # Generate optimization prompt for DeepSeek
            prompt = self.prompt_optimizer.generate_optimization_prompt(
                winston_result, content, current_config
            )

            # Get DeepSeek's optimization recommendations
            response = self.deepseek_client.generate_simple(
                prompt=prompt, max_tokens=1000, temperature=0.3
            )

            # Parse the optimization response
            optimized_config = self.prompt_optimizer.parse_optimization_response(
                response, current_config
            )

            # Extract the DeepSeek response text for logging
            if hasattr(response, "content"):
                deepseek_response_text = response.content
            else:
                deepseek_response_text = str(response)

            # Validate the optimized configuration
            if self.validator.validate_config(optimized_config):
                # OPTIMIZATION: Check if rollback is needed before applying changes
                current_score = winston_result.get("overall_score", 0)
                baseline_score = self._get_baseline_score()

                if baseline_score is not None and self._should_rollback(
                    current_score, baseline_score
                ):
                    logger.warning(
                        "Rolling back to previous configuration due to score degradation"
                    )
                    if self.rollback_config():
                        # Return the rolled back config
                        rolled_back_config = self._load_current_config()
                        return (
                            rolled_back_config,
                            "Configuration rolled back due to score degradation",
                        )

                # Create backup before modifying
                self.validator.create_backup()

                # Save the optimized configuration
                self.validator.save_config(optimized_config)

                # OPTIMIZATION: Preserve baseline if score is good
                self._preserve_baseline_config(optimized_config, current_score)

                # Record successful configuration for learning
                self._record_successful_config(optimized_config, winston_result)

                logger.info("Successfully optimized AI detection configuration")
                return optimized_config, deepseek_response_text
            else:
                logger.warning(
                    "Optimized configuration validation failed, using current config"
                )
                return current_config, deepseek_response_text

        except Exception as e:
            logger.error(f"Failed to optimize configuration: {e}")
            return current_config, None

    def _should_rollback(self, new_score: float, baseline_score: float) -> bool:
        """Determine if configuration should be rolled back based on score comparison."""
        score_drop = baseline_score - new_score
        should_rollback = score_drop > self.rollback_threshold
        
        if should_rollback:
            logger.warning(
                f"Score dropped {score_drop:.1f} points from baseline {baseline_score:.1f} "
                f"(threshold: {self.rollback_threshold})"
            )
        
        return should_rollback

    def _preserve_baseline_config(self, config: Dict[str, Any], score: float) -> None:
        """Preserve configuration as baseline if score meets threshold."""
        if score >= self.baseline_score_threshold:
            baseline_entry = {
                "config": config.copy(),
                "score": score,
                "timestamp": str(datetime.now()),
            }
            
            self.baseline_configs.append(baseline_entry)
            
            # Keep only the best 5 baseline configurations
            self.baseline_configs = sorted(
                self.baseline_configs, key=lambda x: x["score"], reverse=True
            )[:5]
            
            logger.info(f"Preserved baseline configuration with score {score:.1f}")

    def _record_successful_config(
        self, config: Dict[str, Any], winston_result: Dict[str, Any]
    ) -> None:
        """Record configuration that produced good results for learning."""
        score = winston_result.get("overall_score", 0)
        
        if score >= self.baseline_score_threshold:
            success_entry = {
                "config": config.copy(),
                "score": score,
                "winston_data": winston_result,
                "timestamp": str(datetime.now()),
            }
            
            self.successful_configs.append(success_entry)
            
            # Keep only recent successful configurations (last 10)
            self.successful_configs = self.successful_configs[-10:]
            
            logger.info(f"Recorded successful configuration with score {score:.1f}")

    def _get_baseline_score(self) -> Optional[float]:
        """Get the baseline score from preserved configurations."""
        try:
            if not self.baseline_configs:
                return None

            # Return the highest score from baseline configs
            best_score = max(config["score"] for config in self.baseline_configs)
            logger.info(f"Retrieved baseline score: {best_score:.1f}")
            return best_score
        except Exception as e:
            logger.warning(f"Failed to get baseline score: {e}")
            return None

    def rollback_config(self) -> bool:
        """Rollback to previous configuration if available."""
        return self.validator.rollback_config()

    def get_learning_insights(self) -> Dict[str, Any]:
        """Extract learning insights from successful configurations."""
        return self.utils.get_learning_insights(self.successful_configs)
