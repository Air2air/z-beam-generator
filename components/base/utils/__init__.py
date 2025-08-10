"""
Z-Beam Generator Base Utilities

This package contains utility modules for content formatting, validation,
and other common operations used across the Z-Beam generator components.

Available modules:
- content_formatter: Main content formatting utilities
- bullet_formatter: Bullet point processing utilities  
- table_formatter: Table processing utilities
- jsonld_formatter: JSON-LD formatting utilities
- validation: Content validation utilities
- formatting: Legacy formatting utilities
- slug_utils: URL slug generation utilities
"""

# Main exports
from .content_formatter import ContentFormatter
from .bullet_formatter import extract_bullet_points, format_bullet_points, format_bullet_points_as_markdown
from .table_formatter import TableFormatter
from .jsonld_formatter import JsonldFormatter
from .validation import validate_non_empty, validate_category_consistency
from .slug_utils import SlugUtils

__all__ = [
    'ContentFormatter',
    'extract_bullet_points', 
    'format_bullet_points',
    'format_bullet_points_as_markdown',
    'TableFormatter',
    'JsonldFormatter', 
    'validate_non_empty',
    'validate_category_consistency',
    'SlugUtils'
]
