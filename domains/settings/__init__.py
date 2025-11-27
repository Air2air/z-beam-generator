"""
Settings Domain

Manages laser machine settings data for the Z-Beam Generator.

This domain handles:
- Loading Settings.yaml data
- Caching settings data
- Settings module for frontmatter generation
- Machine parameter ranges and configurations

Data Location: data/settings/Settings.yaml
"""

from domains.settings.data_loader import (
    load_settings_yaml,
    load_settings_data,
    get_settings_path,
    SettingsDataError
)

__all__ = [
    'load_settings_yaml',
    'load_settings_data',
    'get_settings_path',
    'SettingsDataError'
]
