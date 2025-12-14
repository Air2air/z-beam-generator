#!/usr/bin/env python3
"""
Optimized Field Ordering Service

Provides clean, logical field ordering for frontmatter YAML content.
Follows canonical structure defined in materials/data/frontmatter_template.yaml

CANONICAL REFERENCE: materials/data/frontmatter_template.yaml
This is the single source of truth for field order and structure.

Field Order (per template):
1. name, category, subcategory, title, material_description, settings_description
2. author (determines voice)
3. images (hero, micro)
4. micro (description, before, after)
5. regulatoryStandards
6. applications
7. materialProperties (GROUPED: material_characteristics, laser_material_interaction)
8. materialCharacteristics (qualitative properties)
9. machineSettings
10. environmentalImpact
11. outcomeMetrics
12. faq
13. _metadata
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class FieldOrderingService:
    """Service for applying optimized field ordering to frontmatter data"""

    @staticmethod
    def apply_field_ordering(frontmatter_data: Dict) -> Dict:
        """
        Apply canonical field ordering per materials/data/frontmatter_template.yaml.
        
        REFERENCE: materials/data/frontmatter_template.yaml (SINGLE SOURCE OF TRUTH)
        
        Canonical hierarchy:
        1. Basic Identification (name, category, subcategory)
        2. Content Metadata (title, material_description, settings_description)
        3. Author (determines voice generation)
        4. Visual Assets (images: hero, micro)
        5. Micro (description, before, after)
        6. Regulatory Standards
        7. Applications
        8. Material Properties (GROUPED: material_characteristics, laser_material_interaction)
        9. Material Characteristics (qualitative properties)
        10. Machine Settings
        11. Environmental Impact
        12. Outcome Metrics
        13. FAQ
        14. Internal Metadata (_metadata)
        
        Args:
            frontmatter_data: Dictionary of frontmatter fields to order
            
        Returns:
            Dictionary with fields ordered per canonical template
        """
        ordered_data = {}
        
        # === CANONICAL ORDER per materials/data/frontmatter_template.yaml ===
        # REFERENCE: materials/data/frontmatter_template.yaml is the single source of truth
        
        # === 1. BASIC IDENTIFICATION ===
        for field in ["name", "category", "subcategory"]:
            if field in frontmatter_data:
                ordered_data[field] = frontmatter_data[field]
                
        # === 2. CONTENT METADATA ===
        for field in ["title", "material_description", "settings_description", "headline", "keywords"]:
            if field in frontmatter_data:
                ordered_data[field] = frontmatter_data[field]
                
        # === 3. AUTHOR (moved earlier per template) ===
        if "author" in frontmatter_data:
            ordered_data["author"] = frontmatter_data["author"]
            
        # === 4. VISUAL ASSETS (moved earlier per template) ===
        if "images" in frontmatter_data:
            ordered_data["images"] = frontmatter_data["images"]
            
        # === 5. MICRO (new per template) ===
        if "micro" in frontmatter_data:
            ordered_data["micro"] = frontmatter_data["micro"]
            
        # === 6. REGULATORY STANDARDS (moved earlier per template) ===
        if "regulatoryStandards" in frontmatter_data:
            ordered_data["regulatoryStandards"] = frontmatter_data["regulatoryStandards"]
            
        # === 7. APPLICATIONS ===
        if "applications" in frontmatter_data:
            ordered_data["applications"] = frontmatter_data["applications"]
            
        # === 8. MATERIAL PROPERTIES (GROUPED structure preserved) ===
        if "materialProperties" in frontmatter_data:
            ordered_data["materialProperties"] = FieldOrderingService._create_clean_properties_structure(
                frontmatter_data["materialProperties"]
            )
            
        # === 9. MATERIAL CHARACTERISTICS (qualitative properties) ===
        if "materialCharacteristics" in frontmatter_data:
            ordered_data["materialCharacteristics"] = frontmatter_data["materialCharacteristics"]
            
        # === 10. MACHINE SETTINGS ===
        if "machineSettings" in frontmatter_data:
            ordered_data["machineSettings"] = FieldOrderingService._create_clean_machine_settings_structure(
                frontmatter_data["machineSettings"]
            )
            
        # === 11. ENVIRONMENTAL IMPACT ===
        if "environmentalImpact" in frontmatter_data:
            ordered_data["environmentalImpact"] = frontmatter_data["environmentalImpact"]
            
        # === 12. OUTCOME METRICS ===
        if "outcomeMetrics" in frontmatter_data:
            ordered_data["outcomeMetrics"] = frontmatter_data["outcomeMetrics"]
            
        # === 13. FAQ ===
        if "faq" in frontmatter_data:
            ordered_data["faq"] = frontmatter_data["faq"]
            
        # === 14. METADATA (internal) ===
        if "_metadata" in frontmatter_data:
            ordered_data["_metadata"] = frontmatter_data["_metadata"]
        
        # Legacy fields (for backward compatibility)
        for field in ["chemicalProperties", "composition", "compatibility", "outcomes"]:
            if field in frontmatter_data and field not in ordered_data:
                ordered_data[field] = frontmatter_data[field]
                
        # Add any remaining fields that weren't explicitly ordered
        for key, value in frontmatter_data.items():
            if key not in ordered_data:
                ordered_data[key] = value
                
        logger.debug(f"Applied optimal field ordering to {len(ordered_data)} fields")
        return ordered_data

    @staticmethod
    def _create_clean_properties_structure(properties: Dict) -> Dict:
        """
        Create clean properties structure - PRESERVES CATEGORIZED STRUCTURE.
        
        Per GROK_INSTRUCTIONS.md: No fallbacks. If categorized structure exists, preserve it.
        Only process flat structure if no categories detected.
        """
        # Check if this is a categorized structure (has category objects with 'label' key)
        # Note: Materials.yaml uses flattened structure (properties directly under category, not nested under 'properties')
        if properties and isinstance(properties, dict):
            first_key = next(iter(properties.keys()), None)
            if first_key and isinstance(properties[first_key], dict):
                first_value = properties[first_key]
                # Check for 'label' key which indicates a category group
                if 'label' in first_value:
                    # CATEGORIZED STRUCTURE - return as-is (already organized by category)
                    logger.debug(f"Preserving categorized material properties structure with {len(properties)} categories")
                    return properties
        
        # FLAT STRUCTURE - apply legacy ordering (for backward compatibility only)
        logger.debug("Processing flat material properties structure (legacy)")
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
        for field in ["wavelength", "fluenceRange", "chemicalFormula"]:
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
