#!/usr/bin/env python3
"""
Property Research Service

Coordinates property value research using PropertyValueResearcher.
Handles research for both material properties and machine settings.

Responsibilities:
- Coordinate AI research for material properties
- Coordinate AI research for machine settings
- Apply category ranges from Categories.yaml
- Enhance properties with standardized descriptions
- Handle research errors with proper fallbacks

Follows fail-fast principles:
- No mocks or default values in production
- Explicit error handling with PropertyDiscoveryError
- Validates researcher availability
"""

import logging
from typing import Dict, Optional, Callable
from components.frontmatter.research.property_value_researcher import PropertyValueResearcher
from validation.errors import PropertyDiscoveryError

# Phase 3.3: Import validation utilities
from components.frontmatter.services.validation_utils import ValidationUtils

logger = logging.getLogger(__name__)


class PropertyResearchService:
    """
    Service for coordinating property value research.
    
    Encapsulates all PropertyValueResearcher interactions and provides
    a clean interface for property and machine settings research.
    """
    
    def __init__(
        self,
        property_researcher: PropertyValueResearcher,
        get_category_ranges_func: Optional[Callable] = None,
        enhance_descriptions_func: Optional[Callable] = None
    ):
        """
        Initialize property research service.
        
        Args:
            property_researcher: PropertyValueResearcher instance for AI research
            get_category_ranges_func: Function to get category ranges for properties
            enhance_descriptions_func: Function to enhance with standardized descriptions
            
        Raises:
            PropertyDiscoveryError: If property_researcher is None
        """
        if not property_researcher:
            raise PropertyDiscoveryError(
                "PropertyValueResearcher required for property research service. "
                "Cannot operate without AI research capability."
            )
        
        self.property_researcher = property_researcher
        self.get_category_ranges = get_category_ranges_func
        self.enhance_descriptions = enhance_descriptions_func
        self.logger = logger
    
    def research_material_properties(
        self,
        material_name: str,
        material_category: str,
        existing_properties: Dict
    ) -> Dict[str, Dict]:
        """
        Research material properties using AI discovery.
        
        Args:
            material_name: Name of the material
            material_category: Category (metal, plastic, etc.)
            existing_properties: Properties already present (from YAML)
            
        Returns:
            Dict of researched properties with complete data structure
            
        Raises:
            PropertyDiscoveryError: If research fails
        """
        try:
            # AI discovery for all material properties
            discovered_properties = self.property_researcher.discover_all_material_properties(material_name)
            
            self.logger.info(f"AI discovered {len(discovered_properties)} properties for {material_name}")
            
            # Process and enhance discovered properties
            researched = {}
            for prop_name, prop_data in discovered_properties.items():
                # Skip if already in existing properties (YAML takes precedence)
                if prop_name in existing_properties:
                    continue
                
                # Skip redundant meltingPoint if thermalDestruction exists
                if prop_name == 'meltingPoint' and 'thermalDestruction' in existing_properties:
                    self.logger.info(f"⏭️  Skipping {prop_name} - using thermalDestruction instead")
                    continue
                
                # Build property structure
                property_data = {
                    'value': prop_data['value'],
                    'unit': prop_data['unit'],
                    'confidence': prop_data['confidence'],
                    'description': prop_data['description'],
                    'min': None,
                    'max': None
                }
                
                # Apply category ranges if available
                if self.get_category_ranges:
                    category_ranges = self.get_category_ranges(material_category, prop_name)
                    if category_ranges:
                        property_data['min'] = category_ranges.get('min')
                        property_data['max'] = category_ranges.get('max')
                
                # Enhance with standardized descriptions if available
                if self.enhance_descriptions:
                    property_data = self.enhance_descriptions(
                        property_data, prop_name, 'materialProperties'
                    )
                
                researched[prop_name] = property_data
                self.logger.info(
                    f"🤖 Researched {prop_name}: {prop_data['value']} {prop_data['unit']} "
                    f"(confidence: {prop_data['confidence']}%)"
                )
            
            return researched
            
        except Exception as e:
            self.logger.error(f"Material property research failed for {material_name}: {e}")
            raise PropertyDiscoveryError(
                f"Failed to research material properties for {material_name}: {e}"
            )
    
    def research_machine_settings(
        self,
        material_name: str
    ) -> Dict[str, Dict]:
        """
        Research machine settings using AI discovery.
        
        Args:
            material_name: Name of the material
            
        Returns:
            Dict of researched machine settings with complete data structure
            
        Raises:
            PropertyDiscoveryError: If research fails or no settings found
        """
        try:
            # Use comprehensive AI discovery for all relevant machine settings
            discovered_settings = self.property_researcher.discover_all_machine_settings(material_name)
            
            self.logger.info(f"AI discovered {len(discovered_settings)} machine settings for {material_name}")
            
            if not discovered_settings:
                raise PropertyDiscoveryError(
                    f"No machine settings discovered for {material_name}. "
                    "Comprehensive discovery required per fail-fast principles."
                )
            
            # Process and enhance discovered settings
            researched = {}
            for setting_name, setting_data in discovered_settings.items():
                # Build machine setting structure
                machine_setting_data = {
                    'value': setting_data['value'],
                    'unit': setting_data['unit'],
                    'confidence': setting_data['confidence'],
                    'description': setting_data['description'],
                    'min': setting_data.get('min'),
                    'max': setting_data.get('max')
                }
                
                # Enhance with standardized descriptions if available
                if self.enhance_descriptions:
                    machine_setting_data = self.enhance_descriptions(
                        machine_setting_data, setting_name, 'machineSettings'
                    )
                
                researched[setting_name] = machine_setting_data
                self.logger.info(
                    f"🤖 Researched {setting_name}: {setting_data['value']} {setting_data['unit']} "
                    f"(confidence: {setting_data['confidence']}%)"
                )
            
            return researched
            
        except PropertyDiscoveryError:
            # Re-raise PropertyDiscoveryErrors as-is
            raise
        except Exception as e:
            self.logger.error(f"Machine settings research failed for {material_name}: {e}")
            raise PropertyDiscoveryError(
                f"Failed to research machine settings for {material_name}: {e}"
            )
    
    def add_category_thermal_property(
        self,
        properties: Dict,
        yaml_properties: Dict,
        material_category: str,
        thermal_property_map: Dict
    ) -> bool:
        """
        Add category-specific thermal property field.
        
        Uses thermal property mapping to determine the appropriate thermal field
        for the material's category (e.g., meltingPoint for metals, degradationPoint
        for plastics, sinteringPoint for ceramics).
        
        Args:
            properties: Current properties dict to modify
            yaml_properties: Raw YAML properties for thermal data lookup
            material_category: Category (metal, plastic, etc.)
            thermal_property_map: Mapping of categories to thermal properties
            
        Returns:
            True if a new thermal field was added, False otherwise
        """
        category_lower = material_category.lower()
        
        # Skip if no thermal mapping for this category
        if category_lower not in thermal_property_map:
            self.logger.debug(f"No thermal property mapping for category: {category_lower}")
            return False
        
        thermal_info = thermal_property_map[category_lower]
        category_field = thermal_info['field']
        yaml_field = thermal_info['yaml_field']
        
        # Skip if category field is same as meltingPoint (metals, semiconductors)
        if category_field == 'meltingPoint':
            return False
        
        # Skip if category-specific field already exists
        if category_field in properties:
            self.logger.debug(f"Category thermal field {category_field} already exists")
            return False
        
        # Try to get thermal data from Materials.yaml
        thermal_value = None
        thermal_unit = None
        thermal_confidence = None
        thermal_description = None
        
        if yaml_field in yaml_properties:
            yaml_thermal = yaml_properties[yaml_field]
            if isinstance(yaml_thermal, dict):
                thermal_value = yaml_thermal.get('value')
                thermal_unit = yaml_thermal.get('unit', '°C')
                thermal_confidence = yaml_thermal.get('confidence', 0.85)
                thermal_description = yaml_thermal.get('description', '')
        
        # Fallback: copy from meltingPoint if available
        if thermal_value is None and 'meltingPoint' in properties:
            melting_data = properties['meltingPoint']
            thermal_value = melting_data.get('value')
            thermal_unit = melting_data.get('unit', '°C')
            thermal_confidence = melting_data.get('confidence', 85)
            thermal_description = thermal_info['description']
            self.logger.info(f"📋 Copying thermal data from meltingPoint to {category_field}")
        
        # Only add if we have a value
        if thermal_value is not None:
            properties[category_field] = {
                'value': thermal_value,
                'unit': thermal_unit or '°C',
                'confidence': ValidationUtils.normalize_confidence(thermal_confidence),
                'description': thermal_description or thermal_info['description'],
                'min': None,
                'max': None
            }
            
            # Apply category ranges if available
            if self.get_category_ranges:
                category_ranges = self.get_category_ranges(material_category, category_field)
                if category_ranges:
                    properties[category_field]['min'] = category_ranges.get('min')
                    properties[category_field]['max'] = category_ranges.get('max')
            
            self.logger.info(
                f"✅ Added category thermal field {category_field} = {thermal_value} {thermal_unit} "
                f"(label: '{thermal_info['label']}')"
            )
            return True
        
        return False
