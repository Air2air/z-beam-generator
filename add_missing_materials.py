#!/usr/bin/env python3
"""
Add Missing Materials to Index
Adds all missing materials to material_index with proper categories and subcategories
"""

import yaml
from pathlib import Path

def add_missing_materials_to_index():
    """Add missing materials to the material_index with proper categorization"""
    materials_path = Path("data/materials.yaml")
    
    # Load materials.yaml
    with open(materials_path, 'r') as f:
        data = yaml.safe_load(f)
    
    # Materials to add with their proper categories and subcategories
    missing_materials = {
        'Boron Carbide': {'category': 'ceramic', 'subcategory': 'carbide'},
        'Ceramic Matrix Composites Cmcs': {'category': 'composite', 'subcategory': 'matrix'},
        'Chromium': {'category': 'metal', 'subcategory': 'non-ferrous'},
        'Crown Glass': {'category': 'glass', 'subcategory': 'soda-lime'},
        'Fiber Reinforced Polyurethane Frpu': {'category': 'composite', 'subcategory': 'fiber-reinforced'},
        'Glass Fiber Reinforced Polymers Gfrp': {'category': 'composite', 'subcategory': 'fiber-reinforced'},
        'Gorilla Glass': {'category': 'glass', 'subcategory': 'specialty-glass'},
        'Kevlar Reinforced Polymer': {'category': 'composite', 'subcategory': 'fiber-reinforced'},
        'Manganese': {'category': 'metal', 'subcategory': 'non-ferrous'},
        'Mdf': {'category': 'wood', 'subcategory': 'engineered'},
        'Metal Matrix Composites Mmcs': {'category': 'composite', 'subcategory': 'matrix'},
        'Sapphire Glass': {'category': 'glass', 'subcategory': 'specialty-glass'},
        'Silicon Oxide': {'category': 'ceramic', 'subcategory': 'oxide'},
        'Soda Lime Glass': {'category': 'glass', 'subcategory': 'soda-lime'},
        'Titanium Carbide': {'category': 'ceramic', 'subcategory': 'carbide'},
        'Tungsten Carbide': {'category': 'ceramic', 'subcategory': 'carbide'}
    }
    
    print("🔧 Adding missing materials to index...")
    
    # Add missing materials to material_index
    if 'material_index' not in data:
        data['material_index'] = {}
    
    materials_added = 0
    for material_name, material_info in missing_materials.items():
        if material_name not in data['material_index']:
            data['material_index'][material_name] = material_info
            print(f"  ✅ Added {material_name}: {material_info['category']}/{material_info['subcategory']}")
            materials_added += 1
    
    # Save the updated materials.yaml
    with open(materials_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, width=120, indent=2)
    
    print(f"\n✅ Added {materials_added} materials to index")
    print(f"📊 Total materials in index: {len(data['material_index'])}")
    
    return materials_added

if __name__ == "__main__":
    added = add_missing_materials_to_index()