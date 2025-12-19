"""
Centralized data loading utilities for the export system.

Provides consistent YAML loading with caching and error handling
for domain data, library data, and configuration files.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import yaml
import logging

logger = logging.getLogger(__name__)


class DataLoader:
    """
    Centralized YAML data loader with caching.
    
    Provides consistent interface for loading domain data, library data,
    and configuration files throughout the export system.
    
    Features:
        - Automatic caching to avoid repeated file reads
        - Consistent error handling
        - UTF-8 encoding by default
        - Path validation
    
    Example:
        loader = DataLoader()
        materials = loader.load_domain_data('data/materials/Materials.yaml', 'materials')
        library = loader.load_library_data('data/safety/regulatory_standards.yaml')
    """
    
    def __init__(self):
        """Initialize data loader with empty cache."""
        self._cache: Dict[str, Any] = {}
    
    def load_domain_data(
        self,
        file_path: Path | str,
        items_key: Optional[str] = None,
        cache_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Load domain data from YAML file.
        
        Args:
            file_path: Path to YAML file
            items_key: Key containing items dict (e.g., 'materials', 'compounds')
                      If provided, validates key exists in data
            cache_key: Optional cache key (defaults to str(file_path))
        
        Returns:
            Dict containing domain data
        
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If items_key provided but not found in data
            yaml.YAMLError: If YAML parsing fails
        
        Example:
            data = loader.load_domain_data('data/materials/Materials.yaml', 'materials')
            materials_dict = data['materials']
        """
        file_path = Path(file_path)
        cache_key = cache_key or str(file_path)
        
        # Check cache first
        if cache_key in self._cache:
            logger.debug(f"Using cached data: {cache_key}")
            return self._cache[cache_key]
        
        # Validate file exists
        if not file_path.exists():
            raise FileNotFoundError(f"Domain data file not found: {file_path}")
        
        # Load YAML
        logger.debug(f"Loading domain data from: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Validate items key if provided
        if items_key and items_key not in data:
            raise ValueError(
                f"Items key '{items_key}' not found in {file_path}\n"
                f"Available keys: {', '.join(data.keys())}"
            )
        
        # Cache and return
        self._cache[cache_key] = data
        
        if items_key:
            logger.info(f"Loaded {len(data[items_key])} items from {file_path}")
        else:
            logger.info(f"Loaded data from {file_path}")
        
        return data
    
    def load_library_data(
        self,
        file_path: Path | str,
        cache_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Load library data from YAML file.
        
        Library files are typically reference data like:
        - Regulatory standards
        - PPE requirements
        - Material properties
        - Chemical properties
        
        Args:
            file_path: Path to library YAML file
            cache_key: Optional cache key (defaults to str(file_path))
        
        Returns:
            Dict containing library data
        
        Raises:
            FileNotFoundError: If file doesn't exist
            yaml.YAMLError: If YAML parsing fails
        
        Example:
            library = loader.load_library_data('data/safety/regulatory_standards.yaml')
        """
        file_path = Path(file_path)
        cache_key = cache_key or str(file_path)
        
        # Check cache first
        if cache_key in self._cache:
            logger.debug(f"Using cached library: {cache_key}")
            return self._cache[cache_key]
        
        # Validate file exists
        if not file_path.exists():
            raise FileNotFoundError(f"Library file not found: {file_path}")
        
        # Load YAML
        logger.debug(f"Loading library data from: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Cache and return
        self._cache[cache_key] = data
        logger.info(f"Loaded library from {file_path}")
        
        return data
    
    def load_config(
        self,
        file_path: Path | str,
        cache_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Load configuration file.
        
        Alias for load_library_data - configs are loaded the same way.
        
        Args:
            file_path: Path to config YAML file
            cache_key: Optional cache key (defaults to str(file_path))
        
        Returns:
            Dict containing configuration
        
        Raises:
            FileNotFoundError: If file doesn't exist
            yaml.YAMLError: If YAML parsing fails
        
        Example:
            config = loader.load_config('export/config/materials.yaml')
        """
        return self.load_library_data(file_path, cache_key)
    
    def clear_cache(self, cache_key: Optional[str] = None):
        """
        Clear cached data.
        
        Args:
            cache_key: Specific key to clear, or None to clear all
        
        Example:
            loader.clear_cache()  # Clear all
            loader.clear_cache('materials')  # Clear specific
        """
        if cache_key:
            self._cache.pop(cache_key, None)
            logger.debug(f"Cleared cache: {cache_key}")
        else:
            self._cache.clear()
            logger.debug("Cleared all cache")
    
    def get_cache_info(self) -> Dict[str, int]:
        """
        Get cache statistics.
        
        Returns:
            Dict with cache info (size, keys)
        
        Example:
            info = loader.get_cache_info()
            print(f"Cached {info['size']} files")
        """
        return {
            'size': len(self._cache),
            'keys': list(self._cache.keys())
        }


# Singleton instance for convenience
_default_loader = DataLoader()


def load_domain_data(
    file_path: Path | str,
    items_key: Optional[str] = None,
    cache_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Load domain data using default loader.
    
    Convenience function for quick access without creating loader instance.
    
    Args:
        file_path: Path to YAML file
        items_key: Key containing items dict
        cache_key: Optional cache key
    
    Returns:
        Dict containing domain data
    
    Example:
        from export.utils.data_loader import load_domain_data
        materials = load_domain_data('data/materials/Materials.yaml', 'materials')
    """
    return _default_loader.load_domain_data(file_path, items_key, cache_key)


def load_library_data(
    file_path: Path | str,
    cache_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Load library data using default loader.
    
    Convenience function for quick access without creating loader instance.
    
    Args:
        file_path: Path to library YAML file
        cache_key: Optional cache key
    
    Returns:
        Dict containing library data
    
    Example:
        from export.utils.data_loader import load_library_data
        library = load_library_data('data/safety/regulatory_standards.yaml')
    """
    return _default_loader.load_library_data(file_path, cache_key)


def load_config(
    file_path: Path | str,
    cache_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Load configuration file using default loader.
    
    Convenience function for quick access without creating loader instance.
    
    Args:
        file_path: Path to config YAML file
        cache_key: Optional cache key
    
    Returns:
        Dict containing configuration
    
    Example:
        from export.utils.data_loader import load_config
        config = load_config('export/config/materials.yaml')
    """
    return _default_loader.load_config(file_path, cache_key)


def clear_cache(cache_key: Optional[str] = None):
    """
    Clear default loader cache.
    
    Args:
        cache_key: Specific key to clear, or None to clear all
    
    Example:
        from export.utils.data_loader import clear_cache
        clear_cache()  # Clear all cached data
    """
    _default_loader.clear_cache(cache_key)
