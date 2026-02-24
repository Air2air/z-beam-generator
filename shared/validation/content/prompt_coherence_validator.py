"""
Backward-compat shim — implementation moved to prompt_validators.py

All symbols re-exported from the canonical module:
  shared.validation.content.prompt_validators

Date: February 23, 2026
"""
from shared.validation.content.prompt_validators import (
    CoherenceIssueType,
    CoherenceIssue,
    CoherenceValidationResult,
    PromptCoherenceValidator,
    validate_prompt_coherence,
)

__all__ = [
    "CoherenceIssueType",
    "CoherenceIssue",
    "CoherenceValidationResult",
    "PromptCoherenceValidator",
    "validate_prompt_coherence",
]
