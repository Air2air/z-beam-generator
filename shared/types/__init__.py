"""
Shared Type Definitions

Common data structures used across multiple domains.
No domain-specific logic - pure data types only.
"""

from .contamination import (
    ContaminantCategory,
    ContaminationContext,
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
)

__all__ = [
    'ContaminationContext',
    'ContaminantCategory',
    'ValidationSeverity',
    'ValidationResult',
    'ValidationIssue',
]
