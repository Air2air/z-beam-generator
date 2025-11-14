#!/usr/bin/env python3
"""
Category Data Loader with Backward Compatibility

Unified loader for category data that supports both:
1. NEW: Split subcategory files (data/categories/*.yaml)
2. OLD: Monolithic Categories.yaml (backward compatibility)

Features:
- Automatic detection of available data sources
- Lazy loading for performance
- LRU caching for frequently accessed data
- Fail-fast validation per GROK_INSTRUCTIONS.md
- Thread-safe caching

Usage:
    loader = CategoryDataLoader()
    
    # Load specific subcategories
    machine_settings = loader.get_machine_settings()
    safety_data = loader.get_safety_regulatory()
    properties = loader.get_material_properties()
    
    # Load all category data (legacy)
    all_data = loader.get_all_categories()

Author: Z-Beam Generator
Date: October 30, 2025
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging
import threading

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when category data configuration is invalid"""
    pass


class CategoryDataLoader:
    """
    Loader for category data from monolithic Categories.yaml.
    
    Uses single-file architecture for simplicity and performance.
    Categories.yaml is the single source of truth for all category-level data.
    """
    
    # Class-level cache lock for thread safety
    _cache_lock = threading.Lock()
    _instance_cache: Dict[str, Any] = {}
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize the category data loader.
        
        Args:
            project_root: Path to project root. Auto-detected if not provided.
        """
        self.project_root = project_root or self._find_project_root()
        self.materials_data_dir = self.project_root / 'data' / 'materials'
        self.categories_file = self.materials_data_dir / 'CategoryTaxonomy.yaml'  # Updated from Categories.yaml
        
        if not self.categories_file.exists():
            raise ConfigurationError(
                f"CategoryTaxonomy.yaml not found at: {self.categories_file}\n"
                f"Per GROK_INSTRUCTIONS.md: No fallbacks allowed."
            )
        
        logger.debug(f"CategoryDataLoader using: {self.categories_file}")
    
    @staticmethod
    def _find_project_root() -> Path:
        """Find project root by looking for key markers"""
        current = Path(__file__).resolve()
        for parent in [current] + list(current.parents):
            # Look for materials/data/Materials.yaml as marker of project root
            if (parent / 'materials' / 'data' / 'Materials.yaml').exists():
                return parent
            # Fallback: Look for run.py (main entry point)
            if (parent / 'run.py').exists():
                return parent
        raise ConfigurationError("Could not find project root (no materials/data/Materials.yaml or run.py found)")
    
    def _load_yaml_file(self, filepath: Path) -> Dict[str, Any]:
        """Load and cache a YAML file"""
        cache_key = str(filepath)
        
        with self._cache_lock:
            if cache_key in self._instance_cache:
                return self._instance_cache[cache_key]
        
        if not filepath.exists():
            raise ConfigurationError(f"Required file not found: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            with self._cache_lock:
                self._instance_cache[cache_key] = data
            
            return data
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in {filepath}: {e}")
    
    def _load_categories_data(self) -> Dict[str, Any]:
        """Load complete Categories.yaml file"""
        return self._load_yaml_file(self.categories_file)
    
    def _get_key(self, key: str) -> Any:
        """Get a specific key from Categories.yaml"""
        data = self._load_categories_data()
        
        if key not in data:
            raise ConfigurationError(f"Key '{key}' not found in {self.categories_file}")
        
        return data[key]
    
    # Public API - Specific subcategory loaders
    
    def get_material_index(self) -> Dict[str, str]:
        """
        Get material name to category mapping.
        
        NOTE: material_index is actually stored in Materials.yaml, not Categories.yaml.
        Use materials.data.materials.load_materials_cached() to access this data instead.
        
        Returns:
            Dict mapping material names to their categories
            Example: {"Aluminum": "metal", "Granite": "stone"}
        """
        materials_file = self.materials_data_dir / 'Materials.yaml'
        if materials_file.exists():
            data = self._load_yaml_file(materials_file)
            return data.get('material_index', {})
        return {}
    
    def get_category_metadata(self) -> Dict[str, Any]:
        """
        Get category metadata (article types, descriptions).
        
        Returns:
            Dict with metadata and categories
        """
        return {
            'metadata': self._get_key('metadata'),
            'categories': self._get_key('categories')
        }
    
    def get_machine_settings(self) -> Dict[str, Any]:
        """
        Get machine settings ranges and descriptions.
        
        Returns:
            Dict with machineSettingsRanges and machineSettingsDescriptions
        """
        return {
            'machineSettingsRanges': self._get_key('machineSettingsRanges'),
            'machineSettingsDescriptions': self._get_key('machineSettingsDescriptions')
        }
    
    def get_material_properties(self) -> Dict[str, Any]:
        """
        Get material property descriptions.
        
        Returns:
            Dict with materialPropertyDescriptions and categories
        """
        return {
            'materialPropertyDescriptions': self._get_key('materialPropertyDescriptions'),
            'categories': self._get_key('categories')
        }
    
    def get_property_taxonomy(self) -> Dict[str, Any]:
        """
        Get property category classification.
        
        Returns:
            Dict with propertyCategories
        """
        return {
            'propertyCategories': self._get_key('propertyCategories')
        }
    
    def get_safety_regulatory(self) -> Dict[str, Any]:
        """
        Get safety and regulatory standards.
        
        Returns:
            Dict with safetyRegulatory data
        """
        data = self._load_categories_data()
        return {'safetyRegulatory': data.get('safetyRegulatory', {})}
    
    def get_industry_applications(self) -> Dict[str, Any]:
        """
        Get industry application types and descriptions.
        
        Returns:
            Dict with industryApplications
        """
        data = self._load_categories_data()
        result = {
            'industryGuidance': data.get('industryGuidance', {}),
            'applicationTypeDefinitions': data.get('applicationTypeDefinitions', {}),
            'standardOutcomeMetrics': data.get('standardOutcomeMetrics', {})
        }
        
        # Extract per-category applications and industry tags
        result['category_applications'] = {}
        result['category_industry_tags'] = {}
        for cat, info in data.get('categories', {}).items():
            if 'common_applications' in info:
                result['category_applications'][cat] = info['common_applications']
            if 'industryTags' in info:
                result['category_industry_tags'][cat] = info['industryTags']
        
        return result
    
    def get_environmental_impact(self) -> Dict[str, Any]:
        """
        Get environmental impact templates.
        
        Returns:
            Dict with environmental impact templates
        """
        return {
            'environmentalImpactTemplates': self._get_key('environmentalImpactTemplates')
        }
    
    def get_all_categories(self) -> Dict[str, Any]:
        """
        Load complete Categories.yaml file.
        
        Returns:
            Complete category data structure
        """
        return self._load_categories_data()
    
    def get_category_ranges(self, category: str) -> Dict[str, Any]:
        """
        Get property ranges for a specific category.
        
        Args:
            category: Category name (e.g., 'metal', 'ceramic', 'glass')
        
        Returns:
            Dict with category_ranges for the specified category
        """
        props = self.get_material_properties()
        
        if category not in props.get('categories', {}):
            raise ConfigurationError(f"Category '{category}' not found in material properties")
        
        return props['categories'][category].get('category_ranges', {})
    
    def clear_cache(self):
        """Clear the internal cache (useful for testing)"""
        with self._cache_lock:
            self._instance_cache.clear()
        logger.debug("CategoryDataLoader cache cleared")


# Convenience function for quick access
def load_category_data(subcategory: Optional[str] = None) -> Dict[str, Any]:
    """
    Quick access function to load category data.
    
    Args:
        subcategory: Specific subcategory to load (None = all data)
            Options: 'material_index', 'machine_settings', 'material_properties',
                    'property_taxonomy', 'safety_regulatory', 'industry_applications',
                    'environmental_impact', 'category_metadata'
    
    Returns:
        Requested category data
    
    Example:
        >>> settings = load_category_data('machine_settings')
        >>> all_data = load_category_data()  # Load everything
    """
    loader = CategoryDataLoader()
    
    if subcategory is None:
        return loader.get_all_categories()
    
    method_map = {
        'material_index': loader.get_material_index,
        'category_metadata': loader.get_category_metadata,
        'machine_settings': loader.get_machine_settings,
        'material_properties': loader.get_material_properties,
        'property_taxonomy': loader.get_property_taxonomy,
        'safety_regulatory': loader.get_safety_regulatory,
        'industry_applications': loader.get_industry_applications,
        'environmental_impact': loader.get_environmental_impact
    }
    
    if subcategory not in method_map:
        raise ValueError(
            f"Invalid subcategory '{subcategory}'. "
            f"Options: {', '.join(method_map.keys())}"
        )
    
    return method_map[subcategory]()


# For backward compatibility with existing code
def load_categories() -> Dict[str, Any]:
    """Legacy function name - loads all category data"""
    return load_category_data()
