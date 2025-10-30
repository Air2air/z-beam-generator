"""
Redirect wrapper for backward compatibility.

The schema_validator module has been consolidated into validation/core/.
This file provides backward-compatible imports.

Updated: October 29, 2025 - Validation consolidation
"""

import warnings

# Redirect to new consolidated location
from validation.core.schema import SchemaValidator, SchemaValidationResult
from validation.errors import ValidationResult

# Deprecation warning
warnings.warn(
    "Importing from validation.schema_validator is deprecated. "
    "Use 'from validation.core import SchemaValidator' instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ['SchemaValidator', 'ValidationResult', 'SchemaValidationResult']
