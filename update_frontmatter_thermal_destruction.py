#!/usr/bin/env python3
"""
Update thermalDestruction in existing frontmatter files to use normalized nested structure.

This script:
1. Reads existing frontmatter YAML files
2. Removes old thermalDestructionPoint, thermalDestructionType, meltingPoint properties
3. Adds normalized thermalDestruction with point/type structure
4. Gets values from materials.yaml and min/max from Categories.yaml
"""

import yaml
from pathlib import Path
from datetime import datetime
import sys

# Category to destruction type mapping
CATEGORY_DESTRUCTION_TYPES = {
    'ceramic': 'thermal_shock',
    'composite': 'decomposition',
    'glass': 'melting',
    'masonry': 'spalling',
    'metal': 'melting',
    'plastic': 'decomposition',
    'semiconductor': 'melting',
    'stone': 'thermal_shock',
    'wood': 'carbonization'
}

def load_materials_data():
    """Load materials.yaml"""
    with open('data/materials.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data['materials']

def load_categories_data():
    """Load Categories.yaml"""
    with open('data/Categories.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data['categories']

def get_category_thermal_ranges(categories, category):
    """Get thermalDestruction ranges from Categories.yaml for a category"""
    # Normalize to lowercase for lookup
    category = category.lower() if category else None
    
    if not category or category not in categories:
        return None
    
    cat_data = categories[category]
    if 'category_ranges' not in cat_data:
        return None
    
    ranges = cat_data['category_ranges']
    if 'thermalDestruction' not in ranges:
        return None
    
    td = ranges['thermalDestruction']
    if 'point' not in td:
        return None
    
    return {
        'min': td['point'].get('min'),
        'max': td['point'].get('max'),
        'unit': td['point'].get('unit'),
        'type': td.get('type', 'melting')
    }

def update_frontmatter_file(file_path, materials, categories):
    """Update a single frontmatter file"""
    try:
        # Load frontmatter
        with open(file_path, 'r', encoding='utf-8') as f:
            frontmatter = yaml.safe_load(f)
        
        if not frontmatter or 'materialProperties' not in frontmatter:
            return None, "No materialProperties section"
        
        # Get material name and category (they're at top level)
        material_name = frontmatter.get('name')
        category = frontmatter.get('category')
        
        if not material_name or not category:
            return None, "Missing material name or category"
        
        # Check if material exists in materials.yaml
        if material_name not in materials:
            return None, f"Material {material_name} not found in materials.yaml"
        
        material_data = materials[material_name]
        
        # Get thermalDestruction from materials.yaml
        if 'properties' not in material_data or 'thermalDestruction' not in material_data['properties']:
            return None, f"No thermalDestruction in materials.yaml for {material_name}"
        
        mat_td = material_data['properties']['thermalDestruction']
        
        # Get category ranges
        cat_ranges = get_category_thermal_ranges(categories, category)
        if not cat_ranges:
            return None, f"No category ranges for {category}"
        
        # Build normalized thermalDestruction structure
        normalized_td = {
            'point': {
                'value': mat_td['point'].get('value'),
                'unit': mat_td['point'].get('unit', '°C'),
                'min': cat_ranges['min'],
                'max': cat_ranges['max'],
                'confidence': int(mat_td['point'].get('confidence', 0) * 100) if mat_td['point'].get('confidence', 0) < 1 else int(mat_td['point'].get('confidence', 0)),
                'description': mat_td['point'].get('description', 'Thermal destruction point')
            },
            'type': mat_td.get('type', cat_ranges['type'])
        }
        
        # Find and update in materialProperties
        changes = []
        found_thermal_category = False
        
        for cat_key, cat_data in frontmatter['materialProperties'].items():
            if not isinstance(cat_data, dict) or 'properties' not in cat_data:
                continue
            
            props = cat_data['properties']
            
            # Remove old properties
            removed = []
            if 'thermalDestructionPoint' in props:
                del props['thermalDestructionPoint']
                removed.append('thermalDestructionPoint')
            if 'thermalDestructionType' in props:
                del props['thermalDestructionType']
                removed.append('thermalDestructionType')
            if 'meltingPoint' in props:
                del props['meltingPoint']
                removed.append('meltingPoint')
            
            if removed:
                changes.append(f"Removed: {', '.join(removed)}")
            
            # Add normalized thermalDestruction to thermal category
            if cat_key == 'thermal' or (cat_data.get('label') and 'thermal' in cat_data.get('label', '').lower()):
                props['thermalDestruction'] = normalized_td
                found_thermal_category = True
                changes.append(f"Added normalized thermalDestruction")
        
        if not found_thermal_category:
            return None, "No thermal category found in materialProperties"
        
        if not changes:
            return None, "No changes needed"
        
        # Write updated frontmatter
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(frontmatter, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)
        
        return changes, None
        
    except Exception as e:
        return None, f"Error: {str(e)}"

def main():
    print("=" * 70)
    print("Updating Frontmatter Files: thermalDestruction Normalization")
    print("=" * 70)
    
    # Load data
    print("\n📖 Loading data files...")
    try:
        materials = load_materials_data()
        categories = load_categories_data()
        print(f"   ✅ Loaded {len(materials)} materials")
        print(f"   ✅ Loaded {len(categories)} categories")
    except Exception as e:
        print(f"   ❌ Error loading data: {e}")
        sys.exit(1)
    
    # Find all frontmatter files
    frontmatter_dir = Path('content/components/frontmatter')
    if not frontmatter_dir.exists():
        print(f"❌ Error: {frontmatter_dir} not found")
        sys.exit(1)
    
    yaml_files = list(frontmatter_dir.glob('*.yaml'))
    print(f"\n🔍 Found {len(yaml_files)} frontmatter files")
    
    # Process each file
    print("\n🔄 Processing files...")
    print("=" * 70)
    
    updated = 0
    skipped = 0
    errors = 0
    
    for yaml_file in sorted(yaml_files):
        changes, error = update_frontmatter_file(yaml_file, materials, categories)
        
        if changes:
            updated += 1
            print(f"\n✅ {yaml_file.name}")
            for change in changes:
                print(f"   • {change}")
        elif error:
            if "No changes needed" in error or "not found in materials.yaml" in error:
                skipped += 1
                print(f"⏭️  {yaml_file.name}: {error}")
            else:
                errors += 1
                print(f"❌ {yaml_file.name}: {error}")
    
    # Summary
    print("\n" + "=" * 70)
    print("\n📊 Summary:")
    print(f"   Total files: {len(yaml_files)}")
    print(f"   ✅ Updated: {updated}")
    print(f"   ⏭️  Skipped: {skipped}")
    print(f"   ❌ Errors: {errors}")
    
    if updated > 0:
        print(f"\n✨ Successfully updated {updated} frontmatter files!")
    else:
        print(f"\n⚠️  No files were updated")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    main()
