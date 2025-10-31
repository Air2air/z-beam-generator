"""
DEPRECATED: Redirect wrapper for backward compatibility.
Use validation.core.content instead.
"""
import warnings
from shared.validation.core.content import CaptionIntegrationValidator
from shared.validation.errors import ValidationResult

warnings.warn(
    "Importing from shared.validation.caption_integration_validator is deprecated. "
    "Use 'from shared.validation.core.content import CaptionIntegrationValidator' instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ['CaptionIntegrationValidator', 'ValidationResult']
