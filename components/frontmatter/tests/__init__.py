#!/usr/bin/env python3
"""
Frontmatter Tests Package

Modular test suite for the frontmatter component.
"""

# Import available test modules
try:
    from .test_frontmatter_consolidated import *
except ImportError:
    pass

try:
    from .test_schema_validation import *
except ImportError:
    pass

__all__ = []
