"""
Validation module for Z-Beam Generator

Provides consolidated validation functions for content validation,
reference validation, and other validation tasks.
"""

from .frontmatter_validator import FrontmatterDependencyValidator
from .layer_validator import LayerValidator
from .content.quality_validator import QualityScoreValidator

# Reference validation (new)
from .reference_registry import ReferenceInfo, ReferenceRegistry
from .validation_schema import ValidationSchema
from .validator import (
    FixAction,
    IssueCategory,
    IssueSeverity,
    Validator,
    ValidationIssue,
    ValidationReport,
    ValidationStage,
    ValidationStatus,
    create_validator,
    validate_and_fix,
    validate_prompt_quick,
)
from .validator_mixin import ReferenceValidatorMixin

__all__ = [
    "QualityScoreValidator",
    "FrontmatterDependencyValidator",
    "LayerValidator",
    # Unified validation
    "Validator",
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
