#!/usr/bin/env python3
"""
File Operations Wrapper

Wrapper module for file operations functions to maintain backward compatibility
with existing test patches and imports.
"""

from pathlib import Path
from shared.utils.file_ops.file_operations import (
    save_component_to_file_original,
    create_backup_file,
    create_backup_directory,
)
from shared.utils.file_ops.path_manager import PathManager

# Re-export functions for backward compatibility
__all__ = [
    'save_component_to_file_original',
    'create_backup_file',
    'create_backup_directory',
    'get_project_root',
]


def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Uses PathManager to find project root by looking for marker files
    (requirements.txt, data/ directory) rather than counting parent directories.
    
    Returns:
        Path to project root directory
        
    Example:
        >>> from shared.utils.file_operations import get_project_root
        >>> project_root = get_project_root()
        >>> materials_file = project_root / 'data' / 'materials' / 'Materials.yaml'
    """
    return PathManager.get_project_root()
