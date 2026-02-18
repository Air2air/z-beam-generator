"""
Backward-compatible prompt validator import.

Canonical implementation lives in shared.validation.content.prompt_validator.
This shim preserves legacy import paths.
"""

from shared.validation.content.prompt_validator import (  # noqa: F401
    PromptValidationResult,
    PromptValidator,
    ValidationCategory,
    ValidationIssue,
    ValidationSeverity,
    validate_image_prompt,
    validate_text_prompt,
)
