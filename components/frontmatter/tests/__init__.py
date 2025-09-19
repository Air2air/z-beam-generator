#!/usr/bin/env python3
"""
Frontmatter Tests Package

Modular test suite for the refactored frontmatter component.
Organized by service responsibility for better maintainability.
"""

from .test_core_generator import TestCoreGenerator, TestGeneratorEdgeCases
from .test_field_ordering import TestFieldOrderingService
from .test_property_enhancement import TestPropertyEnhancementService, TestPropertyEnhancementEdgeCases
from .test_validation_helpers import TestValidationHelpers, TestValidationHelpersEdgeCases
from .test_integration import TestModularIntegration, TestModularArchitectureQuality

__all__ = [
    'TestCoreGenerator',
    'TestGeneratorEdgeCases', 
    'TestFieldOrderingService',
    'TestPropertyEnhancementService',
    'TestPropertyEnhancementEdgeCases',
    'TestValidationHelpers',
    'TestValidationHelpersEdgeCases',
    'TestModularIntegration',
    'TestModularArchitectureQuality'
]
