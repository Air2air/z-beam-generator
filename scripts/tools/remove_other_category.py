#!/usr/bin/env python3
"""
Remove 'other' category from materialProperties and recategorize properties.

The 'other' category is NOT valid per frontmatter_template.yaml.
Only 2 valid category groups exist:
  - material_characteristics
  - laser_material_interaction

This script moves all properties from 'other' to their correct category groups
based on Categories.yaml property taxonomy.

Author: GitHub Copilot
Date: November 3, 2025
"""

import yaml
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Set


def load_property_categorization() -> Dict[str, str]:
    """Load property-to-category mapping from Categories.yaml."""
    categories_file = Path('data/materials/Categories.yaml')
    
    with open(categories_file) as f:
        data = yaml.safe_load(f)
    
    categories = data.get('propertyCategories', {}).get('categories', {})
    
    # Build property -> category mapping
    prop_to_cat = {}
    for cat_id, cat_data in categories.items():
        props = cat_data.get('properties', [])
        for prop in props:
            prop_to_cat[prop] = cat_id
    
    return prop_to_cat


def map_category_to_group(category_id: str) -> str:
    """Map Categories.yaml category to materialProperties group name."""
    # Laser-related categories map to laser_material_interaction
    if category_id in ['laser_material_interaction', 'optical', 'laser_absorption']:
        return 'laser_material_interaction'
    # Everything else maps to material_characteristics
    else:
        return 'material_characteristics'


def remove_other_category():
    """Remove 'other' category and recategorize its properties."""
    
    materials_file = Path('data/materials/materials.yaml')
    
    # Create backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = materials_file.with_suffix(f'.backup_before_other_removal_{timestamp}.yaml')
    shutil.copy2(materials_file, backup_file)
    print(f"📦 Backup created: {backup_file.name}")
    
    # Load property categorization
    prop_to_cat = load_property_categorization()
    print(f"📚 Loaded categorization for {len(prop_to_cat)} properties")
    
    # Load materials
    with open(materials_file) as f:
        data = yaml.safe_load(f)
    
    materials = data.get('materials', {})
    metadata_keys = {'label', 'description', 'percentage'}
    
    # Track statistics
    materials_fixed = 0
    properties_moved = 0
    uncategorized_props: Set[str] = set()
    
    print()
    print("=== PROCESSING MATERIALS ===")
    
    for mat_name, mat_data in materials.items():
        mp = mat_data.get('materialProperties', {})
        
        if 'other' not in mp:
            continue
        
        other_data = mp['other']
        
        # Extract properties from 'other' (exclude metadata)
        other_props = {k: v for k, v in other_data.items() if k not in metadata_keys}
        
        if not other_props:
            # Just remove empty 'other' category
            del mp['other']
            materials_fixed += 1
            print(f"✓ {mat_name}: Removed empty 'other' category")
            continue
        
        # Recategorize each property
        moved_count = 0
        for prop_name, prop_data in other_props.items():
            # Determine correct category
            category_id = prop_to_cat.get(prop_name)
            
            if category_id:
                # Map to materialProperties group name
                group_name = map_category_to_group(category_id)
                
                # Ensure target group exists
                if group_name not in mp:
                    mp[group_name] = {'label': 'Material Characteristics' if group_name == 'material_characteristics' else 'Laser-Material Interaction'}
                
                # Move property to correct group
                mp[group_name][prop_name] = prop_data
                moved_count += 1
                properties_moved += 1
            else:
                uncategorized_props.add(prop_name)
                print(f"  ⚠️  {mat_name}: Cannot categorize '{prop_name}' - not in Categories.yaml")
        
        # Remove 'other' category
        del mp['other']
        materials_fixed += 1
        
        print(f"✓ {mat_name}: Moved {moved_count} properties from 'other'")
    
    # Write updated data
    with open(materials_file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, indent=2, sort_keys=False, allow_unicode=True)
    
    print()
    print("=== SUMMARY ===")
    print(f"✅ Materials fixed: {materials_fixed}")
    print(f"✅ Properties moved: {properties_moved}")
    
    if uncategorized_props:
        print(f"⚠️  Uncategorized properties: {uncategorized_props}")
    else:
        print("✅ All properties successfully categorized")
    
    print()
    print(f"💾 Updated: {materials_file}")
    print(f"📦 Backup: {backup_file}")


if __name__ == '__main__':
    remove_other_category()
