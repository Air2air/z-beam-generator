#!/usr/bin/env python3
"""
Data Orchestrator

Orchestrates data loading and merging across domains.
This is the CORRECT place for cross-domain data operations.

ALLOWED PATTERN per DOMAIN_INDEPENDENCE_POLICY.md:
"Orchestrators Can Access Multiple Domains - ALLOWED"

Moved from domains/materials/data_loader.py (Nov 26, 2025)
to eliminate cross-domain contamination.

Author: AI Assistant
Date: November 26, 2025
"""

from typing import Any, Dict

# ✅ CORRECT: Orchestrator imports from multiple domains
from domains.materials.data_loader import load_materials_yaml, load_properties_yaml
from domains.settings.data_loader import load_settings_yaml


class DataOrchestrationError(Exception):
    """Raised when data orchestration fails"""
    pass


def _deep_merge(base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.
    
    Values from overlay take precedence, but base values fill gaps where
    overlay has None or missing keys. Recursively merges nested dicts.
    
    Args:
        base: Base dictionary (values preserved if overlay is None/missing)
        overlay: Overlay dictionary (non-None values take precedence)
        
    Returns:
        Merged dictionary
    """
    result = base.copy()
    
    for key, overlay_value in overlay.items():
        if key in result:
            base_value = result[key]
            # If both are dicts, recursively merge
            if isinstance(base_value, dict) and isinstance(overlay_value, dict):
                result[key] = _deep_merge(base_value, overlay_value)
            # If overlay is None, keep base value
            elif overlay_value is None:
                pass  # Keep result[key] (base_value)
            # Otherwise, overlay takes precedence
            else:
                result[key] = overlay_value
        else:
            # Key not in base, use overlay (even if None)
            result[key] = overlay_value
    
    return result


def merge_materials_settings(
    materials_data: Dict[str, Any],
    properties_data: Dict[str, Any],
    settings_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Merge materials, properties, and settings data.
    
    This is the integration point where cross-domain data comes together.
    Individual domains remain independent.
    
    Args:
        materials_data: Data from Materials.yaml (materials domain)
        properties_data: Data from MaterialProperties.yaml (materials domain)
        settings_data: Data from Settings.yaml (settings domain)
        
    Returns:
        Merged data structure with all information combined
        
    Raises:
        DataOrchestrationError: If merging fails
    """
    try:
        # Get materials dict
        materials = materials_data.get('materials', {})
        
        # Merge properties and settings into each material
        merged_count = 0
        for material_name, material_data in materials.items():
            # Merge properties if available (DEEP MERGE to preserve existing data)
            if material_name in properties_data:
                existing_props = material_data.get('properties', {})
                new_props = properties_data[material_name]
                # Deep merge: new_props values override existing, but existing fills gaps
                material_data['properties'] = _deep_merge(existing_props, new_props)
                merged_count += 1
            
            # Merge machine_settings if available
            if material_name in settings_data:
                material_data['machine_settings'] = settings_data[material_name]
        
        # Update materials in the data structure
        materials_data['materials'] = materials
        
        return materials_data
        
    except Exception as e:
        raise DataOrchestrationError(f"Failed to merge materials and settings data: {e}")


def load_complete_materials_data() -> Dict[str, Any]:
    """
    Load complete materials data with properties and settings merged.
    
    This is the NEW recommended way to load materials data when you need
    everything (materials + properties + settings) in one structure.
    
    Replaces: domains.materials.data_loader.load_materials_data()
    
    Returns:
        Complete merged data structure:
        {
            'materials': {
                'MaterialName': {
                    ...core metadata...,
                    'properties': {...},  # From properties domain
                    'machine_settings': {...}       # From settings domain
                }
            },
            'category_metadata': {...},
            'material_index': {...}
        }
        
    Raises:
        DataOrchestrationError: If loading or merging fails
        
    Example:
        >>> data = load_complete_materials_data()
        >>> aluminum = data['materials']['Aluminum']
        >>> density = aluminum['properties']['density']
        >>> power = aluminum['machine_settings']['powerRange']
    """
    try:
        # Load from each domain independently
        materials_data = load_materials_yaml()
        properties_data = load_properties_yaml()
        settings_data = load_settings_yaml()
        
        # Merge at orchestrator level
        return merge_materials_settings(materials_data, properties_data, settings_data)
        
    except Exception as e:
        raise DataOrchestrationError(f"Failed to load complete materials data: {e}")
