"""
DEPRECATED: Redirect wrapper for backward compatibility.
Use validation.core.schema instead.
"""
import warnings
from validation.core.schema import DuplicationDetector
from validation.errors import ValidationResult

warnings.warn(
    "Importing from validation.duplication_detector is deprecated. "
    "Use 'from validation.core.schema import DuplicationDetector' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Legacy function wrapper for backward compatibility
def validate_duplication(data, context=None):
    """Legacy function wrapper - use DuplicationDetector class instead."""
    detector = DuplicationDetector()
    return detector.validate(data, context)

__all__ = ['DuplicationDetector', 'ValidationResult', 'validate_duplication']
