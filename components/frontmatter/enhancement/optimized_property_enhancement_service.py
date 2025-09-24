#!/usr/bin/env python3
"""
Optimized Property Enhancement Service

Provides optimized property enhancement functionality for frontmatter content
with pure numeric structures eliminating redundant fields.

Key Optimizations:
- Single numeric values (no *Numeric redundancy)
- Consolidated units (single unit field for min/max pairs)
- No string concatenations with units
- Maximum computational efficiency
"""

import logging
import re
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class OptimizedPropertyEnhancementService:
    """Service for enhancing frontmatter properties with optimized pure numeric structures"""

    @staticmethod
    def add_optimized_machine_settings(machine_settings: Dict) -> None:
        """
        Add optimized numeric fields for machine settings with pure numeric structure.
        
        BEFORE (redundant):
        - powerRange: 50-200W
        - powerRangeNumeric: 125.0
        - powerRangeUnit: W
        - powerRangeMin: 20W
        - powerRangeMinNumeric: 20.0
        - powerRangeMinUnit: W
        
        AFTER (optimized):
        - powerRange: 125.0
        - powerRangeUnit: W
        - powerRangeMin: 20.0
        - powerRangeMax: 500.0
        
        Args:
            machine_settings: Dictionary of machine settings to enhance
        """
        # Create new ordered machine settings dict
        new_machine_settings = {}
        
        # Machine settings that need optimization with industry-standard ranges
        settings_config = {
            "powerRange": {
                "unit": "W",
                "min": 20.0, "max": 500.0,
                "default": 60.0,
                "description": "Laser output power range"
            },
            "pulseDuration": {
                "unit": "ns", 
                "min": 1.0, "max": 1000.0,
                "default": 55.0,
                "description": "Pulse duration for pulsed lasers"
            },
            "wavelength": {
                "unit": "nm",
                "min": 355.0, "max": 2940.0,
                "default": 1064.0,
                "description": "Laser wavelength range (UV to IR)"
            },
            "spotSize": {
                "unit": "mm",
                "min": 0.01, "max": 10.0,
                "default": 1.05,
                "description": "Focused beam spot diameter"
            },
            "repetitionRate": {
                "unit": "kHz",
                "min": 1.0, "max": 1000.0,
                "default": 30.0,
                "description": "Pulse repetition frequency"
            },
            "fluenceRange": {
                "unit": "J/cm²",
                "min": 0.1, "max": 50.0,
                "default": 2.75,
                "description": "Laser fluence (energy density)"
            },
            "scanningSpeed": {
                "unit": "mm/s",
                "min": 1.0, "max": 5000.0,
                "default": 500.0,
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
                
                # Extract numeric value from original string if needed
                value_str = str(machine_settings[setting_key])
                numeric_value = OptimizedPropertyEnhancementService._extract_numeric_value(value_str)
                
                # Use extracted value or default if extraction fails
                if numeric_value is None:
                    numeric_value = config["default"]
                
                # Add optimized structure
                new_machine_settings[setting_key] = numeric_value
                new_machine_settings[f"{setting_key}Unit"] = config["unit"]
                new_machine_settings[f"{setting_key}Min"] = config["min"]
                new_machine_settings[f"{setting_key}Max"] = config["max"]
                
                logger.debug(f"Added optimized machine setting for {setting_key}: {numeric_value} {config['unit']}")
        
        # Add remaining settings that don't need optimization
        remaining_settings = ["beamProfile", "beamProfileOptions", "safetyClass"]
        
        for setting in remaining_settings:
            if setting in machine_settings:
                new_machine_settings[setting] = machine_settings[setting]
        
        # Update the machine settings dict
        machine_settings.clear()
        machine_settings.update(new_machine_settings)
        
        logger.debug("Applied optimized machine settings with pure numeric structure")

    @staticmethod
    def add_optimized_properties(properties: Dict) -> None:
        """
        Add optimized numeric fields for material properties with clean structure.
        
        BEFORE (problematic):
        - density: 2.33
        - densityUnit: "g/cm³" densityMin: 1.8
        - densityMinNumeric: "null"
        
        AFTER (optimized):
        - density: 2.33
        - densityUnit: "g/cm³"
        - densityRange: [1.8, 6.0]
        - densityPercentile: 12.6
        
        Args:
            properties: Dictionary of material properties to enhance
        """
        # Create new clean properties structure
        clean_properties = {}
        
        # Material property ranges from category_ranges
        property_ranges = {
            "density": {"min": 1.8, "max": 6.0, "unit": "g/cm³"},
            "meltingPoint": {"min": 1200.0, "max": 2800.0, "unit": "°C"},
            "thermalConductivity": {"min": 0.5, "max": 200.0, "unit": "W/(m·K)"},
            "tensileStrength": {"min": 50.0, "max": 1000.0, "unit": "MPa"},
            "hardness": {"min": 1.0, "max": 10.0, "unit": "Mohs"},
            "youngsModulus": {"min": 20.0, "max": 80.0, "unit": "GPa"}
        }
        
        # Process each property with clean structure
        for prop_name, range_config in property_ranges.items():
            if prop_name in properties:
                # Extract numeric value from string if needed
                value_str = str(properties[prop_name])
                numeric_value = OptimizedPropertyEnhancementService._extract_numeric_value(value_str)
                
                if numeric_value is not None:
                    # Clean structure: value, unit, range, percentile
                    clean_properties[prop_name] = numeric_value
                    clean_properties[f"{prop_name}Unit"] = range_config["unit"]
                    clean_properties[f"{prop_name}Range"] = [range_config["min"], range_config["max"]]
                    
                    # Calculate percentile for category context
                    percentile = OptimizedPropertyEnhancementService._calculate_percentile(
                        numeric_value, range_config["min"], range_config["max"]
                    )
                    clean_properties[f"{prop_name}Percentile"] = percentile
                    
                    logger.debug(f"Optimized property {prop_name}: {numeric_value} {range_config['unit']}")
        
        # Add any other properties that aren't in standard config (but exclude non-property fields)
        excluded_fields = [
            # Redundant fields we're replacing
            'densityMin', 'densityMax', 'densityMinNumeric', 'densityMaxNumeric',
            'meltingPointMin', 'meltingPointMax', 'meltingPointMinNumeric', 'meltingPointMaxNumeric',
            'thermalConductivityMin', 'thermalConductivityMax', 'thermalConductivityMinNumeric', 'thermalConductivityMaxNumeric',
            'tensileStrengthMin', 'tensileStrengthMax', 'tensileStrengthMinNumeric', 'tensileStrengthMaxNumeric',
            'hardnessMin', 'hardnessMax', 'hardnessMinNumeric', 'hardnessMaxNumeric',
            'youngsModulusMin', 'youngsModulusMax', 'youngsModulusMinNumeric', 'youngsModulusMaxNumeric',
            'densityMinUnit', 'densityMaxUnit', 'meltingPointMinUnit', 'meltingPointMaxUnit',
            'thermalConductivityMinUnit', 'thermalConductivityMaxUnit', 'tensileStrengthMinUnit', 'tensileStrengthMaxUnit',
            'hardnessMinUnit', 'hardnessMaxUnit', 'youngsModulusMinUnit', 'youngsModulusMaxUnit',
            # Non-property fields that don't belong in properties section
            'laserType', 'wavelength', 'fluenceRange', 'chemicalFormula', 'pulseDuration', 'spotSize',
            'repetitionRate', 'scanningSpeed', 'powerRange', 'beamProfile', 'safetyClass'
        ]
        
        for key, value in properties.items():
            if key not in excluded_fields and key not in clean_properties:
                clean_properties[key] = value
        
        # Replace original properties with clean version
        properties.clear()
        properties.update(clean_properties)
        
        logger.debug("Applied clean optimized properties structure")

    @staticmethod
    def _extract_numeric_value(value_str: str) -> float:
        """
        Extract numeric value from a property string.
        
        Args:
            value_str: String containing numeric value with possible units
            
        Returns:
            Numeric value or None if extraction fails
        """
        if not value_str:
            return None
            
        # Try direct float conversion first
        try:
            return float(value_str)
        except ValueError:
            pass
        
        # Extract from string with units
        numeric_pattern = r'(\d+\.?\d*)'
        match = re.search(numeric_pattern, str(value_str))
        
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        
        return None

    @staticmethod
    def _calculate_percentile(value: float, min_val: float, max_val: float) -> float:
        """Calculate percentile position within range"""
        if max_val == min_val:
            return 50.0
        
        percentile = ((value - min_val) / (max_val - min_val)) * 100
        return round(max(0.0, min(100.0, percentile)), 1)

    @staticmethod
    def remove_redundant_sections(frontmatter: Dict) -> None:
        """Remove redundant sections that duplicate optimized structure"""
        sections_to_remove = [
            'technicalSpecifications',
            'prompt_chain_verification', 
            'laser_parameters'
        ]
        
        removed_count = 0
        for section in sections_to_remove:
            if section in frontmatter:
                del frontmatter[section]
                removed_count += 1
                logger.debug(f"Removed redundant section: {section}")
        
        if removed_count > 0:
            logger.info(f"Removed {removed_count} redundant sections for optimization")

    @staticmethod
    def apply_full_optimization(frontmatter: Dict) -> Dict[str, int]:
        """
        Apply complete optimization to frontmatter structure.
        
        Returns:
            Dictionary with optimization statistics
        """
        stats = {
            "properties_optimized": 0,
            "machine_settings_optimized": 0,
            "redundant_sections_removed": 0
        }
        
        # Optimize properties section
        if 'properties' in frontmatter:
            original_count = len(frontmatter['properties'])
            OptimizedPropertyEnhancementService.add_optimized_properties(frontmatter['properties'])
            stats["properties_optimized"] = len(frontmatter['properties']) - original_count
        
        # Optimize machine settings section
        if 'machineSettings' in frontmatter:
            original_count = len(frontmatter['machineSettings'])
            OptimizedPropertyEnhancementService.add_optimized_machine_settings(frontmatter['machineSettings'])
            stats["machine_settings_optimized"] = len(frontmatter['machineSettings']) - original_count
        
        # Remove redundant sections
        sections_before = len(frontmatter)
        OptimizedPropertyEnhancementService.remove_redundant_sections(frontmatter)
        stats["redundant_sections_removed"] = sections_before - len(frontmatter)
        
        logger.info(f"Applied full optimization: {stats}")
        return stats
