"""
Centralized YAML writing utilities for the export system.

Provides consistent YAML serialization with proper formatting
and SafeDumper usage to prevent Python-specific tags.
"""

import logging
from pathlib import Path
from typing import Any, Dict

import yaml

logger = logging.getLogger(__name__)


def write_yaml(
    file_path: Path | str,
    data: Dict[str, Any],
    create_dirs: bool = True,
    width: int = 120
) -> None:
    """
    Write data to YAML file with consistent formatting.
    
    Uses SafeDumper to prevent Python-specific tags (!!python/object)
    that break JavaScript YAML parsers like js-yaml.
    
    Args:
        file_path: Output file path
        data: Dict to serialize
        create_dirs: Create parent directories if needed (default: True)
        width: Line width for YAML formatting (default: 120)
    
    Raises:
        IOError: If write fails
    
    Example:
        from export.utils.yaml_writer import write_yaml
        write_yaml('output/material.yaml', frontmatter)
    """
    file_path = Path(file_path)
    
    # Create output directory if needed
    if create_dirs:
        file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # CRITICAL: Do NOT convert OrderedDict to dict
    # SafeDumper handles OrderedDict properly without Python tags
    # Converting to dict loses field ordering
    
    # Serialize to YAML string
    # 🚨 CRITICAL: Use SafeDumper to prevent Python-specific tags
    # SafeDumper handles OrderedDict without !!python/object tags
    # AND preserves insertion order for correct field arrangement
    yaml_string = yaml.dump(
        data,  # Keep as OrderedDict to preserve field order
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,  # Preserve field order
        width=width,
        Dumper=yaml.SafeDumper  # MANDATORY - prevents Python tags, handles OrderedDict
    )
    
    # Write to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(yaml_string)
    
    logger.debug(f"Wrote {file_path} ({len(data)} fields)")


def write_frontmatter(
    file_path: Path | str,
    frontmatter: Dict[str, Any],
    create_dirs: bool = True
) -> None:
    """
    Write frontmatter data to YAML file.
    
    Alias for write_yaml with frontmatter-specific defaults.
    
    Args:
        file_path: Output file path
        frontmatter: Frontmatter dict to write
        create_dirs: Create parent directories if needed (default: True)
    
    Raises:
        IOError: If write fails
    
    Example:
        from export.utils.yaml_writer import write_frontmatter
        write_frontmatter('frontmatter/materials/aluminum.yaml', data)
    """
    write_yaml(file_path, frontmatter, create_dirs=create_dirs, width=120)


def serialize_yaml(
    data: Dict[str, Any],
    width: int = 120
) -> str:
    """
    Serialize data to YAML string without writing to file.
    
    Useful for testing, debugging, or when you need the YAML string
    directly without writing to disk.
    
    Args:
        data: Dict to serialize
        width: Line width for YAML formatting (default: 120)
    
    Returns:
        YAML string
    
    Example:
        from export.utils.yaml_writer import serialize_yaml
        yaml_str = serialize_yaml(frontmatter)
        print(yaml_str)
    """
    # CRITICAL: Do NOT convert OrderedDict to dict
    # SafeDumper handles OrderedDict properly without Python tags
    
    return yaml.dump(
        data,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        width=width,
        Dumper=yaml.SafeDumper
    )


def validate_yaml_format(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate that data can be safely serialized to YAML.
    
    Checks for Python-specific types that would create !!python tags.
    Automatically converts OrderedDict to dict.
    
    Args:
        data: Data to validate
    
    Returns:
        Cleaned data safe for YAML serialization
    
    Raises:
        TypeError: If data contains unsupported types
    
    Example:
        from export.utils.yaml_writer import validate_yaml_format
        cleaned = validate_yaml_format(frontmatter)
        write_yaml('output.yaml', cleaned)
    """
    # Convert OrderedDict to dict recursively
    def _clean(obj):
        if isinstance(obj, dict):
            return {k: _clean(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [_clean(item) for item in obj]
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            # Check for problematic types
            type_name = type(obj).__name__
            if type_name in ('OrderedDict', 'defaultdict'):
                return {k: _clean(v) for k, v in obj.items()}
            else:
                raise TypeError(
                    f"Unsupported type for YAML serialization: {type_name}\n"
                    f"Value: {obj}"
                )
    
    return _clean(data)
