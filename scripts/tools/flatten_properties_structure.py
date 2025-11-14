#!/usr/bin/env python3
"""
Flatten materialProperties structure to match frontmatter_template.yaml.

BEFORE (WRONG):
materialProperties:
  material_characteristics:
    label: "..."
    description: "..."
    properties:
      density: {value: 8.8, unit: "g/cm³"}
      porosity: {value: 0.5, unit: "%"}

AFTER (CORRECT per template):
materialProperties:
  material_characteristics:
    label: "..."
    density: {value: 8.8, unit: "g/cm³"}
    porosity: {value: 0.5, unit: "%"}
"""

import yaml
from pathlib import Path
from datetime import datetime

def flatten_material_properties(material_data):
    """
    Remove 'properties' wrapper and move properties directly under category groups.
    
    Returns: (modified, changes_made)
    """
    if not isinstance(material_data, dict):
        return material_data, False
    
    mat_props = material_data.get('materialProperties', {})
    if not isinstance(mat_props, dict):
        return material_data, False
    
    changes_made = False
    
    # Process both category groups
    for category in ['material_characteristics', 'laser_material_interaction']:
        if category not in mat_props:
            continue
            
        category_data = mat_props[category]
        if not isinstance(category_data, dict):
            continue
        
        # Check if this category has the nested 'properties' key
        if 'properties' in category_data and isinstance(category_data['properties'], dict):
            nested_props = category_data['properties']
            
            # Move all properties up one level (even if empty)
            for prop_name, prop_value in nested_props.items():
                category_data[prop_name] = prop_value
            
            # Remove the 'properties' wrapper (even if it was empty)
            del category_data['properties']
            
            changes_made = True
    
    return material_data, changes_made

def main():
    materials_file = Path("data/materials/Materials.yaml")
    
    if not materials_file.exists():
        print("❌ Materials.yaml not found")
        return False
    
    # Create backup
    backup_file = materials_file.parent / f"Materials.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
    print(f"📦 Creating backup: {backup_file.name}")
    
    with open(materials_file) as f:
        original_content = f.read()
    
    with open(backup_file, 'w') as f:
        f.write(original_content)
    
    # Load data
    print(f"📂 Loading {materials_file}")
    with open(materials_file) as f:
        data = yaml.safe_load(f)
    
    materials = data.get('materials', {})
    total_materials = len(materials)
    migrated_count = 0
    
    print(f"🔍 Checking {total_materials} materials...")
    print()
    
    # Process each material
    for material_name, material_data in materials.items():
        modified_data, changes_made = flatten_material_properties(material_data)
        
        if changes_made:
            materials[material_name] = modified_data
            migrated_count += 1
            print(f"✅ {material_name}")
    
    if migrated_count == 0:
        print("✨ All materials already have correct structure!")
        return True
    
    # Save updated data
    print()
    print(f"💾 Saving changes to {materials_file}")
    
    with open(materials_file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print()
    print("=" * 60)
    print(f"✅ Migration complete!")
    print(f"   Migrated: {migrated_count} materials")
    print(f"   Unchanged: {total_materials - migrated_count} materials")
    print(f"   Backup: {backup_file.name}")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
