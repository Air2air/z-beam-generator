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

# Import validation utilities (Step 4 refactored)
from components.frontmatter.services.validation_service import ValidationService

# Phase 4: Import qualitative property definitions
from components.frontmatter.qualitative_properties import (
    QUALITATIVE_PROPERTIES,
    is_qualitative_property,
    get_property_definition,
    validate_qualitative_value
)

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
                
                # Skip redundant thermalDestructionPoint if thermalDestruction exists
                if prop_name == 'thermalDestructionPoint' and 'thermalDestruction' in existing_properties:
                    self.logger.info(f"Skipping redundant thermalDestructionPoint (thermalDestruction already exists)")
                    continue
                
                # REQUIREMENT 1: Check if this is a qualitative property (categorical)
                if is_qualitative_property(prop_name):
                    # Skip - qualitative properties handled by research_material_characteristics()
                    self.logger.debug(f"Skipping qualitative property '{prop_name}' - will be handled by materialCharacteristics research")
                    continue
                
                # Build property structure (quantitative only from here on)
                property_data = {
                    'value': prop_data['value'],
                    'unit': prop_data['unit'],
                    'confidence': prop_data['confidence'],
                    'description': prop_data['description'],
                    'min': None,
                    'max': None
                }
                
                # Check if property value is qualitative by inspection (backup for undefined qualitative props)
                is_qualitative_value = isinstance(prop_data['value'], str) and not self._is_numeric_string(prop_data['value'])
                
                if is_qualitative_value:
                    # Discovered qualitative property not in definitions - log warning
                    self.logger.warning(
                        f"Discovered qualitative property '{prop_name}' not in QUALITATIVE_PROPERTIES definitions. "
                        f"Value: {prop_data['value']}. Consider adding to qualitative_properties.py"
                    )
                    # Skip this property - should be added to qualitative definitions first
                    continue
                else:
                    # Apply category ranges if available
                    if self.get_category_ranges:
                        category_ranges = self.get_category_ranges(material_category, prop_name)
                        
                        # AUTO-REMEDIATION: Research and populate missing/incomplete ranges
                        needs_research = (
                            not category_ranges or 
                            category_ranges.get('min') is None or 
                            category_ranges.get('max') is None
                        )
                        
                        if needs_research:
                            self.logger.warning(f"Property '{prop_name}' missing/incomplete in Categories.yaml - researching ranges...")
                            
                            try:
                                from research.category_range_researcher import CategoryRangeResearcher
                                researcher = CategoryRangeResearcher()
                                
                                range_data = researcher.research_property_range(
                                    property_name=prop_name,
                                    category=material_category,
                                    material_name=material_name
                                )
                                
                                if range_data and 'min' in range_data and 'max' in range_data:
                                    # Update Categories.yaml with researched range
                                    self._update_categories_yaml_with_range(
                                        category=material_category,
                                        property_name=prop_name,
                                        range_data=range_data
                                    )
                                    
                                    # Use the researched ranges
                                    property_data['min'] = range_data['min']
                                    property_data['max'] = range_data['max']
                                    self.logger.info(f"✅ Auto-researched and populated {prop_name} range for {material_category}")
                                else:
                                    self.logger.warning(f"Could not research range for '{prop_name}' - setting to None")
                                    property_data['min'] = None
                                    property_data['max'] = None
                            except Exception as e:
                                self.logger.warning(f"Auto-remediation failed for '{prop_name}': {e} - setting to None")
                                property_data['min'] = None
                                property_data['max'] = None
                        else:
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
                    'description': setting_data['description']
                }
                
                # Machine settings follow same rules as material properties - must have non-null min/max
                min_val = setting_data.get('min')
                max_val = setting_data.get('max')
                
                if min_val is None or max_val is None:
                    # ❌ FAIL-FAST: Machine settings MUST have ranges (Zero Null Policy)
                    raise PropertyDiscoveryError(
                        f"Machine setting '{setting_name}' missing min/max ranges for {material_name}. "
                        f"Zero Null Policy violation - all machine settings must have non-null min/max ranges. "
                        f"Got min={min_val}, max={max_val}"
                    )
                
                machine_setting_data['min'] = min_val
                machine_setting_data['max'] = max_val
                
                # Enhance with standardized descriptions if available
                if self.enhance_descriptions:
                    machine_setting_data = self.enhance_descriptions(
                        machine_setting_data, setting_name, 'machineSettings'
                    )
                
                researched[setting_name] = machine_setting_data
                self.logger.info(
                    f"🤖 Researched {setting_name}: {setting_data['value']} {setting_data['unit']} "
                    f"(min: {min_val}, max: {max_val}, confidence: {setting_data['confidence']}%)"
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
    
    def research_material_characteristics(
        self,
        material_name: str,
        material_category: str,
        existing_characteristics: Optional[Dict] = None
    ) -> Dict[str, Dict]:
        """
        Research qualitative material characteristics using AI discovery.
        
        Args:
            material_name: Name of the material
            material_category: Category (metal, plastic, etc.)
            existing_characteristics: Characteristics already present (from YAML)
            
        Returns:
            Dict of researched qualitative characteristics organized by category
            
        Raises:
            PropertyDiscoveryError: If research fails
        """
        try:
            existing_characteristics = existing_characteristics or {}
            discovered = {}
            
            # Research each qualitative property
            for prop_name, prop_def in QUALITATIVE_PROPERTIES.items():
                # Skip if already present with valid value
                if prop_name in existing_characteristics:
                    existing_value = existing_characteristics[prop_name]
                    if isinstance(existing_value, dict) and 'value' in existing_value:
                        # Validate against allowedValues
                        if validate_qualitative_value(prop_name, existing_value['value']):
                            discovered[prop_name] = existing_value
                            continue
                
                # Use AI to research the characteristic value
                try:
                    result = self.property_researcher.discover_property_value(
                        material_name=material_name,
                        property_name=prop_name,
                        material_category=material_category
                    )
                    
                    if result and 'value' in result:
                        # Validate the discovered value
                        if validate_qualitative_value(prop_name, result['value']):
                            discovered[prop_name] = {
                                'value': result['value'],
                                'confidence': result.get('confidence', 80),
                                'description': prop_def.description,
                                'allowedValues': prop_def.allowed_values,
                                'unit': prop_def.unit
                            }
                            self.logger.info(
                                f"🎯 Discovered {prop_name}: {result['value']} "
                                f"(confidence: {result.get('confidence', 80)}%)"
                            )
                        else:
                            self.logger.warning(
                                f"Invalid value '{result['value']}' for {prop_name}. "
                                f"Must be one of: {prop_def.allowed_values}"
                            )
                except Exception as e:
                    self.logger.debug(f"Could not discover {prop_name} for {material_name}: {e}")
                    continue
            
            self.logger.info(f"Researched {len(discovered)} material characteristics for {material_name}")
            return discovered
            
        except Exception as e:
            self.logger.error(f"Material characteristics research failed for {material_name}: {e}")
            raise PropertyDiscoveryError(
                f"Failed to research material characteristics for {material_name}: {e}"
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
        
        # Skip if category field is same as thermalDestructionPoint (metals, semiconductors)
        if category_field == 'thermalDestructionPoint':
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
        
        # Fallback: copy from thermalDestructionPoint if available
        if thermal_value is None and 'thermalDestructionPoint' in properties:
            melting_data = properties['thermalDestructionPoint']
            thermal_value = melting_data.get('value')
            thermal_unit = melting_data.get('unit', '°C')
            thermal_confidence = melting_data.get('confidence', 85)
            thermal_description = thermal_info['description']
            self.logger.info(f"📋 Copying thermal data from thermalDestructionPoint to {category_field}")
        
        # Only add if we have a value
        if thermal_value is not None:
            properties[category_field] = {
                'value': thermal_value,
                'unit': thermal_unit or '°C',
                'confidence': ValidationService.normalize_confidence(thermal_confidence),
                'description': thermal_description or thermal_info['description'],
                'min': None,
                'max': None
            }
            
            # Apply category ranges (REQUIRED - Zero Null Policy)
            if self.get_category_ranges:
                category_ranges = self.get_category_ranges(material_category, category_field)
                if category_ranges and category_ranges.get('min') is not None and category_ranges.get('max') is not None:
                    properties[category_field]['min'] = category_ranges['min']
                    properties[category_field]['max'] = category_ranges['max']
                else:
                    # ❌ FAIL-FAST: Thermal properties MUST have ranges (Zero Null Policy)
                    raise PropertyDiscoveryError(
                        f"Thermal property '{category_field}' missing category ranges for {material_category}. "
                        f"Zero Null Policy violation - all numerical properties must have non-null min/max ranges."
                    )
            else:
                raise PropertyDiscoveryError(f"Category range service not available for '{category_field}'")
            
            self.logger.info(
                f"✅ Added category thermal field {category_field} = {thermal_value} {thermal_unit} "
                f"(min: {properties[category_field]['min']}, max: {properties[category_field]['max']}, "
                f"label: '{thermal_info['label']}')"
            )
            return True
        
        return False
    
    def _is_numeric_string(self, value: str) -> bool:
        """Check if a string represents a numeric value"""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    
    def _update_categories_yaml_with_range(self, category: str, property_name: str, range_data: Dict) -> None:
        """Update Categories.yaml with a researched range for a property"""
        try:
            import yaml
            from pathlib import Path
            
            categories_file = Path(__file__).parent.parent.parent.parent / 'data' / 'Categories.yaml'
            
            # Read current Categories.yaml
            with open(categories_file, 'r', encoding='utf-8') as f:
                categories_data = yaml.safe_load(f)
            
            # Add the property range to the category
            if 'categories' not in categories_data:
                self.logger.error("Categories.yaml missing 'categories' section")
                return
            
            if category not in categories_data['categories']:
                self.logger.error(f"Category '{category}' not found in Categories.yaml")
                return
            
            if 'properties' not in categories_data['categories'][category]:
                categories_data['categories'][category]['properties'] = {}
            
            # Add the new property range
            categories_data['categories'][category]['properties'][property_name] = {
                'min': range_data['min'],
                'max': range_data['max'],
                'unit': range_data.get('unit', '')
            }
            
            # Write back to file
            with open(categories_file, 'w', encoding='utf-8') as f:
                yaml.dump(categories_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            self.logger.info(f"✅ Added {property_name} range to Categories.yaml: min={range_data['min']}, max={range_data['max']} {range_data.get('unit', '')}")
            
        except Exception as e:
            self.logger.error(f"Failed to update Categories.yaml with {property_name}: {e}")
