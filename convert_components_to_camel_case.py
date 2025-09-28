#!/usr/bin/env python3
"""
Convert all component files from snake_case to camelCase property naming.
"""

import os
import re
from pathlib import Path
from datetime import datetime

def snake_to_camel_case(snake_str):
    """Convert snake_case to camelCase."""
    components = snake_str.split('_')
    return components[0] + ''.join(word.capitalize() for word in components[1:])

def convert_components_to_camel_case():
    """Convert all snake_case property references to camelCase in component files."""
    
    print("🔄 Converting component files to camelCase...")
    
    # Property mappings from snake_case to camelCase
    property_mappings = {
        # Property groups
        'thermal_properties': 'thermalProperties',
        'mechanical_properties': 'mechanicalProperties',
        'electrical_properties': 'electricalProperties',
        'processing_properties': 'processingProperties',
        'magnetic_properties': 'magneticProperties',
        'antimicrobial_properties': 'antimicrobialProperties',
        
        # Individual properties
        'thermal_conductivity': 'thermalConductivity',
        'melting_point': 'meltingPoint',
        'specific_heat': 'specificHeat',
        'operating_temperature': 'operatingTemperature',
        'compressive_strength': 'compressiveStrength',
        'flexural_strength': 'flexuralStrength',
        'fracture_toughness': 'fractureToughness',
        'dielectric_constant': 'dielectricConstant',
        'firing_temperature': 'firingTemperature',
        'moisture_content': 'moistureContent',
        'resin_content': 'resinContent',
        'grain_structure_type': 'grainStructureType',
        'glass_transition_temperature': 'glassTransitionTemperature',
        'decomposition_point': 'decompositionPoint'
    }
    
    # Find all Python files in components directory
    component_files = []
    components_dir = Path("components")
    if components_dir.exists():
        for py_file in components_dir.rglob("*.py"):
            component_files.append(py_file)
    
    total_files_changed = 0
    total_changes_made = 0
    
    for file_path in component_files:
        if file_path.name == "__init__.py":
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            file_changes = []
            
            # Apply property mappings
            for snake_case, camel_case in property_mappings.items():
                # Pattern 1: String literals with quotes
                patterns = [
                    f'"{snake_case}"',
                    f"'{snake_case}'",
                    f'"{snake_case}":',
                    f"'{snake_case}':",
                    f'get("{snake_case}"',
                    f"get('{snake_case}'",
                ]
                
                replacements = [
                    f'"{camel_case}"',
                    f"'{camel_case}'",
                    f'"{camel_case}":',
                    f"'{camel_case}':",
                    f'get("{camel_case}"',
                    f"get('{camel_case}'",
                ]
                
                for pattern, replacement in zip(patterns, replacements):
                    if pattern in content:
                        content = content.replace(pattern, replacement)
                        file_changes.append(f"{pattern} -> {replacement}")
                
                # Pattern 2: Dictionary key access
                dict_patterns = [
                    f'["{snake_case}"]',
                    f"['{snake_case}']",
                ]
                
                dict_replacements = [
                    f'["{camel_case}"]',
                    f"['{camel_case}']",
                ]
                
                for pattern, replacement in zip(dict_patterns, dict_replacements):
                    if pattern in content:
                        content = content.replace(pattern, replacement)
                        file_changes.append(f"{pattern} -> {replacement}")
            
            # Special case for list literals containing property names
            for snake_case, camel_case in property_mappings.items():
                list_patterns = [
                    f"'{snake_case}',",
                    f'"{snake_case}",',
                    f"'{snake_case}']",
                    f'"{snake_case}"]',
                ]
                
                list_replacements = [
                    f"'{camel_case}',",
                    f'"{camel_case}",',
                    f"'{camel_case}']",
                    f'"{camel_case}"]',
                ]
                
                for pattern, replacement in zip(list_patterns, list_replacements):
                    if pattern in content:
                        content = content.replace(pattern, replacement)
                        file_changes.append(f"{pattern} -> {replacement}")
            
            # Write changes if any were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                total_files_changed += 1
                total_changes_made += len(file_changes)
                
                print(f"✅ Updated {file_path.relative_to('.')} ({len(file_changes)} changes)")
                # Show first few changes for each file
                for change in file_changes[:3]:
                    print(f"   • {change}")
                if len(file_changes) > 3:
                    print(f"   ... and {len(file_changes) - 3} more changes")
        
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    print(f"\n🎯 Summary:")
    print(f"   📁 Files updated: {total_files_changed}")
    print(f"   🔄 Total changes: {total_changes_made}")
    
    if total_files_changed > 0:
        print(f"✅ Component files successfully converted to camelCase!")
        return True
    else:
        print(f"ℹ️  No changes needed - components already use camelCase")
        return False

if __name__ == "__main__":
    convert_components_to_camel_case()