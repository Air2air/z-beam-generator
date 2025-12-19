"""
YAML Utilities - Centralized YAML loading with consistent error handling

Provides standardized YAML loading functions to replace repeated
`with open() / yaml.safe_load()` patterns across the codebase.

Created: December 19, 2025
Purpose: Code consolidation and DRY compliance
"""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml


def load_yaml(file_path: Path, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Load YAML file with consistent error handling.
    
    Args:
        file_path: Path to YAML file
        default: Default value if file empty (default: {})
    
    Returns:
        Loaded YAML data as dict
    
    Raises:
        FileNotFoundError: If file doesn't exist
        yaml.YAMLError: If YAML parsing fails
    
    Example:
        >>> data = load_yaml(Path('data/materials/Materials.yaml'))
        >>> materials = data.get('materials', {})
    """
    if default is None:
        default = {}
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or default


def load_yaml_safe(file_path: Path, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Load YAML file with error suppression (returns default on error).
    
    Use this when a missing/invalid file should not stop execution.
    
    Args:
        file_path: Path to YAML file
        default: Default value if file missing/empty/invalid (default: {})
    
    Returns:
        Loaded YAML data or default
    
    Example:
        >>> # Won't raise if file missing
        >>> data = load_yaml_safe(Path('optional_config.yaml'), default={'enabled': False})
    """
    if default is None:
        default = {}
    
    try:
        return load_yaml(file_path, default)
    except (FileNotFoundError, yaml.YAMLError):
        return default
