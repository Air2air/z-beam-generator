"""
Settings Data Loader

Centralized loader for Settings.yaml:
- Machine settings with parameter ranges and descriptions

This module provides a unified interface to load settings data
for all materials.

**MIGRATION NOTICE**: This is the legacy function-based loader.
New code should use `data_loader_v2.SettingsDataLoader` instead.
See: docs/decisions/ADR-008-settings-data-loader-migration.md

Usage:
    from domains.settings.data_loader import load_settings_yaml, get_settings_path
    
    # Load all settings
    settings_data = load_settings_yaml()
    
    # Get Settings.yaml path
    settings_path = get_settings_path()
"""

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

import yaml

# File path - Point to data/settings directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "settings"
SETTINGS_FILE = DATA_DIR / "Settings.yaml"


class SettingsDataError(Exception):
    """Raised when settings data cannot be loaded"""
    pass


def get_settings_path() -> Path:
    """
    Get path to Settings.yaml file
    
    Returns:
        Path object for Settings.yaml
    
    Example:
        >>> from domains.settings.data_loader import get_settings_path
        >>> settings_path = get_settings_path()
        >>> print(settings_path)
        /path/to/data/settings/Settings.yaml
    """
    return SETTINGS_FILE


@lru_cache(maxsize=1)
def load_settings_yaml() -> Dict[str, Dict[str, Any]]:
    """
    Load Settings.yaml
    
    Returns:
        Dict mapping material names to settings data (extracts from nested structure)
        Format: { "Aluminum": { "powerRange": {...}, "wavelength": {...}, ... }, ... }
    
    Raises:
        SettingsDataError: If file cannot be loaded
    
    Example:
        >>> from domains.settings.data_loader import load_settings_yaml
        >>> settings = load_settings_yaml()
        >>> aluminum_settings = settings['Aluminum']
        >>> power_range = aluminum_settings['powerRange']
    """
    if not SETTINGS_FILE.exists():
        raise SettingsDataError(f"Settings.yaml not found at {SETTINGS_FILE}")
    
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            settings = data.get('settings', {})
            
            # Extract machine_settings from nested structure
            # Settings.yaml has: settings.MaterialName.machine_settings.{params}
            # We need to return: { MaterialName: {params} }
            extracted = {}
            for material_name, material_settings in settings.items():
                if 'machine_settings' in material_settings:
                    extracted[material_name] = material_settings['machine_settings']
            
            return extracted
    except Exception as e:
        raise SettingsDataError(f"Failed to load Settings.yaml: {e}")


def load_settings_data() -> Dict[str, Any]:
    """
    Load complete settings data
    
    Alias for load_settings_yaml() for consistency with other domains
    
    Returns:
        Complete settings data
    
    Raises:
        SettingsDataError: If file cannot be loaded
    """
    return load_settings_yaml()


def get_material_settings(material_name: str) -> Dict[str, Any]:
    """
    Get settings for a specific material
    
    Args:
        material_name: Name of material (e.g., "Aluminum")
    
    Returns:
        Settings data for the material, or empty dict if not found
    
    Raises:
        SettingsDataError: If Settings.yaml cannot be loaded
    
    Example:
        >>> from domains.settings.data_loader import get_material_settings
        >>> aluminum = get_material_settings("Aluminum")
        >>> print(aluminum['powerRange'])
    """
    settings = load_settings_yaml()
    return settings.get(material_name, {})


def clear_cache() -> None:
    """
    Clear the LRU cache for loader function
    
    Use this if Settings.yaml is modified at runtime and needs to be reloaded.
    
    Example:
        >>> from domains.settings.data_loader import clear_cache
        >>> # Modify Settings.yaml
        >>> clear_cache()  # Force reload on next access
    """
    load_settings_yaml.cache_clear()
