#!/usr/bin/env python3
"""
Normalize Categories.yaml Structure

Ensures Categories.yaml uses the same flattened materialProperties structure
as Materials.yaml (after flattening).

Structure:
  materialProperties:
    material_characteristics:
      label: ...
      property1: {...}
      property2: {...}
    laser_material_interaction:
      label: ...
      property1: {...}
      property2: {...}

Date: November 2, 2025
"""

import yaml
from pathlib import Path
from datetime import datetime

categories_file = Path('data/materials/categories.yaml')
backup_file = Path(f'data/materials/categories_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml')

print("📋 Normalizing Categories.yaml structure...")
print(f"📂 Input: {categories_file}")
print(f"💾 Backup: {backup_file}\n")

# Load categories.yaml
with open(categories_file, 'r') as f:
    data = yaml.safe_load(f)

categories = data.get('categories', {})
normalized_count = 0
categories_with_props = []

for cat_name, cat_data in categories.items():
    if not isinstance(cat_data, dict):
        continue
    
    # Check if this category has materialProperties
    if 'materialProperties' not in cat_data:
        continue
    
    categories_with_props.append(cat_name)
    mp = cat_data['materialProperties']
    
    if not isinstance(mp, dict):
        continue
    
    # Check each group (material_characteristics, laser_material_interaction, etc.)
    for group_name, group_data in mp.items():
        if not isinstance(group_data, dict):
            continue
        
        # Check if it has nested 'properties' key (old structure)
        if 'properties' in group_data:
            print(f"  🔧 Flattening {cat_name}.{group_name}")
            props = group_data.pop('properties')
            group_data.update(props)
            normalized_count += 1

print(f"\n✅ Categories with materialProperties: {len(categories_with_props)}")
for cat in categories_with_props:
    print(f"   - {cat}")

print(f"\n✅ Normalized {normalized_count} property groups\n")

# Create backup
print("💾 Creating backup...")
with open(backup_file, 'w') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

# Write normalized structure
print("📝 Writing normalized structure...")
with open(categories_file, 'w') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

print(f"\n✅ Structure normalized successfully!")
print(f"   Backup saved: {backup_file}")
print(f"   Categories updated: {categories_file}")

# Verify the structure
print("\n🔍 Verifying normalized structure...")
with open(categories_file, 'r') as f:
    verify_data = yaml.safe_load(f)

verify_cats = verify_data.get('categories', {})
has_nested = False
for cat_name, cat_data in verify_cats.items():
    if isinstance(cat_data, dict) and 'materialProperties' in cat_data:
        mp = cat_data['materialProperties']
        if isinstance(mp, dict):
            for group_name, group_data in mp.items():
                if isinstance(group_data, dict) and 'properties' in group_data:
                    print(f"   ⚠️  {cat_name}.{group_name} still has nested 'properties' key")
                    has_nested = True

if not has_nested:
    print("   ✅ No nested 'properties' keys found - structure is flat")
else:
    print("   ⚠️  Some nested 'properties' keys remain")
