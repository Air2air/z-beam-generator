"""
Materials Data Package

Provides centralized loading of materials data from multiple YAML files.
"""

from .loader import (
    load_materials_data,
    load_material,
    load_materials_yaml,
    load_properties_yaml,
    load_settings_yaml,
    get_material_names,
    get_category_metadata,
    get_material_index,
    clear_cache,
    MaterialDataError,
)

__all__ = [
    'load_materials_data',
    'load_material',
    'load_materials_yaml',
    'load_properties_yaml',
    'load_settings_yaml',
    'get_material_names',
    'get_category_metadata',
    'get_material_index',
    'clear_cache',
    'MaterialDataError',
]
