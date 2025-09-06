"""
Badge Symbol Component

Generates standardized badge symbol tables from frontmatter data.
This is a static component that extracts data without requiring API calls.
"""

from .generator import (
    BadgeSymbolGenerator,
    create_badge_symbol_template,
    generate_badge_symbol_content,
)

__all__ = [
    "BadgeSymbolGenerator",
    "generate_badge_symbol_content",
    "create_badge_symbol_template",
]
