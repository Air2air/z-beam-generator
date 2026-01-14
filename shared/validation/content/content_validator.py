"""
DEPRECATED: Redirect wrapper for backward compatibility.
Use validation.core.content instead.
"""
import warnings

from shared.validation.core.content import (
    ContentQualityScore,
    ContentValidator,
    MicroIntegrationValidator,
)
from shared.validation.errors import ValidationResult

warnings.warn(
    "Importing from shared.validation.content_validator is deprecated. "
    "Use 'from shared.validation.core.content import ContentValidator' instead.",
    DeprecationWarning,
    stacklevel=2
)

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
