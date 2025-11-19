#!/usr/bin/env python3
"""
Author Manager Wrapper

Wrapper module for author management functions to maintain backward compatibility
with existing test patches and imports.
"""

from export.utils.author_manager import (
    extract_author_info_from_frontmatter_file,
    get_author_by_id,
    get_author_info_for_material,
    load_authors,
)

# Re-export functions for backward compatibility
__all__ = [
    'extract_author_info_from_frontmatter_file',
    'get_author_by_id',
    'get_author_info_for_material',
    'load_authors',
]
