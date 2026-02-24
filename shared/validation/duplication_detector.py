"""
Backward-compat shim — implementation at shared.validation.core.schema

Date: February 23, 2026
"""

from shared.validation.core.schema import DuplicationDetector
from shared.validation.errors import ValidationResult


# Legacy function wrapper for backward compatibility
def validate_duplication(data, context=None):
    """Legacy function wrapper - use DuplicationDetector class instead."""
    detector = DuplicationDetector()
    return detector.validate(data, context)

__all__ = ['DuplicationDetector', 'ValidationResult', 'validate_duplication']
