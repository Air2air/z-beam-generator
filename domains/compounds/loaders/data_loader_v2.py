"""
Compounds Data Loader - NEW ARCHITECTURE (December 21, 2025)

This module provides BaseDataLoader-based loading for compounds data.
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
    from domains.compounds.data_loader_v2 import CompoundsDataLoader
    
    loader = CompoundsDataLoader()
    compounds = loader.load_compounds()

Usage (Legacy - still works):
    from domains.compounds.data_loader_v2 import load_compounds_yaml
    
    compounds = load_compounds_yaml()
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from shared.cache.manager import cache_manager
from shared.data.base_loader import BaseDataLoader

logger = logging.getLogger(__name__)


class CompoundsDataLoader(BaseDataLoader):
    """
    Data loader for compounds domain.
    
    Loads data from:
    - Compounds.yaml: Core compound metadata, health effects, exposure limits
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize compounds data loader"""
        super().__init__(project_root)
        self.data_dir = self.project_root / 'data' / 'compounds'
        
        # File paths
        self.compounds_file = self.data_dir / 'Compounds.yaml'
        self.data_path = self.compounds_file  # For compatibility
    
    def _get_data_file_path(self) -> Path:
        """Return path to primary data file (Compounds.yaml)"""
        return self.compounds_file
    
    def _validate_loaded_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate Compounds.yaml structure.
        
        Args:
            data: Loaded YAML data
        
        Returns:
            True if valid structure
        """
        # Compounds.yaml should have 'compounds' or 'categories' key
        return 'compounds' in data or 'categories' in data
    
    def load_compounds(self) -> Dict[str, Any]:
        """
        Load Compounds.yaml (core metadata only).
        
        Returns:
            Dict with 'compounds', 'category_metadata', 'material_index', etc.
        
        Raises:
            ConfigurationError: If file cannot be loaded
        """
        # Check cache first
        cached = cache_manager.get('compounds', 'compounds_yaml')
        if cached:
            return cached
        
        # Load using base class method
        data = self._load_yaml_file(self.compounds_file)
        
        # Cache for 1 hour
        cache_manager.set('compounds', 'compounds_yaml', data, ttl=3600)
        
        return data
    
    def get_material(self, material_name: str) -> Optional[Dict[str, Any]]:
        """
        Get specific material by name.
        
        Args:
            material_name: Name of material (e.g., "Aluminum")
        
        Returns:
            Material data dict or None if not found
        """
        compounds_data = self.load_compounds()
        compounds = compounds_data.get('compounds', {})
        return compounds.get(material_name)
    
    def get_all_compounds(self) -> Dict[str, Any]:
        """
        Get all compounds.
        
        Returns:
            Dict mapping compound IDs to compound data
        """
        compounds_data = self.load_compounds()
        return compounds_data.get('compounds', {})
    
    def get_compound(self, compound_id: str) -> Optional[Dict[str, Any]]:
        """
        Get specific compound by ID.
        
        Args:
            compound_id: ID of compound (e.g., "formaldehyde-compound")
        
        Returns:
            Compound data dict or None if not found
        """
        compounds = self.get_all_compounds()
        return compounds.get(compound_id)
    
    def get_compounds_by_hazard_class(self, hazard_class: str) -> Dict[str, Any]:
        """
        Get compounds filtered by hazard class.
        
        Args:
            hazard_class: Hazard class to filter by (e.g., "carcinogenic")
        
        Returns:
            Dict of matching compounds
        """
        all_compounds = self.get_all_compounds()
        # Filter by hazardClass or hazard_class field
        return {
            cid: cdata for cid, cdata in all_compounds.items()
            if cdata.get('hazardClass') == hazard_class or cdata.get('hazard_class') == hazard_class
        }
    
    def get_compounds_by_category(self, category: str) -> Dict[str, Any]:
        """
        Get compounds filtered by category.
        
        Args:
            category: Category to filter by (e.g., "toxic_gas")
        
        Returns:
            Dict of matching compounds
        """
        all_compounds = self.get_all_compounds()
        return {
            cid: cdata for cid, cdata in all_compounds.items()
            if cdata.get('category') == category
        }
    
    def clear_cache(self):
        """Clear all compounds cache"""
        cache_manager.invalidate('compounds')
        logger.info("Cleared compounds cache")


# Singleton instance for convenience
_loader_instance = None

def get_loader() -> CompoundsDataLoader:
    """Get singleton CompoundsDataLoader instance"""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = CompoundsDataLoader()
    return _loader_instance


# ============================================================================
# BACKWARD COMPATIBILITY FUNCTIONS (for v1 imports)
# ============================================================================

def load_compounds_data() -> Dict[str, Any]:
    """Load all compounds from Compounds.yaml (backward compat)."""
    return get_loader().load_compounds()


def load_compounds_yaml() -> Dict[str, Any]:
    """Load Compounds.yaml (backward compat)."""
    return get_loader().load_compounds()


def clear_cache():
    """Clear all compounds caches (backward compat)."""
    get_loader().clear_cache()
