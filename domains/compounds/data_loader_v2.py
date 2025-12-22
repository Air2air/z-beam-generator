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
from shared.utils.file_io import read_yaml_file

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
    
    def load_properties(self) -> Dict[str, Dict[str, Any]]:
        """
        Load Compounds.yaml.
        
        Returns:
            Dict mapping material names to property data
        
        Raises:
            ConfigurationError: If file cannot be loaded
        """
        # Check cache
        cached = cache_manager.get('compounds', 'properties_yaml')
        if cached:
            return cached
        
        # Load file
        data = read_yaml_file(self.properties_file)
        properties = data.get('properties', {})
        
        # Cache for 1 hour
        cache_manager.set('compounds', 'properties_yaml', properties, ttl=3600)
        
        return properties
    
    def load_industry_applications(self) -> Dict[str, Any]:
        """
        Load  (optional).
        
        Returns:
            Dict with industry guidance, or empty dict if not found
        """
        if not self.industry_file.exists():
            return {}
        
        # Check cache
        cached = cache_manager.get('compounds', 'industry_yaml')
        if cached:
            return cached
        
        # Load file
        data = read_yaml_file(self.industry_file)
        
        # Cache for 1 hour
        cache_manager.set('compounds', 'industry_yaml', data, ttl=3600)
        
        return data
    
    def load_categories(self) -> Dict[str, Any]:
        """
        Load .
        
        Returns:
            Dict with category hierarchies
        
        Raises:
            ConfigurationError: If file cannot be loaded
        """
        # Check cache
        cached = cache_manager.get('compounds', 'categories_yaml')
        if cached:
            return cached
        
        # Load file
        data = read_yaml_file(self.categories_file)
        
        # Cache for 1 hour
        cache_manager.set('compounds', 'categories_yaml', data, ttl=3600)
        
        return data
    
    def load_property_definitions(self) -> Dict[str, Any]:
        """
        Load .
        
        Returns:
            Dict with property metadata and definitions
        """
        if not self.property_defs_file.exists():
            return {}
        
        # Check cache
        cached = cache_manager.get('compounds', 'property_defs_yaml')
        if cached:
            return cached
        
        # Load file
        data = read_yaml_file(self.property_defs_file)
        
        # Cache for 1 hour
        cache_manager.set('compounds', 'property_defs_yaml', data, ttl=3600)
        
        return data
    
    def load_parameter_definitions(self) -> Dict[str, Any]:
        """
        Load .
        
        Returns:
            Dict with parameter definitions
        """
        if not self.parameter_defs_file.exists():
            return {}
        
        # Check cache
        cached = cache_manager.get('compounds', 'parameter_defs_yaml')
        if cached:
            return cached
        
        # Load file
        data = read_yaml_file(self.parameter_defs_file)
        
        # Cache for 1 hour
        cache_manager.set('compounds', 'parameter_defs_yaml', data, ttl=3600)
        
        return data
    
    def load_regulatory_standards(self) -> Dict[str, Any]:
        """
        Load .
        
        Returns:
            Dict with regulatory frameworks
        """
        if not self.regulatory_file.exists():
            return {}
        
        # Check cache
        cached = cache_manager.get('compounds', 'regulatory_yaml')
        if cached:
            return cached
        
        # Load file
        data = read_yaml_file(self.regulatory_file)
        
        # Cache for 1 hour
        cache_manager.set('compounds', 'regulatory_yaml', data, ttl=3600)
        
        return data
    
    def load_micros(self) -> Dict[str, Any]:
        """
        Load Micros.yaml (material captions).
        
        Returns:
            Dict with 'micros' mapping material names to captions
        """
        content_dir = self.project_root / 'compounds' / 'data' / 'content'
        micros_file = content_dir / 'Micros.yaml'
        
        if not micros_file.exists():
            # Legacy file - content now stored in Compounds.yaml
            logger.debug(f"Legacy Micros.yaml not found (expected - content in Compounds.yaml)")
            return {}
        
        # Check cache
        cached = cache_manager.get('compounds', 'micros_yaml')
        if cached:
            return cached
        
        # Load file
        data = read_yaml_file(micros_file)
        micros = data.get('micros', {})
        
        # Cache for 1 hour
        cache_manager.set('compounds', 'micros_yaml', micros, ttl=3600)
        
        return micros
    
    def load_faqs(self) -> Dict[str, Any]:
        """
        Load FAQs.yaml (material FAQs).
        
        Returns:
            Dict with 'faqs' mapping material names to FAQ lists
        """
        content_dir = self.project_root / 'compounds' / 'data' / 'content'
        faqs_file = content_dir / 'FAQs.yaml'
        
        if not faqs_file.exists():
            # Legacy file - content now stored in Compounds.yaml
            logger.debug(f"Legacy FAQs.yaml not found (expected - content in Compounds.yaml)")
            return {}
        
        # Check cache
        cached = cache_manager.get('compounds', 'faqs_yaml')
        if cached:
            return cached
        
        # Load file
        data = read_yaml_file(faqs_file)
        faqs = data.get('faqs', {})
        
        # Cache for 1 hour
        cache_manager.set('compounds', 'faqs_yaml', faqs, ttl=3600)
        
        return faqs
    
    def load_regulatory_standards_content(self) -> Dict[str, Any]:
        """
        Load  (material-specific standards).
        
        Note: Different from load_regulatory_standards() which loads
        from data/compounds/. This loads from
        compounds/data/content/.
        
        Returns:
            Dict with 'regulatory_standards' mapping material names to standards
        """
        content_dir = self.project_root / 'compounds' / 'data' / 'content'
        regulatory_file = content_dir / ''
        
        if not regulatory_file.exists():
            # Legacy file - content now stored in Compounds.yaml
            logger.debug(f"Legacy  not found (expected - content in Compounds.yaml)")
            return {}
        
        # Check cache
        cached = cache_manager.get('compounds', 'regulatory_content_yaml')
        if cached:
            return cached
        
        # Load file
        data = read_yaml_file(regulatory_file)
        standards = data.get('regulatory_standards', {})
        
        # Cache for 1 hour
        cache_manager.set('compounds', 'regulatory_content_yaml', standards, ttl=3600)
        
        return standards
    
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


def load_material(material_name: str) -> Optional[Dict[str, Any]]:
    """Load single material by name (backward compat)."""
    return get_loader().load_material(material_name)


def get_material_names() -> list:
    """Get list of all material names (backward compat)."""
    return list(load_compounds_data().keys())


def load_compounds_yaml() -> Dict[str, Any]:
    """Load Compounds.yaml (backward compat)."""
    return get_loader().load_item_data()


def load_properties_yaml() -> Dict[str, Any]:
    """Load Compounds.yaml (backward compat)."""
    return get_loader().load_properties()


def get_property_definitions() -> Dict[str, Any]:
    """Get property definitions (backward compat)."""
    return get_loader().load_properties()


def load_parameter_definitions_yaml() -> Dict[str, Any]:
    """Load parameter definitions (backward compat)."""
    return get_loader().load_properties()


def get_category_ranges(category: str) -> Optional[Dict[str, Any]]:
    """Get ranges for a category (backward compat)."""
    loader = get_loader()
    categories = loader.load_item_data().get('categories', {})
    return categories.get(category)


def clear_cache():
    """Clear all compounds caches (backward compat)."""
    get_loader().clear_cache()
