#!/usr/bin/env python3
"""
Robust Configuration Loader

Provides safe configuration loading with fallback mechanisms and validation.
Handles missing files, invalid formats, and provides sensible defaults.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional, Union
import logging

logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    Robust configuration loader with fallback mechanisms.

    Features:
    - Safe file loading with fallbacks
    - Configuration validation
    - Environment variable support
    - Default value handling
    """

    _config_cache: Dict[str, Any] = {}

    @classmethod
    def load_yaml_config(cls, filepath: Union[str, Path], defaults: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Load YAML configuration with fallback to defaults.

        Args:
            filepath: Path to YAML file
            defaults: Default configuration values

        Returns:
            Configuration dictionary
        """
        cache_key = str(filepath)

        if cache_key in cls._config_cache:
            return cls._config_cache[cache_key].copy()

        config = defaults.copy() if defaults else {}

        try:
            # Try to import yaml
            import yaml
        except ImportError:
            logger.warning("PyYAML not available, cannot load YAML config")
            cls._config_cache[cache_key] = config
            return config

        try:
            path = Path(filepath)
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    file_config = yaml.safe_load(f) or {}

                # Merge with defaults (file takes precedence)
                if defaults:
                    config.update(file_config)
                else:
                    config = file_config

                logger.info(f"Loaded configuration from {filepath}")
            else:
                logger.warning(f"Configuration file not found: {filepath}")
                if defaults:
                    logger.info("Using default configuration values")

        except Exception as e:
            logger.error(f"Error loading configuration from {filepath}: {e}")
            if defaults:
                logger.info("Falling back to default configuration")

        cls._config_cache[cache_key] = config
        return config.copy()

    @classmethod
    def load_api_keys(cls, filepath: Union[str, Path] = None) -> Dict[str, str]:
        """
        Load API keys from configuration file.

        Args:
            filepath: Path to API keys file

        Returns:
            Dictionary of API keys
        """
        if filepath is None:
            # Try to find API keys file
            search_paths = [
                Path("config/api_keys.py"),
                Path("config/api_keys.yaml"),
                Path("api_keys.py"),
            ]

            for path in search_paths:
                if path.exists():
                    filepath = path
                    break

        if filepath is None:
            logger.warning("No API keys file found")
            return {}

        path = Path(filepath)

        if path.suffix == '.py':
            return cls._load_api_keys_from_python(path)
        elif path.suffix in ['.yaml', '.yml']:
            return cls._load_api_keys_from_yaml(path)
        else:
            logger.error(f"Unsupported API keys file format: {path.suffix}")
            return {}

    @classmethod
    def _load_api_keys_from_python(cls, filepath: Path) -> Dict[str, str]:
        """Load API keys from Python file."""
        try:
            # Create a namespace for the config
            import types
            config_module = types.ModuleType('config')

            with open(filepath, 'r', encoding='utf-8') as f:
                config_code = f.read()

            # Execute in the module's namespace
            exec(config_code, config_module.__dict__)

            # Extract API keys (look for uppercase variables)
            api_keys = {}
            for name in dir(config_module):
                if name.isupper():
                    value = getattr(config_module, name)
                    if isinstance(value, str) and value:
                        api_keys[name.lower()] = value

            logger.info(f"Loaded {len(api_keys)} API keys from {filepath}")
            return api_keys

        except Exception as e:
            logger.error(f"Error loading API keys from {filepath}: {e}")
            return {}

    @classmethod
    def _load_api_keys_from_yaml(cls, filepath: Path) -> Dict[str, str]:
        """Load API keys from YAML file."""
        try:
            import yaml
            with open(filepath, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}

            api_keys = {}
            for key, value in config.items():
                if isinstance(value, str) and value:
                    api_keys[key.lower()] = value

            logger.info(f"Loaded {len(api_keys)} API keys from {filepath}")
            return api_keys

        except ImportError:
            logger.warning("PyYAML not available for YAML API keys")
            return {}
        except Exception as e:
            logger.error(f"Error loading API keys from {filepath}: {e}")
            return {}

    @classmethod
    def get_env_var(cls, name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get environment variable with fallback.

        Args:
            name: Environment variable name
            default: Default value if not found

        Returns:
            Environment variable value or default
        """
        value = os.getenv(name, default)
        if value:
            logger.debug(f"Found environment variable: {name}")
        else:
            logger.debug(f"Environment variable not found: {name}")
        return value

    @classmethod
    def clear_cache(cls) -> None:
        """Clear configuration cache."""
        cls._config_cache.clear()
        logger.info("Configuration cache cleared")


def load_materials_config() -> Dict[str, Any]:
    """Load materials configuration with robust error handling."""
    try:
        from utils.path_manager import PathManager
        materials_file = PathManager.get_materials_file()
    except ImportError:
        materials_file = Path("data/materials.yaml")

    defaults = {
        "materials": {
            "metal": {"items": []},
            "ceramic": {"items": []},
            "composite": {"items": []},
        }
    }

    return ConfigLoader.load_yaml_config(materials_file, defaults)


def load_api_keys() -> Dict[str, str]:
    """Load API keys with robust error handling."""
    try:
        from utils.path_manager import PathManager
        api_keys_file = PathManager.get_api_keys_file()
    except ImportError:
        api_keys_file = None

    return ConfigLoader.load_api_keys(api_keys_file)


__all__ = [
    'ConfigLoader',
    'load_materials_config',
    'load_api_keys',
]
