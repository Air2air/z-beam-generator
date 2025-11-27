"""
Validation Constants - Dynamic Threshold Management

Centralizes all validation thresholds with database-driven adaptive learning.
Thresholds now learn from success patterns instead of static config values.

Architecture:
- Thresholds start with sensible defaults
- Learn from database (sweet spot analysis, 75th percentile)
- Adapt based on actual success patterns
- Fall back to defaults only when insufficient data

Usage:
    from shared.text.validation.constants import ValidationConstants
    
    constants = ValidationConstants()
    winston_threshold = constants.get_winston_threshold()  # Dynamic!
    if ai_score < winston_threshold:
        print("Passes Winston validation")
"""

from pathlib import Path
from typing import Dict, Any, Optional
import yaml
import logging

logger = logging.getLogger(__name__)


class ValidationConstants:
    """
    Centralized validation constants with dynamic threshold learning.
    
    Thresholds adapt based on learned success patterns from database.
    """
    
    # Static defaults (ONLY used when database learning unavailable)
    DEFAULT_WINSTON_AI_THRESHOLD = 0.33          # AI score must be < 0.33 (33% AI, 67%+ human)
    DEFAULT_WINSTON_HUMAN_THRESHOLD = 0.67       # Human score must be >= 67%
    WINSTON_MIN_CHARS = 300                       # Minimum characters for Winston API
    
    # Threshold manager (lazy-loaded)
    _threshold_manager: Optional['ThresholdManager'] = None
    
    @classmethod
    def _get_threshold_manager(cls):
        """Lazy-load threshold manager to avoid circular imports."""
        if cls._threshold_manager is None:
            try:
                from learning.threshold_manager import ThresholdManager
                cls._threshold_manager = ThresholdManager(db_path='z-beam.db')
            except Exception as e:
                logger.warning(f"[VALIDATION] ThresholdManager unavailable: {e}")
                cls._threshold_manager = None
        return cls._threshold_manager
    
    @classmethod
    def get_winston_threshold(cls, use_learned: bool = True) -> float:
        """
        Get Winston AI threshold (dynamic learning enabled).
        
        Args:
            use_learned: If True, use database-learned threshold
            
        Returns:
            Threshold value (0-1.0 scale)
        """
        if use_learned:
            manager = cls._get_threshold_manager()
            if manager:
                return manager.get_winston_threshold(use_learned=True)
        
        return cls.DEFAULT_WINSTON_AI_THRESHOLD
    
    # Legacy constant for backward compatibility (deprecated)
    @property
    def WINSTON_AI_THRESHOLD(self) -> float:
        """DEPRECATED: Use get_winston_threshold() instead."""
        logger.warning(
            "[VALIDATION] WINSTON_AI_THRESHOLD constant is deprecated, "
            "use get_winston_threshold() for dynamic learning"
        )
        return self.DEFAULT_WINSTON_AI_THRESHOLD
    
    # Keep as class variable for backward compatibility
    WINSTON_HUMAN_THRESHOLD = DEFAULT_WINSTON_HUMAN_THRESHOLD
    
    # REMOVED: Default/fallback scores violate fail-fast architecture (GROK_INSTRUCTIONS.md)
    # System must fail immediately if validation cannot run - no mock/placeholder scores
    # See: Core Principle #2 - No Mocks or Fallbacks in Production Code
    # OLD CODE (DELETED):
    #   DEFAULT_AI_SCORE = 0.0               # Perfect score when skipping (0% AI)
    #   DEFAULT_HUMAN_SCORE = 1.0            # Perfect score when skipping (100% human)
    #   DEFAULT_FALLBACK_AI_SCORE = 0.5      # Neutral score on error (50%)
    
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
    def passes_winston(ai_score: float, use_learned: bool = True) -> bool:
        """
        Check if AI score passes Winston threshold.
        
        Args:
            ai_score: AI detection score (0-1.0)
            use_learned: If True, use database-learned threshold
            
        Returns:
            True if passes (ai_score below threshold)
        """
        threshold = ValidationConstants.get_winston_threshold(use_learned)
        return ai_score < threshold
    
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
