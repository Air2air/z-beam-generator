#!/usr/bin/env python3
"""
Backward-compat shim - implementation moved to shared.validation.services

Date: February 23, 2026
"""
from shared.validation.services import (
    ComprehensiveValidationResult,
    ValidationOrchestrator,
    validate_material,
    validate_material_lifecycle,
    SchemaType,
    SchemaValidator,
    ValidationResult,
    ValidationMode,
    validate_categories_yaml,
    validate_frontmatter,
    validate_materials_yaml,
)

__all__ = [
    "ValidationOrchestrator",
    "SchemaValidator",
    "ComprehensiveValidationResult",
    "ValidationResult",
    "ValidationMode",
    "SchemaType",
    "validate_material_lifecycle",
    "validate_material",
    "validate_frontmatter",
    "validate_materials_yaml",
    "validate_categories_yaml",
]
