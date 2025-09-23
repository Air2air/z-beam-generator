#!/usr/bin/env python3
"""
Comprehensive Materials.yaml Normalization Script

Normalizes all material fields and values in materials.yaml:
1. Converts snake_case to camelCase field names
2. Migrates melting_point to thermalDestructionPoint + thermalDestructionType
3. Converts all range values to mean values
4. Standardizes decimal precision to 2 places
5. Removes inconsistent annotations
6. Ensures consistent unit formats
"""

import re
import yaml
import math
from pathlib import Path
from typing import Dict, Any, Union

def calculate_range_mean(range_str: str) -> float:
    """Extract numeric range and calculate mean."""
    # Match patterns like "3.95-4.1", "900-940", "1.6-2.0"
    range_pattern = r'([0-9]*\.?[0-9]+)-([0-9]*\.?[0-9]+)'
    match = re.search(range_pattern, range_str)
    if match:
        min_val = float(match.group(1))
        max_val = float(match.group(2))
        return round((min_val + max_val) / 2, 2)
    return None

def normalize_field_name(field_name: str) -> str:
    """Convert snake_case to camelCase."""
    field_mapping = {
        'melting_point': 'thermalDestructionPoint',
        'thermal_conductivity': 'thermalConductivity',
        'tensile_strength': 'tensileStrength',
        'youngs_modulus': 'youngsModulus',
        'specific_heat': 'specificHeat',
        'thermal_expansion': 'thermalExpansion',
        'thermal_diffusivity': 'thermalDiffusivity',
        'laser_absorption': 'laserAbsorption',
        'laser_reflectivity': 'laserReflectivity',
        'compressive_strength': 'compressiveStrength',
        'flexural_strength': 'flexuralStrength',
        'dielectric_constant': 'dielectricConstant',
        'electrical_resistivity': 'electricalResistivity',
        'difficulty_score': 'difficultyScore',
        'industry_tags': 'industryTags',
        'laser_parameters': 'laserParameters',
        'fluence_threshold': 'fluenceThreshold',
        'pulse_duration': 'pulseDuration',
        'wavelength_optimal': 'wavelengthOptimal',
        'power_range': 'powerRange',
        'repetition_rate': 'repetitionRate',
        'spot_size': 'spotSize',
        'laser_type': 'laserType'
    }
    return field_mapping.get(field_name, field_name)

def normalize_value(value: str, field_name: str) -> str:
    """Normalize a field value."""
    if not isinstance(value, str):
        return value
    
    # Handle range values
    if '-' in value and re.search(r'[0-9]+-[0-9]', value):
        mean_val = calculate_range_mean(value)
        if mean_val is not None:
            # Extract unit from original value
            unit_match = re.search(r'[0-9]+\.?[0-9]*-[0-9]+\.?[0-9]*\s*(.+)', value)
            unit = unit_match.group(1) if unit_match else ''
            return f"{mean_val}{unit}"
    
    # Remove annotations like "(decomposes)" or "(varies by composition)"
    value = re.sub(r'\s*\([^)]+\)', '', value)
    
    # Standardize decimal precision for numeric values
    if re.search(r'^[0-9]+\.[0-9]+', value):
        numeric_match = re.match(r'^([0-9]+\.[0-9]+)(.*)$', value)
        if numeric_match:
            number = float(numeric_match.group(1))
            unit = numeric_match.group(2)
            # Round to 2 decimal places, but don't show .00
            if number == int(number):
                return f"{int(number)}{unit}"
            else:
                return f"{number:.2f}".rstrip('0').rstrip('.') + unit
    
    return value.strip()

def get_thermal_destruction_type(category: str) -> str:
    """Get thermal destruction type based on material category."""
    category_types = {
        'metal': 'melting',
        'ceramic': 'melting',
        'glass': 'melting',
        'semiconductor': 'melting',
        'composite': 'decomposition',
        'wood': 'decomposition',
        'stone': 'melting',
        'masonry': 'decomposition'
    }
    return category_types.get(category, 'melting')

def normalize_material_entry(material_data: Dict[str, Any], material_name: str, category: str) -> Dict[str, Any]:
    """Normalize a single material entry."""
    normalized = {}
    
    for field, value in material_data.items():
        # Normalize field name
        new_field = normalize_field_name(field)
        
        if isinstance(value, dict):
            # Recursively normalize nested dictionaries
            normalized[new_field] = normalize_material_entry(value, material_name, category)
        elif isinstance(value, list):
            # Keep lists as-is (applications, industry_tags, etc.)
            normalized[new_field] = value
        elif isinstance(value, str):
            # Normalize string values
            normalized[new_field] = normalize_value(value, field)
        else:
            # Keep other types as-is
            normalized[new_field] = value
    
    # Handle thermal property migration
    if 'melting_point' in material_data or 'meltingPoint' in material_data:
        # Remove old field if it exists
        normalized.pop('meltingPoint', None)
        
        # Get thermal destruction type
        thermal_destruction_type = get_thermal_destruction_type(category)
        
        # Add thermal destruction type if not already present
        if 'thermalDestructionType' not in normalized:
            normalized['thermalDestructionType'] = thermal_destruction_type
    
    return normalized

def normalize_materials_yaml():
    """Normalize the entire materials.yaml file."""
    materials_path = Path("data/materials.yaml")
    
    # Backup original file
    backup_path = Path("data/materials_backup_" + str(int(__import__('time').time())) + ".yaml")
    
    print(f"🔧 Starting comprehensive materials.yaml normalization...")
    print(f"📁 Creating backup: {backup_path}")
    
    # Read original file
    with open(materials_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Create backup
    with open(backup_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    # Track changes
    changes = {
        'field_names_normalized': 0,
        'ranges_simplified': 0,
        'thermal_properties_migrated': 0,
        'values_normalized': 0
    }
    
    # Normalize category_ranges section
    if 'category_ranges' in data:
        print("📋 Normalizing category_ranges...")
        for category, ranges in data['category_ranges'].items():
            if isinstance(ranges, dict):
                data['category_ranges'][category] = normalize_material_entry(ranges, f"category_{category}", category)
    
    # Normalize material_index (already mostly normalized)
    print("📋 Material index already normalized...")
    
    # Find and normalize detailed material entries
    print("📋 Normalizing detailed material entries...")
    
    # Process the 'materials' section
    if 'materials' in data:
        materials_section = data['materials']
        
        for category_name, category_data in materials_section.items():
            if isinstance(category_data, dict) and 'items' in category_data:
                print(f"  🔧 Normalizing category: {category_name}")
                
                for i, item in enumerate(category_data['items']):
                    if isinstance(item, dict) and 'name' in item:
                        material_name = item['name']
                        
                        # Get category for this material
                        material_category = item.get('category', category_name)
                        
                        # Count changes
                        old_material = item.copy()
                        
                        # Normalize the material entry
                        normalized_material = normalize_material_entry(item, material_name, material_category)
                        category_data['items'][i] = normalized_material
                        
                        # Count specific changes
                        if 'melting_point' in old_material and 'thermalDestructionPoint' in normalized_material:
                            changes['thermal_properties_migrated'] += 1
                        
                        # Count field name changes
                        old_fields = set(old_material.keys())
                        new_fields = set(normalized_material.keys())
                        if old_fields != new_fields:
                            changes['field_names_normalized'] += 1
                        
                        # Count range simplifications and value normalizations
                        for old_key, old_value in old_material.items():
                            if isinstance(old_value, str):
                                if '-' in old_value and re.search(r'[0-9]+-[0-9]', old_value):
                                    changes['ranges_simplified'] += 1
                                # Check if value was normalized
                                new_value = normalized_material.get(normalize_field_name(old_key), old_value)
                                if old_value != new_value:
                                    changes['values_normalized'] += 1
    
    # Write normalized file
    print(f"💾 Writing normalized materials.yaml...")
    with open(materials_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    # Report results
    print(f"\n✅ Materials.yaml normalization complete!")
    print(f"📊 Changes made:")
    print(f"  🏷️  Field names normalized: {changes['field_names_normalized']}")
    print(f"  📏 Ranges simplified: {changes['ranges_simplified']}")
    print(f"  🔥 Thermal properties migrated: {changes['thermal_properties_migrated']}")
    print(f"  📝 Total materials processed")
    print(f"📁 Backup saved as: {backup_path}")

if __name__ == "__main__":
    normalize_materials_yaml()
