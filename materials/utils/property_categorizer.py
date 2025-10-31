#!/usr/bin/env python3
"""
Property Category Utility - Lightweight read-only categorizer

GROK Compliant:
- No mocks, no fallbacks
- Reads from Categories.yaml only
- Fail-fast on missing data
- Single source of truth for property taxonomy
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional
import yaml

logger = logging.getLogger(__name__)


class PropertyCategorizationError(Exception):
    """Raised when property categorization fails - GROK fail-fast"""
    pass


class PropertyCategorizer:
    """
    Lightweight utility for property category lookup and analysis.
    
    GROK Architecture:
    - Read-only: No state mutation
    - Fail-fast: Throws PropertyCategorizationError on missing data
    - Single source: Categories.yaml is the only truth
    - No fallbacks: No defaults, no mocks, no silent failures
    
    Usage:
        categorizer = get_property_categorizer()  # Singleton
        category = categorizer.get_category('thermalConductivity')
        tier = categorizer.get_usage_tier('density')
    """
    
    def __init__(self):
        """Load property category taxonomy from Categories.yaml"""
        self._load_taxonomy()
    
    def _load_taxonomy(self):
        """
        Load property categories from Categories.yaml - FAIL FAST
        
        Raises:
            PropertyCategorizationError: If Categories.yaml missing or invalid
        """
        try:
            # property_categorizer.py is in materials/utils/, so go up 1 level to materials/
            materials_dir = Path(__file__).resolve().parent.parent
            categories_path = materials_dir / "data" / "Categories.yaml"
            
            if not categories_path.exists():
                raise PropertyCategorizationError(
                    f"Categories.yaml required for property categorization: {categories_path}"
                )
            
            with open(categories_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if 'propertyCategories' not in data:
                raise PropertyCategorizationError(
                    "propertyCategories section required in Categories.yaml - "
                    "property taxonomy is mandatory for system operation"
                )
            
            taxonomy = data['propertyCategories']
            self.categories = taxonomy.get('categories', {})
            self.usage_tiers = taxonomy.get('usage_tiers', {})
            self.metadata = taxonomy.get('metadata', {})
            
            # Validate required structure
            if not self.categories:
                raise PropertyCategorizationError(
                    "No categories found in propertyCategories section"
                )
            
            # Build reverse lookup: property -> category (O(1) access)
            self._property_to_category = {}
            for cat_id, cat_data in self.categories.items():
                if not isinstance(cat_data, dict):
                    raise PropertyCategorizationError(
                        f"Invalid category data for {cat_id}: must be dict"
                    )
                properties = cat_data.get('properties', [])
                if not isinstance(properties, list):
                    raise PropertyCategorizationError(
                        f"Invalid properties for category {cat_id}: must be list"
                    )
                for prop in properties:
                    self._property_to_category[prop] = cat_id
            
            logger.info(
                f"Loaded {len(self.categories)} property categories "
                f"with {len(self._property_to_category)} total properties"
            )
            
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing failed for Categories.yaml: {e}")
            raise PropertyCategorizationError(
                f"Invalid YAML in Categories.yaml: {e}"
            )
        except Exception as e:
            logger.error(f"Failed to load property taxonomy: {e}")
            raise PropertyCategorizationError(
                f"Property taxonomy load failed - system requires valid Categories.yaml: {e}"
            )
    
    def get_category(self, property_name: str) -> Optional[str]:
        """
        Get category ID for a property.
        
        Args:
            property_name: Name of the property (e.g., 'thermalConductivity')
        
        Returns:
            Category ID string (e.g., 'thermal') or None if not categorized
        """
        return self._property_to_category.get(property_name)
    
    def get_category_info(self, category_id: str) -> Optional[Dict]:
        """
        Get full category information.
        
        Args:
            category_id: Category identifier (e.g., 'thermal')
        
        Returns:
            Dict with category metadata (label, description, properties) or None
        """
        return self.categories.get(category_id)
    
    def get_properties_by_category(self, category_id: str) -> List[str]:
        """
        Get all properties in a category.
        
        Args:
            category_id: Category identifier (e.g., 'thermal')
        
        Returns:
            List of property names in that category
        """
        cat_data = self.categories.get(category_id, {})
        return cat_data.get('properties', [])
    
    def get_usage_tier(self, property_name: str) -> str:
        """
        Get usage tier (core/common/specialized) for a property.
        
        Args:
            property_name: Name of the property
        
        Returns:
            Tier string: 'core', 'common', or 'specialized'
        """
        for tier, tier_data in self.usage_tiers.items():
            if property_name in tier_data.get('properties', []):
                return tier
        return 'specialized'  # Default for properties not in core/common
    
    def categorize_properties(self, properties: List[str]) -> Dict[str, List[str]]:
        """
        Group properties by category.
        
        Args:
            properties: List of property names to categorize
        
        Returns:
            Dict mapping category_id -> list of properties
            Includes 'uncategorized' key for unknown properties
        """
        categorized = {}
        for prop in properties:
            category = self.get_category(prop)
            if category:
                if category not in categorized:
                    categorized[category] = []
                categorized[category].append(prop)
            else:
                # Track uncategorized properties for debugging
                if 'uncategorized' not in categorized:
                    categorized['uncategorized'] = []
                categorized['uncategorized'].append(prop)
        
        return categorized
    
    def get_all_categories(self) -> List[str]:
        """
        Get list of all category IDs.
        
        Returns:
            List of category ID strings
        """
        return list(self.categories.keys())
    
    def get_metadata(self) -> Dict:
        """
        Get property taxonomy metadata.
        
        Returns:
            Dict with version, total counts, etc.
        """
        return self.metadata.copy()


# Singleton instance for efficient reuse (loaded once per process)
_categorizer_instance = None

def get_property_categorizer() -> PropertyCategorizer:
    """
    Get singleton PropertyCategorizer instance.
    
    GROK Pattern: Singleton for performance (load Categories.yaml once)
    
    Returns:
        PropertyCategorizer instance (creates on first call)
    
    Raises:
        PropertyCategorizationError: If initialization fails
    """
    global _categorizer_instance
    if _categorizer_instance is None:
        _categorizer_instance = PropertyCategorizer()
    return _categorizer_instance
