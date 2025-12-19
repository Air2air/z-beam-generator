"""
Redirect wrapper for backward compatibility.

The schema_validator module has been consolidated into validation/core/.
This file provides backward-compatible imports.

Updated: October 29, 2025 - Validation consolidation
"""

import warnings

# Redirect to new consolidated location
from shared.validation.core.schema import SchemaValidationResult, SchemaValidator
from shared.validation.errors import ValidationResult

# Deprecation warning
warnings.warn(
    "Importing from shared.validation.schema_validator is deprecated. "
    "Use 'from shared.validation.core import SchemaValidator' instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ['SchemaValidator', 'ValidationResult', 'SchemaValidationResult']
