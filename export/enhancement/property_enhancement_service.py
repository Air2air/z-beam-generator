#!/usr/bin/env python3
"""
Property Enhancement Service

Provides property enhancement functionality for frontmatter content including
numeric/unit separation and triple format generation.
Extracted from the monolithic generator for better separation of concerns.
"""

import logging
import re
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class PropertyEnhancementService:
    """Service for enhancing frontmatter properties with numeric/unit separation"""

    @staticmethod
    def add_triple_format_machine_settings(machine_settings: Dict) -> None:
        """
        Add numeric, unit, min/max fields for machine settings with grouped organization.
        
        Groups related machine settings together:
        - powerRange: 50-200W
        - powerRangeNumeric: 125.0
        - powerRangeUnit: W
        - powerRangeMin: 20W
        - powerRangeMinNumeric: 20.0
        - powerRangeMinUnit: W
        - powerRangeMax: 500W
        - powerRangeMaxNumeric: 500.0
        - powerRangeMaxUnit: W
        
        Args:
            machine_settings: Dictionary of machine settings to enhance
        """
        # Create new ordered machine settings dict
        new_machine_settings = {}
        
        # Machine settings that need triple format with industry-standard ranges
        settings_config = {
            "powerRange": {
                "unit": "W",
                "min": "20W", "max": "500W",
                "description": "Laser output power range"
            },
            "pulseDuration": {
                "unit": "ns", 
                "min": "1ns", "max": "1000ns",
                "description": "Pulse duration for pulsed lasers"
            },
            "wavelength": {
                "unit": "nm",
                "min": "355nm", "max": "2940nm", 
                "description": "Laser wavelength range (UV to IR)"
            },
            "spotSize": {
                "unit": "mm",
                "min": "0.01mm", "max": "10mm",
                "description": "Focused beam spot diameter"
            },
            "repetitionRate": {
                "unit": "kHz",
                "min": "1kHz", "max": "1000kHz",
                "description": "Pulse repetition frequency"
            },
            "fluenceRange": {
                "unit": "J/cm²",
                "min": "0.1J/cm²", "max": "50J/cm²",
                "description": "Laser fluence (energy density)"
            },
            "scanningSpeed": {
                "unit": "mm/s",
                "min": "1mm/s", "max": "5000mm/s",
                "description": "Beam scanning velocity"
            }
        }
        
        # Process machine settings in groups - ensure scanningSpeed is included
        setting_order = [
            "powerRange", "pulseDuration", "wavelength", "spotSize", 
            "repetitionRate", "fluenceRange", "scanningSpeed"
        ]
        
        # NOTE: scanningSpeed must be researched by AI if needed for the specific material
        # No fallback defaults allowed - fail-fast architecture requires researched values
        
        for setting_key in setting_order:
            if setting_key in machine_settings:
                config = settings_config[setting_key]
                value_str = str(machine_settings[setting_key])
                numeric_value, unit = PropertyEnhancementService._extract_numeric_and_unit(value_str)
                
                # Add main setting
                new_machine_settings[setting_key] = machine_settings[setting_key]
                
                # Add grouped numeric and unit components
                numeric_key = f"{setting_key}Numeric"
                unit_key = f"{setting_key}Unit"
                min_key = f"{setting_key}Min"
                max_key = f"{setting_key}Max"
                
                new_machine_settings[numeric_key] = numeric_value
                new_machine_settings[unit_key] = config["unit"]
                
                # Add min with numeric/unit separation
                new_machine_settings[min_key] = config["min"]
                min_numeric, min_unit = PropertyEnhancementService._extract_numeric_and_unit(config["min"])
                new_machine_settings[f"{min_key}Numeric"] = min_numeric
                new_machine_settings[f"{min_key}Unit"] = min_unit
                
                # Add max with numeric/unit separation
                new_machine_settings[max_key] = config["max"]
                max_numeric, max_unit = PropertyEnhancementService._extract_numeric_and_unit(config["max"])
                new_machine_settings[f"{max_key}Numeric"] = max_numeric
                new_machine_settings[f"{max_key}Unit"] = max_unit
                
                logger.debug(f"Added grouped machine setting for {setting_key}: {numeric_value} {config['unit']}")
        
        # Add remaining settings that don't need triple format - ensure legacy compatibility
        remaining_settings = ["beamProfile", "beamProfileOptions", "safetyClass"]
        
        # NOTE: beamProfile, beamProfileOptions, and safetyClass must be researched by AI
        # No fallback defaults allowed - fail-fast architecture requires all values to be researched
        
        # Add any existing remaining settings
        for setting in remaining_settings:
            if setting in machine_settings:
                new_machine_settings[setting] = machine_settings[setting]
        
        # Update the machine settings dict
        machine_settings.clear()
        machine_settings.update(new_machine_settings)
        
        logger.debug("Reorganized machine settings with grouped numeric/unit components")

    @staticmethod
    def _extract_unit_from_range(property_config: Dict) -> str:
        """Extract unit from Materials.yaml range configuration."""
        min_val = property_config.get("min", "")
        max_val = property_config.get("max", "")
        
        # Extract unit from min value first, then max
        for val in [min_val, max_val]:
            if val:
                _, unit = PropertyEnhancementService._extract_numeric_and_unit(str(val))
                if unit:
                    return unit
        return ""

    @staticmethod
    def _add_complete_property_breakdown(new_properties: Dict, base_prop: str, value_str: str, config: Dict = None) -> None:
        """
        Add complete property breakdown with calculated numeric variants, min/max, and percentiles.
        
        Args:
            new_properties: Dictionary to add breakdown to
            base_prop: Base property name (e.g., 'density')
            value_str: Property value string (e.g., '2.5-2.8 g/cm³')
            config: Configuration dict with standard ranges if available
        """
        # Extract numeric value and unit from the property string
        numeric_value, unit = PropertyEnhancementService._extract_numeric_and_unit(value_str)
        
        # Handle range values (e.g., "2.5-2.8 g/cm³" -> average = 2.65)
        if '-' in value_str and numeric_value:
            # For ranges, use the average as the numeric value
            range_match = re.search(r'(\d+(?:\.\d+)?)[-–](\d+(?:\.\d+)?)', value_str)
            if range_match:
                min_val = float(range_match.group(1))
                max_val = float(range_match.group(2))
                numeric_value = round((min_val + max_val) / 2, 2)
        
        # If no numeric value extracted, try to get just the first number
        if numeric_value is None:
            numeric_match = re.search(r'(\d+(?:\.\d+)?)', value_str)
            numeric_value = float(numeric_match.group(1)) if numeric_match else 0.0
        
        # Use config unit if available, otherwise extract from value
        if config and not unit:
            unit = config["unit"]
        elif not unit:
            # FAIL-FAST: No unit defaults allowed
            raise ValueError(f"Unit not provided for {base_prop} and no unit in existing value: {value_str}")
        
        # Add numeric breakdown
        new_properties[f"{base_prop}Numeric"] = numeric_value
        new_properties[f"{base_prop}Unit"] = unit
        
        # Add Min/Max ranges - FAIL-FAST: Require config data  
        if config:
            min_str = config["min"]
            max_str = config["max"]
        else:
            # FAIL-FAST: No hardcoded min/max ranges allowed
            raise ValueError(f"No configuration found for {base_prop} min/max ranges - data must be provided in Materials.yaml")
        
        # Add Min/Max properties
        new_properties[f"{base_prop}Min"] = min_str
        new_properties[f"{base_prop}Max"] = max_str
        
        # Extract numeric values for min/max
        min_numeric, min_unit = PropertyEnhancementService._extract_numeric_and_unit(min_str)
        max_numeric, max_unit = PropertyEnhancementService._extract_numeric_and_unit(max_str)
        
        new_properties[f"{base_prop}MinNumeric"] = min_numeric
        new_properties[f"{base_prop}MinUnit"] = min_unit or unit
        new_properties[f"{base_prop}MaxNumeric"] = max_numeric
        new_properties[f"{base_prop}MaxUnit"] = max_unit or unit
        
        # Calculate percentile based on where the value falls in the range
        if min_numeric and max_numeric and numeric_value:
            try:
                percentile = ((numeric_value - min_numeric) / (max_numeric - min_numeric)) * 100
                percentile = max(0.0, min(100.0, round(percentile, 1)))
            except (ZeroDivisionError, TypeError):
                percentile = 50.0
        else:
            percentile = 50.0
        
        # Add percentile with proper naming convention
        percentile_key = PropertyEnhancementService._get_percentile_key(base_prop)
        new_properties[percentile_key] = percentile
        
        logger.debug(f"Added complete breakdown for {base_prop}: {numeric_value} {unit} (percentile: {percentile})")

    @staticmethod 
    def _get_percentile_key(base_prop: str) -> str:
        """Get the correct percentile key name for legacy compatibility."""
        percentile_mappings = {
            "meltingPoint": "meltingPercentile",
            "thermalConductivity": "thermalPercentile", 
            "tensileStrength": "tensilePercentile",
            "hardness": "hardnessPercentile",
            "youngsModulus": "modulusPercentile"
        }
        return percentile_mappings.get(base_prop, f"{base_prop}Percentile")

    @staticmethod
    def add_triple_format_properties(frontmatter_data: Dict) -> None:
        """
        Add comprehensive numeric and unit fields for complete legacy format compatibility.
        
        Generates complete property structure matching legacy format:
        - density: 2.70 g/cm³
        - densityNumeric: 2.70
        - densityUnit: g/cm³
        - densityMin: 1.8 g/cm³
        - densityMinNumeric: 1.8
        - densityMinUnit: g/cm³
        - densityMax: 3.0 g/cm³
        - densityMaxNumeric: 3.0
        - densityMaxUnit: g/cm³
        - densityPercentile: 60.0
        
        Args:
            frontmatter_data: Dictionary containing properties to enhance
        """
        properties = frontmatter_data.get("properties", {})
        if not properties:
            return

        # Create new ordered properties dict
        new_properties = {}
        
        # Get material configuration from Materials.yaml
        # FAIL-FAST: No hardcoded defaults - require proper material configuration
        material_name = frontmatter_data.get("title", "").strip()
        if not material_name:
            logger.error("Material name (title) is required for property enhancement")
            return
            
        # Import Materials.yaml configuration
        try:
            import yaml
            import os
            materials_yaml_path = os.path.join(os.path.dirname(__file__), "../../../data/Materials.yaml")
            with open(materials_yaml_path, 'r') as f:
                materials_config = yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load Materials.yaml configuration: {e}")
            return
            
        # Find material category and configuration
        material_category = None
        # Look for material in material_index section
        material_index = materials_config.get("material_index", {})
        if material_name in material_index:
            material_category = material_index[material_name].get("category")
        
        if not material_category:
            logger.error(f"Material '{material_name}' not found in Materials.yaml configuration")
            return
            
        # Get category-based property ranges
        category_config = materials_config.get("category_ranges", {}).get(material_category, {})
        if not category_config:
            logger.error(f"Category '{material_category}' configuration not found in Materials.yaml")
            return        # Process properties in order for comprehensive numeric breakdown
        property_order = [
            "density", "thermalConductivity", "thermalDestructionPoint",
            "tensileStrength", "hardness", "youngsModulus"
        ]
        
        for base_prop in property_order:
            # Add main property
            if base_prop in properties:
                value_str = str(properties[base_prop])
                new_properties[base_prop] = properties[base_prop]
                
                # Calculate comprehensive numeric breakdown using category configuration
                property_config = category_config.get(base_prop, {})
                if property_config:
                    # Convert Materials.yaml format to expected config format
                    formatted_config = {
                        "min": property_config.get("min", ""),
                        "max": property_config.get("max", ""),
                        "unit": PropertyEnhancementService._extract_unit_from_range(property_config)
                    }
                    PropertyEnhancementService._add_complete_property_breakdown(
                        new_properties, base_prop, value_str, formatted_config
                    )
                else:
                    logger.warning(f"Property '{base_prop}' not configured for category '{material_category}'")
                    # FAIL-FAST: No fallback - just add the base property without enhancement
                    new_properties[base_prop] = properties[base_prop]
            
            # Also handle existing Min/Max properties if they exist
            for suffix in ["Min", "Max"]:
                prop_key = f"{base_prop}{suffix}"
                if prop_key in properties:
                    value_str = str(properties[prop_key])
                    new_properties[prop_key] = properties[prop_key]
                    
                    # Add numeric breakdown for Min/Max
                    numeric_value, unit = PropertyEnhancementService._extract_numeric_and_unit(value_str)
                    if numeric_value is not None:
                        new_properties[f"{prop_key}Numeric"] = numeric_value
                        new_properties[f"{prop_key}Unit"] = unit
        
        # Add remaining properties that weren't processed
        for key, value in properties.items():
            if key not in new_properties:
                new_properties[key] = value
        
        # Update the original properties dictionary with enhanced properties
        properties.clear()
        properties.update(new_properties)
        
        logger.debug(f"Enhanced properties with comprehensive numeric breakdown: {len(new_properties)} total fields")

    @staticmethod
    def _has_units(value_str: str) -> bool:
        """
        Check if a property value string contains units.
        
        Examples:
            "2.70 g/cm³" -> True
            "385 MPa" -> True
            "70-120 HB" -> True
            "1668" -> False
            
        Args:
            value_str: String value to check for units
            
        Returns:
            bool: True if units are detected, False otherwise
        """
        # Check if string contains letters (indicating units) after numbers
        return bool(re.search(r'\d\s*[a-zA-Z°·/²³]+', value_str))

    @staticmethod
    def _extract_numeric_and_unit(value_str: str) -> Tuple[float, str]:
        """
        Extract numeric value and unit from a property string.
        
        Examples:
            "2.70 g/cm³" -> (2.70, "g/cm³")
            "385 MPa" -> (385.0, "MPa") 
            "70-120 HB" -> (95.0, "HB")  # midpoint of range
            
        Args:
            value_str: String containing numeric value and unit
            
        Returns:
            tuple: (numeric_value, unit_string)
        """
        if not value_str:
            return 0.0, ""
        
        # Handle range values by taking the midpoint
        if '-' in value_str and not value_str.startswith('-'):
            parts = value_str.split('-')
            if len(parts) == 2:
                try:
                    num1_match = re.search(r'[\d.]+', parts[0].strip())
                    num2_match = re.search(r'[\d.]+', parts[1].strip())
                    
                    if num1_match and num2_match:
                        num1 = float(num1_match.group())
                        num2 = float(num2_match.group())
                        midpoint = (num1 + num2) / 2
                        
                        # Extract unit from second part
                        unit_match = re.search(r'[a-zA-Z°/³²·]+', parts[1].strip())
                        unit = unit_match.group() if unit_match else ""
                        
                        return midpoint, unit
                except (ValueError, AttributeError):
                    pass
        
        # Extract single value
        try:
            num_match = re.search(r'[\d.]+', value_str)
            if num_match:
                numeric_value = float(num_match.group())
                
                # Extract unit
                unit_match = re.search(r'[a-zA-Z°/³²·]+', value_str)
                unit = unit_match.group() if unit_match else ""
                
                return numeric_value, unit
        except (ValueError, AttributeError):
            pass
        
        return 0.0, ""
