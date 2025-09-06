"""
Utilities module for Z-Beam Generator

Provides common utility functions for slug generation, file management,
and other shared functionality across the generator system.
"""

from .slug_utils import (

    create_filename_slug,
    create_material_slug,
    extract_material_from_filename,
    get_clean_material_mapping,
    normalize_material_name,
    validate_slug,
)

__all__ = [
    "create_material_slug",
    "create_filename_slug",
    "extract_material_from_filename",
    "normalize_material_name",
    "get_clean_material_mapping",
    "validate_slug",
]
