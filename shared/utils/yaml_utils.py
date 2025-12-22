"""
YAML Utilities - Centralized YAML I/O with consistent error handling

Provides standardized YAML loading and saving functions to replace repeated
`with open() / yaml.safe_load()` and `yaml.safe_dump()` patterns across the codebase.

Consolidates 27+ YAML loading functions across the codebase.

Created: December 19, 2025
Updated: December 21, 2025 - Enhanced with additional convenience functions
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


def load_yaml_with_backup(
    file_path: Path,
    backup_dir: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Load YAML and automatically create timestamped backup.
    
    Useful when loading file that will be modified and saved back.
    
    Args:
        file_path: Path to YAML file
        backup_dir: Directory for backup (default: same as file)
    
    Returns:
        Loaded YAML data
    
    Example:
        >>> # Load and auto-backup before modification
        >>> data = load_yaml_with_backup(Path('data/Materials.yaml'))
        >>> data['materials']['new_material'] = {...}
        >>> save_yaml(Path('data/Materials.yaml'), data)
    """
    from shared.utils.backup_utils import create_timestamped_backup
    
    # Create backup first
    create_timestamped_backup(file_path, backup_dir)
    
    # Then load
    return load_yaml(file_path)


def merge_yaml_files(*file_paths: Path) -> Dict[str, Any]:
    """
    Load and merge multiple YAML files.
    
    Later files override earlier ones for duplicate keys.
    
    Args:
        *file_paths: Paths to YAML files to merge
    
    Returns:
        Merged data dictionary
    
    Example:
        >>> # Merge base config with overrides
        >>> config = merge_yaml_files(
        ...     Path('config/base.yaml'),
        ...     Path('config/production.yaml')
        ... )
    """
    result = {}
    
    for file_path in file_paths:
        data = load_yaml_safe(file_path)
        if data:
            result.update(data)
    
    return result


def validate_yaml_structure(
    file_path: Path,
    required_keys: list[str]
) -> bool:
    """
    Validate YAML file has required top-level keys.
    
    Args:
        file_path: Path to YAML file
        required_keys: List of required keys
    
    Returns:
        True if all required keys present, False otherwise
    
    Example:
        >>> # Validate Materials.yaml structure
        >>> valid = validate_yaml_structure(
        ...     Path('data/Materials.yaml'),
        ...     ['materials', 'categories']
        ... )
        >>> if not valid:
        ...     raise ValueError("Invalid Materials.yaml structure")
    """
    try:
        data = load_yaml(file_path)
        return all(key in data for key in required_keys)
    except (FileNotFoundError, yaml.YAMLError):
        return False


def get_yaml_size_stats(file_path: Path) -> Dict[str, Any]:
    """
    Get size statistics for YAML file.
    
    Args:
        file_path: Path to YAML file
    
    Returns:
        Dict with file size, item counts, and depth
    
    Example:
        >>> stats = get_yaml_size_stats(Path('data/Materials.yaml'))
        >>> print(f"File size: {stats['size_kb']} KB")
        >>> print(f"Top-level keys: {stats['top_level_keys']}")
    """
    data = load_yaml(file_path)
    file_size = file_path.stat().st_size
    
    def get_depth(obj, current_depth=0):
        """Recursively calculate max depth."""
        if not isinstance(obj, dict):
            return current_depth
        if not obj:
            return current_depth
        return max(get_depth(v, current_depth + 1) for v in obj.values())
    
    return {
        'size_bytes': file_size,
        'size_kb': file_size / 1024,
        'size_mb': file_size / (1024 * 1024),
        'top_level_keys': len(data),
        'max_depth': get_depth(data),
        'is_empty': not data
    }
