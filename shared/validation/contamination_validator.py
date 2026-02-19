"""Backward-compatible import path for contamination validator.

This module preserves legacy imports:
    from shared.validation.contamination_validator import ContaminationValidator

Canonical implementation lives in:
    shared.validation.domain.contamination_validator
"""

from shared.validation.domain.contamination_validator import ContaminationValidator

__all__ = ["ContaminationValidator"]
