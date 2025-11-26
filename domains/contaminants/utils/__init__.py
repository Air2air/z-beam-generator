"""
Contamination Domain Utilities

Utility functions for laser property operations, unit normalization,
and property classification.

Author: Z-Beam Generator
Date: November 25, 2025
"""

from .laser_property_helpers import (
    extract_wavelength_value,
    normalize_laser_unit,
    classify_laser_property,
    validate_optical_physics,
    parse_fluence_range,
    parse_speed_range
)

from .pattern_cache import PatternPropertyCache

__all__ = [
    'extract_wavelength_value',
    'normalize_laser_unit',
    'classify_laser_property',
    'validate_optical_physics',
    'parse_fluence_range',
    'parse_speed_range',
    'PatternPropertyCache'
]
