"""
Unified YAML I/O Module
========================

Consolidates all YAML loading and saving functionality from:
- yaml_loader.py (fast C-based loading)
- yaml_parser.py (multi-document parsing)
- yaml_utils.py (safe loading with defaults)

Created: January 4, 2026
Purpose: Single source of truth for YAML operations

Usage:
    from shared.utils.yaml_io import load_yaml, save_yaml, load_multi_document
    
    # Fast loading with C-based parser (default)
    data = load_yaml('data/materials/Materials.yaml')
    
    # Safe loading with fallback default
    config = load_yaml('config.yaml', default={}, safe=True)
    
    # Atomic saving with backup
    save_yaml('output.yaml', data, atomic=True, backup=True)
    
    # Multi-document YAML (component files)
    docs = load_multi_document('components/micro.yaml')
"""

import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

# Try to import C-based loaders (10x faster)
try:
    from yaml import CDumper as Dumper
    from yaml import CLoader as Loader
    FAST_LOADER_AVAILABLE = True
    YAML_LOADER_TYPE = "C-based (LibYAML)"
except ImportError:
    from yaml import Dumper, Loader
    FAST_LOADER_AVAILABLE = False
    YAML_LOADER_TYPE = "Python (slower)"


def load_yaml(
    file_path: Union[str, Path],
    default: Optional[Dict[str, Any]] = None,
    fast: bool = True,
    safe: bool = True,
    encoding: str = 'utf-8'
) -> Dict[str, Any]:
    """
    Load YAML file with unified interface.
    
    Args:
        file_path: Path to YAML file
        default: Default value if file empty or missing (when safe=True)
        fast: Use C-based loader if available (10x faster)
        safe: Return default instead of raising on missing file
        encoding: File encoding (default: utf-8)
    
    Returns:
        Loaded YAML data as dict
    
    Raises:
        FileNotFoundError: If file doesn't exist and safe=False
        yaml.YAMLError: If YAML parsing fails
    
    Examples:
        >>> # Fast loading (default)
        >>> data = load_yaml('Materials.yaml')
        
        >>> # Safe loading with default
        >>> config = load_yaml('config.yaml', default={}, safe=True)
        
        >>> # Python loader (for compatibility)
        >>> data = load_yaml('file.yaml', fast=False)
    """
    if default is None:
        default = {}
    
    file_path = Path(file_path)
    
    # Handle missing file
    if not file_path.exists():
        if safe:
            return default
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Select loader
    loader = Loader if (fast and FAST_LOADER_AVAILABLE) else yaml.SafeLoader
    
    # Load YAML
    with open(file_path, 'r', encoding=encoding) as f:
        data = yaml.load(f, Loader=loader)
        return data if data is not None else default


def save_yaml(
    file_path: Union[str, Path],
    data: Any,
    atomic: bool = True,
    backup: bool = False,
    fast: bool = True,
    encoding: str = 'utf-8'
) -> None:
    """
    Save data to YAML file with atomic writes and optional backup.
    
    Args:
        file_path: Path to output YAML file
        data: Data to save
        atomic: Use atomic write (temp file + rename)
        backup: Create .backup file before overwriting
        fast: Use C-based dumper if available
        encoding: File encoding (default: utf-8)
    
    Raises:
        IOError: If write fails
    
    Examples:
        >>> # Atomic write (default, safest)
        >>> save_yaml('output.yaml', data)
        
        >>> # With backup
        >>> save_yaml('Materials.yaml', data, backup=True)
        
        >>> # Direct write (faster, less safe)
        >>> save_yaml('temp.yaml', data, atomic=False)
    """
    file_path = Path(file_path)
    
    # Create backup if requested
    if backup and file_path.exists():
        backup_path = file_path.with_suffix(file_path.suffix + '.backup')
        import shutil
        shutil.copy2(file_path, backup_path)
    
    # Select dumper
    dumper = Dumper if (fast and FAST_LOADER_AVAILABLE) else yaml.SafeDumper
    
    # Serialize to YAML
    yaml_content = yaml.dump(
        data,
        Dumper=dumper,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False
    )
    
    if atomic:
        # Atomic write: temp file + rename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode='w',
            encoding=encoding,
            dir=file_path.parent,
            delete=False,
            suffix='.tmp'
        ) as tmp:
            tmp.write(yaml_content)
            tmp_path = Path(tmp.name)
        
        # Atomic rename
        tmp_path.replace(file_path)
    else:
        # Direct write
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(yaml_content)


def load_multi_document(
    file_path: Union[str, Path],
    fast: bool = True,
    encoding: str = 'utf-8'
) -> List[Dict[str, Any]]:
    """
    Load YAML file with multiple documents (--- separators).
    
    Used for component files that contain multiple YAML documents.
    
    Args:
        file_path: Path to multi-document YAML file
        fast: Use C-based loader if available
        encoding: File encoding (default: utf-8)
    
    Returns:
        List of document dicts
    
    Raises:
        FileNotFoundError: If file doesn't exist
        yaml.YAMLError: If YAML parsing fails
    
    Examples:
        >>> # Load component file with multiple docs
        >>> docs = load_multi_document('components/micro.yaml')
        >>> for doc in docs:
        >>>     print(doc['component_type'])
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Select loader
    loader = Loader if (fast and FAST_LOADER_AVAILABLE) else yaml.SafeLoader
    
    # Load all documents
    with open(file_path, 'r', encoding=encoding) as f:
        docs = list(yaml.load_all(f, Loader=loader))
    
    # Filter out None documents
    return [doc for doc in docs if doc is not None]


def load_yaml_with_retry(
    file_path: Union[str, Path],
    max_retries: int = 3,
    retry_delay: float = 0.1,
    **kwargs
) -> Dict[str, Any]:
    """
    Load YAML with retry logic for file system race conditions.
    
    Useful when files might be temporarily locked or in use.
    
    Args:
        file_path: Path to YAML file
        max_retries: Maximum retry attempts
        retry_delay: Delay between retries (seconds)
        **kwargs: Additional args passed to load_yaml()
    
    Returns:
        Loaded YAML data
    
    Raises:
        FileNotFoundError: After all retries if file not found
        IOError: After all retries if read fails
    """
    import time
    
    last_error = None
    for attempt in range(max_retries):
        try:
            return load_yaml(file_path, **kwargs)
        except (IOError, OSError) as e:
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            continue
    
    raise IOError(f"Failed to load {file_path} after {max_retries} attempts: {last_error}")


def validate_yaml_structure(
    data: Dict[str, Any],
    required_keys: List[str],
    optional_keys: Optional[List[str]] = None
) -> bool:
    """
    Validate YAML data has required structure.
    
    Args:
        data: Loaded YAML data
        required_keys: Keys that must be present
        optional_keys: Keys that may be present
    
    Returns:
        True if valid
    
    Raises:
        ValueError: If validation fails
    
    Examples:
        >>> data = load_yaml('config.yaml')
        >>> validate_yaml_structure(data, ['domain', 'source_file'])
    """
    if optional_keys is None:
        optional_keys = []
    
    # Check required keys
    missing = [key for key in required_keys if key not in data]
    if missing:
        raise ValueError(f"Missing required keys: {missing}")
    
    # Check for unexpected keys
    all_keys = set(required_keys + optional_keys)
    unexpected = [key for key in data.keys() if key not in all_keys]
    if unexpected:
        import warnings
        warnings.warn(f"Unexpected keys in YAML: {unexpected}")
    
    return True


# Convenience aliases for backward compatibility
load_yaml_fast = load_yaml  # Default is fast=True
load_yaml_safe = lambda path, default=None: load_yaml(path, default=default, safe=True)
dump_yaml_fast = save_yaml  # Default is fast=True

# Module info
__all__ = [
    'load_yaml',
    'save_yaml',
    'load_multi_document',
    'load_yaml_with_retry',
    'validate_yaml_structure',
    'load_yaml_fast',
    'load_yaml_safe',
    'dump_yaml_fast',
    'YAML_LOADER_TYPE',
    'FAST_LOADER_AVAILABLE'
]
