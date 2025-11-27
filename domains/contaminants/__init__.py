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
    MaterialCompatibility,
)
# ✅ FIXED (Nov 26, 2025): Export shared types from shared/ to avoid cross-domain imports
from shared.types.contamination import (
    ContaminationContext,
    ValidationResult,
    ValidationIssue,
    ContaminantCategory,
    ValidationSeverity
)
# Re-export contamination_levels from shared for backward compatibility
from shared.types import contamination_levels

# Import validator locally (don't re-export to avoid circular import)
from .validator import ContaminationValidator as _LocalValidator

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
    'contamination_levels',
    'ContaminationLibrary',
    'get_library',
    'reload_library',
]
