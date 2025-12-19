"""
YAML Utilities - Centralized YAML I/O with consistent error handling

Provides standardized YAML loading and saving functions to replace repeated
`with open() / yaml.safe_load()` and `yaml.safe_dump()` patterns across the codebase.

Created: December 19, 2025
Updated: December 19, 2025 - Added save_yaml() and save_yaml_atomic()
Purpose: Code consolidation and DRY compliance
"""

import tempfile
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


def save_yaml(
    file_path: Path,
    data: Dict[str, Any],
    backup: bool = False,
    sort_keys: bool = False
) -> None:
    """
    Save YAML file with consistent formatting.
    
    Args:
        file_path: Path to save YAML file
        data: Data to write
        backup: Create .bak file before overwriting (default: False)
        sort_keys: Sort keys alphabetically (default: False)
    
    Raises:
        IOError: If file cannot be written
    
    Example:
        >>> data = {'materials': {'Aluminum': {...}}}
        >>> save_yaml(Path('data/materials/Materials.yaml'), data)
    """
    if backup and file_path.exists():
        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
        backup_path.write_bytes(file_path.read_bytes())
    
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(
            data,
            f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=sort_keys
        )


def save_yaml_atomic(
    file_path: Path,
    data: Dict[str, Any],
    sort_keys: bool = False
) -> None:
    """
    Save YAML file with atomic write (temp file + rename).
    
    Ensures file is either fully written or not modified at all.
    Prevents corruption if write is interrupted.
    
    Args:
        file_path: Path to save YAML file
        data: Data to write
        sort_keys: Sort keys alphabetically (default: False)
    
    Raises:
        IOError: If file cannot be written
    
    Example:
        >>> # Critical data - use atomic write
        >>> save_yaml_atomic(Path('data/materials/Materials.yaml'), data)
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to temp file in same directory (ensures same filesystem)
    with tempfile.NamedTemporaryFile(
        mode='w',
        encoding='utf-8',
        dir=file_path.parent,
        delete=False,
        suffix='.tmp'
    ) as tmp_file:
        yaml.safe_dump(
            data,
            tmp_file,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=sort_keys
        )
        tmp_path = Path(tmp_file.name)
    
    # Atomic rename
    tmp_path.replace(file_path)
