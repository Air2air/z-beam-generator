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
from typing import Any, Dict, Optional, Union

import yaml

# Try to import C-based loaders (10x faster for large files)
try:
    from yaml import CDumper as _CDumper
    from yaml import CLoader as _CLoader
    _FAST_LOADER_AVAILABLE = True
    YAML_LOADER_TYPE = "C-based (LibYAML)"
except ImportError:
    from yaml import Dumper as _CDumper  # type: ignore[assignment]
    from yaml import Loader as _CLoader  # type: ignore[assignment]
    _FAST_LOADER_AVAILABLE = False
    YAML_LOADER_TYPE = "Python (slower)"

def load_yaml(file_path: Path) -> Dict[str, Any]:
    """
    Load YAML file with consistent error handling.
    
    Args:
        file_path: Path to YAML file
    
    Returns:
        Loaded YAML data as dict
    
    Raises:
        FileNotFoundError: If file doesn't exist
        yaml.YAMLError: If YAML parsing fails
    
    Example:
        >>> data = load_yaml(Path('data/materials/Materials.yaml'))
        >>> materials = data.get('materials', {})
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    if data is None:
        raise ValueError(f"YAML file is empty: {file_path}")
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a dictionary: {file_path}")
    return data


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
        data = load_yaml(file_path)
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
    except (FileNotFoundError, yaml.YAMLError, ValueError):
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


# ---------------------------------------------------------------------------
# Fast C-loader variants (10x faster for large files when LibYAML is installed)
# Migrated from shared/utils/yaml_loader.py
# ---------------------------------------------------------------------------

def load_yaml_fast(file_path: Union[str, Path]) -> Any:
    """
    Load YAML with fastest available loader (C-based LibYAML when available).

    Args:
        file_path: Path to YAML file

    Returns:
        Parsed YAML data

    Raises:
        FileNotFoundError: If file doesn't exist
        yaml.YAMLError: If YAML is invalid

    Performance:
        ~0.5s for 3 MB file with C loader vs ~5s with Python loader.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"YAML file not found: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.load(f, Loader=_CLoader)


def dump_yaml_fast(data: Any, file_path: Union[str, Path], **kwargs) -> None:
    """
    Dump YAML with fastest available dumper.

    Args:
        data: Data to dump
        file_path: Output file path
        **kwargs: Passed to yaml.dump() (default_flow_style, allow_unicode, etc.)
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    dump_kwargs: Dict[str, Any] = {
        'allow_unicode': True,
        'default_flow_style': False,
        'sort_keys': False,
    }
    dump_kwargs.update(kwargs)
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, Dumper=_CDumper, **dump_kwargs)


def get_loader_info() -> Dict[str, Any]:
    """Return information about the active YAML loader."""
    return {
        'loader_type': YAML_LOADER_TYPE,
        'fast_loader_available': _FAST_LOADER_AVAILABLE,
        'estimated_speedup': '10x' if _FAST_LOADER_AVAILABLE else '1x',
    }
