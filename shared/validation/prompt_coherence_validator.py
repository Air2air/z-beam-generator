"""
Backward-compatible prompt coherence validator import.

Canonical implementation lives in shared.validation.content.prompt_coherence_validator.
This shim preserves legacy import paths.
"""

from shared.validation.content.prompt_coherence_validator import (  # noqa: F401
    CoherenceIssue,
    CoherenceIssueType,
    CoherenceValidationResult,
    PromptCoherenceValidator,
    validate_prompt_coherence,
)
