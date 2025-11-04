#!/usr/bin/env python3
"""
Fix Invalid 'properties:' Nesting in Frontmatter Files

According to frontmatter_template.yaml, properties should be DIRECT children
of category groups (material_characteristics, laser_material_interaction),
NOT nested under a 'properties:' key.

WRONG:
  material_characteristics:
    label: "..."
    properties:           # ❌ Invalid nesting
      density: {...}

CORRECT:
  material_characteristics:
    label: "..."
    density: {...}      # ✅ Direct child

This script flattens the structure to match the template.
"""

import yaml
from pathlib import Path
import sys

def fix_properties_nesting(data):
    """
    Remove invalid 'properties:' nesting from materialProperties.
    
    Returns True if changes were made.
    """
    if 'materialProperties' not in data:
        return False
    
    mp = data['materialProperties']
    changes_made = False
    
    for category in ['material_characteristics', 'laser_material_interaction']:
        if category not in mp:
            continue
        
        cat_data = mp[category]
        
        # Check if there's invalid 'properties:' nesting
        if 'properties' in cat_data and isinstance(cat_data['properties'], dict):
            # Flatten: move properties from nested dict to parent level
            nested_props = cat_data.pop('properties')
            
            # Add each property as direct child of category
            for prop_name, prop_value in nested_props.items():
                if prop_name not in cat_data:  # Don't overwrite metadata
                    cat_data[prop_name] = prop_value
            
            changes_made = True
            print(f"    ✓ Flattened 'properties:' in {category} ({len(nested_props)} properties)")
    
    return changes_made


def main():
    frontmatter_dir = Path('frontmatter/materials')
    
    if not frontmatter_dir.exists():
        print(f"❌ Directory not found: {frontmatter_dir}")
        return 1
    
    files = list(frontmatter_dir.glob('*.yaml'))
    
    print("=" * 70)
    print("FIXING INVALID 'properties:' NESTING IN FRONTMATTER FILES")
    print("=" * 70)
    print(f"\nTotal files: {len(files)}\n")
    
    fixed_count = 0
    skipped_count = 0
    
    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        material_name = data.get('name', file_path.stem)
        
        # Fix the structure
        if fix_properties_nesting(data):
            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            print(f"  ✅ Fixed: {material_name}")
            fixed_count += 1
        else:
            skipped_count += 1
    
    print("\n" + "=" * 70)
    print(f"✅ Fixed: {fixed_count} files")
    print(f"⏭️  Skipped (already correct): {skipped_count} files")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
