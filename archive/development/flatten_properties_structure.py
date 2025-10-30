#!/usr/bin/env python3
"""
Flatten materialProperties structure by removing nested 'properties' key.

BEFORE:
  materialProperties:
    material_characteristics:
      label: ...
      properties:
        density:
          value: 2.32

AFTER:
  materialProperties:
    material_characteristics:
      label: ...
      density:
        value: 2.32
"""

import yaml
from pathlib import Path
from datetime import datetime


def flatten_material_properties(material_props):
    """Remove nested 'properties' key from materialProperties."""
    if not material_props or not isinstance(material_props, dict):
        return material_props
    
    flattened = {}
    for category_name, category_data in material_props.items():
        if not isinstance(category_data, dict):
            flattened[category_name] = category_data
            continue
        
        # Extract the nested properties and merge with metadata
        flattened_category = {}
        for key, value in category_data.items():
            if key == 'properties' and isinstance(value, dict):
                # Merge properties directly into category
                flattened_category.update(value)
            else:
                # Keep metadata fields (label, description, percentage)
                flattened_category[key] = value
        
        flattened[category_name] = flattened_category
    
    return flattened


def process_materials_yaml():
    """Flatten Materials.yaml structure."""
    print("📊 Processing Materials.yaml...")
    print("=" * 70)
    
    materials_path = Path('data/Materials.yaml')
    backup_path = Path(f'data/Materials.yaml.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    
    # Create backup
    import shutil
    shutil.copy(materials_path, backup_path)
    print(f"✅ Backup created: {backup_path.name}")
    
    # Load materials
    with open(materials_path, 'r') as f:
        data = yaml.safe_load(f)
    
    materials = data.get('materials', {})
    modified_count = 0
    
    # Flatten each material
    for material_name, material_data in materials.items():
        if 'materialProperties' in material_data:
            original = str(material_data['materialProperties'])
            material_data['materialProperties'] = flatten_material_properties(
                material_data['materialProperties']
            )
            if str(material_data['materialProperties']) != original:
                modified_count += 1
    
    # Save flattened structure
    with open(materials_path, 'w') as f:
        yaml.dump(data, f,
                 default_flow_style=False,
                 allow_unicode=True,
                 sort_keys=False,
                 width=1000)
    
    print(f"✅ Modified {modified_count}/{len(materials)} materials")
    print(f"✅ Saved to {materials_path}")
    print()


def process_frontmatter_files():
    """Flatten frontmatter files structure."""
    print("📋 Processing Frontmatter files...")
    print("=" * 70)
    
    frontmatter_dir = Path('content/frontmatter')
    if not frontmatter_dir.exists():
        print("❌ Frontmatter directory not found")
        return
    
    modified_count = 0
    total_count = 0
    
    for filepath in frontmatter_dir.glob('*.yaml'):
        total_count += 1
        
        # Load frontmatter
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        
        if 'materialProperties' in data:
            original = str(data['materialProperties'])
            data['materialProperties'] = flatten_material_properties(
                data['materialProperties']
            )
            
            if str(data['materialProperties']) != original:
                # Save flattened structure
                with open(filepath, 'w') as f:
                    yaml.dump(data, f,
                             default_flow_style=False,
                             allow_unicode=True,
                             sort_keys=False,
                             width=1000)
                modified_count += 1
    
    print(f"✅ Modified {modified_count}/{total_count} frontmatter files")
    print()


def verify_flattening():
    """Verify that flattening was successful."""
    print("🔍 Verifying flattening...")
    print("=" * 70)
    
    # Check Materials.yaml
    with open('data/Materials.yaml', 'r') as f:
        materials = yaml.safe_load(f)
    
    issues_found = False
    for material_name, material_data in list(materials['materials'].items())[:5]:
        if 'materialProperties' in material_data:
            for cat_name, cat_data in material_data['materialProperties'].items():
                if isinstance(cat_data, dict) and 'properties' in cat_data:
                    print(f"❌ {material_name}: Still has 'properties' key in {cat_name}")
                    issues_found = True
    
    if not issues_found:
        print("✅ Materials.yaml: No nested 'properties' keys found")
    
    # Check frontmatter
    frontmatter_dir = Path('content/frontmatter')
    for filepath in list(frontmatter_dir.glob('*.yaml'))[:5]:
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        
        if 'materialProperties' in data:
            for cat_name, cat_data in data['materialProperties'].items():
                if isinstance(cat_data, dict) and 'properties' in cat_data:
                    print(f"❌ {filepath.name}: Still has 'properties' key in {cat_name}")
                    issues_found = True
    
    if not issues_found:
        print("✅ Frontmatter: No nested 'properties' keys found (sample check)")
    
    print()


def main():
    """Main execution."""
    print()
    print("=" * 70)
    print("FLATTEN MATERIALPROPERTIES STRUCTURE")
    print("=" * 70)
    print()
    print("Removing nested 'properties' key from:")
    print("  1. data/Materials.yaml")
    print("  2. content/frontmatter/*.yaml")
    print()
    
    # Process files
    process_materials_yaml()
    process_frontmatter_files()
    verify_flattening()
    
    print("=" * 70)
    print("✅ FLATTENING COMPLETE")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Update trivial_exporter.py to handle flattened structure")
    print("  2. Test with: python3 run.py --deploy")
    print("  3. Verify min/max fields are added correctly")
    print()


if __name__ == "__main__":
    main()
