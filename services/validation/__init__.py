#!/usr/bin/env python3
"""
Validation Services Module

Consolidated validation services with unified interfaces.
Part of system consolidation to organize validation functionality.

Services:
- ValidationOrchestrator: Unified validation coordination
- UnifiedSchemaValidator: Single schema validation system

Last Updated: October 22, 2025
"""

from .orchestrator import ValidationOrchestrator, ComprehensiveValidationResult
from .unified_schema_validator import (
    UnifiedSchemaValidator,
    UnifiedValidationResult,
    ValidationMode,
    SchemaType
)

# Convenience functions
from .orchestrator import validate_material_lifecycle, validate_material
from .unified_schema_validator import (
    validate_frontmatter,
    validate_materials_yaml,
    validate_categories_yaml
)

__all__ = [
    # Primary Services
    'ValidationOrchestrator',
    'UnifiedSchemaValidator',
    
    # Result Types
    'ComprehensiveValidationResult',
    'UnifiedValidationResult',
    
    # Enums
    'ValidationMode',
    'SchemaType',
    
    # Convenience Functions
    'validate_material_lifecycle',
    'validate_material',
    'validate_frontmatter',
    'validate_materials_yaml',
    'validate_categories_yaml',
]