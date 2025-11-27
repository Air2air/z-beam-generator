"""
Shared Type Definitions

Common data structures used across multiple domains.
No domain-specific logic - pure data types only.
"""

from .contamination import (
    ContaminationContext,
    ContaminantCategory,
    ValidationSeverity,
    ValidationResult,
    ValidationIssue
)

__all__ = [
    'ContaminationContext',
    'ContaminantCategory',
    'ValidationSeverity',
    'ValidationResult',
    'ValidationIssue',
]
