#!/usr/bin/env python3
"""
Reusable YAML Data Helper

Domain-agnostic helper for atomic YAML file operations.
Handles loading, saving with atomic writes, and field updates.

Usage:
    from shared.generation.yaml_helper import (
        load_yaml_file,
        save_yaml_file,
        update_yaml_field
    )
    
    # Load data
    data = load_yaml_file("data/settings/Settings.yaml")
    
    # Update and save
    data['settings']['Aluminum']['field'] = value
    save_yaml_file("data/settings/Settings.yaml", data)
    
    # Or use helper for single field update
    update_yaml_field(
        yaml_path="data/settings/Settings.yaml",
        keys=['settings', 'Aluminum', 'component_summaries'],
        value=summaries_dict
    )
"""

import logging
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import yaml

logger = logging.getLogger(__name__)


def load_yaml_file(path: str | Path) -> Dict[str, Any]:
    """
    Load YAML file and return contents.
    
    Args:
        path: Path to YAML file
    
    Returns:
        Parsed YAML data as dict
    
    Raises:
        FileNotFoundError: If file doesn't exist
        yaml.YAMLError: If file is invalid YAML
    """
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    if data is None:
        raise ValueError(f"YAML file is empty: {path}")
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return data


def save_yaml_file(
    path: str | Path,
    data: Dict[str, Any],
    atomic: bool = True
) -> None:
    """
    Save data to YAML file.
    
    Args:
        path: Path to YAML file
        data: Data to save
        atomic: Use atomic write (temp file + rename) for safety
    
    Raises:
        IOError: If write fails
    """
    path = Path(path)
    
    if atomic:
        # Atomic write: write to temp file, then rename
        with tempfile.NamedTemporaryFile(
            mode='w',
            encoding='utf-8',
            dir=path.parent,
            delete=False,
            suffix='.yaml'
        ) as temp_f:
            yaml.safe_dump(
                data,
                temp_f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False
            )
            temp_path = temp_f.name
        
        # Atomic rename (POSIX guarantees atomicity)
        Path(temp_path).replace(path)
    else:
        # Direct write (faster but not atomic)
        with open(path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(
                data,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False
            )


def update_yaml_field(
    yaml_path: str | Path,
    keys: List[str],
    value: Any,
    atomic: bool = True
) -> bool:
    """
    Update a nested field in a YAML file.
    
    Args:
        yaml_path: Path to YAML file
        keys: List of nested keys to traverse (e.g., ['settings', 'Aluminum', 'field'])
        value: Value to set
        atomic: Use atomic write
    
    Returns:
        True if successful
    
    Example:
        update_yaml_field(
            "data/settings/Settings.yaml",
            ['settings', 'Aluminum', 'component_summaries'],
            {'machine_settings': {...}}
        )
    """
    yaml_path = Path(yaml_path)
    
    try:
        data = load_yaml_file(yaml_path)
        
        # Navigate to parent of target key
        current = data
        for key in keys[:-1]:
            if key not in current:
                logger.error(f"Key '{key}' not found in path {keys}")
                return False
            current = current[key]
        
        # Set the value
        current[keys[-1]] = value
        
        # Save
        save_yaml_file(yaml_path, data, atomic=atomic)
        return True
        
    except Exception as e:
        logger.error(f"Failed to update YAML field: {e}")
        return False


def get_yaml_field(
    yaml_path: str | Path,
    keys: List[str],
    default: Any = None
) -> Any:
    """
    Get a nested field from a YAML file.
    
    Args:
        yaml_path: Path to YAML file
        keys: List of nested keys to traverse
        default: Default value if key not found
    
    Returns:
        The value at the path, or default if not found
    """
    try:
        data = load_yaml_file(yaml_path)
        
        current = data
        for key in keys:
            if key not in current:
                return default
            current = current[key]
        
        return current
        
    except Exception:
        return default
