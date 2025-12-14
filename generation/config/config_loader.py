"""
Processing Configuration Loader

Single source of truth for ALL processing configuration.
Loads from processing/config.yaml and provides typed access.

Usage:
    from processing.config_loader import ProcessingConfig
    
    config = ProcessingConfig()
    threshold = config.get_ai_threshold()
    temperature = config.get_temperature()
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Path to config file
CONFIG_DIR = Path(__file__).parent.parent  # processing/ directory
CONFIG_FILE = CONFIG_DIR / "config.yaml"


class ProcessingConfig:
    """
    Central configuration manager for processing pipeline.
    
    Loads from processing/config.yaml and provides typed accessors.
    All processing components should use this instead of hardcoded values.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Load processing configuration.
        
        Args:
            config_path: Optional custom config file path
        """
        self.config_path = config_path or CONFIG_FILE
        self.config = self._load_config()
        logger.info(f"Loaded processing config from {self.config_path}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load YAML configuration file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(
                f"Processing config not found: {self.config_path}\n"
                f"Expected location: processing/config.yaml"
            )
        
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            if not isinstance(config, dict):
                raise ValueError("Config file must contain a YAML dictionary")
            
            return config
        except Exception as e:
            raise RuntimeError(f"Failed to load config from {self.config_path}: {e}")
    
    # =========================================================================
    # INTENSITY SLIDERS (User-facing controls) - NOW 1-10 SCALE
    # =========================================================================
    
    def get_author_voice_intensity(self) -> int:
        """Get author voice intensity (1-10)."""
        return self.config.get('author_voice_intensity', 5)
    
    def get_personality_intensity(self) -> int:
        """Get personality intensity (1-10)."""
        return self.config.get('personality_intensity', 5)
    
    def get_engagement_style(self) -> int:
        """Get engagement style (1-10)."""
        return self.config.get('engagement_style', 5)
    
    def get_emotional_intensity(self) -> int:
        """Get emotional intensity (1-10)."""
        return self.config.get('emotional_intensity', 5)
    
    def get_technical_language_intensity(self) -> int:
        """Get technical language intensity (1-10)."""
        return self.config.get('technical_language_intensity', 5)
    
    def get_context_specificity(self) -> int:
        """Get context specificity (1-10)."""
        return self.config.get('context_specificity', 5)
    
    def get_sentence_rhythm_variation(self) -> int:
        """Get sentence rhythm variation (1-10)."""
        return self.config.get('sentence_rhythm_variation', 5)
    
    def get_imperfection_tolerance(self) -> int:
        """Get imperfection tolerance (1-10)."""
        return self.config.get('imperfection_tolerance', 5)
    
    def get_structural_predictability(self) -> int:
        """Get structural predictability (1-10)."""
        return self.config.get('structural_predictability', 5)
    
    def get_ai_avoidance_intensity(self) -> int:
        """Get AI avoidance intensity (1-10)."""
        return self.config.get('ai_avoidance_intensity', 5)
    
    def get_length_variation_range(self) -> int:
        """Get length variation range (1-10)."""
        return self.config.get('length_variation_range', 5)
    
    def get_learning_target(self) -> float:
        """
        Get human score learning target for adaptive improvement.
        
        Returns:
            Target human score (0-100) that system tries to achieve through learning
        """
        return self.config.get('human_score_learning_target', 50)
    
    def get_humanness_intensity(self) -> int:
        """
        Get humanness_intensity (1-10 scale) for AI evasion control.
        
        Returns:
            1 = Minimal (fast, weak penalties) → 10 = Maximum (aggressive, high penalties)
        """
        return self.config.get('humanness_intensity', 5)
    
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
        detection = self.config.get('detection', {})
        if strict_mode:
            return detection.get('strict_mode_threshold', 25)
        return detection.get('ai_threshold', 30)  # Lowered from 40 to 30 based on phrasely.ai validation
    
    def get_confidence_thresholds(self) -> Dict[str, float]:
        """Get AI confidence thresholds."""
        detection = self.config.get('detection', {})
        return {
            'high': detection.get('high_confidence_threshold', 70),
            'medium': detection.get('medium_confidence_threshold', 50)
        }
    
    def get_recommendation_thresholds(self) -> Dict[str, float]:
        """Get recommendation thresholds."""
        detection = self.config.get('detection', {})
        return {
            'regenerate': detection.get('regenerate_threshold', 70),
            'revise': detection.get('revise_threshold', 50)
        }
    
    def get_repetition_thresholds(self) -> Dict[str, int]:
        """Get repetition detection thresholds."""
        detection = self.config.get('detection', {})
        return {
            'word_frequency': detection.get('word_frequency_threshold', 3),
            'word_frequency_critical': detection.get('word_frequency_critical', 5),
            'structural_repetition': detection.get('structural_repetition_threshold', 2)
        }
    
    def use_ml_detection(self) -> bool:
        """Check if ML-based detection is enabled."""
        detection = self.config.get('detection', {})
        return detection.get('use_ml_model', False)
    
    # =========================================================================
    # READABILITY SETTINGS
    # =========================================================================
    
    def get_readability_thresholds(self) -> Dict[str, float]:
        """Get readability score thresholds."""
        readability = self.config.get('readability', {})
        return {
            'min': readability.get('min_flesch_score', 60.0),
            'max': readability.get('max_flesch_score', 100.0)
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
        api = self.config.get('api', {})
        # Could add component-specific temps in future
        return api.get('base_temperature', 0.8)
    
    def get_max_tokens(self, component_type: str = 'default') -> int:
        """
        Get max tokens for component type based on word count target.
        
        Converts component_lengths.target (word count) to tokens.
        Token estimation: words × 1.3 (approximate tokens per word)
        
        Args:
            component_type: Component type (micro, description, faq, etc.)
            
        Returns:
            Max tokens value (converted from word count)
        """
        # Get target word count from component_lengths
        lengths = self.config.get('component_lengths', {})
        component_config = lengths.get(component_type, {})
        
        if isinstance(component_config, dict):
            target_words = component_config.get('target')
        else:
            # Legacy: component_config might be int (word count)
            target_words = component_config
        
        if target_words:
            # Convert words to tokens (1.3 tokens per word approximation)
            return int(target_words * 1.3)
        
        # Fallback for unknown component types
        return 130  # ~100 words default
    
    def get_max_attempts(self) -> int:
        """Get maximum generation attempts."""
        api = self.config.get('api', {})
        return api.get('max_attempts', 5)
    
    def get_retry_temperature_increase(self) -> float:
        """Get temperature increase per retry."""
        api = self.config.get('api', {})
        return api.get('retry_temperature_increase', 0.1)
    
    # =========================================================================
    # COMPONENT EXTRACTION STRATEGIES
    # =========================================================================
    
    def get_extraction_strategy(self, component_type: str) -> str:
        """Get extraction strategy for component type.
        
        Looks in component_extraction (new) then component_lengths (legacy).
        """
        # Try new location first
        extraction = self.config.get('component_extraction', {})
        if component_type in extraction:
            return extraction[component_type].get('extraction_strategy', 'raw')
        
        # Fall back to legacy location
        lengths = self.config.get('component_lengths', {})
        if component_type in lengths and isinstance(lengths[component_type], dict):
            return lengths[component_type].get('extraction_strategy', 'raw')
        
        return 'raw'  # Default
    
    def get_component_length(self, component_type: str) -> int:
        """Get target word count for component type.
        
        NOTE: Word counts are now defined in prompts (Option B).
        This returns a legacy fallback value only.
        """
        lengths = self.config.get('component_lengths', {})
        if component_type in lengths:
            val = lengths[component_type]
            if isinstance(val, dict):
                return val.get('target', 100)
            return val
        return 100  # Default fallback
    
    # =========================================================================
    # DATA SOURCES
    # =========================================================================
    
    def get_materials_yaml_path(self) -> str:
        """Get path to Materials.yaml."""
        sources = self.config.get('data_sources', {})
        return sources.get('materials_yaml', 'data/materials/Materials.yaml')
    
    def get_categories_yaml_path(self) -> str:
        """Get path to Categories.yaml."""
        sources = self.config.get('data_sources', {})
        return sources.get('categories_yaml', 'data/materials/Categories.yaml')
    
    # =========================================================================
    # OUTPUT SETTINGS
    # =========================================================================
    
    def get_output_dir(self) -> str:
        """Get frontmatter output directory."""
        output = self.config.get('output', {})
        return output.get('frontmatter_dir', 'frontmatter/materials')
    
    def get_backup_dir(self) -> str:
        """Get backup directory."""
        output = self.config.get('output', {})
        return output.get('backup_dir', 'frontmatter/materials/.backup')
    
    def should_create_backup(self) -> bool:
        """Check if backups should be created."""
        output = self.config.get('output', {})
        return output.get('create_backup', True)
    
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
            'component_lengths', 'data_sources', 'output'
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
            'ai_avoidance_intensity', 'length_variation_range'
        ]
        for field in intensity_fields:
            value = self.config.get(field)
            if value is None:
                errors.append(f"Missing intensity slider: {field}")
            elif not isinstance(value, int) or not 0 <= value <= 100:
                errors.append(f"{field} must be integer 0-100, got: {value}")
        
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
