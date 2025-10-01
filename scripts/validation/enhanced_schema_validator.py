#!/usr/bin/env python3
"""
Enhanced Schema Validator - Compatibility Wrapper

This file provides backward compatibility for existing enhanced_schema_validator imports.
All functionality has been consolidated into the SchemaValidator.

DEPRECATED: Use validation.schema_validator.SchemaValidator directly
"""

import warnings
from pathlib import Path
import sys

# Add validation directory to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from validation.schema_validator import SchemaValidator, ValidationResult


class EnhancedSchemaValidator:
    """
    DEPRECATED: Compatibility wrapper for UnifiedSchemaValidator
    
    This class maintains the original EnhancedSchemaValidator interface
    while delegating to the new unified validator.
    """
    
    def __init__(self, schema_path: str = None):
        warnings.warn(
            "EnhancedSchemaValidator is deprecated. Use SchemaValidator directly.",
            DeprecationWarning,
            stacklevel=2
        )
        self._unified = SchemaValidator(schema_path, validation_mode="enhanced")
    
    def validate_with_detailed_report(self, data: dict, material_name: str = "unknown") -> str:
        """Compatibility method - delegates to unified validator"""
        return self._unified.validate_with_detailed_report(data, material_name)
    
    def validate(self, data: dict, material_name: str = "unknown") -> ValidationResult:
        """Compatibility method - delegates to unified validator"""
        return self._unified.validate(data, material_name)


# Legacy function compatibility
def validate_frontmatter_schema(data: dict, schema_path: str = None) -> ValidationResult:
    """
    DEPRECATED: Legacy function compatibility
    Use SchemaValidator directly
    """
    warnings.warn(
        "validate_frontmatter_schema is deprecated. Use SchemaValidator.validate() directly.",
        DeprecationWarning,
        stacklevel=2
    )
    
    validator = SchemaValidator(schema_path, validation_mode="enhanced")
    return validator.validate(data)
