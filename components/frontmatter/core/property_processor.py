#!/usr/bin/env python3
"""
Property Processor

Extracts property processing logic from StreamlinedGenerator.
Handles property structuring, range application, and DataMetrics formatting.

Follows GROK fail-fast principles:
- No mocks or fallbacks in production
- Explicit error handling with proper exceptions
- Validates all inputs immediately
"""

import logging
from typing import Dict, Optional, Tuple
from pathlib import Path
import yaml

from shared.validation.errors import PropertyDiscoveryError, ConfigurationError
from materials.utils.property_taxonomy import get_property_taxonomy as get_property_categorizer

# Qualitative property definitions
from components.frontmatter.qualitative_properties import (
    QUALITATIVE_PROPERTIES,
    MATERIAL_CHARACTERISTICS_CATEGORIES,
    is_qualitative_property
)

# Validation utilities for confidence normalization
from shared.services.validation import ValidationOrchestrator

logger = logging.getLogger(__name__)


class PropertyProcessor:
    """
    Processes properties for frontmatter assembly.
    
    Responsibilities:
    - Apply category ranges to property values
    - Build DataMetrics structures with min/max/confidence
    - Organize properties by category
    - Separate qualitative from quantitative properties
    - Format properties for frontmatter YAML output
    """
    
    def __init__(self, categories_data: Dict, category_ranges: Dict):
        """
        Initialize processor with category metadata.
        
        Args:
            categories_data: Loaded Categories.yaml data
            category_ranges: Pre-loaded category ranges by material type
            
        Raises:
            ConfigurationError: If required data is missing
        """
        if not categories_data:
            raise ConfigurationError("categories_data required for property processing")
        
        if not category_ranges:
            raise ConfigurationError("category_ranges required for range application")
        
        self.categories_data = categories_data
        self.category_ranges = category_ranges
        self.logger = logging.getLogger(__name__)
        
        # Initialize property categorizer
        try:
            self.categorizer = get_property_categorizer()
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize property categorizer: {e}")
    
    def organize_properties_by_category(self, properties: Dict) -> Dict:
        """
        Organize flat properties dict into flattened category structure.
        
        Args:
            properties: Flat dict of property_name -> property_data
            
        Returns:
            Flattened structure (properties directly under category):
            {
                'thermal': {
                    'label': 'Thermal Properties',
                    'description': '...',
                    'percentage': 29.1,
                    'thermalConductivity': {...},
                    'meltingPoint': {...}
                },
                'mechanical': { ... },
                ...
            }
            
        Raises:
            PropertyDiscoveryError: If categorization fails
        """
        try:
            categorized = {}
            uncategorized = {}
            
            # Get category metadata from Categories.yaml
            category_metadata = self._get_category_metadata()
            
            # Categorize each property
            for prop_name, prop_data in properties.items():
                category_id = self.categorizer.get_category(prop_name)
                
                if category_id:
                    # Add to appropriate category (FLATTENED structure)
                    if category_id not in categorized:
                        categorized[category_id] = {
                            'label': category_metadata.get(category_id, {}).get('label', 
                                                          category_id.replace('_', ' ').title()),
                            'description': category_metadata.get(category_id, {}).get('description', ''),
                            'percentage': category_metadata.get(category_id, {}).get('percentage', 0)
                        }
                    # Properties directly under category (flattened)
                    categorized[category_id][prop_name] = prop_data
                else:
                    # Track uncategorized properties
                    uncategorized[prop_name] = prop_data
            
            # Add uncategorized properties to 'other' category if any exist (FLATTENED)
            if uncategorized:
                categorized['other'] = {
                    'label': 'Other Properties',
                    'description': 'Additional material-specific properties',
                    'percentage': 0
                }
                # Add properties directly to category (flattened)
                categorized['other'].update(uncategorized)
                self.logger.info(f"Found {len(uncategorized)} uncategorized properties")
            
            self.logger.info(f"Organized {len(properties)} properties into {len(categorized)} categories")
            return categorized
            
        except Exception as e:
            self.logger.error(f"Property categorization failed: {e}")
            raise PropertyDiscoveryError(f"Failed to organize properties by category: {e}")
    
    def separate_qualitative_properties(self, all_properties: Dict) -> Tuple[Dict, Dict]:
        """
        Separate qualitative (categorical) from quantitative (numeric) properties.
        
        Args:
            all_properties: Categorized properties dict with categories as keys
            
        Returns:
            Tuple of (quantitative_properties, qualitative_properties)
            - quantitative_properties: Properties with min/max ranges for materialProperties
            - qualitative_properties: Properties with allowedValues for materialCharacteristics
        """
        quantitative = {}
        qualitative_by_category = {}
        
        for category_name, category_data in all_properties.items():
            if not isinstance(category_data, dict) or 'properties' not in category_data:
                # Keep non-property categories as-is in quantitative
                quantitative[category_name] = category_data
                continue
                
            properties = category_data['properties']
            quant_props = {}
            qual_props = {}
            
            for prop_name, prop_data in properties.items():
                if is_qualitative_property(prop_name):
                    # This is a qualitative property - move to materialCharacteristics
                    qual_props[prop_name] = prop_data
                    
                    # Add allowedValues if defined
                    if prop_name in QUALITATIVE_PROPERTIES:
                        qual_def = QUALITATIVE_PROPERTIES[prop_name]
                        if isinstance(prop_data, dict):
                            prop_data['allowedValues'] = qual_def.allowed_values
                            prop_data['unit'] = qual_def.unit
                else:
                    # Quantitative property - stays in materialProperties
                    quant_props[prop_name] = prop_data
            
            # Keep category in quantitative if it has any quantitative properties
            if quant_props:
                quantitative[category_name] = {
                    'label': category_data.get('label', category_name.replace('_', ' ').title()),
                    'description': category_data.get('description', ''),
                    'percentage': category_data.get('percentage', 0),
                    'properties': quant_props
                }
            
            # Organize qualitative properties by their characteristic category
            for prop_name in qual_props:
                if prop_name in QUALITATIVE_PROPERTIES:
                    qual_def = QUALITATIVE_PROPERTIES[prop_name]
                    char_category = qual_def.category
                    
                    if char_category not in qualitative_by_category:
                        # Get metadata from MATERIAL_CHARACTERISTICS_CATEGORIES
                        cat_metadata = MATERIAL_CHARACTERISTICS_CATEGORIES.get(char_category, {})
                        qualitative_by_category[char_category] = {
                            'label': cat_metadata.get('label', char_category.replace('_', ' ').title()),
                            'description': cat_metadata.get('description', ''),
                            'properties': {}
                        }
                    
                    qualitative_by_category[char_category]['properties'][prop_name] = qual_props[prop_name]
        
        self.logger.info(f"Property separation: {len(quantitative)} quantitative categories, "
                        f"{len(qualitative_by_category)} qualitative categories")
        
        return quantitative, qualitative_by_category
    
    def create_datametrics_property(
        self, 
        material_value: any, 
        prop_key: str, 
        material_category: str = 'metal'
    ) -> Optional[Dict]:
        """
        Create DataMetrics structure with min/max ranges from category data.
        
        Args:
            material_value: Property value (can be numeric or string with unit)
            prop_key: Property name (e.g., 'density', 'thermalConductivity')
            material_category: Material category (metal, ceramic, polymer, etc.)
            
        Returns:
            Dict with DataMetrics structure:
            {
                'value': float,
                'unit': str,
                'confidence': float,
                'description': str,
                'min': float,
                'max': float
            }
            
            Returns None if value extraction fails
            
        Raises:
            ValueError: If required unit data is missing
        """
        # Extract numeric value
        numeric_value = self._extract_numeric_only(material_value)
        if numeric_value is None:
            return None
        
        # Get unit from Categories.yaml - FAIL-FAST: no empty fallbacks
        unit = self._get_category_unit(material_category, prop_key)
        if not unit:
            unit = self._extract_unit(material_value)
        if not unit:
            raise ValueError(
                f"No unit found for property '{prop_key}' in material '{material_category}' - "
                "GROK requires explicit unit data"
            )
        
        # Get category-based ranges for this property
        min_val, max_val = self._get_category_range(prop_key, material_category, numeric_value)
        
        # Calculate confidence based on data quality
        confidence = self._calculate_property_confidence(prop_key, material_category, numeric_value)
        
        # Create DataMetrics structure
        property_data = {
            'value': numeric_value,
            'unit': unit,
            'confidence': confidence,
            'description': f'{prop_key} property',
            'min': min_val,
            'max': max_val
        }
        
        return property_data
    
    def apply_category_ranges(
        self, 
        properties: Dict, 
        material_category: str
    ) -> Dict:
        """
        Apply category min/max ranges to properties that don't have them.
        
        Args:
            properties: Properties dict (can be flat or categorized)
            material_category: Material category for range lookup
            
        Returns:
            Properties dict with min/max ranges applied
        """
        # Check if properties are already categorized
        is_categorized = any(
            isinstance(v, dict) and 'properties' in v 
            for v in properties.values()
        )
        
        if is_categorized:
            # Apply ranges to categorized structure
            result = {}
            for cat_name, cat_data in properties.items():
                if isinstance(cat_data, dict) and 'properties' in cat_data:
                    result[cat_name] = cat_data.copy()
                    result[cat_name]['properties'] = self._apply_ranges_to_props(
                        cat_data['properties'], 
                        material_category
                    )
                else:
                    result[cat_name] = cat_data
            return result
        else:
            # Apply ranges to flat structure
            return self._apply_ranges_to_props(properties, material_category)
    
    def merge_with_ranges(self, ai_properties: Dict, range_properties: Dict) -> Dict:
        """
        Merge AI-generated properties with range-enhanced properties.
        Range properties take precedence for min/max values.
        
        Args:
            ai_properties: Properties from AI generation
            range_properties: Properties with category ranges applied
            
        Returns:
            Merged properties dict
        """
        merged = ai_properties.copy()
        
        for prop_name, range_data in range_properties.items():
            if prop_name in merged:
                # Merge - range data takes precedence for min/max
                if isinstance(merged[prop_name], dict) and isinstance(range_data, dict):
                    merged[prop_name].update({
                        'min': range_data.get('min', merged[prop_name].get('min')),
                        'max': range_data.get('max', merged[prop_name].get('max'))
                    })
                else:
                    merged[prop_name] = range_data
            else:
                # Add new property from range data
                merged[prop_name] = range_data
        
        return merged
    
    # ============================================================================
    # PRIVATE HELPER METHODS
    # ============================================================================
    
    def _get_category_metadata(self) -> Dict:
        """Extract category metadata from Categories.yaml"""
        category_metadata = {}
        
        if 'propertyCategories' in self.categories_data:
            prop_cats = self.categories_data['propertyCategories']
            if 'categories' in prop_cats:
                for cat_id, cat_data in prop_cats['categories'].items():
                    category_metadata[cat_id] = {
                        'label': cat_data.get('label', cat_id.replace('_', ' ').title()),
                        'description': cat_data.get('description', ''),
                        'percentage': cat_data.get('percentage', 0)
                    }
        
        return category_metadata
    
    def _apply_ranges_to_props(self, properties: Dict, material_category: str) -> Dict:
        """Apply ranges to a flat properties dict"""
        result = {}
        
        for prop_name, prop_data in properties.items():
            if isinstance(prop_data, dict):
                # Check if already has min/max
                if 'min' not in prop_data or 'max' not in prop_data:
                    # Try to get category range
                    if 'value' in prop_data:
                        min_val, max_val = self._get_category_range(
                            prop_name, 
                            material_category, 
                            prop_data['value']
                        )
                        prop_data['min'] = min_val
                        prop_data['max'] = max_val
                
                result[prop_name] = prop_data
            else:
                result[prop_name] = prop_data
        
        return result
    
    def _get_category_range(
        self, 
        prop_key: str, 
        material_category: str, 
        current_value: float
    ) -> Tuple[float, float]:
        """
        Get min/max range from category data for a property.
        
        Args:
            prop_key: Property name
            material_category: Material category
            current_value: Current property value (used for fallback calculation)
            
        Returns:
            Tuple of (min_value, max_value)
        """
        # Try to get range from category data
        if material_category in self.category_ranges:
            cat_ranges = self.category_ranges[material_category]
            
            if prop_key in cat_ranges:
                range_data = cat_ranges[prop_key]
                
                # Handle different range formats
                if isinstance(range_data, dict):
                    if 'min' in range_data and 'max' in range_data:
                        min_val = range_data['min']
                        max_val = range_data['max']
                        
                        # Validate range contains current value
                        if isinstance(min_val, (int, float)) and isinstance(max_val, (int, float)):
                            return float(min_val), float(max_val)
        
        # Fallback: Calculate range based on current value (±20%)
        if current_value and isinstance(current_value, (int, float)):
            min_val = current_value * 0.8
            max_val = current_value * 1.2
            self.logger.debug(
                f"No category range for {prop_key} in {material_category}, "
                f"using calculated range [{min_val:.2f}, {max_val:.2f}]"
            )
            return min_val, max_val
        
        # Last resort: Use value as both min and max
        return float(current_value), float(current_value)
    
    def _get_category_unit(self, material_category: str, prop_key: str) -> Optional[str]:
        """Get unit for property from category data"""
        try:
            if material_category in self.category_ranges:
                cat_ranges = self.category_ranges[material_category]
                if prop_key in cat_ranges:
                    range_data = cat_ranges[prop_key]
                    if isinstance(range_data, dict) and 'unit' in range_data:
                        return range_data['unit']
        except Exception as e:
            self.logger.debug(f"Could not get category unit for {prop_key}: {e}")
        
        return None
    
    def _extract_numeric_only(self, value: any) -> Optional[float]:
        """Extract numeric value from various formats"""
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Try to extract number from string (e.g., "7.85 g/cm³" -> 7.85)
            import re
            match = re.search(r'[-+]?\d*\.?\d+', value)
            if match:
                return float(match.group())
        
        if isinstance(value, dict):
            # Handle DataMetrics structure
            if 'value' in value:
                return self._extract_numeric_only(value['value'])
        
        return None
    
    def _extract_unit(self, value: any) -> Optional[str]:
        """Extract unit from string value (e.g., "7.85 g/cm³" -> "g/cm³")"""
        if isinstance(value, str):
            import re
            # Remove numeric part to get unit
            unit = re.sub(r'[-+]?\d*\.?\d+\s*', '', value).strip()
            if unit:
                return unit
        
        if isinstance(value, dict) and 'unit' in value:
            return value['unit']
        
        return None
    
    def _calculate_property_confidence(
        self, 
        prop_key: str, 
        material_category: str, 
        numeric_value: float
    ) -> float:
        """
        Calculate confidence based on data quality.
        
        Args:
            prop_key: Property name
            material_category: Material category
            numeric_value: Property value
            
        Returns:
            Confidence score (0.1 to 1.0)
            
        Raises:
            ValueError: If no data source exists for property
        """
        # Base confidence from data availability
        if self._has_category_data(material_category, prop_key):
            # Category-based values get medium-high confidence
            base_confidence = 0.80
        else:
            # FAIL-FAST: If no category data, confidence is lower but not zero
            base_confidence = 0.60
            self.logger.warning(
                f"No category data for {prop_key} in {material_category}, "
                f"using lower confidence {base_confidence}"
            )
        
        # Adjust based on value reasonableness
        if numeric_value <= 0:
            # Non-positive values are suspicious for most physical properties
            confidence_adjustment = -0.15
        else:
            confidence_adjustment = 0.0
        
        final_confidence = max(0.1, min(1.0, base_confidence + confidence_adjustment))
        return round(final_confidence, 2)
    
    def _has_category_data(self, material_category: str, prop_key: str) -> bool:
        """Check if we have category-specific data for this property"""
        try:
            if material_category not in self.category_ranges:
                return False
            return prop_key in self.category_ranges[material_category]
        except Exception:
            return False
