"""
Unified Data Loader

Single point of access for all data files across all domains.
Provides consistent caching, error handling, and thread safety.

Usage:
    from shared.data.unified_loader import get_data_loader
    
    # Get domain-specific loader
    materials_loader = get_data_loader('materials')
    contaminants_loader = get_data_loader('contaminants')
    settings_loader = get_data_loader('settings')
    
    # Load data
    materials = materials_loader.load_materials()
    patterns = contaminants_loader.load_patterns()
    settings = settings_loader.load_settings()

Benefits:
- Single import for all data access
- Consistent caching via CacheManager
- Thread-safe singleton instances
- Zero duplicate YAML loading code
- Easy to swap implementations

Author: Z-Beam Development Team
Date: December 11, 2025
"""

from typing import Union, Literal
import logging

from domains.materials.data_loader_v2 import MaterialsDataLoader
from domains.contaminants.data_loader_v2 import ContaminantsDataLoader
from domains.settings.data_loader_v2 import SettingsDataLoader

logger = logging.getLogger(__name__)

# Type definitions
DataLoaderType = Union[MaterialsDataLoader, ContaminantsDataLoader, SettingsDataLoader]
DomainName = Literal['materials', 'contaminants', 'settings']

# Singleton instances (cached per domain)
_loaders = {}


def get_data_loader(domain: DomainName) -> DataLoaderType:
    """
    Get data loader for specified domain.
    
    Returns cached singleton instance for performance.
    Thread-safe via loader's internal caching.
    
    Args:
        domain: Domain name ('materials', 'contaminants', 'settings')
    
    Returns:
        Domain-specific data loader instance (cached singleton)
    
    Raises:
        ValueError: If domain name is invalid
    
    Examples:
        >>> # Get materials loader
        >>> loader = get_data_loader('materials')
        >>> materials = loader.load_materials()
        >>> properties = loader.load_properties()
        
        >>> # Get contaminants loader
        >>> loader = get_data_loader('contaminants')
        >>> patterns = loader.load_patterns()
        >>> pattern = loader.get_pattern('rust_oxidation')
        
        >>> # Get settings loader
        >>> loader = get_data_loader('settings')
        >>> settings = loader.load_settings()
        >>> aluminum_settings = loader.get_material_settings('Aluminum')
    """
    if domain not in _loaders:
        logger.debug(f"Creating new data loader for domain: {domain}")
        
        if domain == 'materials':
            _loaders[domain] = MaterialsDataLoader()
        elif domain == 'contaminants':
            _loaders[domain] = ContaminantsDataLoader()
        elif domain == 'settings':
            _loaders[domain] = SettingsDataLoader()
        else:
            raise ValueError(
                f"Unknown domain: {domain}. "
                f"Valid domains: 'materials', 'contaminants', 'settings'"
            )
    
    return _loaders[domain]


def get_materials_loader() -> MaterialsDataLoader:
    """
    Convenience function to get materials loader.
    
    Returns:
        MaterialsDataLoader instance
    
    Example:
        >>> from shared.data.unified_loader import get_materials_loader
        >>> loader = get_materials_loader()
        >>> materials = loader.load_materials()
    """
    return get_data_loader('materials')


def get_contaminants_loader() -> ContaminantsDataLoader:
    """
    Convenience function to get contaminants loader.
    
    Returns:
        ContaminantsDataLoader instance
    
    Example:
        >>> from shared.data.unified_loader import get_contaminants_loader
        >>> loader = get_contaminants_loader()
        >>> patterns = loader.load_patterns()
    """
    return get_data_loader('contaminants')


def get_settings_loader() -> SettingsDataLoader:
    """
    Convenience function to get settings loader.
    
    Returns:
        SettingsDataLoader instance
    
    Example:
        >>> from shared.data.unified_loader import get_settings_loader
        >>> loader = get_settings_loader()
        >>> settings = loader.load_settings()
    """
    return get_data_loader('settings')


def clear_all_loaders():
    """
    Clear all cached loader instances.
    
    Useful for testing or when needing fresh data.
    Note: Individual loaders may still have internal caches.
    """
    global _loaders
    _loaders.clear()
    logger.debug("Cleared all cached data loader instances")
