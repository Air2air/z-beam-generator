#!/usr/bin/env python3
"""
Clean Up Duplicate Materials
Removes duplicate entries with different naming conventions and keeps consistent names
"""

import yaml
from pathlib import Path

def clean_duplicate_materials():
    """Remove duplicate materials with different naming conventions"""
    materials_path = Path("data/Materials.yaml")
    
    # Load Materials.yaml
    with open(materials_path, 'r') as f:
        data = yaml.safe_load(f)
    
    # Define the materials to remove (duplicates with inconsistent names)
    materials_to_remove = [
        'Ceramic Matrix Composites Cmcs',
        'Fiber Reinforced Polyurethane Frpu', 
        'Glass Fiber Reinforced Polymers Gfrp',
        'Kevlar Reinforced Polymer',
        'Mdf',
        'Metal Matrix Composites Mmcs',
        'Soda Lime Glass'
    ]
    
    print("🔧 Removing duplicate materials with inconsistent naming...")
    
    materials_removed = 0
    if 'material_index' in data:
        for material_name in materials_to_remove:
            if material_name in data['material_index']:
                del data['material_index'][material_name]
                print(f"  ✅ Removed duplicate: {material_name}")
                materials_removed += 1
    
    # Save the cleaned Materials.yaml
    with open(materials_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, width=120, indent=2)
    
    print(f"\n✅ Removed {materials_removed} duplicate materials")
    print(f"📊 Total materials in index: {len(data['material_index'])}")
    
    return materials_removed

if __name__ == "__main__":
    removed = clean_duplicate_materials()