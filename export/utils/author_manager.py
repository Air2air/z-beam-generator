#!/usr/bin/env python3
"""
Author Management — export layer shim.

Canonical implementation lives in shared.utils.author_manager.
This module preserves backward-compatible import paths for callers that
use 'from export.utils.author_manager import ...'.
"""

from shared.utils.author_manager import (  # noqa: F401
    extract_author_info_from_content,
    extract_author_info_from_frontmatter_file,
    get_author_by_id,
    get_author_info_for_generation,
    get_author_info_for_material,
    list_authors,
    load_authors,
)

__all__ = [
    "extract_author_info_from_content",
    "extract_author_info_from_frontmatter_file",
    "get_author_by_id",
    "get_author_info_for_generation",
    "get_author_info_for_material",
    "list_authors",
    "load_authors",
]
