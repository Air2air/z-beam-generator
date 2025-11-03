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
    Unified loader for category data with automatic fallback.
    
    Loads from split subcategory files (preferred) or falls back to
    Categories.yaml (backward compatibility).
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
        self.categories_dir = self.project_root / 'data' / 'categories'
        self.legacy_file = self.project_root / 'data' / 'Categories.yaml'
        
        # Determine data source
        self.use_split_files = self.categories_dir.exists() and self._has_split_files()
        
        if not self.use_split_files and not self.legacy_file.exists():
            raise ConfigurationError(
                f"No category data found. Expected either:\n"
                f"  - Split files in: {self.categories_dir}\n"
                f"  - Legacy file: {self.legacy_file}\n"
                f"Per GROK_INSTRUCTIONS.md: No fallbacks allowed."
            )
        
        logger.debug(f"CategoryDataLoader using: {'split files' if self.use_split_files else 'legacy Categories.yaml'}")
    
    @staticmethod
    def _find_project_root() -> Path:
        """Find project root by looking for key markers"""
        current = Path(__file__).resolve()
        for parent in [current] + list(current.parents):
            if (parent / 'data' / 'Materials.yaml').exists():
                return parent
        raise ConfigurationError("Could not find project root (no data/Materials.yaml found)")
    
    def _has_split_files(self) -> bool:
        """Check if split files exist (updated for Option A consolidation)"""
        required_files = [
            'core_definitions.yaml',  # Merged from material_categories + material_types
            'laser_parameters.yaml',  # Renamed from machine_settings.yaml
            'property_system.yaml'    # Merged from property_descriptions + property_taxonomy
        ]
        return all((self.categories_dir / f).exists() for f in required_files)
    
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
    
    def _load_split_file(self, filename: str) -> Dict[str, Any]:
        """Load a split subcategory file"""
        filepath = self.categories_dir / filename
        data = self._load_yaml_file(filepath)
        
        # Remove metadata header if present
        if '_metadata' in data:
            data = {k: v for k, v in data.items() if k != '_metadata'}
        
        return data
    
    def _load_from_legacy(self, key: str) -> Any:
        """Load a specific key from legacy Categories.yaml"""
        data = self._load_yaml_file(self.legacy_file)
        
        if key not in data:
            raise ConfigurationError(f"Key '{key}' not found in {self.legacy_file}")
        
        return data[key]
    
    # Public API - Specific subcategory loaders
    
    def get_material_index(self) -> Dict[str, str]:
        """
        Get material name to category mapping.
        
        NOTE: material_index is actually stored in Materials.yaml, not Categories.yaml.
        Use MaterialsDataLoader to access this data instead.
        
        Returns:
            Dict mapping material names to their categories
            Example: {"Aluminum": "metal", "Granite": "stone"}
        """
        # NOTE: material_index.yaml was removed (redundant 226 bytes, Oct 30 2025)
        # Material index is actually stored in Materials.yaml, not Categories.yaml
        # This method loads directly from the authoritative source
        materials_file = self.project_root / 'data' / 'Materials.yaml'
        if materials_file.exists():
            data = self._load_yaml_file(materials_file)
            return data.get('material_index', {})
        return {}
    
    def get_category_metadata(self) -> Dict[str, Any]:
        """
        Get category metadata (article types, descriptions).
        
        NOTE: Now loads from core_definitions.yaml (Option A consolidation, Oct 30, 2025)
        
        Returns:
            Dict with category metadata
        """
        if self.use_split_files:
            data = self._load_split_file('core_definitions.yaml')
            return data
        return {
            'metadata': self._load_from_legacy('metadata'),
            'categories': self._load_from_legacy('categories')
        }
    
    def get_machine_settings(self) -> Dict[str, Any]:
        """
        Get machine settings ranges and descriptions.
        
        NOTE: Now loads from laser_parameters.yaml (Option A rename, Oct 30, 2025)
        
        Returns:
            Dict with machineSettingsRanges and machineSettingsDescriptions
        """
        if self.use_split_files:
            return self._load_split_file('laser_parameters.yaml')
        return {
            'machineSettingsRanges': self._load_from_legacy('machineSettingsRanges'),
            'machineSettingsDescriptions': self._load_from_legacy('machineSettingsDescriptions')
        }
    
    def get_material_properties(self) -> Dict[str, Any]:
        """
        Get material property descriptions.
        
        NOTE: Now loads from property_system.yaml (Option A merge, Oct 30, 2025)
        
        Returns:
            Dict with materialPropertyDescriptions and categories
        """
        if self.use_split_files:
            return self._load_split_file('property_system.yaml')
        return {
            'materialPropertyDescriptions': self._load_from_legacy('materialPropertyDescriptions'),
            'categories': self._load_from_legacy('categories')
        }
    
    def get_property_taxonomy(self) -> Dict[str, Any]:
        """
        Get property category classification.
        
        NOTE: Now loads from property_system.yaml (Option A merge, Oct 30, 2025)
        
        Returns:
            Dict with propertyCategories
        """
        if self.use_split_files:
            return self._load_split_file('property_system.yaml')
        return {
            'propertyCategories': self._load_from_legacy('propertyCategories')
        }
    
    def get_safety_regulatory(self) -> Dict[str, Any]:
        """
        Get safety and regulatory standards.
        
        NOTE: Now loads from industry_safety.yaml (Option A merge, Oct 30, 2025)
        
        Returns:
            Dict with safetyRegulatory data
        """
        if self.use_split_files:
            return self._load_split_file('industry_safety.yaml')
    
    def get_industry_applications(self) -> Dict[str, Any]:
        """
        Get industry application types and descriptions.
        
        NOTE: Now loads from industry_safety.yaml (Option A merge, Oct 30, 2025)
        
        Returns:
            Dict with industryApplications
        """
        if self.use_split_files:
            return self._load_split_file('industry_safety.yaml')
        
        data = self._load_yaml_file(self.legacy_file)
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
        
        NOTE: Consolidated into templates.yaml as of Oct 30, 2025
        
        Returns:
            Dict with environmental impact templates
        """
        if self.use_split_files:
            data = self._load_split_file('templates.yaml')
            return {'environmentalImpactTemplates': data.get('environmentalImpactTemplates', {})}
        return {
            'environmentalImpactTemplates': self._load_from_legacy('environmentalImpactTemplates')
        }
    
    def get_all_categories(self) -> Dict[str, Any]:
        """
        Load all category data (legacy compatibility).
        
        Returns:
            Complete category data structure
        """
        if self.use_split_files:
            # Combine all split files
            return {
                **self.get_material_index(),
                **self.get_category_metadata(),
                **self.get_machine_settings(),
                **self.get_material_properties(),
                **self.get_property_taxonomy(),
                **self.get_safety_regulatory(),
                **self.get_industry_applications(),
                **self.get_environmental_impact()
            }
        
        # Load entire legacy file
        return self._load_yaml_file(self.legacy_file)
    
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
