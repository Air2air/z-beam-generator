#!/usr/bin/env python3
"""
Frontmatter Core Schema Validator - Compatibility Wrapper

This file provides backward compatibility for existing core schema validator imports.
All functionality has been consolidated into the UnifiedSchemaValidator.

DEPRECATED: Use validation.unified_schema_validator.UnifiedSchemaValidator directly
"""

import warnings
from pathlib import Path
import sys
from typing import Tuple, List, Dict

# Add validation directory to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from validation.unified_schema_validator import UnifiedSchemaValidator


class FrontmatterSchemaValidator:
    """
    DEPRECATED: Compatibility wrapper for UnifiedSchemaValidator
    
    Maintains the original FrontmatterSchemaValidator interface
    while delegating to the unified validator.
    """
    
    def __init__(self, schema_path: str = None):
        warnings.warn(
            "FrontmatterSchemaValidator is deprecated. Use UnifiedSchemaValidator directly.",
            DeprecationWarning,
            stacklevel=2
        )
        self._unified = UnifiedSchemaValidator(schema_path, validation_mode="basic")
    
    def validate_frontmatter(self, data: Dict, material_name: str = "unknown") -> Tuple[bool, List[str]]:
        """Compatibility method - delegates to unified validator"""
        return self._unified.validate_frontmatter(data, material_name)


# Legacy function compatibility
def validate_frontmatter_and_log(data: Dict, material_name: str) -> bool:
    """
    DEPRECATED: Legacy function compatibility
    Use UnifiedSchemaValidator directly
    """
    warnings.warn(
        "validate_frontmatter_and_log is deprecated. Use UnifiedSchemaValidator.validate() directly.",
        DeprecationWarning,
        stacklevel=2
    )
    
    validator = UnifiedSchemaValidator(validation_mode="basic")
    result = validator.validate(data, material_name)
    
    if not result.is_valid:
        print(f"Validation failed for {material_name}:")
        for error in result.errors:
            print(f"  - {error.message}")
    
    return result.is_valid
