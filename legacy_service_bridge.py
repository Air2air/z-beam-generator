#!/usr/bin/env python3
"""
Legacy Service Bridge - Backward Compatibility

Provides backward compatibility for existing imports while transitioning
to the new consolidated services architecture. This bridge ensures that
existing code continues to work during the transition period.

This file should be removed after all imports are updated to use the
new services structure.

Last Updated: October 22, 2025
"""

import warnings
from typing import Any

# Import new consolidated services
from services.validation import (
    ValidationOrchestrator,
    UnifiedSchemaValidator,
    validate_material_lifecycle
)
from services.research import AIResearchEnrichmentService
from services.property import PropertyManager, MaterialAuditor

# Legacy import paths - issue deprecation warnings
def _deprecated_import(old_path: str, new_path: str) -> None:
    """Issue deprecation warning for old import paths"""
    warnings.warn(
        f"Import from '{old_path}' is deprecated. Use '{new_path}' instead.",
        DeprecationWarning,
        stacklevel=3
    )

# Legacy validation service imports
class LegacyValidationServiceBridge:
    """Bridge for legacy validation service imports"""
    
    @staticmethod
    def get_pre_generation_service():
        _deprecated_import(
            "validation.services.pre_generation_service",
            "services.validation.ValidationOrchestrator"
        )
        return ValidationOrchestrator()
    
    @staticmethod
    def get_post_generation_service():
        _deprecated_import(
            "validation.services.post_generation_service", 
            "services.validation.ValidationOrchestrator"
        )
        return ValidationOrchestrator()
    
    @staticmethod
    def get_material_auditor():
        _deprecated_import(
            "components.frontmatter.services.material_auditor",
            "services.property.MaterialAuditor"
        )
        return MaterialAuditor()

# Legacy component service imports
class LegacyComponentServiceBridge:
    """Bridge for legacy component service imports"""
    
    @staticmethod
    def get_property_manager(*args, **kwargs):
        _deprecated_import(
            "components.frontmatter.services.property_manager",
            "services.property.PropertyManager"
        )
        return PropertyManager(*args, **kwargs)
    
    @staticmethod
    def get_validation_service():
        _deprecated_import(
            "components.frontmatter.services.validation_service",
            "services.validation.ValidationOrchestrator"
        )
        return ValidationOrchestrator()

# Convenience functions for common legacy patterns
def get_unified_validator(**kwargs) -> ValidationOrchestrator:
    """
    Get unified validation interface (replaces multiple validation services).
    
    This replaces patterns like:
    - PreGenerationValidationService()  
    - PostGenerationQualityService()
    - MaterialAuditor()
    - ValidationService()
    
    Returns single ValidationOrchestrator that coordinates all validation.
    """
    return ValidationOrchestrator()

def get_material_validator(**kwargs) -> MaterialAuditor:
    """Get material auditor (legacy compatibility)"""
    return MaterialAuditor()

def get_schema_validator(**kwargs) -> UnifiedSchemaValidator:
    """Get unified schema validator (replaces multiple schema validators)"""
    return UnifiedSchemaValidator(**kwargs)

# Export legacy compatibility interfaces
__all__ = [
    'LegacyValidationServiceBridge',
    'LegacyComponentServiceBridge', 
    'get_unified_validator',
    'get_material_validator',
    'get_schema_validator',
]