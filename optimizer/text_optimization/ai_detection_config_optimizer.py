"""
AI Detection Configuration Optimizer

Uses DeepSeek to analyze Winston AI detection results and dynamically
optimize the ai_detection.yaml configuration to improve content generation quality.

The optimizer:
1. Analyzes Winston results and current configuration
2. Uses DeepSeek to determine optimal enhancement flags
3. Modifies ai_detection.yaml with improved settings
4. Maintains backup/restore capabilities for safety
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from api.client_manager import create_api_client

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
        self.baseline_score_threshold = (
            50.0  # Score threshold for baseline preservation
        )
        self.rollback_threshold = 15.0  # Score drop that triggers rollback

    @property
    def deepseek_client(self):
        """Lazy initialization of DeepSeek client."""
        if self._deepseek_client is None:
            from api.client_manager import create_api_client

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
            prompt = self._generate_optimization_prompt(
                winston_result, content, current_config
            )

            # Get DeepSeek's optimization recommendations
            response = self.deepseek_client.generate_simple(
                prompt=prompt, max_tokens=1000, temperature=0.3
            )

            # Parse the optimization response
            optimized_config = self._parse_optimization_response(
                response, current_config
            )

            # Extract the DeepSeek response text for logging
            if hasattr(response, "content"):
                deepseek_response_text = response.content
            else:
                deepseek_response_text = str(response)

            # Validate the optimized configuration
            if self._validate_config(optimized_config):
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
                self._create_backup()

                # Save the optimized configuration
                self._save_config(optimized_config)

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

    def _generate_optimization_prompt(
        self, winston_result: Dict[str, Any], content: str, config: Dict[str, Any]
    ) -> str:
        """Generate the prompt for DeepSeek to optimize the configuration using comprehensive Winston AI data."""

        # Extract comprehensive metrics from Winston result
        overall_score = winston_result.get("overall_score", 0)
        confidence = winston_result.get("confidence", 0)
        classification = winston_result.get("classification", "unclear")

        # Extract detailed analysis from Winston response
        details = winston_result.get(
            "analysis", {}
        )  # Changed from 'details' to 'analysis'
        readability_score = details.get("readability_score")
        attack_detected = details.get("attack_detected", {})

        # Extract sentence-level analysis if available
        sentences_data = details.get("sentences", [])
        sentence_analysis = self._analyze_sentence_patterns(sentences_data)

        # Get learning insights
        learning_insights = self.get_learning_insights()
        recommended_flags = learning_insights.get("recommended_flags", [])

        learning_context = ""
        if recommended_flags:
            learning_context = f"\nLEARNING INSIGHTS:\n- Previously successful flags: {', '.join(recommended_flags)}\n- Consider these proven combinations for better results"

        # Current flag states
        current_flags = {
            flag: config.get(flag, False) for flag in self.optimization_flags
        }

        # Build comprehensive analysis summary
        analysis_summary = self._build_analysis_summary(
            overall_score,
            confidence,
            classification,
            readability_score,
            attack_detected,
            sentence_analysis,
            content,
        )

        # Build comprehensive analysis summary
        analysis_summary = self._build_analysis_summary(
            overall_score,
            confidence,
            classification,
            readability_score,
            attack_detected,
            sentence_analysis,
            content,
        )

        prompt = f"""You are an expert AI content optimization specialist with deep knowledge of linguistic patterns, cognitive authenticity markers, and advanced rhetorical techniques. Analyze Winston AI detection results and provide targeted, multi-layered enhancements for achieving high detection scores.

{analysis_summary}

CONTENT ANALYSIS:
- Overall Score: {overall_score:.1f}/100 ({classification})
- Readability: {readability_score if readability_score is not None else 'N/A'}
- Low-Scoring Sentences: {sentence_analysis.get('low_score_percentage', 0):.1f}%

{learning_context}

SCORE-BASED ENHANCEMENT STRATEGY:

1. **CRITICAL SCORES (< 40)**: Aggressive multi-layered approach
   - Apply 3-4 enhancements simultaneously
   - Focus on: natural_language_patterns, syntactic_complexity_variation, cognitive_dissonance_indicators, mid_thought_interruptions
   - Target: Core manipulation detection + cognitive authenticity

2. **MODERATE SCORES (40-60)**: Authenticity enhancement
   - Apply 2-3 enhancements per iteration
   - Focus on: cultural_adaptation, personal_reflection_indicators, uncertainty_expressions, discourse_marker_diversity
   - Target: Human-like imperfections and cultural markers

3. **GOOD SCORES (60-80)**: Refinement and sophistication
   - Apply 1-2 enhancements per iteration
   - Focus on: rhetorical_question_patterns, metaphorical_language_usage, paragraph_rhythm_variation, pragmatic_context_markers
   - Target: Advanced rhetorical devices and structural variation

4. **EXCELLENT SCORES (80+)**: Fine-tuning
   - Apply 1 enhancement per iteration
   - Focus on: epistemic_markers, politeness_strategies, expertise_level_markers
   - Target: Subtle authenticity markers

GRADUAL APPLICATION PRINCIPLES:
- Start with foundational enhancements, then layer advanced techniques
- Combine linguistic + cognitive + structural approaches for maximum impact
- Use learning history to identify most effective enhancement combinations
- Prioritize enhancements that address specific detection patterns

CURRENT FLAGS: {json.dumps(current_flags, indent=2)}

Return ONLY JSON with targeted enhancements for this score range:
{{
  "natural_language_patterns": true/false,
  "sentence_variability": true/false,
  "paragraph_structure": true/false,
  "cultural_adaptation": true/false,
  "lexical_diversity": true/false,
  "emotional_depth": true/false,
  "conversational_style": true/false,
  "syntactic_complexity_variation": true/false,
  "discourse_marker_diversity": true/false,
  "pragmatic_context_markers": true/false,
  "information_structure_variation": true/false,
  "register_shifting": true/false,
  "hedging_and_qualification": true/false,
  "epistemic_markers": true/false,
  "mid_thought_interruptions": true/false,
  "cognitive_dissonance_indicators": true/false,
  "uncertainty_expressions": true/false,
  "subjective_evaluation_markers": true/false,
  "personal_reflection_indicators": true/false,
  "contextual_memory_references": true/false,
  "paragraph_rhythm_variation": true/false,
  "thematic_progression_markers": true/false,
  "coherence_breaking_devices": true/false,
  "narrative_digression_patterns": true/false,
  "perspective_shifting": true/false,
  "temporal_reference_diversity": true/false,
  "domain_specific_jargon_variation": true/false,
  "cultural_reference_integration": true/false,
  "situational_context_markers": true/false,
  "professional_experience_indicators": true/false,
  "expertise_level_markers": true/false,
  "metaphorical_language_usage": true/false,
  "rhetorical_question_patterns": true/false,
  "contrastive_construction_usage": true/false,
  "emphasis_and_intensification": true/false,
  "politeness_strategies": true/false,
  "persuasive_language_markers": true/false,
  "reasoning": "Specific analysis: which enhancements to enable/disable and why, focusing on score-based strategy and multi-layered approach"
}}

Focus on GRADUAL improvements that combine multiple enhancement types for breakthrough score improvements."""

        return prompt

    def _analyze_sentence_patterns(self, sentences_data: list) -> Dict[str, Any]:
        """Analyze sentence-level patterns from Winston AI response."""
        if not sentences_data:
            return {"available": False}

        try:
            scores = [s.get("score", 0) for s in sentences_data if isinstance(s, dict)]
            texts = [s.get("text", "") for s in sentences_data if isinstance(s, dict)]

            # Filter out None scores
            valid_scores = [score for score in scores if score is not None]
            valid_texts = [
                text for score, text in zip(scores, texts) if score is not None
            ]

            if not valid_scores:
                return {"available": False}

            scores = valid_scores
            texts = valid_texts

            # Calculate sentence-level statistics
            avg_sentence_score = sum(scores) / len(scores)
            score_variance = sum((s - avg_sentence_score) ** 2 for s in scores) / len(
                scores
            )

            # Analyze sentence length patterns
            sentence_lengths = [len(text.split()) for text in texts if text]
            avg_length = (
                sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
            )

            # Identify problematic sentences (very low scores)
            low_score_sentences = [i for i, score in enumerate(scores) if score < 20]

            return {
                "available": True,
                "sentence_count": len(sentences_data),
                "avg_sentence_score": avg_sentence_score,
                "score_variance": score_variance,
                "avg_sentence_length": avg_length,
                "low_score_count": len(low_score_sentences),
                "low_score_percentage": (len(low_score_sentences) / len(sentences_data))
                * 100
                if sentences_data
                else 0,
            }

        except Exception as e:
            logger.warning(f"Error analyzing sentence patterns: {e}")
            return {"available": False, "error": str(e)}

    def _build_analysis_summary(
        self,
        overall_score: float,
        confidence: float,
        classification: str,
        readability_score: Optional[float],
        attack_detected: Dict,
        sentence_analysis: Dict,
        content: str,
    ) -> str:
        """Build comprehensive analysis summary from Winston AI data."""

        summary_parts = []

        # Core metrics
        summary_parts.append("WINDSOR AI ANALYSIS RESULTS:")
        summary_parts.append(
            f"- Overall Score: {overall_score:.1f}/100 ({classification})"
        )
        summary_parts.append(f"- Confidence: {confidence:.2f}")
        summary_parts.append(
            f"- Target Range: {AI_DETECTION_CONFIG['target_score']} (realistic technical content)"
        )

        # Readability analysis
        if readability_score is not None:
            readability_level = (
                "Low"
                if readability_score < 40
                else "Medium"
                if readability_score < 60
                else "High"
            )
            summary_parts.append(
                f"- Readability Score: {readability_score:.1f} ({readability_level})"
            )
            if readability_score < 40:
                summary_parts.append(
                    "  → Content may be too complex - needs simplification"
                )
            elif readability_score > 60:
                summary_parts.append(
                    "  → Content may be too simple - needs technical depth"
                )

        # Attack detection
        if attack_detected:
            summary_parts.append(f"- Attack Detection: {attack_detected}")
            if any(attack_detected.values()):
                summary_parts.append(
                    "  → Manipulation patterns detected - prioritize natural patterns"
                )

        # Sentence-level analysis
        if sentence_analysis.get("available", False):
            summary_parts.append("SENTENCE-LEVEL ANALYSIS:")
            summary_parts.append(
                f"- Sentences Analyzed: {sentence_analysis['sentence_count']}"
            )
            summary_parts.append(
                f"- Average Sentence Score: {sentence_analysis['avg_sentence_score']:.1f}"
            )
            summary_parts.append(
                f"- Score Variance: {sentence_analysis['score_variance']:.2f}"
            )
            summary_parts.append(
                f"- Average Sentence Length: {sentence_analysis['avg_sentence_length']:.1f} words"
            )

            if sentence_analysis["low_score_percentage"] > 20:
                summary_parts.append(
                    f"- Problem Sentences: {sentence_analysis['low_score_percentage']:.1f}% have very low scores"
                )
                summary_parts.append("  → Multiple sentences triggering AI detection")

        # Content characteristics analysis
        content_analysis = self._analyze_content_characteristics(content)
        if content_analysis:
            summary_parts.append("CONTENT CHARACTERISTICS:")
            for characteristic, value in content_analysis.items():
                summary_parts.append(f"- {characteristic}: {value}")

        return "\n".join(summary_parts)

    def _analyze_content_characteristics(self, content: str) -> Dict[str, str]:
        """Analyze basic content characteristics that might affect AI detection."""
        try:
            sentences = content.split(".")
            words = content.split()
            paragraphs = content.split("\n\n")

            characteristics = {}

            # Sentence analysis
            if len(sentences) > 0:
                avg_sentence_length = sum(len(s.split()) for s in sentences) / len(
                    sentences
                )
                characteristics[
                    "Average Sentence Length"
                ] = f"{avg_sentence_length:.1f} words"

            # Vocabulary analysis
            unique_words = len(set(words))
            total_words = len(words)
            if total_words > 0:
                lexical_diversity = unique_words / total_words
                characteristics["Lexical Diversity"] = f"{lexical_diversity:.3f}"

            # Structure analysis
            characteristics["Paragraph Count"] = str(len(paragraphs))
            characteristics["Total Words"] = str(total_words)

            # Paragraph structure analysis
            if len(paragraphs) > 1:
                paragraph_lengths = [len(p.split()) for p in paragraphs if p.strip()]
                if paragraph_lengths:
                    avg_paragraph_length = sum(paragraph_lengths) / len(
                        paragraph_lengths
                    )
                    characteristics[
                        "Average Paragraph Length"
                    ] = f"{avg_paragraph_length:.1f} words"

                    # Check for regimented structure (similar paragraph lengths)
                    length_variance = sum(
                        (l - avg_paragraph_length) ** 2 for l in paragraph_lengths
                    ) / len(paragraph_lengths)
                    characteristics[
                        "Paragraph Length Variance"
                    ] = f"{length_variance:.1f}"

                    if (
                        length_variance < 50
                    ):  # Low variance indicates regimented structure
                        characteristics[
                            "Paragraph Structure"
                        ] = "Regimented (similar lengths)"
                    else:
                        characteristics[
                            "Paragraph Structure"
                        ] = "Varied (natural lengths)"

            # Technical indicators
            technical_terms = sum(
                1 for word in words if len(word) > 8
            )  # Long technical terms
            if total_words > 0:
                technical_density = technical_terms / total_words
                characteristics["Technical Term Density"] = f"{technical_density:.3f}"

            return characteristics

        except Exception as e:
            logger.warning(f"Error analyzing content characteristics: {e}")
            return {}

    def _parse_optimization_response(
        self, response, current_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse DeepSeek's optimization response and apply changes to config."""

        try:
            # Extract content from APIResponse object
            if hasattr(response, "content"):
                response_text = response.content
            else:
                response_text = str(response)

            # Clean up the response text
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            # Parse the JSON response
            optimization = json.loads(response_text.strip())

            # Create updated config with optimized flags
            updated_config = current_config.copy()

            # Apply the optimized flags
            for flag in self.optimization_flags:
                if flag in optimization:
                    updated_config[flag] = optimization[flag]

            # Log the reasoning
            if "reasoning" in optimization:
                logger.info(
                    f"DeepSeek optimization reasoning: {optimization['reasoning']}"
                )

            return updated_config

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse DeepSeek optimization response: {e}")
            logger.error(
                f"Response was: {response_text if 'response_text' in locals() else response}"
            )
            return current_config
        except Exception as e:
            logger.error(f"Error parsing optimization response: {e}")
            return current_config

    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate the optimized configuration with rollback capability."""
        try:
            # Store current config for potential rollback
            current_config = self._load_current_config()
            self.previous_configs.append(current_config)

            # Keep only last 3 configs for memory efficiency
            if len(self.previous_configs) > 3:
                self.previous_configs.pop(0)

            # Ensure all core flags are present
            for flag in self.optimization_flags:
                if flag not in config:
                    logger.warning(f"Missing optimization flag: {flag}")
                    return False

            # Ensure flags are boolean values
            for flag in self.optimization_flags:
                if not isinstance(config[flag], bool):
                    logger.warning(
                        f"Invalid flag type for {flag}: {type(config[flag])}"
                    )
                    return False

            # Dynamic enhancement limits based on current score context
            # Allow more enhancements for lower scores that need aggressive optimization
            enabled_flags = [flag for flag in self.optimization_flags if config[flag]]
            
            # Get current score from winston_result if available (passed from optimize_config)
            current_score = 50  # Default fallback
            if hasattr(self, '_current_winston_result') and self._current_winston_result:
                current_score = self._current_winston_result.get("overall_score", 50)
            
            if current_score < 40:
                max_enhancements = 4  # Aggressive for critical scores
                logger.info(f"Critical score ({current_score:.1f}) - allowing up to {max_enhancements} enhancements")
            elif current_score < 60:
                max_enhancements = 3  # Moderate for low-medium scores
                logger.info(f"Moderate score ({current_score:.1f}) - allowing up to {max_enhancements} enhancements")
            elif current_score < 80:
                max_enhancements = 2  # Conservative for good scores
                logger.info(f"Good score ({current_score:.1f}) - allowing up to {max_enhancements} enhancements")
            else:
                max_enhancements = 1  # Minimal for excellent scores
                logger.info(f"Excellent score ({current_score:.1f}) - allowing up to {max_enhancements} enhancements")

            if len(enabled_flags) > max_enhancements:
                logger.warning(
                    f"Too many flags enabled ({len(enabled_flags)}) > max {max_enhancements}. "
                    f"Enforcing intelligent optimization."
                )

                # Keep only highest priority enhancements
                prioritized_flags = self._prioritize_enhancements_from_config(config)
                selected_flags = prioritized_flags[:max_enhancements]

                # Disable excess flags
                for flag in enabled_flags:
                    if flag not in selected_flags:
                        config[flag] = False

                logger.info(
                    f"Selected {len(selected_flags)} enhancements: {selected_flags}"
                )

            return True

        except Exception as e:
            logger.error(f"Configuration validation error: {e}")
            return False

    def _create_backup(self) -> None:
        """Create a backup of the current configuration."""
        try:
            if self.config_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = self.config_path.with_suffix(f".backup_{timestamp}.yaml")
                backup_path.write_text(self.config_path.read_text())
                logger.info(f"Created configuration backup: {backup_path}")
        except Exception as e:
            logger.warning(f"Failed to create configuration backup: {e}")

    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save the optimized configuration to file."""
        try:
            with open(self.config_path, "w") as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            logger.info(f"Saved optimized configuration to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise

    def _record_successful_config(
        self, config: Dict[str, Any], winston_result: Dict[str, Any]
    ) -> None:
        """Record successful configuration for learning."""
        try:
            score = winston_result.get("overall_score", 0)
            # Record all configurations, not just successful ones, to learn from failures too
            successful_entry = {
                "config": config.copy(),
                "score": score,
                "timestamp": datetime.now(),
                "enabled_flags": [
                    flag for flag in self.optimization_flags if config.get(flag, False)
                ],
            }
            self.successful_configs.append(successful_entry)

            # Keep only last 10 configs for better learning
            if len(self.successful_configs) > 10:
                self.successful_configs.pop(0)

            logger.info(f"Recorded configuration with score {score:.1f} for learning")
        except Exception as e:
            logger.warning(f"Failed to record configuration: {e}")

    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights from configuration history for learning."""
        try:
            if not self.successful_configs:
                return {
                    "recommended_flags": [],
                    "insights": "No configuration history recorded yet",
                }

            # Analyze all configurations, not just successful ones
            all_flags = []
            high_score_configs = []

            for config_entry in self.successful_configs:
                flags = config_entry.get("enabled_flags", [])
                all_flags.extend(flags)

                # Track high-performing configurations
                if config_entry.get("score", 0) > 60:
                    high_score_configs.append(config_entry)

            # Count flag frequencies
            flag_counts = {}
            for flag in all_flags:
                flag_counts[flag] = flag_counts.get(flag, 0) + 1

            # Get most frequently used flags
            recommended_flags = sorted(
                flag_counts.keys(), key=lambda x: flag_counts[x], reverse=True
            )

            # Prioritize flags that appear in high-scoring configurations
            if high_score_configs:
                high_score_flags = []
                for config in high_score_configs:
                    high_score_flags.extend(config.get("enabled_flags", []))

                high_score_flag_counts = {}
                for flag in high_score_flags:
                    high_score_flag_counts[flag] = (
                        high_score_flag_counts.get(flag, 0) + 1
                    )

                # Boost high-scoring flags in recommendations
                recommended_flags = sorted(
                    high_score_flag_counts.keys(),
                    key=lambda x: high_score_flag_counts[x],
                    reverse=True,
                )
                # Add other flags that might be useful
                for flag in flag_counts:
                    if flag not in recommended_flags:
                        recommended_flags.append(flag)

            # Limit to top 3 recommendations
            recommended_flags = recommended_flags[:3]

            insights = {
                "recommended_flags": recommended_flags,
                "total_configs_analyzed": len(self.successful_configs),
                "flag_usage_counts": flag_counts,
                "high_score_configs": len(high_score_configs),
                "insights": f"Analyzed {len(self.successful_configs)} configurations. Top flags: {', '.join(recommended_flags)}",
            }

            logger.info(f"Learning insights: {insights['insights']}")
            return insights

        except Exception as e:
            logger.warning(f"Error getting learning insights: {e}")
            return {"recommended_flags": [], "insights": "Error retrieving insights"}

    def rollback_config(self) -> bool:
        """Rollback to the previous configuration."""
        try:
            if not self.previous_configs:
                logger.warning("No previous configurations to rollback to")
                return False

            # Get the last previous config
            previous_config = self.previous_configs[-1]

            # Save current config as backup
            self._create_backup()

            # Restore previous config
            self._save_config(previous_config)

            logger.info("Successfully rolled back to previous configuration")
            return True

            logger.info("Successfully rolled back to previous configuration")
            return True

        except Exception as e:
            logger.error(f"Failed to rollback configuration: {e}")
            return False

    def _should_rollback(self, new_score: float, baseline_score: float) -> bool:
        """Determine if configuration should rollback based on score degradation."""
        degradation = baseline_score - new_score
        should_rollback = degradation > self.rollback_threshold
        if should_rollback:
            logger.warning(
                f"Score degradation detected: {baseline_score:.1f} → {new_score:.1f} "
                f"({degradation:.1f} point drop > {self.rollback_threshold} threshold)"
            )
        return should_rollback

    def _prioritize_enhancements_from_config(self, config: Dict[str, Any]) -> List[str]:
        """Prioritize enhancements based on configuration settings and DeepSeek recommendations."""
        try:
            enabled_flags = [
                flag for flag in self.optimization_flags if config.get(flag, False)
            ]

            # Get learning insights to dynamically adjust priorities
            learning_insights = self.get_learning_insights()
            recommended_flags = learning_insights.get("recommended_flags", [])

            # Dynamic priority order based on current score and DeepSeek recommendations
            current_score = self._current_winston_result.get("overall_score", 50) if hasattr(self, '_current_winston_result') and self._current_winston_result else 50
            
            if current_score < 40:
                # Critical scores: Focus on core + cognitive authenticity
                base_priority_order = [
                    "natural_language_patterns", "syntactic_complexity_variation",
                    "cognitive_dissonance_indicators", "mid_thought_interruptions",
                    "sentence_variability", "paragraph_structure", "lexical_diversity"
                ]
            elif current_score < 60:
                # Moderate scores: Authenticity and cultural markers
                base_priority_order = [
                    "cultural_adaptation", "personal_reflection_indicators",
                    "uncertainty_expressions", "discourse_marker_diversity",
                    "natural_language_patterns", "sentence_variability", "emotional_depth"
                ]
            elif current_score < 80:
                # Good scores: Advanced rhetorical and structural
                base_priority_order = [
                    "rhetorical_question_patterns", "metaphorical_language_usage",
                    "paragraph_rhythm_variation", "pragmatic_context_markers",
                    "cultural_adaptation", "lexical_diversity", "conversational_style"
                ]
            else:
                # Excellent scores: Fine-tuning with subtle markers
                base_priority_order = [
                    "epistemic_markers", "politeness_strategies", "expertise_level_markers",
                    "emphasis_and_intensification", "persuasive_language_markers"
                ]

            # Boost priority of DeepSeek-recommended flags
            if recommended_flags:
                # Move recommended flags to the front
                adjusted_order = recommended_flags.copy()
                for flag in base_priority_order:
                    if flag not in adjusted_order:
                        adjusted_order.append(flag)
                priority_order = adjusted_order
                logger.info(
                    f"Adjusted priority order based on learning: {priority_order}"
                )
            else:
                priority_order = base_priority_order

            # Sort enabled flags by dynamic priority
            prioritized = []
            for flag in priority_order:
                if flag in enabled_flags:
                    prioritized.append(flag)

            return prioritized

        except Exception as e:
            logger.warning(f"Error prioritizing enhancements: {e}")
            return enabled_flags  # Return as-is if prioritization fails

    def _preserve_baseline_config(self, config: Dict[str, Any], score: float) -> None:
        """Preserve high-performing configurations as baselines."""
        try:
            if score >= self.baseline_score_threshold:
                baseline_entry = {
                    "config": config.copy(),
                    "score": score,
                    "timestamp": datetime.now(),
                }
                self.baseline_configs.append(baseline_entry)

                # Keep only top 3 baseline configs
                if len(self.baseline_configs) > 3:
                    self.baseline_configs.sort(key=lambda x: x["score"], reverse=True)
                    self.baseline_configs = self.baseline_configs[:3]

                logger.info(f"Preserved baseline configuration with score {score:.1f}")
        except Exception as e:
            logger.warning(f"Failed to preserve baseline config: {e}")

    def _analyze_content_stability(
        self, content: str, previous_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze content stability across iterations."""
        try:
            if not previous_content:
                return {"stability_score": 100.0, "change_percentage": 0.0}

            # Calculate content changes
            current_words = len(content.split())
            previous_words = len(previous_content.split())

            if previous_words == 0:
                return {"stability_score": 100.0, "change_percentage": 0.0}

            change_percentage = (
                abs(current_words - previous_words) / previous_words * 100
            )

            # Stability score (lower change = higher stability)
            stability_score = max(0, 100 - change_percentage)

            return {
                "stability_score": stability_score,
                "change_percentage": change_percentage,
                "current_words": current_words,
                "previous_words": previous_words,
            }
        except Exception as e:
            logger.warning(f"Failed to analyze content stability: {e}")
            return {"stability_score": 50.0, "change_percentage": 0.0}

    def _learn_from_iterations(
        self, iteration_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Learn patterns from iteration history to improve future optimizations."""
        try:
            if not iteration_history:
                return {"insights": "No iteration history available"}

            # Analyze score patterns
            scores = [entry.get("score", 0) for entry in iteration_history]
            score_changes = []
            for i in range(1, len(scores)):
                score_changes.append(scores[i] - scores[i - 1])

            # Identify successful patterns
            successful_iterations = [
                entry for entry in iteration_history if entry.get("score", 0) > 50
            ]

            insights = {
                "total_iterations": len(iteration_history),
                "average_score": sum(scores) / len(scores) if scores else 0,
                "score_trend": "improving"
                if score_changes and sum(score_changes) > 0
                else "declining",
                "successful_iterations": len(successful_iterations),
                "insights": f"Analyzed {len(iteration_history)} iterations with {len(successful_iterations)} successful ones",
            }

            logger.info(f"Learned from iteration history: {insights['insights']}")
            return insights

        except Exception as e:
            logger.warning(f"Failed to learn from iterations: {e}")
            return {"insights": "Error analyzing iteration history"}

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
