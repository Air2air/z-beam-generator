"""
Settings Data Loader - NEW ARCHITECTURE (December 11, 2025)

This module provides BaseDataLoader-based loading for machine settings data.
Maintains backward compatibility with existing function-based API.

New Architecture:
- Inherits from shared.data.base_loader.BaseDataLoader
- Uses shared.cache.manager.CacheManager for caching
- Uses shared.utils.file_io for file operations
- Eliminates duplicate YAML loading code

Backward Compatibility:
- All existing functions remain available
- No breaking changes to existing code
- Gradual migration path

Usage (New):
    from domains.settings.data_loader_v2 import SettingsDataLoader
    
    loader = SettingsDataLoader()
    settings = loader.load_settings()
    material_settings = loader.get_material_settings('Aluminum')

Usage (Legacy - still works):
    from domains.settings.data_loader import load_settings_yaml
    
    settings = load_settings_yaml()
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

from shared.data.base_loader import BaseDataLoader
from shared.cache.manager import cache_manager

logger = logging.getLogger(__name__)


class SettingsDataLoader(BaseDataLoader):
    """
    Data loader for settings domain.
    
    Loads data from:
    - Settings.yaml: Machine settings with parameter ranges and descriptions
    
    Features:
    - Thread-safe caching via CacheManager
    - Fail-fast validation
    - Convenient access methods for material-specific settings
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize settings data loader"""
        super().__init__(project_root)
        self.data_dir = self.project_root / 'data' / 'settings'
        
        # File paths
        self.settings_file = self.data_dir / 'Settings.yaml'
    
    def _get_data_file_path(self) -> Path:
        """Return path to primary data file (Settings.yaml)"""
        return self.settings_file
    
    def _validate_loaded_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate Settings.yaml structure.
        
        Args:
            data: Loaded YAML data
        
        Returns:
            True if valid structure
        """
        # Settings.yaml should have 'settings' key
        return 'settings' in data
    
    def load_settings(self, extract_machine_settings: bool = True) -> Dict[str, Any]:
        """
        Load Settings.yaml.
        
        Args:
            extract_machine_settings: If True, extract machine_settings from nested structure
                                     If False, return raw settings structure
        
        Returns:
            Dict mapping material names to settings data
            
            If extract_machine_settings=True (default):
                Format: { "Aluminum": { "powerRange": {...}, "wavelength": {...}, ... }, ... }
            
            If extract_machine_settings=False:
                Format: { "settings": { "Aluminum": { "machine_settings": {...}, ... }, ... } }
        
        Raises:
            ConfigurationError: If file cannot be loaded
        """
        # Check cache first
        cache_key = f'settings_extract_{extract_machine_settings}'
        cached = cache_manager.get('settings', cache_key)
        if cached:
            return cached
        
        # Load using base class method
        data = self._load_yaml_file(self.settings_file)
        
        if extract_machine_settings:
            # Extract machine_settings from nested structure
            # Settings.yaml has: settings.MaterialName.machine_settings.{params}
            # We return: { MaterialName: {params} }
            settings = data.get('settings', {})
            extracted = {}
            for material_name, material_settings in settings.items():
                if 'machine_settings' in material_settings:
                    extracted[material_name] = material_settings['machine_settings']
            
            result = extracted
        else:
            # Return raw structure
            result = data
        
        # Cache for 1 hour
        cache_manager.set('settings', cache_key, result, ttl=3600)
        
        return result
    
    def get_material_settings(self, material_name: str) -> Dict[str, Any]:
        """
        Get machine settings for a specific material.
        
        Args:
            material_name: Material name (e.g., 'Aluminum', 'Steel')
        
        Returns:
            Dict with machine settings for the material
        
        Raises:
            ConfigurationError: If material not found
        """
        settings = self.load_settings(extract_machine_settings=True)
        
        if material_name not in settings:
            from shared.validation.errors import ConfigurationError
            available = list(settings.keys())[:10]  # Show first 10
            raise ConfigurationError(
                f"Material '{material_name}' not found in Settings.yaml. "
                f"Available materials (showing first 10): {available}"
            )
        
        return settings[material_name]
    
    def get_parameter(self, material_name: str, parameter_name: str) -> Dict[str, Any]:
        """
        Get specific parameter for a material.
        
        Args:
            material_name: Material name
            parameter_name: Parameter name (e.g., 'powerRange', 'wavelength')
        
        Returns:
            Dict with parameter data (min, max, unit, description, etc.)
        
        Raises:
            ConfigurationError: If material or parameter not found
        """
        material_settings = self.get_material_settings(material_name)
        
        if parameter_name not in material_settings:
            from shared.validation.errors import ConfigurationError
            available = list(material_settings.keys())
            raise ConfigurationError(
                f"Parameter '{parameter_name}' not found for material '{material_name}'. "
                f"Available parameters: {available}"
            )
        
        return material_settings[parameter_name]
    
    def get_all_materials(self) -> List[str]:
        """
        Get list of all materials that have settings.
        
        Returns:
            List of material names
        """
        settings = self.load_settings(extract_machine_settings=True)
        return list(settings.keys())
    
    def validate_material_exists(self, material_name: str) -> bool:
        """
        Check if a material has settings.
        
        Args:
            material_name: Material name
        
        Returns:
            True if material has settings, False otherwise
        """
        settings = self.load_settings(extract_machine_settings=True)
        return material_name in settings
    
    def get_parameter_range(self, material_name: str, parameter_name: str) -> Optional[tuple]:
        """
        Get min/max range for a parameter.
        
        Args:
            material_name: Material name
            parameter_name: Parameter name
        
        Returns:
            Tuple of (min, max) or None if parameter doesn't have range
        """
        param = self.get_parameter(material_name, parameter_name)
        
        min_val = param.get('min')
        max_val = param.get('max')
        
        if min_val is not None and max_val is not None:
            return (min_val, max_val)
        
        return None
    
    def get_settings_path(self) -> Path:
        """
        Get path to Settings.yaml file.
        
        Returns:
            Path object for Settings.yaml
        """
        return self.settings_file
