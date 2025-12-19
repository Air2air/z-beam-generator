"""
Category Property Validation Cache

This module provides caching for valid property mappings per material category.
Prevents repeated parsing of Categories.yaml and ensures properties are only
researched if they're valid for a material's category.

Author: GitHub Copilot
Date: October 17, 2025
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Set

import yaml


class CategoryPropertyCache:
    """
    Cache valid properties per category to prevent invalid research attempts.
    
    Implements:
    - Persistent cache to disk (JSON)
    - Automatic invalidation when Categories.yaml changes
    - Fast in-memory lookup after initial load
    - Validation against category definitions
    """
    
    def __init__(self, categories_file: Path = None, cache_file: Path = None):
        """
        Initialize category property cache.
        
        Args:
            categories_file: Path to Categories.yaml (default: data/Categories.yaml)
            cache_file: Path to cache file (default: .cache/category_properties.json)
        """
        self.categories_file = categories_file or Path("data/materials/Categories.yaml")
        self.cache_file = cache_file or Path(".cache/category_properties.json")
        
        # In-memory cache
        self._valid_properties: Optional[Dict[str, Set[str]]] = None
        self._categories_hash: Optional[str] = None
        self._last_loaded: Optional[datetime] = None
        
        # Ensure cache directory exists
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file contents for change detection."""
        if not file_path.exists():
            return ""
        
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5.update(chunk)
        return md5.hexdigest()
    
    def _load_from_categories_file(self) -> Dict[str, Set[str]]:
        """Load valid properties directly from Categories.yaml."""
        if not self.categories_file.exists():
            raise FileNotFoundError(f"Categories file not found: {self.categories_file}")
        
        with open(self.categories_file) as f:
            categories_data = yaml.safe_load(f)
        
        valid_properties = {}
        for cat_name, cat_data in categories_data.get('categories', {}).items():
            category_ranges = cat_data.get('category_ranges', {})
            valid_properties[cat_name] = set(category_ranges.keys())
        
        return valid_properties
    
    def _load_from_cache_file(self) -> Optional[Dict[str, Set[str]]]:
        """Load valid properties from cache file if valid."""
        if not self.cache_file.exists():
            return None
        
        try:
            with open(self.cache_file) as f:
                cache_data = json.load(f)
            
            # Check if cache is still valid (Categories.yaml unchanged)
            current_hash = self._calculate_file_hash(self.categories_file)
            if cache_data.get('categories_hash') != current_hash:
                return None  # Cache invalidated
            
            # Convert lists back to sets
            valid_properties = {
                cat: set(props) 
                for cat, props in cache_data.get('valid_properties', {}).items()
            }
            
            self._categories_hash = current_hash
            return valid_properties
            
        except (json.JSONDecodeError, KeyError):
            return None  # Corrupted cache
    
    def _save_to_cache_file(self, valid_properties: Dict[str, Set[str]]):
        """Save valid properties to cache file."""
        cache_data = {
            'categories_hash': self._calculate_file_hash(self.categories_file),
            'valid_properties': {
                cat: sorted(props)  # Convert sets to sorted lists for JSON
                for cat, props in valid_properties.items()
            },
            'cached_at': datetime.now().isoformat(),
            'version': '1.0'
        }
        
        with open(self.cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
    
    def load(self, force_reload: bool = False) -> Dict[str, Set[str]]:
        """
        Load valid properties per category (from cache if available).
        
        Args:
            force_reload: Force reload from Categories.yaml, ignore cache
            
        Returns:
            Dict mapping category names to sets of valid property names
        """
        # Return cached in-memory version if available
        if self._valid_properties and not force_reload:
            return self._valid_properties
        
        # Try loading from disk cache first
        if not force_reload:
            cached = self._load_from_cache_file()
            if cached:
                self._valid_properties = cached
                self._last_loaded = datetime.now()
                return cached
        
        # Load from Categories.yaml
        valid_properties = self._load_from_categories_file()
        
        # Update in-memory cache
        self._valid_properties = valid_properties
        self._last_loaded = datetime.now()
        self._categories_hash = self._calculate_file_hash(self.categories_file)
        
        # Save to disk cache
        self._save_to_cache_file(valid_properties)
        
        return valid_properties
    
    def get_valid_properties(self, category: str) -> Set[str]:
        """
        Get valid properties for a specific category.
        
        Args:
            category: Category name (e.g., 'metal', 'ceramic')
            
        Returns:
            Set of valid property names for the category
        """
        if self._valid_properties is None:
            self.load()
        
        return self._valid_properties.get(category, set())
    
    def is_valid_property(self, category: str, property_name: str) -> bool:
        """
        Check if a property is valid for a category.
        
        Args:
            category: Category name
            property_name: Property name to validate
            
        Returns:
            True if property is valid for the category
        """
        valid_props = self.get_valid_properties(category)
        return property_name in valid_props
    
    def get_invalid_properties(self, category: str, property_names: Set[str]) -> Set[str]:
        """
        Get properties that are NOT valid for a category.
        
        Args:
            category: Category name
            property_names: Set of property names to check
            
        Returns:
            Set of invalid property names
        """
        valid_props = self.get_valid_properties(category)
        return property_names - valid_props
    
    def get_all_categories(self) -> Set[str]:
        """Get all known category names."""
        if self._valid_properties is None:
            self.load()
        return set(self._valid_properties.keys())
    
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        if self._valid_properties is None:
            self.load()
        
        return {
            'categories': len(self._valid_properties),
            'total_properties': sum(len(props) for props in self._valid_properties.values()),
            'properties_per_category': {
                cat: len(props) 
                for cat, props in self._valid_properties.items()
            },
            'last_loaded': self._last_loaded.isoformat() if self._last_loaded else None,
            'cache_file': str(self.cache_file),
            'cache_exists': self.cache_file.exists(),
            'categories_hash': self._categories_hash
        }
    
    def invalidate(self):
        """Invalidate cache and force reload on next access."""
        self._valid_properties = None
        self._categories_hash = None
        self._last_loaded = None
        
        if self.cache_file.exists():
            self.cache_file.unlink()
    
    def validate_material_properties(self, material_name: str, category: str, 
                                     properties: Set[str]) -> Dict:
        """
        Validate all properties for a material against its category.
        
        Args:
            material_name: Material name (for reporting)
            category: Material's category
            properties: Set of property names in the material
            
        Returns:
            Dict with validation results:
                - valid: List of valid properties
                - invalid: List of invalid properties
                - missing: List of properties defined in category but missing in material
                - is_valid: Boolean overall validity
        """
        valid_props = self.get_valid_properties(category)
        invalid = properties - valid_props
        missing = valid_props - properties
        
        return {
            'material': material_name,
            'category': category,
            'valid': sorted(properties & valid_props),
            'invalid': sorted(invalid),
            'missing': sorted(missing),
            'is_valid': len(invalid) == 0,
            'completeness': len(properties & valid_props) / len(valid_props) * 100 if valid_props else 0
        }


# Singleton instance for global use
_global_cache: Optional[CategoryPropertyCache] = None


def get_category_property_cache() -> CategoryPropertyCache:
    """Get global singleton cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = CategoryPropertyCache()
    return _global_cache
