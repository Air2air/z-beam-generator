"""
DEPRECATED: Redirect wrapper for backward compatibility.
Use validation.core.content instead.
"""
import warnings
from validation.core.content import ContentValidator
from validation.errors import ValidationResult

warnings.warn(
    "Importing from validation.quality_validator is deprecated. "
    "Use 'from validation.core.content import ContentValidator' instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ['ContentValidator', 'ValidationResult']
