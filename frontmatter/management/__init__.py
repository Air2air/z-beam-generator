"""
Frontmatter Management Module
Core management classes and utilities for frontmatter handling.
"""

from .manager import (
    FrontmatterManager,
    FrontmatterNotFoundError,
    FrontmatterValidationError
)

from .migrator import FrontmatterMigrator

__all__ = [
    'FrontmatterManager',
    'FrontmatterNotFoundError', 
    'FrontmatterValidationError',
    'FrontmatterMigrator'
]
