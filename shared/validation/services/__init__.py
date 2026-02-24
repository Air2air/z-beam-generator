"""
Validation Services Module

Consolidated validation services for the Z-Beam generation pipeline.
Includes:
- PreGenerationValidationService, PostGenerationQualityService (generation lifecycle)
- ValidationOrchestrator, SchemaValidator (comprehensive validation)
"""

from .post_generation_service import PostGenerationQualityService
from .pre_generation_service import PreGenerationValidationService
from .orchestrator import (
    ComprehensiveValidationResult,
    ValidationOrchestrator,
    validate_material,
    validate_material_lifecycle,
)
from .schema_validator import (
    SchemaType,
    SchemaValidator,
    ValidationResult,
    ValidationMode,
    validate_categories_yaml,
    validate_frontmatter,
    validate_materials_yaml,
)

__all__ = [
    # Lifecycle services
    'PreGenerationValidationService',
    'PostGenerationQualityService',
    # Orchestration
    'ValidationOrchestrator',
    'ComprehensiveValidationResult',
    'validate_material',
    'validate_material_lifecycle',
    # Schema validation
    'SchemaValidator',
    'SchemaType',
    'ValidationResult',
    'ValidationMode',
    'validate_frontmatter',
    'validate_materials_yaml',
    'validate_categories_yaml',
]
