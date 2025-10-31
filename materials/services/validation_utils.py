"""
DEPRECATED: Validation Utilities for Frontmatter Generation

This file is deprecated as part of the service consolidation plan.
Use services.validation.ValidationOrchestrator instead.

Functionality moved to:
- services.validation.ValidationOrchestrator (main validation interface)
- services.validation.UnifiedSchemaValidator (schema validation)

Last Updated: October 22, 2025 - Deprecated
"""

import warnings

# Issue deprecation warning
warnings.warn(
    "components.frontmatter.services.validation_utils is deprecated. "
    "Use services.validation.ValidationOrchestrator instead.",
    DeprecationWarning,
    stacklevel=2
)

from typing import Union


class ValidationUtils:
    """Lightweight utilities for common validation operations"""
    
    # Confidence thresholds (centralized constants)
    YAML_CONFIDENCE_THRESHOLD = 0.85  # High confidence for YAML data
    AI_CONFIDENCE_THRESHOLD = 0.80    # Acceptable confidence for AI research
    
    @staticmethod
    def normalize_confidence(confidence: Union[int, float]) -> int:
        """
        Normalize confidence values to integer percentage (0-100).
        
        Handles both fractional (0.0-1.0) and percentage (0-100) formats.
        Phase 3.3: Eliminates duplicate normalization logic across 3+ files.
        
        Args:
            confidence: Confidence value (0.0-1.0 or 0-100)
            
        Returns:
            Integer confidence percentage (0-100)
            
        Examples:
            >>> ValidationUtils.normalize_confidence(0.85)
            85
            >>> ValidationUtils.normalize_confidence(95)
            95
            >>> ValidationUtils.normalize_confidence(0.5)
            50
        """
        if confidence < 1:
            # Fractional format (0.0-1.0) -> convert to percentage
            return int(confidence * 100)
        else:
            # Already percentage format (0-100)
            return int(confidence)
    
    @staticmethod
    def is_high_confidence(confidence: Union[int, float], threshold: float = None) -> bool:
        """
        Check if confidence meets high-confidence threshold.
        
        Args:
            confidence: Confidence value to check
            threshold: Optional custom threshold (defaults to YAML_CONFIDENCE_THRESHOLD)
            
        Returns:
            True if confidence >= threshold
            
        Examples:
            >>> ValidationUtils.is_high_confidence(0.9)
            True
            >>> ValidationUtils.is_high_confidence(0.75)
            False
            >>> ValidationUtils.is_high_confidence(90)
            True
        """
        if threshold is None:
            threshold = ValidationUtils.YAML_CONFIDENCE_THRESHOLD
        
        # Normalize both values to same scale for comparison
        if confidence >= 1:
            confidence = confidence / 100.0
        
        return confidence >= threshold
    
    @staticmethod
    def validate_essential_properties(
        properties: dict,
        essential_props: set,
        material_name: str = "unknown"
    ) -> tuple[bool, list[str]]:
        """
        Validate that all essential properties are present.
        
        Args:
            properties: Dictionary of properties to validate
            essential_props: Set of required property names
            material_name: Material name for error messages
            
        Returns:
            Tuple of (is_valid, missing_properties)
            
        Examples:
            >>> props = {'density': {...}, 'hardness': {...}}
            >>> required = {'density', 'hardness', 'melting_point'}
            >>> valid, missing = ValidationUtils.validate_essential_properties(props, required)
            >>> print(valid, missing)
            False ['melting_point']
        """
        missing = essential_props - set(properties.keys())
        is_valid = len(missing) == 0
        return is_valid, sorted(missing)
