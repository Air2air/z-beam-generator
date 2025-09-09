#!/usr/bin/env python3
"""
File Operations Wrapper

Wrapper module for file operations functions to maintain backward compatibility
with existing test patches and imports.
"""

from utils.file_ops.file_operations import save_component_to_file_original

# Re-export functions for backward compatibility
__all__ = [
    'save_component_to_file_original',
]
