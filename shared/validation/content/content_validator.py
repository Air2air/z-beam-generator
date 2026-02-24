"""
Backward-compat shim — implementation at shared.validation.core.content

Date: February 23, 2026
"""

from shared.validation.core.content import (
    ContentQualityScore,
    ContentValidator,
    MicroIntegrationValidator,
)
from shared.validation.errors import ValidationResult

# Legacy aliases for backward compatibility
ContentValidationService = ContentValidator
ContentValidationResult = ValidationResult

# Legacy constants
PERSONA_THRESHOLDS = {
    'australian': 0.7,
    'american': 0.7,
    'british': 0.7,
    'canadian': 0.7
}

__all__ = [
    'ContentValidator',
    'ContentValidationService',
    'ContentValidationResult', 
    'ContentQualityScore',
    'ValidationResult',
    'PERSONA_THRESHOLDS'
]
