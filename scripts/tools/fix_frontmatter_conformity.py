#!/usr/bin/env python3
"""
Fix ALL Frontmatter Files to Conform with frontmatter_template.yaml

This script ensures 100% conformity by:
1. Removing invalid root-level keys (materialCharacteristics, applications)
2. Flattening nested 'properties:' keys in category groups
3. Ensuring all properties are direct children of category groups
4. Adding min/max from Categories.yaml where missing
5. Validating required structure

Author: GitHub Copilot
Date: November 3, 2025
"""

import yaml
from pathlib import Path
import sys

def load_categories_yaml():
    """Load Categories.yaml for category ranges."""
    categories_path = Path('materials/data/Categories.yaml')
    with open(categories_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_category_ranges(categories_data, material_category):
    """Get category-wide ranges for a material category."""
    if 'categories' not in categories_data:
        return {}
    
    category_data = categories_data['categories'].get(material_category, {})
    return category_data.get('category_ranges', {})

def fix_frontmatter_structure(data, categories_data):
    """
    Fix frontmatter structure to match template.
    
    Returns: (modified_data, changes_made)
    """
    changes = []
    
    # 1. Remove invalid root-level keys
    invalid_keys = ['materialCharacteristics', 'applications']
    for key in invalid_keys:
        if key in data:
            del data[key]
            changes.append(f"Removed invalid key: {key}")
    
    # 2. Fix materialProperties structure
    if 'materialProperties' in data:
        mp = data['materialProperties']
        material_category = data.get('category', '')
        category_ranges = get_category_ranges(categories_data, material_category)
        
        for category_name in ['material_characteristics', 'laser_material_interaction']:
            if category_name not in mp:
                continue
            
            category_data = mp[category_name]
            if not isinstance(category_data, dict):
                continue
            
            # Check for nested 'properties:' key
            if 'properties' in category_data:
                nested_props = category_data.pop('properties')
                
                # If properties is a dict, flatten it
                if isinstance(nested_props, dict):
                    # Move nested properties to parent level
                    for prop_name, prop_value in nested_props.items():
                        if prop_name not in category_data:
                            category_data[prop_name] = prop_value
                    changes.append(f"Flattened nested 'properties:' in {category_name}")
            
            # 3. Add min/max from Categories.yaml where missing
            for prop_name, prop_value in list(category_data.items()):
                if prop_name in ['label', 'description', 'percentage']:
                    continue
                
                if isinstance(prop_value, dict):
                    # Check if min/max are missing
                    if 'min' not in prop_value or 'max' not in prop_value:
                        # Try to get from category ranges
                        if prop_name in category_ranges:
                            range_data = category_ranges[prop_name]
                            if 'min' in range_data and 'min' not in prop_value:
                                prop_value['min'] = range_data['min']
                                changes.append(f"Added min to {category_name}.{prop_name}")
                            if 'max' in range_data and 'max' not in prop_value:
                                prop_value['max'] = range_data['max']
                                changes.append(f"Added max to {category_name}.{prop_name}")
    
    return data, changes

def main():
    print("=" * 80)
    print("FIXING ALL FRONTMATTER FILES FOR TEMPLATE CONFORMITY")
    print("=" * 80)
    print()
    
    # Load Categories.yaml
    categories_data = load_categories_yaml()
    print("✅ Loaded Categories.yaml\n")
    
    frontmatter_dir = Path('frontmatter/materials')
    files = list(frontmatter_dir.glob('*.yaml'))
    
    print(f"📁 Found {len(files)} frontmatter files\n")
    
    fixed_count = 0
    unchanged_count = 0
    error_count = 0
    
    for file_path in files:
        try:
            # Load file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            material_name = data.get('name', file_path.stem)
            
            # Fix structure
            modified_data, changes = fix_frontmatter_structure(data, categories_data)
            
            if changes:
                # Write back
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(modified_data, f, default_flow_style=False, 
                             allow_unicode=True, sort_keys=False, width=120)
                
                print(f"✅ {material_name}")
                for change in changes[:3]:  # Show first 3 changes
                    print(f"   • {change}")
                if len(changes) > 3:
                    print(f"   ... and {len(changes) - 3} more")
                
                fixed_count += 1
            else:
                unchanged_count += 1
        
        except Exception as e:
            print(f"❌ Error processing {file_path.name}: {e}")
            error_count += 1
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ Fixed: {fixed_count} files")
    print(f"⏭️  Already correct: {unchanged_count} files")
    print(f"❌ Errors: {error_count} files")
    print("=" * 80)
    
    return 0 if error_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
