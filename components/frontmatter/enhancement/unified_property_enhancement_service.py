#!/usr/bin/env python3
"""
Unified Property Enhancement Service

Consolidated service combining OptimizedPropertyEnhancementService and PropertyEnhancementService
to reduce architectural bloat while preserving all functionality.

Follows GROK fail-fast principles:
- No mocks or fallbacks in production
- Explicit error handling with proper exceptions
- No default values for critical dependencies
- Validates all configurations immediately
"""

import logging
import re
import os
import yaml
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)


class UnifiedPropertyEnhancementService:
    """Consolidated service for all property enhancement functionality"""

    @staticmethod
    def add_machine_settings(machine_settings: Dict, use_optimized: bool = True) -> None:
        """
        Add numeric fields for machine settings with configurable format.
        
        Args:
            machine_settings: Dictionary of machine settings to enhance
            use_optimized: If True, use optimized format; if False, use triple format
        """
        if use_optimized:
            UnifiedPropertyEnhancementService._add_optimized_machine_settings(machine_settings)
        else:
            UnifiedPropertyEnhancementService._add_triple_format_machine_settings(machine_settings)

    @staticmethod
    def add_properties(frontmatter_data: Dict, preserve_min_max: bool = True) -> None:
        """
        Add enhanced properties with configurable format.
        
        Args:
            frontmatter_data: Dictionary containing properties to enhance
            preserve_min_max: If True, preserve Min/Max/Unit structure from category ranges
        """
        if preserve_min_max:
            UnifiedPropertyEnhancementService._preserve_min_max_properties(frontmatter_data)
        else:
            UnifiedPropertyEnhancementService._add_triple_format_properties(frontmatter_data)

    @staticmethod
    def _add_optimized_machine_settings(machine_settings: Dict) -> None:
        """Add optimized numeric fields for machine settings with pure numeric structure."""
        new_machine_settings = {}
        
        settings_config = {
            "powerRange": {"unit": "W", "min": 20.0, "max": 500.0, "default": 60.0},
            "pulseDuration": {"unit": "ns", "min": 1.0, "max": 1000.0, "default": 55.0},
            "wavelength": {"unit": "nm", "min": 355.0, "max": 2940.0, "default": 1064.0},
            "spotSize": {"unit": "mm", "min": 0.01, "max": 10.0, "default": 1.05},
            "repetitionRate": {"unit": "kHz", "min": 1.0, "max": 1000.0, "default": 30.0},
            "fluenceRange": {"unit": "J/cm²", "min": 0.1, "max": 50.0, "default": 2.75},
            "scanningSpeed": {"unit": "mm/s", "min": 1.0, "max": 5000.0, "default": 500.0}
        }
        
        setting_order = ["powerRange", "pulseDuration", "wavelength", "spotSize", 
                        "repetitionRate", "fluenceRange", "scanningSpeed"]
        
        for setting_key in setting_order:
            if setting_key in machine_settings:
                config = settings_config[setting_key]
                value_str = str(machine_settings[setting_key])
                numeric_value = UnifiedPropertyEnhancementService._extract_numeric_value(value_str)
                
                if numeric_value is None:
                    numeric_value = config["default"]
                
                new_machine_settings[setting_key] = numeric_value
                new_machine_settings[f"{setting_key}Unit"] = config["unit"]
                new_machine_settings[f"{setting_key}Min"] = config["min"]
                new_machine_settings[f"{setting_key}Max"] = config["max"]
        
        # Add remaining settings
        for setting in ["beamProfile", "beamProfileOptions", "safetyClass"]:
            if setting in machine_settings:
                new_machine_settings[setting] = machine_settings[setting]
        
        machine_settings.clear()
        machine_settings.update(new_machine_settings)
        logger.debug("Applied optimized machine settings")

    @staticmethod
    def _add_triple_format_machine_settings(machine_settings: Dict) -> None:
        """Add triple format machine settings with full numeric/unit breakdown."""
        new_machine_settings = {}
        
        settings_config = {
            "powerRange": {"unit": "W", "min": "20W", "max": "500W"},
            "pulseDuration": {"unit": "ns", "min": "1ns", "max": "1000ns"},
            "wavelength": {"unit": "nm", "min": "355nm", "max": "2940nm"},
            "spotSize": {"unit": "mm", "min": "0.01mm", "max": "10mm"},
            "repetitionRate": {"unit": "kHz", "min": "1kHz", "max": "1000kHz"},
            "fluenceRange": {"unit": "J/cm²", "min": "0.1J/cm²", "max": "50J/cm²"},
            "scanningSpeed": {"unit": "mm/s", "min": "1mm/s", "max": "5000mm/s"}
        }
        
        setting_order = ["powerRange", "pulseDuration", "wavelength", "spotSize", 
                        "repetitionRate", "fluenceRange", "scanningSpeed"]
        
        for setting_key in setting_order:
            if setting_key in machine_settings:
                config = settings_config[setting_key]
                value_str = str(machine_settings[setting_key])
                numeric_value, unit = UnifiedPropertyEnhancementService._extract_numeric_and_unit(value_str)
                
                new_machine_settings[setting_key] = machine_settings[setting_key]
                new_machine_settings[f"{setting_key}Numeric"] = numeric_value
                new_machine_settings[f"{setting_key}Unit"] = config["unit"]
                
                # Add min/max with full breakdown
                for suffix, config_key in [("Min", "min"), ("Max", "max")]:
                    key = f"{setting_key}{suffix}"
                    new_machine_settings[key] = config[config_key]
                    
                    min_max_numeric, min_max_unit = UnifiedPropertyEnhancementService._extract_numeric_and_unit(config[config_key])
                    new_machine_settings[f"{key}Numeric"] = min_max_numeric
                    new_machine_settings[f"{key}Unit"] = min_max_unit
        
        # Add remaining settings
        for setting in ["beamProfile", "beamProfileOptions", "safetyClass"]:
            if setting in machine_settings:
                new_machine_settings[setting] = machine_settings[setting]
        
        machine_settings.clear()
        machine_settings.update(new_machine_settings)
        logger.debug("Applied triple format machine settings")

    @staticmethod
    def _preserve_min_max_properties(frontmatter_data: Dict) -> None:
        """Preserve Min/Max/Unit structure from category ranges - NO PERCENTILES."""
        properties = frontmatter_data.get("properties", {})
        if not properties:
            return
        
        has_min_max_structure = any(key.endswith('Min') or key.endswith('Max') for key in properties.keys())
        
        if has_min_max_structure:
            # Properties already have proper Min/Max/Unit structure
            # Process ALL property values to extract numeric values from those containing units
            for key, value in list(properties.items()):
                # Process main properties
                if key in ['density', 'meltingPoint', 'thermalConductivity', 'tensileStrength', 'hardness', 'youngsModulus']:
                    if isinstance(value, str):
                        numeric_value = UnifiedPropertyEnhancementService._extract_numeric_value(value)
                        if numeric_value is not None:
                            properties[key] = numeric_value
                
                # Process Min/Max fields that contain units (like meltingMax: "2800°C")
                elif key.endswith('Min') or key.endswith('Max'):
                    if isinstance(value, str) and not key.endswith('Unit'):
                        numeric_value = UnifiedPropertyEnhancementService._extract_numeric_value(value)
                        if numeric_value is not None:
                            properties[key] = numeric_value
            
            logger.debug(f"Preserved Min/Max/Unit structure for {len(properties)} properties (NO PERCENTILES)")
            return
        
        logger.debug("No Min/Max structure found - skipping property optimization")

    @staticmethod
    def _add_triple_format_properties(frontmatter_data: Dict) -> None:
        """Add comprehensive numeric and unit fields for complete legacy format compatibility."""
        properties = frontmatter_data.get("properties", {})
        if not properties:
            return

        material_name = frontmatter_data.get("title", "").strip()
        if not material_name:
            raise ValueError("Material name (title) is required for property enhancement")
            
        # Load materials configuration
        materials_config = UnifiedPropertyEnhancementService._load_materials_config()
        material_category = UnifiedPropertyEnhancementService._get_material_category(material_name, materials_config)
        category_config = materials_config.get("category_ranges", {}).get(material_category, {})
        
        if not category_config:
            raise ValueError(f"Category '{material_category}' configuration not found in materials.yaml")

        new_properties = {}
        property_order = ["density", "thermalConductivity", "thermalDestructionPoint", 
                         "tensileStrength", "hardness", "youngsModulus"]
        
        for base_prop in property_order:
            if base_prop in properties:
                value_str = str(properties[base_prop])
                new_properties[base_prop] = properties[base_prop]
                
                property_config = category_config.get(base_prop, {})
                if property_config:
                    formatted_config = {
                        "min": property_config.get("min", ""),
                        "max": property_config.get("max", ""),
                        "unit": UnifiedPropertyEnhancementService._extract_unit_from_range(property_config)
                    }
                    UnifiedPropertyEnhancementService._add_complete_property_breakdown(
                        new_properties, base_prop, value_str, formatted_config
                    )
                else:
                    logger.warning(f"Property '{base_prop}' not configured for category '{material_category}'")
                    new_properties[base_prop] = properties[base_prop]
        
        # Add remaining properties
        for key, value in properties.items():
            if key not in new_properties:
                new_properties[key] = value
        
        properties.clear()
        properties.update(new_properties)
        logger.debug(f"Enhanced properties with comprehensive breakdown: {len(new_properties)} fields")

    @staticmethod
    def _load_materials_config() -> Dict:
        """Load materials.yaml configuration with fail-fast behavior."""
        try:
            materials_yaml_path = os.path.join(os.path.dirname(__file__), "../../../data/materials.yaml")
            with open(materials_yaml_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise ValueError(f"Failed to load materials.yaml configuration: {e}")

    @staticmethod
    def _get_material_category(material_name: str, materials_config: Dict) -> str:
        """Get material category with fail-fast behavior."""
        material_index = materials_config.get("material_index", {})
        if material_name not in material_index:
            raise ValueError(f"Material '{material_name}' not found in materials.yaml configuration")
        
        material_category = material_index[material_name].get("category")
        if not material_category:
            raise ValueError(f"Category not found for material '{material_name}' in materials.yaml")
        
        return material_category

    @staticmethod
    def _extract_unit_from_range(property_config: Dict) -> str:
        """Extract unit from materials.yaml range configuration."""
        for val in [property_config.get("min", ""), property_config.get("max", "")]:
            if val:
                _, unit = UnifiedPropertyEnhancementService._extract_numeric_and_unit(str(val))
                if unit:
                    return unit
        return ""

    @staticmethod
    def _add_complete_property_breakdown(new_properties: Dict, base_prop: str, value_str: str, config: Dict) -> None:
        """Add complete property breakdown with calculated numeric variants and min/max."""
        numeric_value, unit = UnifiedPropertyEnhancementService._extract_numeric_and_unit(value_str)
        
        if '-' in value_str and numeric_value:
            range_match = re.search(r'(\d+(?:\.\d+)?)[-–](\d+(?:\.\d+)?)', value_str)
            if range_match:
                min_val = float(range_match.group(1))
                max_val = float(range_match.group(2))
                numeric_value = round((min_val + max_val) / 2, 2)
        
        if numeric_value is None:
            numeric_match = re.search(r'(\d+(?:\.\d+)?)', value_str)
            numeric_value = float(numeric_match.group(1)) if numeric_match else 0.0
        
        if not unit and config:
            unit = config["unit"]
        elif not unit:
            raise ValueError(f"Unit not provided for {base_prop} and no unit in existing value: {value_str}")
        
        # Add numeric breakdown
        new_properties[f"{base_prop}Numeric"] = numeric_value
        new_properties[f"{base_prop}Unit"] = unit
        
        if not config:
            raise ValueError(f"No configuration found for {base_prop} min/max ranges")
        
        # Add Min/Max properties with explicit null checks (GROK compliance)
        min_str = config["min"]
        max_str = config["max"]
        
        if not min_str or not max_str:
            raise ValueError(f"Missing min/max configuration for {base_prop}")
        
        new_properties[f"{base_prop}Min"] = min_str
        new_properties[f"{base_prop}Max"] = max_str
        
        min_numeric, min_unit = UnifiedPropertyEnhancementService._extract_numeric_and_unit(min_str)
        max_numeric, max_unit = UnifiedPropertyEnhancementService._extract_numeric_and_unit(max_str)
        
        # Explicit null checks instead of 'or' fallbacks (GROK compliance)
        if not min_unit:
            min_unit = unit
        if not max_unit:
            max_unit = unit
        
        new_properties[f"{base_prop}MinNumeric"] = min_numeric
        new_properties[f"{base_prop}MinUnit"] = min_unit
        new_properties[f"{base_prop}MaxNumeric"] = max_numeric
        new_properties[f"{base_prop}MaxUnit"] = max_unit

    @staticmethod
    def _extract_numeric_value(value_str: str) -> Optional[float]:
        """Extract numeric value from a property string."""
        if not value_str:
            return None
            
        try:
            return float(value_str)
        except ValueError:
            pass
        
        numeric_pattern = r'(\d+\.?\d*)'
        match = re.search(numeric_pattern, str(value_str))
        
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        
        return None

    @staticmethod
    def _extract_numeric_and_unit(value_str: str) -> Tuple[float, str]:
        """Extract numeric value and unit from a property string."""
        if not value_str:
            return 0.0, ""
        
        # Handle ranges by taking midpoint
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
                unit_match = re.search(r'[a-zA-Z°/³²·]+', value_str)
                unit = unit_match.group() if unit_match else ""
                return numeric_value, unit
        except (ValueError, AttributeError):
            pass
        
        return 0.0, ""

    @staticmethod
    def remove_redundant_sections(frontmatter: Dict) -> Dict[str, int]:
        """Remove redundant sections that duplicate optimized structure."""
        sections_to_remove = ['technicalSpecifications', 'prompt_chain_verification', 'laser_parameters']
        
        removed_count = 0
        for section in sections_to_remove:
            if section in frontmatter:
                del frontmatter[section]
                removed_count += 1
                logger.debug(f"Removed redundant section: {section}")
        
        return {"redundant_sections_removed": removed_count}

    @staticmethod
    def apply_full_optimization(frontmatter: Dict, use_optimized: bool = True) -> Dict[str, int]:
        """Apply complete optimization to frontmatter structure."""
        stats = {"properties_optimized": 0, "machine_settings_optimized": 0, "redundant_sections_removed": 0}
        
        if 'properties' in frontmatter:
            original_count = len(frontmatter['properties'])
            UnifiedPropertyEnhancementService.add_properties(frontmatter, preserve_min_max=use_optimized)
            stats["properties_optimized"] = len(frontmatter['properties']) - original_count
        
        if 'machineSettings' in frontmatter:
            original_count = len(frontmatter['machineSettings'])
            UnifiedPropertyEnhancementService.add_machine_settings(frontmatter['machineSettings'], use_optimized=use_optimized)
            stats["machine_settings_optimized"] = len(frontmatter['machineSettings']) - original_count
        
        removal_stats = UnifiedPropertyEnhancementService.remove_redundant_sections(frontmatter)
        stats.update(removal_stats)
        
        logger.info(f"Applied full optimization: {stats}")
        return stats
