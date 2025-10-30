"""
DEPRECATED: Redirect wrapper for backward compatibility.
Use validation.core.content instead.
"""
import warnings
from validation.core.content import CaptionIntegrationValidator
from validation.errors import ValidationResult

warnings.warn(
    "Importing from validation.caption_integration_validator is deprecated. "
    "Use 'from validation.core.content import CaptionIntegrationValidator' instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ['CaptionIntegrationValidator', 'ValidationResult']
