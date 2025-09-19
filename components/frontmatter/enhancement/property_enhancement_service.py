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
        
        # Process machine settings in groups
        setting_order = [
            "powerRange", "pulseDuration", "wavelength", "spotSize", 
            "repetitionRate", "fluenceRange", "scanningSpeed"
        ]
        
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
        
        # Add remaining settings that don't need triple format
        remaining_settings = ["safetyClass", "beamProfile", "beamProfileOptions"]
        for setting in remaining_settings:
            if setting in machine_settings:
                new_machine_settings[setting] = machine_settings[setting]
        
        # Update the machine settings dict
        machine_settings.clear()
        machine_settings.update(new_machine_settings)
        
        logger.debug("Reorganized machine settings with grouped numeric/unit components")

    @staticmethod
    def add_triple_format_properties(frontmatter_data: Dict) -> None:
        """
        Add numeric and unit fields for triple format compatibility.
        
        Groups related properties together:
        - density: 2.70 g/cm³
        - densityNumeric: 2.70
        - densityUnit: g/cm³
        - densityMin: 1.8 g/cm³
        - densityMinNumeric: 1.8
        - densityMinUnit: g/cm³
        
        Args:
            frontmatter_data: Dictionary containing properties to enhance
        """
        properties = frontmatter_data.get("properties", {})
        if not properties:
            return
        
        # Create new ordered properties dict
        new_properties = {}
        
        # Properties that need triple format and their expected units
        main_properties = {
            "density": ("densityNumeric", "densityUnit", "g/cm³"),
            "meltingPoint": ("meltingPointNumeric", "meltingPointUnit", "°C"),
            "thermalConductivity": ("thermalConductivityNumeric", "thermalConductivityUnit", "W/m·K"),
            "tensileStrength": ("tensileStrengthNumeric", "tensileStrengthUnit", "MPa"),
            "hardness": ("hardnessNumeric", "hardnessUnit", "HB"),
            "youngsModulus": ("youngsModulusNumeric", "youngsModulusUnit", "GPa"),
        }
        
        # Process properties in groups for better organization
        property_groups = [
            "density", "meltingPoint", "thermalConductivity", 
            "tensileStrength", "hardness", "youngsModulus"
        ]
        
        for base_prop in property_groups:
            # Add main property
            if base_prop in properties:
                value_str = str(properties[base_prop])
                new_properties[base_prop] = properties[base_prop]
                
                # Add numeric and unit components
                if base_prop in main_properties:
                    numeric_key, unit_key, default_unit = main_properties[base_prop]
                    
                    if not PropertyEnhancementService._has_units(value_str):
                        logger.warning(f"Property {base_prop} missing units: '{value_str}' - adding default unit {default_unit}")
                        value_str = f"{value_str} {default_unit}"
                        new_properties[base_prop] = value_str
                    
                    numeric_value, unit = PropertyEnhancementService._extract_numeric_and_unit(value_str)
                    new_properties[numeric_key] = numeric_value
                    new_properties[unit_key] = unit
            
            # Add related Min/Max properties grouped together
            related_props = [f"{base_prop}Min", f"{base_prop}Max"]
            for related_prop in related_props:
                if related_prop in properties:
                    value_str = str(properties[related_prop])
                    new_properties[related_prop] = properties[related_prop]
                    
                    # Add numeric and unit for Min/Max if they have units
                    if PropertyEnhancementService._has_units(value_str):
                        numeric_value, unit = PropertyEnhancementService._extract_numeric_and_unit(value_str)
                        new_properties[f"{related_prop}Numeric"] = numeric_value
                        new_properties[f"{related_prop}Unit"] = unit
            
            # Add percentile (should come after Min/Max)
            percentile_prop = f"{base_prop}Percentile"
            if base_prop == "meltingPoint":
                percentile_prop = "meltingPercentile"
            elif base_prop == "thermalConductivity":
                percentile_prop = "thermalPercentile"
            elif base_prop == "tensileStrength":
                percentile_prop = "tensilePercentile"
            elif base_prop == "hardness":
                percentile_prop = "hardnessPercentile"
            elif base_prop == "youngsModulus":
                percentile_prop = "modulusPercentile"
            
            if percentile_prop in properties:
                new_properties[percentile_prop] = properties[percentile_prop]
            
            # Handle special case for modulusMin/Max (youngsModulus related)
            if base_prop == "youngsModulus":
                for modulus_prop in ["modulusMin", "modulusMax"]:
                    if modulus_prop in properties:
                        value_str = str(properties[modulus_prop])
                        new_properties[modulus_prop] = properties[modulus_prop]
                        
                        if PropertyEnhancementService._has_units(value_str):
                            numeric_value, unit = PropertyEnhancementService._extract_numeric_and_unit(value_str)
                            new_properties[f"{modulus_prop}Numeric"] = numeric_value
                            new_properties[f"{modulus_prop}Unit"] = unit
        
        # Add remaining properties that weren't processed
        remaining_props = ["laserType", "wavelength", "fluenceRange", "chemicalFormula"]
        for prop in remaining_props:
            if prop in properties:
                new_properties[prop] = properties[prop]
        
        # Update the properties dict
        properties.clear()
        properties.update(new_properties)
        
        logger.debug("Reorganized properties with grouped numeric/unit components")

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
