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

logger = logging.getLogger(__name__)

class AIDetectionConfigOptimizer:
    """Optimizes AI detection configuration using DeepSeek analysis of Winston results."""

    def __init__(self, config_path: str = "config/ai_detection.yaml"):
        self.config_path = Path(config_path)
        # Initialize DeepSeek client when needed
        self._deepseek_client = None
        self.optimization_flags = [
            "conversational_style",
            "natural_language_patterns", 
            "human_error_simulation",
            "cultural_adaptation",
            "emotional_depth",
            "sentence_variability",
            "paragraph_structure",
            "lexical_diversity",
            "rhetorical_devices",
            "personal_anecdotes"
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
        """Generate the prompt for DeepSeek to optimize the configuration."""

        # Extract key metrics from Winston result
        overall_score = winston_result.get('overall_score', 0)
        sentence_scores = winston_result.get('sentence_scores', [])
        analysis = winston_result.get('analysis', {})

        # Current flag states
        current_flags = {flag: config.get(flag, False) for flag in self.optimization_flags}

        prompt = f"""You are an expert AI content optimization specialist. Analyze the Winston AI detection results and current configuration, then recommend optimal settings for the enhancement flags to improve human-like content generation.

CURRENT SITUATION:
- Overall Winston Score: {overall_score}/100 (higher = more human-like)
- Target Score: {config.get('target_score', 70)}
- Current Enhancement Flags: {json.dumps(current_flags, indent=2)}

WINSTON ANALYSIS DETAILS:
{json.dumps(analysis, indent=2)}

SENTENCE-BY-SENTENCE SCORES:
{json.dumps(sentence_scores[:10], indent=2)}  # First 10 sentences

CONTENT SAMPLE (first 500 characters):
{content[:500]}...

ENHANCEMENT FLAGS EXPLANATION:
- conversational_style: Use conversational language patterns and natural flow
- natural_language_patterns: Apply natural language variations and idioms
- human_error_simulation: Simulate minor human-like errors (typos, hesitations)
- cultural_adaptation: Adapt to cultural/national contexts and references
- emotional_depth: Add emotional depth and personality to writing
- sentence_variability: Vary sentence length and structure (short/long sentences)
- paragraph_structure: Use varied paragraph lengths and transitions
- lexical_diversity: Employ rich vocabulary and word choice variety
- rhetorical_devices: Include metaphors, analogies, and rhetorical questions
- personal_anecdotes: Add brief personal stories or examples (use sparingly)

TASK:
Based on the Winston analysis, determine which enhancement flags should be enabled/disabled to improve the overall score. Consider:

1. If score is very low (<30): Enable all human-like features aggressively
2. If score is low (30-50): Focus on basic human elements (conversational, natural patterns, sentence variability)
3. If score is medium (50-70): Add structural improvements (paragraph structure, lexical diversity)
4. If score is high (>70): Fine-tune with advanced techniques (rhetorical devices, emotional depth)

Return ONLY a JSON object with the optimized flag settings:
{{
  "conversational_style": true/false,
  "natural_language_patterns": true/false,
  "human_error_simulation": true/false,
  "cultural_adaptation": true/false,
  "emotional_depth": true/false,
  "sentence_variability": true/false,
  "paragraph_structure": true/false,
  "lexical_diversity": true/false,
  "rhetorical_devices": true/false,
  "personal_anecdotes": true/false,
  "reasoning": "Brief explanation of your optimization decisions"
}}

Be strategic - enable flags progressively based on current score level, and disable flags that might be counterproductive."""

        return prompt

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
