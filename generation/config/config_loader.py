"""
Processing Configuration Loader

Single source of truth for ALL generation configuration.
Loads from generation/config.yaml and provides typed access.

Usage:
    from generation.config.config_loader import ProcessingConfig
    
    config = ProcessingConfig()
    threshold = config.get_ai_threshold()
    temperature = config.get_temperature()
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from shared.utils.yaml_utils import load_yaml

logger = logging.getLogger(__name__)

# Path to config file
CONFIG_DIR = Path(__file__).parent.parent  # generation/ directory
CONFIG_FILE = CONFIG_DIR / "config.yaml"


class ProcessingConfig:
    """
    Central configuration manager for generation pipeline.
    
    Loads from generation/config.yaml and provides typed accessors.
    All generation components should use this instead of hardcoded values.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Load processing configuration.
        
        Args:
            config_path: Optional custom config file path
        """
        self.config_path = Path(config_path) if config_path else CONFIG_FILE
        self.config = self._load_config()
        self._text_field_config: Optional[Dict[str, Any]] = None
        logger.info(f"Loaded processing config from {self.config_path}")

    def _load_text_field_config(self) -> Dict[str, Any]:
        """Load centralized text field configuration."""
        if self._text_field_config is None:
            config_path = Path(__file__).parent.parent / "text_field_config.yaml"
            if not config_path.exists():
                raise FileNotFoundError(
                    f"Text field config not found: {config_path}. "
                    "Expected location: generation/text_field_config.yaml"
                )

            config = load_yaml(config_path)
            if not isinstance(config, dict):
                raise ValueError("Text field config must contain a YAML dictionary")

            self._text_field_config = config

        return self._text_field_config

    def _resolve_text_field_name(self, component_type: str) -> str:
        """Resolve component aliases to canonical field name."""
        text_cfg = self._load_text_field_config()
        aliases = text_cfg.get('aliases', {})
        if aliases and not isinstance(aliases, dict):
            raise ValueError("Invalid aliases block in generation/text_field_config.yaml")
        return aliases.get(component_type, component_type)

    def _get_text_field_length_spec(self, component_type: str) -> Dict[str, Any]:
        """Get centralized base length spec for a text field name."""
        text_cfg = self._load_text_field_config()
        defaults = text_cfg.get('defaults')
        if not isinstance(defaults, dict):
            raise ValueError("Missing defaults block in generation/text_field_config.yaml")

        fields = text_cfg.get('fields')
        if not isinstance(fields, dict):
            raise ValueError("Missing fields block in generation/text_field_config.yaml")

        field_name = self._resolve_text_field_name(component_type)
        if field_name not in fields:
            raise KeyError(
                f"Missing centralized field config for component_type='{component_type}' "
                f"(resolved field: '{field_name}')"
            )

        field_cfg = fields[field_name] or {}
        if not isinstance(field_cfg, dict):
            raise ValueError(
                f"Invalid field config for '{field_name}' in generation/text_field_config.yaml"
            )

        target = field_cfg.get('base_length', defaults.get('base_length'))

        if not isinstance(target, int) or target <= 0:
            raise ValueError(f"Invalid base_length for '{field_name}': {target}")

        multiplier = defaults.get('base_length_multiplier', 1.0)
        if not isinstance(multiplier, (int, float)) or multiplier <= 0:
            raise ValueError(
                f"Invalid defaults.base_length_multiplier in generation/text_field_config.yaml: {multiplier}"
            )

        target = max(1, int(round(target * float(multiplier))))

        return {
            'target': target,
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """Load YAML configuration file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(
                f"Processing config not found: {self.config_path}\n"
                f"Expected location: generation/config.yaml"
            )
        
        try:
            config = load_yaml(self.config_path)
            
            if not isinstance(config, dict):
                raise ValueError("Config file must contain a YAML dictionary")
            
            return config
        except Exception as e:
            raise RuntimeError(f"Failed to load config from {self.config_path}: {e}")

    def _require_value(self, path: str, expected_type: Optional[type] = None) -> Any:
        """
        Require a configuration value at dot-path and optionally validate type.

        Args:
            path: Dot-separated config path (e.g. "api.base_temperature")
            expected_type: Optional expected Python type

        Returns:
            Configuration value

        Raises:
            KeyError: If required key path is missing
            ValueError: If value type is invalid
        """
        keys = path.split('.')
        value: Any = self.config

        for key in keys:
            if not isinstance(value, dict):
                raise KeyError(
                    f"Invalid config structure while resolving '{path}': "
                    f"'{key}' parent is not a dictionary"
                )
            if key not in value:
                raise KeyError(f"Missing required config key: {path}")
            value = value[key]

        if expected_type is not None and not isinstance(value, expected_type):
            raise ValueError(
                f"Invalid config type for '{path}': expected {expected_type.__name__}, "
                f"got {type(value).__name__}"
            )

        return value

    def get_required_config(self, path: str, expected_type: Optional[type] = None) -> Any:
        """
        Public accessor for required config values by dot-path.

        Args:
            path: Dot-separated config path (e.g. "constants.api_helper.max_tokens")
            expected_type: Optional expected Python type

        Returns:
            Configuration value
        """
        return self._require_value(path, expected_type)
    
    # =========================================================================
    # INTENSITY SLIDERS (User-facing controls) - NOW 1-10 SCALE
    # =========================================================================
    
    def get_author_voice_intensity(self) -> int:
        """Get author voice intensity (1-10)."""
        return self._require_value('author_voice_intensity', int)
    
    def get_personality_intensity(self) -> int:
        """Get personality intensity (1-10)."""
        return self._require_value('personality_intensity', int)
    
    def get_engagement_style(self) -> int:
        """Get engagement style (1-10)."""
        return self._require_value('engagement_style', int)
    
    def get_emotional_intensity(self) -> int:
        """Get emotional intensity (1-10)."""
        return self._require_value('emotional_intensity', int)
    
    def get_technical_language_intensity(self) -> int:
        """Get technical language intensity (1-10)."""
        return self._require_value('technical_language_intensity', int)
    
    def get_context_specificity(self) -> int:
        """Get context specificity (1-10)."""
        return self._require_value('context_specificity', int)
    
    def get_sentence_rhythm_variation(self) -> int:
        """Get sentence rhythm variation (1-10)."""
        return self._require_value('sentence_rhythm_variation', int)
    
    def get_imperfection_tolerance(self) -> int:
        """Get imperfection tolerance (1-10)."""
        return self._require_value('imperfection_tolerance', int)
    
    def get_structural_predictability(self) -> int:
        """Get structural predictability (1-10)."""
        return self._require_value('structural_predictability', int)
    
    def get_ai_avoidance_intensity(self) -> int:
        """Get AI avoidance intensity (1-10)."""
        return self._require_value('ai_avoidance_intensity', int)
    
    def get_length_variation_range(self) -> int:
        """
        Get legacy-compatible length variation range (1-10).

        Compatibility shim: derives value from centralized
        generation/text_field_config.yaml randomization_range.
        """
        min_factor, max_factor = self.get_text_length_randomization_factors()

        max_deviation = max(abs(float(min_factor) - 1.0), abs(float(max_factor) - 1.0))
        derived_slider = int(round(max_deviation * 10))
        return max(1, min(10, derived_slider))

    def get_text_length_randomization_factors(self) -> tuple[float, float]:
        """Get centralized text-length randomization factors from text_field_config."""
        text_cfg = self._load_text_field_config()
        randomization_cfg = text_cfg.get('randomization_range')
        if not isinstance(randomization_cfg, dict):
            raise ValueError(
                "Missing required config block: randomization_range in generation/text_field_config.yaml"
            )

        min_factor = randomization_cfg.get('min_factor')
        max_factor = randomization_cfg.get('max_factor')
        if not isinstance(min_factor, (int, float)) or not isinstance(max_factor, (int, float)):
            raise ValueError("randomization_range.min_factor and max_factor must be numeric")
        if min_factor <= 0 or max_factor <= 0 or min_factor > max_factor:
            raise ValueError(
                f"Invalid randomization_range: min_factor={min_factor}, max_factor={max_factor}"
            )

        return float(min_factor), float(max_factor)
    
    def get_learning_target(self) -> float:
        """
        Get human score learning target for adaptive improvement.
        
        Returns:
            Target human score (0-100) that system tries to achieve through learning
        """
        value = self._require_value('human_score_learning_target')
        if not isinstance(value, (int, float)):
            raise ValueError(
                f"Invalid config type for 'human_score_learning_target': "
                f"expected number, got {type(value).__name__}"
            )
        return float(value)
    
    def get_humanness_intensity(self) -> int:
        """
        Get humanness_intensity (1-10 scale) for AI evasion control.
        
        Returns:
            1 = Minimal (fast, weak penalties) → 10 = Maximum (aggressive, high penalties)
        """
        return self._require_value('humanness_intensity', int)
    
    # =========================================================================
    # DETECTION SETTINGS
    # =========================================================================
    
    def get_ai_threshold(self, strict_mode: bool = False) -> float:
        """
        Get AI detection threshold.
        
        Args:
            strict_mode: If True, use stricter threshold
            
        Returns:
            Threshold value (0-100 scale)
        """
        detection = self._require_value('detection', dict)
        if strict_mode:
            value = self._require_value('detection.strict_mode_threshold')
        else:
            value = self._require_value('detection.ai_threshold')
        if not isinstance(value, (int, float)):
            raise ValueError(
                f"Invalid AI threshold type: expected number, got {type(value).__name__}"
            )
        return float(value)
    
    def get_confidence_thresholds(self) -> Dict[str, float]:
        """Get AI confidence thresholds."""
        detection = self._require_value('detection', dict)
        high = self._require_value('detection.high_confidence_threshold')
        medium = self._require_value('detection.medium_confidence_threshold')
        if not isinstance(high, (int, float)) or not isinstance(medium, (int, float)):
            raise ValueError("detection confidence thresholds must be numeric")
        return {
            'high': float(high),
            'medium': float(medium)
        }
    
    def get_recommendation_thresholds(self) -> Dict[str, float]:
        """Get recommendation thresholds."""
        detection = self._require_value('detection', dict)
        regenerate = self._require_value('detection.regenerate_threshold')
        revise = self._require_value('detection.revise_threshold')
        if not isinstance(regenerate, (int, float)) or not isinstance(revise, (int, float)):
            raise ValueError("detection recommendation thresholds must be numeric")
        return {
            'regenerate': float(regenerate),
            'revise': float(revise)
        }
    
    def get_repetition_thresholds(self) -> Dict[str, int]:
        """Get repetition detection thresholds."""
        detection = self._require_value('detection', dict)
        word_frequency = self._require_value('detection.word_frequency_threshold', int)
        word_frequency_critical = self._require_value('detection.word_frequency_critical', int)
        structural_repetition = self._require_value('detection.structural_repetition_threshold', int)
        return {
            'word_frequency': word_frequency,
            'word_frequency_critical': word_frequency_critical,
            'structural_repetition': structural_repetition
        }
    
    def use_ml_detection(self) -> bool:
        """Check if ML-based detection is enabled."""
        value = self._require_value('detection.use_ml_model', bool)
        return value
    
    # =========================================================================
    # READABILITY SETTINGS
    # =========================================================================
    
    def get_readability_thresholds(self) -> Dict[str, float]:
        """Get readability score thresholds."""
        readability = self._require_value('readability', dict)
        min_score = self._require_value('readability.min_flesch_score')
        max_score = self._require_value('readability.max_flesch_score')
        if not isinstance(min_score, (int, float)) or not isinstance(max_score, (int, float)):
            raise ValueError("readability thresholds must be numeric")
        return {
            'min': float(min_score),
            'max': float(max_score)
        }
    
    # =========================================================================
    # API GENERATION SETTINGS
    # =========================================================================
    
    def get_temperature(self, component_type: Optional[str] = None) -> float:
        """
        Get API temperature setting.
        
        Args:
            component_type: Optional component-specific temperature
            
        Returns:
            Temperature value (0.0-1.0)
        """
        api = self._require_value('api', dict)
        # Could add component-specific temps in future
        value = self._require_value('api.base_temperature')
        if not isinstance(value, (int, float)):
            raise ValueError("api.base_temperature must be numeric")
        return float(value)
    
    def get_max_tokens(self, component_type: str = 'default') -> int:
        """
        Get max tokens for component type based on word count target.
        
        Converts centralized text field base_length (word count) to tokens.
        Token estimation: words × 1.3 (approximate tokens per word)
        
        Args:
            component_type: Component type (micro, description, faq, etc.)
            
        Returns:
            Max tokens value (converted from word count)
        """
        length_spec = self._get_text_field_length_spec(component_type)
        target_words = length_spec['target']
        
        if not isinstance(target_words, int) or target_words <= 0:
            raise ValueError(
                f"Invalid target word count for component_type='{component_type}': {target_words}"
            )

        # Convert words to tokens (1.3 tokens per word approximation)
        return int(target_words * 1.3)
    
    def get_max_attempts(self) -> int:
        """Get maximum generation attempts."""
        value = self._require_value('api.max_attempts', int)
        return value
    
    def get_retry_temperature_increase(self) -> float:
        """Get temperature increase per retry."""
        value = self._require_value('api.retry_temperature_increase')
        if not isinstance(value, (int, float)):
            raise ValueError("api.retry_temperature_increase must be numeric")
        return float(value)
    
    # =========================================================================
    # COMPONENT EXTRACTION STRATEGIES
    # =========================================================================
    
    def get_extraction_strategy(self, component_type: str) -> str:
        """Get extraction strategy for component type from component_extraction."""
        extraction = self._require_value('component_extraction', dict)
        if component_type in extraction:
            component_entry = extraction[component_type]
            if not isinstance(component_entry, dict):
                raise ValueError(
                    f"Invalid component_extraction entry for '{component_type}': expected dictionary"
                )
            if 'extraction_strategy' not in component_entry:
                raise KeyError(
                    f"Missing required config key: component_extraction.{component_type}.extraction_strategy"
                )
            strategy = component_entry['extraction_strategy']
            if not strategy:
                raise ValueError(
                    f"Missing extraction_strategy for component_type='{component_type}' in component_extraction"
                )
            return strategy

        # Fallback to component registry as canonical source for standard components.
        # This preserves fail-fast behavior for unknown components while avoiding
        # redundant config entries for components that already declare strategy in specs.
        try:
            from shared.text.utils.component_specs import ComponentRegistry

            spec = ComponentRegistry.get_spec(component_type)
            if not spec.extraction_strategy:
                raise ValueError(
                    f"Component spec for '{component_type}' missing extraction_strategy"
                )
            return spec.extraction_strategy
        except Exception:
            pass

        raise KeyError(
            f"Missing component_extraction entry for component_type='{component_type}'"
        )
    
    def get_component_length(self, component_type: str) -> int:
        """Get target word count for component type from centralized text field config."""
        return self.get_text_field_length(component_type)

    def get_text_field_length(self, field_name: str) -> int:
        """Get centralized base length target for any configured text field name."""
        length_spec = self._get_text_field_length_spec(field_name)
        return length_spec['target']
    
    # =========================================================================
    # DATA SOURCES
    # =========================================================================
    
    def get_materials_yaml_path(self) -> str:
        """Get path to Materials.yaml."""
        value = self._require_value('data_sources.materials_yaml', str)
        return value
    
    def get_categories_yaml_path(self) -> str:
        """Get path to Categories.yaml."""
        value = self._require_value('data_sources.categories_yaml', str)
        return value
    
    # =========================================================================
    # OUTPUT SETTINGS
    # =========================================================================
    
    def get_output_dir(self) -> str:
        """Get frontmatter output directory."""
        value = self._require_value('output.frontmatter_dir', str)
        return value
    
    def get_backup_dir(self) -> str:
        """Get backup directory."""
        value = self._require_value('output.backup_dir', str)
        return value
    
    def should_create_backup(self) -> bool:
        """Check if backups should be created."""
        value = self._require_value('output.create_backup', bool)
        return value
    
    # =========================================================================
    # VALIDATION
    # =========================================================================
    
    def validate(self) -> Dict[str, Any]:
        """
        Validate configuration completeness and correctness.
        
        Returns:
            Dict with:
            - valid: bool
            - errors: List[str]
            - warnings: List[str]
        """
        errors = []
        warnings = []
        
        # Check required sections exist
        required_sections = [
            'detection', 'readability', 'api', 
            'data_sources', 'output'
        ]
        for section in required_sections:
            if section not in self.config:
                errors.append(f"Missing required section: {section}")
        
        # Check intensity sliders are in valid range
        intensity_fields = [
            'author_voice_intensity', 'personality_intensity', 
            'engagement_style', 'technical_language_intensity',
            'context_specificity', 'sentence_rhythm_variation',
            'imperfection_tolerance', 'structural_predictability',
            'ai_avoidance_intensity'
        ]
        for field in intensity_fields:
            value = self.config.get(field)
            if value is None:
                errors.append(f"Missing intensity slider: {field}")
            elif not isinstance(value, int) or not 1 <= value <= 10:
                errors.append(f"{field} must be integer 1-10, got: {value}")
        
        # Check thresholds are reasonable
        if 'detection' in self.config:
            ai_threshold = self.config['detection'].get('ai_threshold')
            if ai_threshold and (ai_threshold < 0 or ai_threshold > 100):
                errors.append(f"ai_threshold must be 0-100, got: {ai_threshold}")
        
        if 'api' in self.config:
            temp = self.config['api'].get('base_temperature')
            if temp and (temp < 0.0 or temp > 2.0):
                warnings.append(f"base_temperature {temp} outside typical range 0.0-2.0")
        
        # Check data source files exist
        if 'data_sources' in self.config:
            materials_path = self.get_materials_yaml_path()
            if not os.path.exists(materials_path):
                errors.append(f"Materials file not found: {materials_path}")

        # Check centralized text field config exists and has required blocks
        try:
            self._get_text_field_length_spec('pageDescription')
        except Exception as e:
            errors.append(f"Centralized text field config invalid: {e}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }


# Global singleton instance
_config_instance = None


def get_config(config_path: Optional[str] = None) -> ProcessingConfig:
    """
    Get global config instance (singleton pattern).
    
    Args:
        config_path: Optional custom config path (only used on first call)
        
    Returns:
        ProcessingConfig instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = ProcessingConfig(config_path)
    return _config_instance


def reload_config(config_path: Optional[str] = None):
    """Force reload of configuration (useful after editing config.yaml)."""
    global _config_instance
    _config_instance = ProcessingConfig(config_path)
    return _config_instance
