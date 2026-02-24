"""
Unified Prompt Validator — backward-compatibility shim.

Canonical implementation: shared.validation.unified_validator
This module preserves legacy import paths.
"""

from shared.validation.unified_validator import (  # noqa: F401
    EarlyStageValidator,
    FixAction,
    IssueSeverity,
    IssueCategory,
    PostStageValidator,
    PromptStageValidator,
    ValidationIssue,
    ValidationReport,
    ValidationStage,
    ValidationStatus,
    Validator,
    create_validator,
    validate_and_fix,
    validate_prompt_quick,
)

__all__ = [
    "EarlyStageValidator",
    "FixAction",
    "IssueSeverity",
    "IssueCategory",
    "PostStageValidator",
    "PromptStageValidator",
    "ValidationIssue",
    "ValidationReport",
    "ValidationStage",
    "ValidationStatus",
    "Validator",
    "create_validator",
    "validate_and_fix",
    "validate_prompt_quick",
]
