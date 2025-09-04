"""
AI Detection Configuration Optimizer

This module uses DeepSeek to analyze Winston AI detection results and dynamically
optimize the ai_detection.yaml configuration to improve content generation quality.

The optimizer:
1. Analyzes Winston results and current configuration
2. Uses DeepSeek to determine optimal enhancement flags
3. Modifies ai_detection.yaml with improved settings
4. Maintains backup/restore capabilities for safety
"""

import yaml
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

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
        "winston_human_range": (70, 100)
    }

logger = logging.getLogger(__name__)

class AIDetectionConfigOptimizer:
    """Optimizes AI detection configuration using DeepSeek analysis of Winston results."""

    def __init__(self, config_path: str = "config/ai_detection.yaml"):
        self.config_path = Path(config_path)
        # Initialize DeepSeek client when needed
        self._deepseek_client = None
        self.optimization_flags = [
            "conversational_style",        # Core: Keep enabled
            "natural_language_patterns",   # Core: Keep enabled  
            "cultural_adaptation",         # Core: Keep enabled
            "sentence_variability",        # Core: Keep enabled
            # Disable over-engineering features
            "human_error_simulation",      # Disabled: Can backfire
            "emotional_depth",             # Disabled: Over-engineering
            "paragraph_structure",         # Disabled: Let content flow naturally
            "lexical_diversity",           # Disabled: Over-engineering vocabulary
            "rhetorical_devices",          # Disabled: Can seem forced
            "personal_anecdotes"           # Disabled: Keep professional tone
        ]

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
                with open(self.config_path, 'r') as f:
                    return yaml.safe_load(f) or {}
            else:
                logger.warning(f"Configuration file not found: {self.config_path}")
                return {}
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return {}

    def optimize_config(self, winston_result: Dict[str, Any],
                       content: str, current_config: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[str]]:
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
            # Generate optimization prompt for DeepSeek
            prompt = self._generate_optimization_prompt(winston_result, content, current_config)

            # Get DeepSeek's optimization recommendations
            response = self.deepseek_client.generate_simple(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.3
            )

            # Parse the optimization response
            optimized_config = self._parse_optimization_response(response, current_config)

            # Extract the DeepSeek response text for logging
            if hasattr(response, 'content'):
                deepseek_response_text = response.content
            else:
                deepseek_response_text = str(response)

            # Validate the optimized configuration
            if self._validate_config(optimized_config):
                # Create backup before modifying
                self._create_backup()

                # Save the optimized configuration
                self._save_config(optimized_config)

                logger.info("Successfully optimized AI detection configuration")
                return optimized_config, deepseek_response_text
            else:
                logger.warning("Optimized configuration validation failed, using current config")
                return current_config, deepseek_response_text

        except Exception as e:
            logger.error(f"Failed to optimize configuration: {e}")
            return current_config, None

    def _generate_optimization_prompt(self, winston_result: Dict[str, Any],
                                    content: str, config: Dict[str, Any]) -> str:
        """Generate the prompt for DeepSeek to optimize the configuration using comprehensive Winston AI data."""

        # Extract comprehensive metrics from Winston result
        overall_score = winston_result.get('overall_score', 0)
        confidence = winston_result.get('confidence', 0)
        classification = winston_result.get('classification', 'unclear')

        # Extract detailed analysis from Winston response
        details = winston_result.get('details', {})
        readability_score = details.get('readability_score')
        attack_detected = details.get('attack_detected', {})

        # Extract sentence-level analysis if available
        sentences_data = details.get('sentences', [])
        sentence_analysis = self._analyze_sentence_patterns(sentences_data)

        # Current flag states
        current_flags = {flag: config.get(flag, False) for flag in self.optimization_flags}

        # Build comprehensive analysis summary
        analysis_summary = self._build_analysis_summary(
            overall_score, confidence, classification, readability_score,
            attack_detected, sentence_analysis, content
        )

        prompt = f"""You are an expert AI content optimization specialist with deep knowledge of Winston AI detection patterns. Analyze the comprehensive Winston AI detection results and recommend precise, data-driven enhancements for technical content.

{analysis_summary}

CURRENT CONFIGURATION:
- Enhancement Flags: {json.dumps(current_flags, indent=2)}
- Target Score: {AI_DETECTION_CONFIG["target_score"]} (realistic for technical content)

CONTENT SAMPLE (first 600 characters for pattern analysis):
{content[:600]}...

WINDSOR AI-DRIVEN OPTIMIZATION FRAMEWORK:

1. **SCORE-BASED STRATEGY** (Primary Driver):
   - Score < 20: Maximum enhancement - content needs fundamental human-like restructuring
   - Score 20-35: Balanced enhancement - focus on natural flow and readability
   - Score 35-50: Targeted refinement - address specific detection patterns
   - Score > 50: Minimal adjustments - preserve working patterns

2. **READABILITY-BASED ADJUSTMENTS** (Secondary Driver):
   - Readability < 40: Enable conversational_style and natural_language_patterns
   - Readability 40-60: Focus on sentence_variability for rhythm
   - Readability > 60: Cultural adaptation may be sufficient

3. **SENTENCE PATTERN ANALYSIS** (Tactical Driver):
   - Uniform sentence lengths: Enable sentence_variability
   - Complex vocabulary clusters: Enable natural_language_patterns
   - Repetitive structures: Enable conversational_style

4. **ATTACK DETECTION RESPONSE** (Safety Driver):
   - If manipulation detected: Prioritize natural_language_patterns
   - If pattern anomalies: Enable sentence_variability

TECHNICAL CONTENT PRINCIPLES:
- Preserve technical accuracy and domain expertise
- Maintain professional credibility over casual tone
- Focus on natural information flow, not forced personality
- Address specific AI detection triggers identified by Winston

Return ONLY a JSON object with data-driven optimization settings:
{{
  "conversational_style": true/false,
  "natural_language_patterns": true/false,
  "cultural_adaptation": true/false,
  "sentence_variability": true/false,
  "human_error_simulation": false,
  "emotional_depth": false,
  "paragraph_structure": false,
  "lexical_diversity": false,
  "rhetorical_devices": false,
  "personal_anecdotes": false,
  "reasoning": "Detailed explanation of Winston data-driven optimization approach"
}}

Provide specific, actionable recommendations based on the Winston AI analysis data."""

        return prompt

    def _analyze_sentence_patterns(self, sentences_data: list) -> Dict[str, Any]:
        """Analyze sentence-level patterns from Winston AI response."""
        if not sentences_data:
            return {"available": False}

        try:
            scores = [s.get('score', 0) for s in sentences_data if isinstance(s, dict)]
            texts = [s.get('text', '') for s in sentences_data if isinstance(s, dict)]

            if not scores:
                return {"available": False}

            # Calculate sentence-level statistics
            avg_sentence_score = sum(scores) / len(scores)
            score_variance = sum((s - avg_sentence_score) ** 2 for s in scores) / len(scores)

            # Analyze sentence length patterns
            sentence_lengths = [len(text.split()) for text in texts if text]
            avg_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0

            # Identify problematic sentences (very low scores)
            low_score_sentences = [i for i, score in enumerate(scores) if score < 20]

            return {
                "available": True,
                "sentence_count": len(sentences_data),
                "avg_sentence_score": avg_sentence_score,
                "score_variance": score_variance,
                "avg_sentence_length": avg_length,
                "low_score_count": len(low_score_sentences),
                "low_score_percentage": (len(low_score_sentences) / len(sentences_data)) * 100 if sentences_data else 0
            }

        except Exception as e:
            logger.warning(f"Error analyzing sentence patterns: {e}")
            return {"available": False, "error": str(e)}

    def _build_analysis_summary(self, overall_score: float, confidence: float,
                              classification: str, readability_score: Optional[float],
                              attack_detected: Dict, sentence_analysis: Dict,
                              content: str) -> str:
        """Build comprehensive analysis summary from Winston AI data."""

        summary_parts = []

        # Core metrics
        summary_parts.append("WINDSOR AI ANALYSIS RESULTS:")
        summary_parts.append(f"- Overall Score: {overall_score:.1f}/100 ({classification})")
        summary_parts.append(f"- Confidence: {confidence:.2f}")
        summary_parts.append(f"- Target Range: {AI_DETECTION_CONFIG['target_score']} (realistic technical content)")

        # Readability analysis
        if readability_score is not None:
            readability_level = "Low" if readability_score < 40 else "Medium" if readability_score < 60 else "High"
            summary_parts.append(f"- Readability Score: {readability_score:.1f} ({readability_level})")
            if readability_score < 40:
                summary_parts.append("  → Content may be too complex - needs simplification")
            elif readability_score > 60:
                summary_parts.append("  → Content may be too simple - needs technical depth")

        # Attack detection
        if attack_detected:
            summary_parts.append(f"- Attack Detection: {attack_detected}")
            if any(attack_detected.values()):
                summary_parts.append("  → Manipulation patterns detected - prioritize natural patterns")

        # Sentence-level analysis
        if sentence_analysis.get("available", False):
            summary_parts.append("SENTENCE-LEVEL ANALYSIS:")
            summary_parts.append(f"- Sentences Analyzed: {sentence_analysis['sentence_count']}")
            summary_parts.append(f"- Average Sentence Score: {sentence_analysis['avg_sentence_score']:.1f}")
            summary_parts.append(f"- Score Variance: {sentence_analysis['score_variance']:.2f}")
            summary_parts.append(f"- Average Sentence Length: {sentence_analysis['avg_sentence_length']:.1f} words")

            if sentence_analysis['low_score_percentage'] > 20:
                summary_parts.append(f"- Problem Sentences: {sentence_analysis['low_score_percentage']:.1f}% have very low scores")
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
            sentences = content.split('.')
            words = content.split()
            paragraphs = content.split('\n\n')

            characteristics = {}

            # Sentence analysis
            if len(sentences) > 0:
                avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
                characteristics["Average Sentence Length"] = f"{avg_sentence_length:.1f} words"

            # Vocabulary analysis
            unique_words = len(set(words))
            total_words = len(words)
            if total_words > 0:
                lexical_diversity = unique_words / total_words
                characteristics["Lexical Diversity"] = f"{lexical_diversity:.3f}"

            # Structure analysis
            characteristics["Paragraph Count"] = str(len(paragraphs))
            characteristics["Total Words"] = str(total_words)

            # Technical indicators
            technical_terms = sum(1 for word in words if len(word) > 8)  # Long technical terms
            if total_words > 0:
                technical_density = technical_terms / total_words
                characteristics["Technical Term Density"] = f"{technical_density:.3f}"

            return characteristics

        except Exception as e:
            logger.warning(f"Error analyzing content characteristics: {e}")
            return {}

    def _parse_optimization_response(self, response, current_config: Dict[str, Any]) -> Dict[str, Any]:
        """Parse DeepSeek's optimization response and apply changes to config."""

        try:
            # Extract content from APIResponse object
            if hasattr(response, 'content'):
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
            if 'reasoning' in optimization:
                logger.info(f"DeepSeek optimization reasoning: {optimization['reasoning']}")

            return updated_config

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse DeepSeek optimization response: {e}")
            logger.error(f"Response was: {response_text if 'response_text' in locals() else response}")
            return current_config
        except Exception as e:
            logger.error(f"Error parsing optimization response: {e}")
            return current_config

    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate the optimized configuration."""
        try:
            # Ensure all required flags are present
            for flag in self.optimization_flags:
                if flag not in config:
                    logger.warning(f"Missing optimization flag: {flag}")
                    return False

            # Ensure flags are boolean values
            for flag in self.optimization_flags:
                if not isinstance(config[flag], bool):
                    logger.warning(f"Invalid flag type for {flag}: {type(config[flag])}")
                    return False

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
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            logger.info(f"Saved optimized configuration to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise

    def restore_backup(self, backup_timestamp: Optional[str] = None) -> bool:
        """Restore configuration from backup."""
        try:
            if backup_timestamp:
                backup_path = self.config_path.with_suffix(f".backup_{backup_timestamp}.yaml")
            else:
                # Find the most recent backup
                backup_files = list(self.config_path.parent.glob(f"{self.config_path.stem}.backup_*.yaml"))
                if not backup_files:
                    logger.warning("No backup files found")
                    return False
                backup_path = max(backup_files, key=lambda p: p.stat().st_mtime)

            if backup_path.exists():
                backup_path.replace(self.config_path)
                logger.info(f"Restored configuration from backup: {backup_path}")
                return True
            else:
                logger.warning(f"Backup file not found: {backup_path}")
                return False

        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False
