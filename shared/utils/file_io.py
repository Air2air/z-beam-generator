"""
File I/O Helpers - Standardized file operations for Z-Beam Generator.

This module provides consistent file reading/writing with proper error handling,
encoding, and formatting across the entire codebase.

Key features:
- Consistent error messages
- UTF-8 encoding by default
- Automatic directory creation
- YAML and JSON support
- Fail-fast behavior

Author: Z-Beam Development Team
Date: December 11, 2025
"""

from pathlib import Path
from typing import Any, Dict, List
import yaml
import json
import logging

from shared.validation.errors import ConfigurationError

logger = logging.getLogger(__name__)


def read_yaml_file(filepath: Path) -> Dict[str, Any]:
    """
    Read YAML file with standardized error handling.
    
    Args:
        filepath: Path to YAML file
    
    Returns:
        Loaded data dictionary
    
    Raises:
        ConfigurationError: If file not found or invalid YAML
    
    Example:
        data = read_yaml_file(Path('data/materials/Materials.yaml'))
    """
    if not filepath.exists():
        raise ConfigurationError(
            f"File not found: {filepath}\n"
            f"Expected location: {filepath.absolute()}"
        )
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if data is None:
            raise ConfigurationError(f"Empty YAML file: {filepath}")
        
        return data
        
    except yaml.YAMLError as e:
        raise ConfigurationError(
            f"Invalid YAML in {filepath}:\n{str(e)}"
        )
    except Exception as e:
        raise ConfigurationError(
            f"Failed to read {filepath}: {str(e)}"
        )


def write_yaml_file(
    filepath: Path,
    data: Dict[str, Any],
    create_dirs: bool = True,
    sort_keys: bool = False
):
    """
    Write YAML file with standardized formatting.
    
    Args:
        filepath: Path to YAML file
        data: Data to write
        create_dirs: Whether to create parent directories
        sort_keys: Whether to sort dictionary keys
    
    Raises:
        ConfigurationError: If write fails
    
    Example:
        write_yaml_file(Path('output/results.yaml'), {'key': 'value'})
    """
    if create_dirs:
        filepath.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(
                data,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=sort_keys,
                indent=2
            )
        logger.debug(f"Wrote YAML: {filepath}")
        
    except Exception as e:
        raise ConfigurationError(
            f"Failed to write {filepath}: {str(e)}"
        )


def read_json_file(filepath: Path) -> Dict[str, Any]:
    """
    Read JSON file with standardized error handling.
    
    Args:
        filepath: Path to JSON file
    
    Returns:
        Loaded data dictionary
    
    Raises:
        ConfigurationError: If file not found or invalid JSON
    
    Example:
        data = read_json_file(Path('config/settings.json'))
    """
    if not filepath.exists():
        raise ConfigurationError(
            f"File not found: {filepath}\n"
            f"Expected location: {filepath.absolute()}"
        )
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
        
    except json.JSONDecodeError as e:
        raise ConfigurationError(
            f"Invalid JSON in {filepath}:\n{str(e)}"
        )
    except Exception as e:
        raise ConfigurationError(
            f"Failed to read {filepath}: {str(e)}"
        )


def write_json_file(
    filepath: Path,
    data: Dict[str, Any],
    create_dirs: bool = True,
    indent: int = 2
):
    """
    Write JSON file with standardized formatting.
    
    Args:
        filepath: Path to JSON file
        data: Data to write
        create_dirs: Whether to create parent directories
        indent: Indentation spaces
    
    Raises:
        ConfigurationError: If write fails
    
    Example:
        write_json_file(Path('output/results.json'), {'key': 'value'})
    """
    if create_dirs:
        filepath.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        logger.debug(f"Wrote JSON: {filepath}")
        
    except Exception as e:
        raise ConfigurationError(
            f"Failed to write {filepath}: {str(e)}"
        )


def read_text_file(filepath: Path) -> str:
    """
    Read text file with standardized error handling.
    
    Args:
        filepath: Path to text file
    
    Returns:
        File contents as string
    
    Raises:
        ConfigurationError: If file not found or read fails
    
    Example:
        content = read_text_file(Path('prompts/template.txt'))
    """
    if not filepath.exists():
        raise ConfigurationError(
            f"File not found: {filepath}\n"
            f"Expected location: {filepath.absolute()}"
        )
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise ConfigurationError(
            f"Failed to read {filepath}: {str(e)}"
        )


def write_text_file(
    filepath: Path,
    content: str,
    create_dirs: bool = True
):
    """
    Write text file with standardized error handling.
    
    Args:
        filepath: Path to text file
        content: Content to write
        create_dirs: Whether to create parent directories
    
    Raises:
        ConfigurationError: If write fails
    
    Example:
        write_text_file(Path('output/results.txt'), 'Hello, world!')
    """
    if create_dirs:
        filepath.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.debug(f"Wrote text: {filepath}")
        
    except Exception as e:
        raise ConfigurationError(
            f"Failed to write {filepath}: {str(e)}"
        )


def read_lines(filepath: Path) -> List[str]:
    """
    Read file as list of lines.
    
    Args:
        filepath: Path to file
    
    Returns:
        List of lines (with newlines stripped)
    
    Raises:
        ConfigurationError: If file not found or read fails
    
    Example:
        lines = read_lines(Path('data/materials_list.txt'))
    """
    content = read_text_file(filepath)
    return [line.strip() for line in content.splitlines() if line.strip()]


def file_exists(filepath: Path) -> bool:
    """
    Check if file exists.
    
    Args:
        filepath: Path to check
    
    Returns:
        True if file exists, False otherwise
    """
    return filepath.exists() and filepath.is_file()


def ensure_directory(dirpath: Path):
    """
    Ensure directory exists, creating if necessary.
    
    Args:
        dirpath: Directory path
    
    Example:
        ensure_directory(Path('output/results'))
    """
    dirpath.mkdir(parents=True, exist_ok=True)
