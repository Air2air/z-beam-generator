#!/usr/bin/env python3
"""
Template Service

Handles template formatting, material abbreviations, thermal property mappings,
field conversions, and category range lookups.

Responsibilities:
- Apply material abbreviation templates
- Get category ranges for properties
- Format material names and titles
- Thermal property field mapping
- Description enhancement (if needed)

Follows fail-fast principles:
- No default values or fallbacks in production
- Explicit error handling
- Validates configuration data
"""

import logging
from functools import lru_cache
from typing import Dict, Optional
from shared.validation.errors import ConfigurationError

logger = logging.getLogger(__name__)


class TemplateService:
    """
    Service for template formatting and field conversions.
    
    Handles material name formatting, abbreviations, category ranges,
    and thermal property mappings.
    """
    
    def __init__(
        self,
        material_abbreviations: Dict,
        thermal_property_map: Dict,
        category_ranges: Optional[Dict] = None
    ):
        """
        Initialize template service.
        
        Args:
            material_abbreviations: Mapping of materials to abbreviations
            thermal_property_map: Mapping of categories to thermal properties
            category_ranges: Category-specific property ranges from Categories.yaml
            
        Raises:
            ConfigurationError: If required configuration is invalid
        """
        if not material_abbreviations:
            raise ConfigurationError("Material abbreviations configuration required")
        
        if not thermal_property_map:
            raise ConfigurationError("Thermal property map configuration required")
        
        # FAIL-FAST: category_ranges can be empty dict but must be explicitly provided
        if category_ranges is None:
            raise ConfigurationError("CRITICAL: category_ranges must be provided (can be empty dict if not using ranges)")
        
        self.material_abbreviations = material_abbreviations
        self.thermal_property_map = thermal_property_map
        self.category_ranges = category_ranges
        self.logger = logger
    
    def apply_abbreviation_template(self, material_name: str) -> Dict[str, str]:
        """
        Apply abbreviation template formatting for materials with known abbreviations.
        
        Args:
            material_name: Name of the material
            
        Returns:
            Dict with formatted name, subcategory, title, and description_suffix
        """
        # Check for exact matches or close matches
        for pattern, mapping in self.material_abbreviations.items():
            if (pattern.lower() == material_name.lower() or 
                mapping['full_name'].lower() == material_name.lower() or
                pattern.lower().replace(' ', '').replace('-', '') in material_name.lower().replace(' ', '').replace('-', '')):
                
                return {
                    'name': mapping['abbreviation'],
                    'subcategory': f"{mapping['full_name']} ({mapping['abbreviation']})",
                    'title': f"{mapping['abbreviation']} Laser Cleaning",
                    'description_suffix': f" ({mapping['abbreviation']})"
                }
        
        # No abbreviation template found - use standard formatting
        return {
            'name': material_name.title(),
            'subcategory': material_name.title(),
            'title': f"{material_name.title()} Laser Cleaning",
            'description_suffix': ''
        }
    
    @lru_cache(maxsize=256)
    def get_category_ranges_for_property(self, category: str, property_name: str) -> Optional[Dict]:
        """
        Get min/max ranges for a property from Categories.yaml category_ranges.
        
        Cached with LRU to avoid repeated YAML lookups. Cache can hold 256 entries
        (9 categories * ~20 properties = ~180 typical entries).
        
        Handles both flat properties (density, hardness) and nested properties (thermalDestruction).
        
        Args:
            category: Material category (metal, ceramic, etc.)
            property_name: Property to get ranges for
            
        Returns:
            Dict with min/max/unit or None if not found (cached result)
        """
        try:
            if not category or category not in self.category_ranges:
                return None
                
            category_range_data = self.category_ranges[category]
            
            if property_name in category_range_data:
                ranges = category_range_data[property_name]
                
                # Handle nested thermalDestruction structure
                if property_name == 'thermalDestruction' and isinstance(ranges, dict) and 'point' in ranges:
                    # Return the full nested structure for special handling
                    return ranges
                
                # Handle regular flat properties
                if 'min' in ranges and 'max' in ranges:
                    if 'unit' not in ranges:
                        self.logger.warning(f"Unit missing for {category}.{property_name} in Categories.yaml")
                        return None  # Fail-fast - no fallback defaults
                    return {
                        'min': ranges['min'],
                        'max': ranges['max'],
                        'unit': ranges['unit']
                    }
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Failed to get category ranges for {property_name} in {category}: {e}")
            return None
    
    def get_thermal_property_info(self, material_category: str) -> Optional[Dict]:
        """
        Get thermal property information for a material category.
        
        Args:
            material_category: Category (metal, plastic, ceramic, etc.)
            
        Returns:
            Dict with field, label, description, scientific_process, yaml_field
            None if category not in mapping
        """
        category_lower = material_category.lower()
        return self.thermal_property_map.get(category_lower)
    
    def get_thermal_field_for_category(self, material_category: str) -> Optional[str]:
        """
        Get the appropriate thermal property field name for a category.
        
        Args:
            material_category: Category (metal, plastic, ceramic, etc.)
            
        Returns:
            Field name (e.g., 'meltingPoint', 'degradationPoint', 'sinteringPoint')
            None if category not in mapping
        """
        thermal_info = self.get_thermal_property_info(material_category)
        return thermal_info['field'] if thermal_info else None
    
    def format_material_title(self, material_name: str, use_abbreviation: bool = True) -> str:
        """
        Format material name for frontmatter title.
        
        Args:
            material_name: Material name
            use_abbreviation: Whether to use abbreviation if available
            
        Returns:
            Formatted title
        """
        if use_abbreviation:
            template = self.apply_abbreviation_template(material_name)
            return template['title']
        else:
            return f"{material_name.title()} Laser Cleaning"
    
    def format_material_subcategory(self, material_name: str, use_abbreviation: bool = True) -> str:
        """
        Format material name for subcategory field.
        
        Args:
            material_name: Material name
            use_abbreviation: Whether to use abbreviation if available
            
        Returns:
            Formatted subcategory
        """
        if use_abbreviation:
            template = self.apply_abbreviation_template(material_name)
            return template['subcategory']
        else:
            return material_name.title()
    
    def enhance_with_standardized_descriptions(
        self,
        property_data: Dict,
        property_name: str,
        property_type: str
    ) -> Dict:
        """
        Enhance property data with standardized descriptions.
        
        Currently a pass-through to reduce verbosity - AI-generated descriptions
        are sufficient. This method exists for future enhancement if needed.
        
        Args:
            property_data: Property data dict
            property_name: Name of the property
            property_type: Type ('properties' or 'machine_settings')
            
        Returns:
            Enhanced property data (currently returns original)
        """
        try:
            # Skip adding standardized descriptions to reduce verbosity
            # The AI-generated description is sufficient
            return property_data.copy()
            
        except Exception as e:
            self.logger.warning(f"Failed to enhance {property_name} with standardized descriptions: {e}")
            return property_data  # Return original data if enhancement fails
    
    def validate_thermal_mapping_completeness(self) -> bool:
        """
        Validate that thermal property mapping covers all expected categories.
        
        Returns:
            True if mapping appears complete, False otherwise
        """
        expected_categories = {
            'metal', 'plastic', 'ceramic', 'composite', 'wood',
            'stone', 'glass', 'semiconductor', 'masonry'
        }
        
        mapped_categories = set(self.thermal_property_map.keys())
        missing = expected_categories - mapped_categories
        
        if missing:
            self.logger.warning(f"Thermal mapping missing categories: {missing}")
            return False
        
        return True
    
    def get_all_supported_abbreviations(self) -> Dict[str, str]:
        """
        Get all supported material abbreviations.
        
        Returns:
            Dict mapping material names to abbreviations
        """
        return {
            mapping['full_name']: mapping['abbreviation']
            for mapping in self.material_abbreviations.values()
        }
    
    def get_all_category_ranges(self, category: str) -> Dict[str, Dict]:
        """
        Load all property ranges for a category at once (batch loading).
        
        This is more efficient than calling get_category_ranges_for_property()
        multiple times when you need ranges for many properties.
        
        Args:
            category: Material category (metal, ceramic, etc.)
            
        Returns:
            Dict mapping property names to their range dicts {min, max, unit}
            Returns empty dict if category not found
            
        Example:
            ranges = service.get_all_category_ranges('metal')
            density_range = ranges.get('density')  # {min: X, max: Y, unit: 'g/cm³'}
        """
        if not category or category not in self.category_ranges:
            return {}
        
        # Return a copy to prevent external modification
        return self.category_ranges[category].copy()
    
    def clear_range_cache(self):
        """
        Clear the category ranges cache.
        
        Call this between material generations to ensure fresh lookups
        if category_ranges dict is modified (shouldn't happen, but safe).
        """
        self.get_category_ranges_for_property.cache_clear()
        logger.debug("Category ranges cache cleared")
    
    def get_cache_stats(self) -> Dict:
        """
        Get cache statistics for performance monitoring.
        
        Returns:
            Dict with cache hits, misses, size, maxsize
        """
        cache_info = self.get_category_ranges_for_property.cache_info()
        return {
            'hits': cache_info.hits,
            'misses': cache_info.misses,
            'size': cache_info.currsize,
            'maxsize': cache_info.maxsize,
            'hit_rate': cache_info.hits / (cache_info.hits + cache_info.misses) if (cache_info.hits + cache_info.misses) > 0 else 0.0
        }
