"""
Validation module for Z-Beam Generator

Provides consolidated validation functions for content validation,
reference validation, and other validation tasks.
"""

from .quality_validator import QualityScoreValidator
from .frontmatter_validator import FrontmatterDependencyValidator
from .layer_validator import LayerValidator
from .validator import (
    UnifiedValidator,
    ValidationReport,
    ValidationStatus,
    ValidationStage,
    ValidationIssue,
    FixAction,
    IssueSeverity,
    IssueCategory,
    create_validator,
    validate_prompt_quick,
    validate_and_fix,
)

# Reference validation (new)
from .reference_registry import ReferenceRegistry, ReferenceInfo
from .validator_mixin import ReferenceValidatorMixin
from .validation_schema import ValidationSchema

__all__ = [
    "QualityScoreValidator",
    "FrontmatterDependencyValidator",
    "LayerValidator",
    # Unified validation
    "UnifiedValidator",
    "ValidationReport",
    "ValidationStatus",
    "ValidationStage",
    "ValidationIssue",
    "FixAction",
    "IssueSeverity",
    "IssueCategory",
    "create_validator",
    "validate_prompt_quick",
    "validate_and_fix",
    # Reference validation
    "ReferenceRegistry",
    "ReferenceInfo",
    "ReferenceValidatorMixin",
    "ValidationSchema",
]
