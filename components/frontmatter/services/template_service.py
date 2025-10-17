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
from typing import Dict, Optional
from validation.errors import ConfigurationError

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
        
        self.material_abbreviations = material_abbreviations
        self.thermal_property_map = thermal_property_map
        self.category_ranges = category_ranges or {}
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
    
    def get_category_ranges_for_property(
        self,
        category: str,
        property_name: str
    ) -> Optional[Dict]:
        """
        Get min/max ranges for a property from Categories.yaml category_ranges.
        
        Handles both flat properties (density, hardness) and nested properties
        (thermalDestruction).
        
        Args:
            category: Material category (metal, plastic, etc.)
            property_name: Property name
            
        Returns:
            Dict with min, max, unit if ranges exist, None otherwise
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
            property_type: Type ('materialProperties' or 'machineSettings')
            
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
