"""
Validation Constants - Single Source of Truth

Centralizes all validation thresholds and quality gates to prevent
scattered hardcoded values across the codebase.

Architecture:
- All thresholds defined in ONE place
- Loaded from config.yaml when available
- Clear fallback defaults
- Used consistently across all validators

Usage:
    from generation.validation.constants import ValidationConstants
    
    constants = ValidationConstants()
    if ai_score < constants.WINSTON_AI_THRESHOLD:
        print("Passes Winston validation")
"""

from pathlib import Path
from typing import Dict, Any
import yaml


class ValidationConstants:
    """
    Centralized validation constants and thresholds.
    
    Single source of truth for all quality gates and validation rules.
    """
    
    # Winston AI Detection Thresholds (ALL on 0-1.0 normalized scale)
    WINSTON_AI_THRESHOLD = 0.33          # AI score must be < 0.33 (33% AI, 67%+ human)
    WINSTON_HUMAN_THRESHOLD = 0.67       # Human score must be >= 67%
    WINSTON_MIN_CHARS = 300              # Minimum characters for Winston API
    
    # Default Scores (when validation skipped) - ALL on 0-1.0 normalized scale
    DEFAULT_AI_SCORE = 0.0               # Perfect score when skipping (0% AI)
    DEFAULT_HUMAN_SCORE = 1.0            # Perfect score when skipping (100% human)
    DEFAULT_FALLBACK_AI_SCORE = 0.5      # Neutral score on error (50%)
    
    # Score Conversions
    @staticmethod
    def ai_to_human_score(ai_score: float) -> float:
        """Convert AI score (0-1) to human percentage (0-100)."""
        return (1.0 - ai_score) * 100.0
    
    @staticmethod
    def human_to_ai_score(human_percent: float) -> float:
        """Convert human percentage (0-100) to AI score (0-1)."""
        return 1.0 - (human_percent / 100.0)
    
    @staticmethod
    def passes_winston(ai_score: float) -> bool:
        """Check if AI score passes Winston threshold."""
        return ai_score < ValidationConstants.WINSTON_AI_THRESHOLD
    
    @staticmethod
    def get_status_label(passes: bool) -> str:
        """Get status emoji and label."""
        return "✅ PASS" if passes else "❌ FAIL"
    
    @staticmethod
    def load_from_config(config_path: str = "generation/config.yaml") -> Dict[str, Any]:
        """
        Load validation constants from config file.
        
        Returns dict with any custom thresholds defined in config.
        Falls back to class constants if not defined.
        """
        config_file = Path(config_path)
        if not config_file.exists():
            return {}
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Extract validation-related settings
        validation_config = {}
        
        # Detection thresholds
        detection = config.get('detection', {})
        if 'ai_threshold' in detection:
            validation_config['winston_ai_threshold'] = detection['ai_threshold'] / 100.0  # Convert percentage
        
        # Winston minimums
        if 'winston_min_chars' in config:
            validation_config['winston_min_chars'] = config['winston_min_chars']
        
        return validation_config


# Global instance for easy import
VALIDATION = ValidationConstants()


# Convenience functions for backward compatibility
def passes_winston_threshold(ai_score: float) -> bool:
    """Check if AI score passes Winston threshold."""
    return VALIDATION.passes_winston(ai_score)


def ai_to_human_percentage(ai_score: float) -> float:
    """Convert AI score to human percentage."""
    return VALIDATION.ai_to_human_score(ai_score)


def get_validation_status(passes: bool) -> str:
    """Get validation status label."""
    return VALIDATION.get_status_label(passes)
