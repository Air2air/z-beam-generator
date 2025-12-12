"""
DEPRECATED: Redirect wrapper for backward compatibility.
Use validation.core.content instead.
"""
import warnings
from shared.validation.core.content import MicroIntegrationValidator
from shared.validation.errors import ValidationResult

warnings.warn(
    "Importing from shared.validation.micro_integration_validator is deprecated. "
    "Use 'from shared.validation.core.content import MicroIntegrationValidator' instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ['MicroIntegrationValidator', 'ValidationResult']
