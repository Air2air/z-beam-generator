"""
Universal Data Loader
=====================

Provides unified data loading for all domains based on domain configuration.
Eliminates duplicate data loading logic across domain coordinators.

Architecture:
- Uses domain config (domains/{domain}/config.yaml) to determine data path
- Requires flat config key (data_path)
- Provides caching for performance
- Handles all YAML domains: materials, contaminants, compounds, settings

Created: January 4, 2026
Purpose: Consolidate 4 domain-specific data loaders into 1 universal loader

Usage:
    from shared/data.universal_loader import UniversalDataLoader
    
    # Load any domain data
    loader = UniversalDataLoader()
    materials_data = loader.load_domain_data('materials')
    contaminants_data = loader.load_domain_data('contaminants')
    
    # With caching
    loader = UniversalDataLoader(cache=True)
    data = loader.load_domain_data('materials')  # Loads from file
    data = loader.load_domain_data('materials')  # Returns cached version
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

logger = logging.getLogger(__name__)


class UniversalDataLoader:
    """
    Universal data loader for all domains.
    
    Loads domain data files based on domain configuration, eliminating the need
    for domain-specific loaders (MaterialsDataLoader, ContaminantsDataLoader, etc.).
    
    Features:
    - Auto-discovers data path from domain config
    - Uses strict flat config structure
    - Optional caching for performance
    - Unified interface for all domains
    """
    
    def __init__(self, cache: bool = True):
        """
        Initialize universal data loader.
        
        Args:
            cache: Whether to cache loaded data (default: True)
        """
        self.cache_enabled = cache
        self._cache: Dict[str, Dict[str, Any]] = {}
        
        # Project root (where domains/ directory is located)
        self.project_root = Path(__file__).parent.parent.parent
    
    def load_domain_data(self, domain_name: str, force_reload: bool = False) -> Dict[str, Any]:
        """
        Load data for any domain based on its configuration.
        
        Args:
            domain_name: Domain identifier (materials, contaminants, compounds, settings)
            force_reload: Bypass cache and reload from file
        
        Returns:
            Dict containing full domain data from YAML file
        
        Raises:
            FileNotFoundError: If domain config or data file doesn't exist
            ValueError: If domain config missing required keys
        
        Examples:
            >>> loader = UniversalDataLoader()
            >>> materials = loader.load_domain_data('materials')
            >>> print(materials['materials'].keys())
            
            >>> contaminants = loader.load_domain_data('contaminants')
            >>> print(contaminants['contamination_patterns'].keys())
        """
        # Check cache
        if self.cache_enabled and not force_reload and domain_name in self._cache:
            logger.debug(f"Returning cached data for domain: {domain_name}")
            return self._cache[domain_name]
        
        # Load domain config
        config = self._load_domain_config(domain_name)
        
        # Get data path from config
        data_path = self._get_data_path(config, domain_name)
        
        # Load data file
        full_path = self.project_root / data_path
        if not full_path.exists():
            raise FileNotFoundError(f"Domain data file not found: {full_path}")
        
        logger.info(f"Loading {domain_name} data from {data_path}")
        with open(full_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Cache if enabled
        if self.cache_enabled:
            self._cache[domain_name] = data
        
        return data
    
    def clear_cache(self, domain_name: Optional[str] = None) -> None:
        """
        Clear cached data.
        
        Args:
            domain_name: Specific domain to clear, or None for all domains
        """
        if domain_name:
            self._cache.pop(domain_name, None)
            logger.debug(f"Cleared cache for domain: {domain_name}")
        else:
            self._cache.clear()
            logger.debug("Cleared all cached domain data")
    
    def get_item(self, domain_name: str, item_id: str) -> Dict[str, Any]:
        """
        Get specific item from domain data.
        
        Args:
            domain_name: Domain identifier
            item_id: Item identifier (material name, compound id, etc.)
        
        Returns:
            Dict containing item data
        
        Raises:
            ValueError: If item not found
        
        Examples:
            >>> loader = UniversalDataLoader()
            >>> aluminum = loader.get_item('materials', 'aluminum-laser-cleaning')
            >>> rust = loader.get_item('contaminants', 'rust')
        """
        data = self.load_domain_data(domain_name)
        
        # Determine root key based on domain
        root_key = self._get_root_key(domain_name, data)
        
        if root_key not in data:
            raise ValueError(f"Root key '{root_key}' not found in {domain_name} data")
        
        items = data[root_key]
        if item_id not in items:
            raise ValueError(f"Item '{item_id}' not found in {domain_name}.{root_key}")
        
        return items[item_id]
    
    def list_items(self, domain_name: str) -> list:
        """
        List all item IDs in domain.
        
        Args:
            domain_name: Domain identifier
        
        Returns:
            List of item identifiers
        
        Examples:
            >>> loader = UniversalDataLoader()
            >>> materials = loader.list_items('materials')
            >>> print(len(materials))  # Number of materials
        """
        data = self.load_domain_data(domain_name)
        root_key = self._get_root_key(domain_name, data)
        if root_key not in data:
            raise ValueError(f"Root key '{root_key}' not found in {domain_name} data")
        return list(data[root_key].keys())
    
    def _load_domain_config(self, domain_name: str) -> Dict[str, Any]:
        """Load domain configuration file."""
        config_path = self.project_root / "domains" / domain_name / "config.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(
                f"Domain config not found: {config_path}\n"
                f"Expected: domains/{domain_name}/config.yaml"
            )
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _get_data_path(self, config: Dict[str, Any], domain_name: str) -> str:
        """Extract data path from strict domain config."""
        if 'data_path' not in config:
            raise ValueError(
                f"Domain config missing required key 'data_path': {domain_name}"
            )
        return config['data_path']
    
    def _get_root_key(self, domain_name: str, data: Dict[str, Any]) -> str:
        """Determine root key for items in domain data."""
        # Standard mappings
        root_keys = {
            'materials': 'materials',
            'contaminants': 'contamination_patterns',
            'compounds': 'compounds',
            'settings': 'settings',
            'applications': 'applications'
        }
        
        if domain_name in root_keys:
            return root_keys[domain_name]
        
        # If not standard, use first key in data
        if data:
            return list(data.keys())[0]
        
        raise ValueError(f"Unable to determine root key for domain: {domain_name}")


# Convenience function for quick loading
def load_domain_data(domain_name: str, cache: bool = True) -> Dict[str, Any]:
    """
    Quick function to load domain data.
    
    Args:
        domain_name: Domain to load (materials, contaminants, compounds, settings)
        cache: Whether to cache loaded data
    
    Returns:
        Full domain data dict
    
    Example:
        >>> from shared.data.universal_loader import load_domain_data
        >>> materials = load_domain_data('materials')
    """
    loader = UniversalDataLoader(cache=cache)
    return loader.load_domain_data(domain_name)


__all__ = [
    'UniversalDataLoader',
    'load_domain_data'
]
