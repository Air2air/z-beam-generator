#!/usr/bin/env python3
"""
Configuration Utilities

Centralized configuration loading and management utilities.
Consolidates YAML loading patterns and provides unified configuration access.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
import yaml


class ConfigurationError(Exception):
    """Raised when configuration loading fails"""
    pass


def load_yaml_file(file_path: Union[str, Path], required: bool = True) -> Optional[Dict[str, Any]]:
    """
    Load a YAML file with comprehensive error handling.

    Args:
        file_path: Path to the YAML file
        required: Whether the file is required (raises exception if missing)

    Returns:
        Dictionary containing the YAML data, or None if file not found and not required

    Raises:
        ConfigurationError: If file cannot be loaded or parsed
        FileNotFoundError: If required file is missing
    """
    file_path = Path(file_path)

    if not file_path.exists():
        if required:
            raise FileNotFoundError(f"Required configuration file not found: {file_path}")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if data is None:
            if required:
                raise ConfigurationError(f"Configuration file is empty: {file_path}")
            return {}

        return data

    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML in {file_path}: {e}")
    except Exception as e:
        raise ConfigurationError(f"Failed to load configuration {file_path}: {e}")


def load_component_config(component_name: str) -> Dict[str, Any]:
    """
    Load configuration for a specific component.

    Args:
        component_name: Name of the component (e.g., 'text', 'author')

    Returns:
        Component configuration dictionary

    Raises:
        ConfigurationError: If component configuration cannot be loaded
    """
    config_path = Path("components") / component_name / "prompt.yaml"

    try:
        config = load_yaml_file(config_path, required=True)
        if not config:
            raise ConfigurationError(f"Empty component configuration: {component_name}")

        # Add component metadata
        config['_component_name'] = component_name
        config['_config_path'] = str(config_path)

        return config

    except Exception as e:
        raise ConfigurationError(f"Failed to load component config for {component_name}: {e}")


def load_ai_detection_config() -> Dict[str, Any]:
    """
    Load AI detection configuration.

    Returns:
        AI detection configuration dictionary

    Raises:
        ConfigurationError: If AI detection configuration cannot be loaded
    """
    config_path = Path("config/ai_detection.yaml")

    try:
        config = load_yaml_file(config_path, required=True)
        if not config:
            raise ConfigurationError("Empty AI detection configuration")

        # Set defaults for missing values
        defaults = {
            'provider': 'winston',
            'enabled': True,
            'target_score': 45.0,
            'max_iterations': 5,
            'timeout': 15,
            'retry_attempts': 2
        }

        for key, default_value in defaults.items():
            if key not in config:
                config[key] = default_value

        return config

    except Exception as e:
        raise ConfigurationError(f"Failed to load AI detection config: {e}")


def load_frontmatter_data(material_name: str) -> Optional[Dict[str, Any]]:
    """
    Load frontmatter data for a specific material.

    Args:
        material_name: Name of the material

    Returns:
        Frontmatter data dictionary, or None if not found
    """
    # Create safe filename
    safe_name = material_name.lower().replace(' ', '-').replace('/', '-')
    file_path = Path("content/components/frontmatter") / f"{safe_name}-laser-cleaning.md"

    if not file_path.exists():
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract frontmatter (between --- markers)
        if not content.startswith('---'):
            return None

        end_marker = content.find('---', 3)
        if end_marker == -1:
            return None

        frontmatter_content = content[3:end_marker].strip()
        return yaml.safe_load(frontmatter_content)

    except Exception as e:
        # Log error but don't raise - frontmatter loading should be graceful
        print(f"Warning: Failed to load frontmatter for {material_name}: {e}")
        return None


def load_materials_data() -> Dict[str, Any]:
    """
    Load materials database.

    Returns:
        Materials data dictionary

    Raises:
        ConfigurationError: If materials data cannot be loaded
    """
    materials_path = Path("data/materials.yaml")

    try:
        data = load_yaml_file(materials_path, required=True)
        if not data:
            raise ConfigurationError("Empty materials database")

        return data

    except Exception as e:
        raise ConfigurationError(f"Failed to load materials data: {e}")


def save_yaml_file(data: Dict[str, Any], file_path: Union[str, Path]) -> None:
    """
    Save data to a YAML file.

    Args:
        data: Data to save
        file_path: Path where to save the YAML file

    Raises:
        ConfigurationError: If file cannot be saved
    """
    file_path = Path(file_path)

    try:
        # Create directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    except Exception as e:
        raise ConfigurationError(f"Failed to save configuration to {file_path}: {e}")


def validate_config_structure(config: Dict[str, Any], required_keys: list) -> bool:
    """
    Validate that a configuration has all required keys.

    Args:
        config: Configuration dictionary to validate
        required_keys: List of required key names

    Returns:
        True if all required keys are present
    """
    for key in required_keys:
        if key not in config:
            return False
        if config[key] is None:
            return False
    return True


def get_config_value(config: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Get a value from configuration with optional default.

    Args:
        config: Configuration dictionary
        key: Key to retrieve
        default: Default value if key not found

    Returns:
        Configuration value or default
    """
    return config.get(key, default)


def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two configuration dictionaries.

    Args:
        base_config: Base configuration
        override_config: Configuration to override with

    Returns:
        Merged configuration dictionary
    """
    merged = base_config.copy()

    for key, value in override_config.items():
        if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
            merged[key] = merge_configs(merged[key], value)
        else:
            merged[key] = value

    return merged
