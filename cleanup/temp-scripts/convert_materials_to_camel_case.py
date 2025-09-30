#!/usr/bin/env python3
"""
Convert Materials.yaml from snake_case to camelCase property naming.
"""

import yaml
from pathlib import Path

def snake_to_camel_case(snake_str):
    """Convert snake_case to camelCase."""
    components = snake_str.split('_')
    return components[0] + ''.join(word.capitalize() for word in components[1:])

def convert_materials_yaml_to_camel_case():
    """Convert all snake_case property names to camelCase in Materials.yaml."""
    
    print("🔄 Converting Materials.yaml to camelCase...")
    
    # Read the file
    materials_file = Path("data/Materials.yaml")
    with open(materials_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Property groups to convert
    property_groups = [
        'thermal_properties',
        'mechanical_properties', 
        'electrical_properties',
        'processing_properties',
        'magnetic_properties',
        'antimicrobial_properties'
    ]
    
    # Convert property group names
    changes_made = []
    for prop_group in property_groups:
        camel_case_name = snake_to_camel_case(prop_group)
        if prop_group in content:
            # Convert both standalone and indented occurrences
            pattern1 = f"  {prop_group}:"
            replacement1 = f"  {camel_case_name}:"
            
            pattern2 = f"      {prop_group}:"
            replacement2 = f"      {camel_case_name}:"
            
            if pattern1 in content:
                content = content.replace(pattern1, replacement1)
                changes_made.append(f"{prop_group} -> {camel_case_name} (root level)")
            
            if pattern2 in content:
                content = content.replace(pattern2, replacement2)
                changes_made.append(f"{prop_group} -> {camel_case_name} (nested level)")
    
    # Individual property names to convert (common snake_case properties)
    individual_properties = [
        'melting_point',
        'specific_heat',
        'operating_temperature',
        'compressive_strength',
        'flexural_strength',
        'fracture_toughness',
        'dielectric_constant',
        'firing_temperature',
        'moisture_content',
        'resin_content',
        'grain_structure_type',
        'glass_transition_temperature',
        'decomposition_point'
    ]
    
    # Convert individual property names
    for prop in individual_properties:
        camel_case_name = snake_to_camel_case(prop)
        if prop in content:
            # Replace property name followed by colon
            pattern = f"{prop}:"
            replacement = f"{camel_case_name}:"
            if pattern in content:
                content = content.replace(pattern, replacement)
                changes_made.append(f"{prop} -> {camel_case_name} (individual property)")
    
    # Write the updated content
    if content != original_content:
        # Create backup
        backup_file = f"data/Materials_backup_snake_case_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"📂 Backup created: {backup_file}")
        
        # Write updated file
        with open(materials_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Materials.yaml updated with {len(changes_made)} changes:")
        for change in changes_made[:10]:  # Show first 10 changes
            print(f"   • {change}")
        if len(changes_made) > 10:
            print(f"   ... and {len(changes_made) - 10} more changes")
        
        return True
    else:
        print("ℹ️  No changes needed - Materials.yaml already uses camelCase")
        return False

if __name__ == "__main__":
    from datetime import datetime
    convert_materials_yaml_to_camel_case()