#!/usr/bin/env python3
"""
Field Ordering Service

Provides field ordering functionality for frontmatter YAML content with hierarchical organization.
Extracted from the monolithic generator for better separation of concerns.
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class FieldOrderingService:
    """Service for applying standardized field ordering to frontmatter data"""

    @staticmethod
    def apply_field_ordering(frontmatter_data: Dict) -> Dict:
        """
        Apply the standard field ordering for optimal readability and consistency.
        
        Organizes fields according to the proposal:
        1. Basic Identification
        2. Content Metadata
        3. Chemical Classification
        4. Material Properties (Grouped)
        5. Material Composition
        6. Laser Machine Settings (Grouped)
        7. Applications
        8. Compatibility
        9. Regulatory Standards
        10. Author Information
        11. Visual Assets
        12. Impact Metrics
        
        Args:
            frontmatter_data: Dictionary of frontmatter fields to order
            
        Returns:
            Dictionary with fields ordered according to the hierarchy
        """
        ordered_data = {}
        
        # === 1. BASIC IDENTIFICATION ===
        if "name" in frontmatter_data:
            ordered_data["name"] = frontmatter_data["name"]
        if "category" in frontmatter_data:
            ordered_data["category"] = frontmatter_data["category"]
            
        # === 2. CONTENT METADATA ===
        for field in ["title", "headline", "description", "keywords"]:
            if field in frontmatter_data:
                ordered_data[field] = frontmatter_data[field]
                
        # === 3. CHEMICAL CLASSIFICATION ===
        if "chemicalProperties" in frontmatter_data:
            ordered_data["chemicalProperties"] = frontmatter_data["chemicalProperties"]
            
        # === 4. MATERIAL PROPERTIES (Grouped) ===
        if "properties" in frontmatter_data:
            ordered_data["properties"] = FieldOrderingService._order_properties_groups(
                frontmatter_data["properties"]
            )
            
        # === 5. MATERIAL COMPOSITION ===
        if "composition" in frontmatter_data:
            ordered_data["composition"] = frontmatter_data["composition"]
            
        # === 6. LASER MACHINE SETTINGS (Grouped) ===
        if "machineSettings" in frontmatter_data:
            ordered_data["machineSettings"] = FieldOrderingService._order_machine_settings_groups(
                frontmatter_data["machineSettings"]
            )
            
        # === 7. APPLICATIONS ===
        if "applications" in frontmatter_data:
            ordered_data["applications"] = frontmatter_data["applications"]
            
        # === 8. COMPATIBILITY ===
        if "compatibility" in frontmatter_data:
            ordered_data["compatibility"] = frontmatter_data["compatibility"]
            
        # === 9. REGULATORY STANDARDS ===
        if "regulatoryStandards" in frontmatter_data:
            ordered_data["regulatoryStandards"] = frontmatter_data["regulatoryStandards"]
            
        # === 10. AUTHOR INFORMATION ===
        for field in ["author", "author_object"]:
            if field in frontmatter_data:
                ordered_data[field] = frontmatter_data[field]
                
        # === 11. VISUAL ASSETS ===
        if "images" in frontmatter_data:
            ordered_data["images"] = frontmatter_data["images"]
            
        # === 12. IMPACT METRICS ===
        for field in ["environmentalImpact", "outcomes"]:
            if field in frontmatter_data:
                ordered_data[field] = frontmatter_data[field]
                
        # Add any remaining fields that weren't explicitly ordered
        for key, value in frontmatter_data.items():
            if key not in ordered_data:
                ordered_data[key] = value
                
        logger.debug(f"Applied field ordering to {len(ordered_data)} fields")
        return ordered_data

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
