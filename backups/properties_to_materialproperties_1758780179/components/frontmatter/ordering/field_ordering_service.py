#!/usr/bin/env python3
"""
Optimized Field Ordering Service

Provides clean, logical field ordering for frontmatter YAML content.
Eliminates scattered organization and creates optimal structure.
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class FieldOrderingService:
    """Service for applying optimized field ordering to frontmatter data"""

    @staticmethod
    def apply_field_ordering(frontmatter_data: Dict) -> Dict:
        """
        Apply optimal field ordering for maximum readability and logical flow.
        
        Reorganized hierarchy:
        1. Basic Identification (name, category)
        2. Content Metadata (title, headline, description, keywords)
        3. Chemical Properties (symbol, formula, materialType)
        4. Physical Properties (organized grouping with clean structure)
        5. Composition & Applications (practical information)
        6. Machine Settings (laser parameters)
        7. Standards & Compatibility (regulatory, compatibility)
        8. Author & Visual Assets (metadata)
        9. Impact Metrics (environmental, outcomes)
        
        Args:
            frontmatter_data: Dictionary of frontmatter fields to order
            
        Returns:
            Dictionary with optimally organized fields
        """
        ordered_data = {}
        
        # === 1. BASIC IDENTIFICATION ===
        for field in ["name", "category", "subcategory"]:
            if field in frontmatter_data:
                ordered_data[field] = frontmatter_data[field]
                
        # === 2. CONTENT METADATA ===
        for field in ["title", "headline", "description", "keywords"]:
            if field in frontmatter_data:
                ordered_data[field] = frontmatter_data[field]
                
        # === 3. CHEMICAL PROPERTIES ===
        if "chemicalProperties" in frontmatter_data:
            ordered_data["chemicalProperties"] = frontmatter_data["chemicalProperties"]
            
        # === 4. PHYSICAL PROPERTIES (Clean Structure) ===
        if "properties" in frontmatter_data:
            ordered_data["properties"] = FieldOrderingService._create_clean_properties_structure(
                frontmatter_data["properties"]
            )
            
        # === 5. COMPOSITION & APPLICATIONS ===
        for field in ["composition", "applications"]:
            if field in frontmatter_data:
                ordered_data[field] = frontmatter_data[field]
                
        # === 6. MACHINE SETTINGS ===
        if "machineSettings" in frontmatter_data:
            ordered_data["machineSettings"] = FieldOrderingService._create_clean_machine_settings_structure(
                frontmatter_data["machineSettings"]
            )
            
        # === 7. STANDARDS & COMPATIBILITY ===
        for field in ["compatibility", "regulatoryStandards"]:
            if field in frontmatter_data:
                ordered_data[field] = frontmatter_data[field]
                
        # === 8. AUTHOR & VISUAL ASSETS ===
        for field in ["author", "author_object", "images"]:
            if field in frontmatter_data:
                ordered_data[field] = frontmatter_data[field]
                
        # === 9. IMPACT METRICS ===
        for field in ["environmentalImpact", "outcomes"]:
            if field in frontmatter_data:
                ordered_data[field] = frontmatter_data[field]
                
        # Add any remaining fields that weren't explicitly ordered
        for key, value in frontmatter_data.items():
            if key not in ordered_data:
                ordered_data[key] = value
                
        logger.debug(f"Applied optimal field ordering to {len(ordered_data)} fields")
        return ordered_data

    @staticmethod
    def _create_clean_properties_structure(properties: Dict) -> Dict:
        """Create clean properties structure with logical grouping and proper formatting"""
        clean_properties = {}
        
        # Property groups in logical order
        property_groups = [
            "density", "meltingPoint", "thermalConductivity", 
            "tensileStrength", "hardness", "youngsModulus"
        ]
        
        # Add each property group cleanly with proper spacing
        for prop in property_groups:
            if prop in properties:
                clean_properties[prop] = properties[prop]
                
                # Add associated fields in order with proper separation
                for suffix in ["Unit", "Range", "Percentile"]:
                    field_name = f"{prop}{suffix}"
                    if field_name in properties:
                        clean_properties[field_name] = properties[field_name]
        
        # Add any remaining properties
        for key, value in properties.items():
            if key not in clean_properties:
                clean_properties[key] = value
                
        return clean_properties

    @staticmethod
    def _create_clean_machine_settings_structure(machine_settings: Dict) -> Dict:
        """Create clean machine settings structure with logical grouping"""
        clean_settings = {}
        
        # Machine setting groups in logical order
        setting_groups = [
            "powerRange", "wavelength", "pulseDuration", "spotSize",
            "repetitionRate", "fluenceRange", "scanningSpeed"
        ]
        
        # Add each setting group cleanly
        for setting in setting_groups:
            if setting in machine_settings:
                clean_settings[setting] = machine_settings[setting]
                
                # Add associated fields in order
                for suffix in ["Unit", "Range"]:
                    field_name = f"{setting}{suffix}"
                    if field_name in machine_settings:
                        clean_settings[field_name] = machine_settings[field_name]
        
        # Add any remaining settings
        for key, value in machine_settings.items():
            if key not in clean_settings:
                clean_settings[key] = value
                
        return clean_settings

    @staticmethod
    def _order_properties_groups(properties: Dict) -> Dict:
        """Order properties with grouped organization following the standard pattern"""
        ordered_properties = {}
        
        # Property groups in order - include both thermal property types
        property_groups = [
            "density", "meltingPoint", "decompositionPoint", "thermalConductivity", 
            "tensileStrength", "hardness", "youngsModulus"
        ]
        
        # Add each group with all its components
        for prop in property_groups:
            if prop in properties:
                # Add main property
                ordered_properties[prop] = properties[prop]
                
                # Add numeric and unit fields
                if f"{prop}Numeric" in properties:
                    ordered_properties[f"{prop}Numeric"] = properties[f"{prop}Numeric"]
                if f"{prop}Unit" in properties:
                    ordered_properties[f"{prop}Unit"] = properties[f"{prop}Unit"]
                    
                # Add min fields with explicit handling for different property types
                if "meltingMin" in properties and prop == "meltingPoint":
                    ordered_properties["meltingMin"] = properties["meltingMin"]
                    ordered_properties["meltingMinNumeric"] = properties.get("meltingMinNumeric")
                    ordered_properties["meltingMinUnit"] = properties.get("meltingMinUnit")
                elif "decompositionMin" in properties and prop == "decompositionPoint":
                    ordered_properties["decompositionMin"] = properties["decompositionMin"]
                    ordered_properties["decompositionMinNumeric"] = properties.get("decompositionMinNumeric")
                    ordered_properties["decompositionMinUnit"] = properties.get("decompositionMinUnit")
                elif f"{prop}Min" in properties:
                    ordered_properties[f"{prop}Min"] = properties[f"{prop}Min"]
                    ordered_properties[f"{prop}MinNumeric"] = properties.get(f"{prop}MinNumeric")
                    ordered_properties[f"{prop}MinUnit"] = properties.get(f"{prop}MinUnit")
                elif "thermalMin" in properties and prop == "thermalConductivity":
                    ordered_properties["thermalMin"] = properties["thermalMin"]
                    ordered_properties["thermalMinNumeric"] = properties.get("thermalMinNumeric")
                    ordered_properties["thermalMinUnit"] = properties.get("thermalMinUnit")
                elif "tensileMin" in properties and prop == "tensileStrength":
                    ordered_properties["tensileMin"] = properties["tensileMin"]
                    ordered_properties["tensileMinNumeric"] = properties.get("tensileMinNumeric")
                    ordered_properties["tensileMinUnit"] = properties.get("tensileMinUnit")
                elif "hardnessMin" in properties and prop == "hardness":
                    ordered_properties["hardnessMin"] = properties["hardnessMin"]
                    ordered_properties["hardnessMinNumeric"] = properties.get("hardnessMinNumeric")
                    ordered_properties["hardnessMinUnit"] = properties.get("hardnessMinUnit")
                elif "modulusMin" in properties and prop == "youngsModulus":
                    ordered_properties["modulusMin"] = properties["modulusMin"]
                    ordered_properties["modulusMinNumeric"] = properties.get("modulusMinNumeric")
                    ordered_properties["modulusMinUnit"] = properties.get("modulusMinUnit")
                    
                # Add max fields
                if "meltingMax" in properties and prop == "meltingPoint":
                    ordered_properties["meltingMax"] = properties["meltingMax"]
                    ordered_properties["meltingMaxNumeric"] = properties.get("meltingMaxNumeric")
                    ordered_properties["meltingMaxUnit"] = properties.get("meltingMaxUnit")
                elif "decompositionMax" in properties and prop == "decompositionPoint":
                    ordered_properties["decompositionMax"] = properties["decompositionMax"]
                    ordered_properties["decompositionMaxNumeric"] = properties.get("decompositionMaxNumeric")
                    ordered_properties["decompositionMaxUnit"] = properties.get("decompositionMaxUnit")
                elif f"{prop}Max" in properties:
                    ordered_properties[f"{prop}Max"] = properties[f"{prop}Max"]
                    ordered_properties[f"{prop}MaxNumeric"] = properties.get(f"{prop}MaxNumeric")
                    ordered_properties[f"{prop}MaxUnit"] = properties.get(f"{prop}MaxUnit")
                elif "thermalMax" in properties and prop == "thermalConductivity":
                    ordered_properties["thermalMax"] = properties["thermalMax"]
                    ordered_properties["thermalMaxNumeric"] = properties.get("thermalMaxNumeric")
                    ordered_properties["thermalMaxUnit"] = properties.get("thermalMaxUnit")
                elif "tensileMax" in properties and prop == "tensileStrength":
                    ordered_properties["tensileMax"] = properties["tensileMax"]
                    ordered_properties["tensileMaxNumeric"] = properties.get("tensileMaxNumeric")
                    ordered_properties["tensileMaxUnit"] = properties.get("tensileMaxUnit")
                elif "hardnessMax" in properties and prop == "hardness":
                    ordered_properties["hardnessMax"] = properties["hardnessMax"]
                    ordered_properties["hardnessMaxNumeric"] = properties.get("hardnessMaxNumeric")
                    ordered_properties["hardnessMaxUnit"] = properties.get("hardnessMaxUnit")
                elif "modulusMax" in properties and prop == "youngsModulus":
                    ordered_properties["modulusMax"] = properties["modulusMax"]
                    ordered_properties["modulusMaxNumeric"] = properties.get("modulusMaxNumeric")
                    ordered_properties["modulusMaxUnit"] = properties.get("modulusMaxUnit")
                    
                # Add percentile
                if f"{prop}Percentile" in properties:
                    ordered_properties[f"{prop}Percentile"] = properties[f"{prop}Percentile"]
                elif "meltingPercentile" in properties and prop == "meltingPoint":
                    ordered_properties["meltingPercentile"] = properties["meltingPercentile"]
                elif "decompositionPercentile" in properties and prop == "decompositionPoint":
                    ordered_properties["decompositionPercentile"] = properties["decompositionPercentile"]
                elif "thermalPercentile" in properties and prop == "thermalConductivity":
                    ordered_properties["thermalPercentile"] = properties["thermalPercentile"]
                elif "tensilePercentile" in properties and prop == "tensileStrength":
                    ordered_properties["tensilePercentile"] = properties["tensilePercentile"]
                elif "hardnessPercentile" in properties and prop == "hardness":
                    ordered_properties["hardnessPercentile"] = properties["hardnessPercentile"]
                elif "modulusPercentile" in properties and prop == "youngsModulus":
                    ordered_properties["modulusPercentile"] = properties["modulusPercentile"]
        
        # Add laser-specific properties at the end
        for field in ["laserType", "wavelength", "fluenceRange", "chemicalFormula"]:
            if field in properties:
                ordered_properties[field] = properties[field]
                
        # Add any remaining properties
        for key, value in properties.items():
            if key not in ordered_properties:
                ordered_properties[key] = value
                
        logger.debug(f"Ordered {len(ordered_properties)} property fields")
        return ordered_properties

    @staticmethod
    def _order_machine_settings_groups(machine_settings: Dict) -> Dict:
        """Order machine settings with grouped organization"""
        ordered_settings = {}
        
        # Machine setting groups in order
        setting_groups = [
            "powerRange", "pulseDuration", "wavelength", "spotSize", 
            "repetitionRate", "fluenceRange", "scanningSpeed"
        ]
        
        # Add each group with all its components
        for setting in setting_groups:
            if setting in machine_settings:
                # Add main setting
                ordered_settings[setting] = machine_settings[setting]
                
                # Add numeric and unit
                if f"{setting}Numeric" in machine_settings:
                    ordered_settings[f"{setting}Numeric"] = machine_settings[f"{setting}Numeric"]
                if f"{setting}Unit" in machine_settings:
                    ordered_settings[f"{setting}Unit"] = machine_settings[f"{setting}Unit"]
                    
                # Add min values
                if f"{setting}Min" in machine_settings:
                    ordered_settings[f"{setting}Min"] = machine_settings[f"{setting}Min"]
                    ordered_settings[f"{setting}MinNumeric"] = machine_settings.get(f"{setting}MinNumeric")
                    ordered_settings[f"{setting}MinUnit"] = machine_settings.get(f"{setting}MinUnit")
                    
                # Add max values
                if f"{setting}Max" in machine_settings:
                    ordered_settings[f"{setting}Max"] = machine_settings[f"{setting}Max"]
                    ordered_settings[f"{setting}MaxNumeric"] = machine_settings.get(f"{setting}MaxNumeric")
                    ordered_settings[f"{setting}MaxUnit"] = machine_settings.get(f"{setting}MaxUnit")
        
        # Add beam and safety settings at the end
        for field in ["beamProfile", "beamProfileOptions", "safetyClass"]:
            if field in machine_settings:
                ordered_settings[field] = machine_settings[field]
                
        # Add any remaining settings
        for key, value in machine_settings.items():
            if key not in ordered_settings:
                ordered_settings[key] = value
                
        logger.debug(f"Ordered {len(ordered_settings)} machine setting fields")
        return ordered_settings
