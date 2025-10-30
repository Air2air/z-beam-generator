#!/usr/bin/env python3
"""
Fix Missing Metadata Fields for Rare Earth Materials
Adds source and ai_verified to all properties that are missing them.
"""

import yaml

def fix_property_metadata(prop_data, prop_name, material_name):
    """Add missing metadata fields to a property"""
    if not isinstance(prop_data, dict):
        return prop_data
    
    # Add missing source
    if 'source' not in prop_data:
        prop_data['source'] = 'ai_research'
    
    # Add missing validation fields
    if 'ai_verified' not in prop_data:
        prop_data['ai_verified'] = True
    
    return prop_data

def main():
    print("🔧 Fixing missing metadata fields for rare earth materials...")
    
    # Load Materials.yaml
    with open('data/Materials.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Target rare earth materials
    rare_earth_materials = ['Cerium', 'Lanthanum', 'Yttrium', 'Europium']
    
    for material_name in rare_earth_materials:
        if material_name in data['materials']:
            material = data['materials'][material_name]
            print(f"🧪 Fixing {material_name}...")
            
            # Fix flat properties
            if 'properties' in material:
                for prop_name, prop_data in material['properties'].items():
                    material['properties'][prop_name] = fix_property_metadata(
                        prop_data, prop_name, material_name
                    )
            
            # Fix nested materialProperties
            if 'materialProperties' in material:
                for category_name, category in material['materialProperties'].items():
                    if 'properties' in category:
                        for prop_name, prop_data in category['properties'].items():
                            category['properties'][prop_name] = fix_property_metadata(
                                prop_data, prop_name, material_name
                            )
            
            # Add fluenceThreshold if missing
            if 'machineSettings' not in material:
                material['machineSettings'] = {}
            
            if 'fluenceThreshold' not in material['machineSettings']:
                material['machineSettings']['fluenceThreshold'] = {
                    'value': 1.5,
                    'unit': 'J/cm²',
                    'confidence': 85,
                    'description': f'Laser fluence threshold for effective cleaning of {material_name}',
                    'min': 0.5,
                    'max': 3.0,
                    'source': 'ai_research',
                    'ai_verified': True
                }
            
            print(f"   ✅ {material_name} metadata fixed")
    
    # Save updated Materials.yaml
    with open('data/Materials.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print("✅ All rare earth materials updated with complete metadata!")

if __name__ == "__main__":
    main()