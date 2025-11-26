"""
Contaminants Domain

Defines contamination patterns, material compatibility, and validation rules
for industrial laser cleaning applications.

This domain provides:
- Contamination pattern definitions with physical properties
- Material-contaminant compatibility matrix
- Pre-generation validation for physically impossible combinations
- Context-aware contamination rules (machinery vs decorative)

Author: AI Assistant
Date: November 25, 2025
"""

from .models import (
    ContaminantPattern,
    MaterialProperties,
    ContaminationContext,
    ValidationResult,
    ValidationIssue,
    MaterialCompatibility,
    ContaminantCategory,
    ValidationSeverity
)

from .validator import ContaminationValidator
from .library import ContaminationLibrary, get_library, reload_library

__all__ = [
    'ContaminantPattern',
    'MaterialProperties',
    'ContaminationContext',
    'ValidationResult',
    'ValidationIssue',
    'MaterialCompatibility',
    'ContaminantCategory',
    'ValidationSeverity',
    'ContaminationValidator',
    'ContaminationLibrary',
    'get_library',
    'reload_library',
]
