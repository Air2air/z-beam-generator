#!/usr/bin/env python3
"""
Re-export frontmatter files with min/max ranges from Categories.yaml
Adds category-level min/max fields to properties and machine settings
"""

import yaml
from pathlib import Path
from datetime import datetime


def load_yaml(filepath):
    """Load YAML file safely"""
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)


def save_yaml(filepath, data):
    """Save YAML file with consistent formatting"""
    with open(filepath, 'w') as f:
        yaml.dump(data, f, 
                 default_flow_style=False,
                 allow_unicode=True,
                 sort_keys=False,
                 width=1000)


def get_category_ranges(categories_data, category_name):
    """Extract category ranges for a given category"""
    if not categories_data or 'categories' not in categories_data:
        return {}
    
    category = categories_data['categories'].get(category_name, {})
    return category.get('category_ranges', {})


def add_min_max_to_property(prop_value, property_name, category_ranges):
    """Add min/max fields to a property value if available in category ranges"""
    if not isinstance(prop_value, dict):
        return prop_value
    
    # Skip if already has min/max
    if 'min' in prop_value and 'max' in prop_value:
        return prop_value
    
    # Look up category range
    range_data = category_ranges.get(property_name, {})
    if not range_data or not isinstance(range_data, dict):
        return prop_value
    
    # Create updated property with min/max
    updated = dict(prop_value)
    if 'min' in range_data:
        updated['min'] = range_data['min']
    if 'max' in range_data:
        updated['max'] = range_data['max']
    
    return updated


def process_material_properties(material_props, category_ranges):
    """Add min/max to all material properties"""
    if not material_props or not isinstance(material_props, dict):
        return material_props
    
    updated_props = {}
    for category_name, category_data in material_props.items():
        if not isinstance(category_data, dict):
            updated_props[category_name] = category_data
            continue
        
        updated_category = {}
        for prop_name, prop_value in category_data.items():
            # Skip metadata fields
            if prop_name in ['label', 'description', 'percentage']:
                updated_category[prop_name] = prop_value
            else:
                updated_category[prop_name] = add_min_max_to_property(
                    prop_value, prop_name, category_ranges
                )
        
        updated_props[category_name] = updated_category
    
    return updated_props


def process_machine_settings(machine_settings, category_ranges):
    """Add min/max to machine settings"""
    if not machine_settings or not isinstance(machine_settings, dict):
        return machine_settings
    
    updated_settings = {}
    for setting_name, setting_value in machine_settings.items():
        updated_settings[setting_name] = add_min_max_to_property(
            setting_value, setting_name, category_ranges
        )
    
    return updated_settings


def export_frontmatter_with_ranges():
    """Main export function"""
    print("🚀 Starting frontmatter re-export with min/max ranges")
    print("=" * 70)
    
    # Load data files
    materials_path = Path('data/Materials.yaml')
    categories_path = Path('data/Categories.yaml')
    frontmatter_dir = Path('content/frontmatter')
    
    if not materials_path.exists():
        print("❌ Materials.yaml not found")
        return
    
    if not categories_path.exists():
        print("❌ Categories.yaml not found")
        return
    
    if not frontmatter_dir.exists():
        print("❌ Frontmatter directory not found")
        return
    
    materials_data = load_yaml(materials_path)
    categories_data = load_yaml(categories_path)
    
    materials = materials_data.get('materials', {})
    
    stats = {
        'total': 0,
        'updated': 0,
        'skipped': 0,
        'errors': 0,
        'properties_updated': 0,
        'settings_updated': 0
    }
    
    print(f"\n📊 Processing {len(materials)} materials...")
    print()
    
    for material_name, material_data in materials.items():
        stats['total'] += 1
        
        # Generate frontmatter filename
        filename = f"{material_name.lower().replace(' ', '-')}-laser-cleaning.yaml"
        filepath = frontmatter_dir / filename
        
        if not filepath.exists():
            print(f"⚠️  Skipped: {filename} (file not found)")
            stats['skipped'] += 1
            continue
        
        try:
            # Load existing frontmatter
            frontmatter_data = load_yaml(filepath)
            
            # Get category
            category = material_data.get('category', frontmatter_data.get('category'))
            if not category:
                print(f"⚠️  Skipped: {material_name} (no category)")
                stats['skipped'] += 1
                continue
            
            # Get category ranges
            category_ranges = get_category_ranges(categories_data, category)
            
            if not category_ranges:
                print(f"⚠️  Skipped: {material_name} (no category ranges for {category})")
                stats['skipped'] += 1
                continue
            
            # Track if any changes made
            changes_made = False
            
            # Update materialProperties
            if 'materialProperties' in frontmatter_data:
                original = str(frontmatter_data['materialProperties'])
                frontmatter_data['materialProperties'] = process_material_properties(
                    frontmatter_data['materialProperties'],
                    category_ranges
                )
                if str(frontmatter_data['materialProperties']) != original:
                    changes_made = True
                    stats['properties_updated'] += 1
            
            # Update machineSettings
            if 'machineSettings' in frontmatter_data:
                original = str(frontmatter_data['machineSettings'])
                frontmatter_data['machineSettings'] = process_machine_settings(
                    frontmatter_data['machineSettings'],
                    category_ranges
                )
                if str(frontmatter_data['machineSettings']) != original:
                    changes_made = True
                    stats['settings_updated'] += 1
            
            # Save if changes made
            if changes_made:
                save_yaml(filepath, frontmatter_data)
                print(f"✅ Updated: {filename}")
                stats['updated'] += 1
            else:
                stats['skipped'] += 1
        
        except Exception as e:
            print(f"❌ Error processing {material_name}: {e}")
            stats['errors'] += 1
    
    # Print summary
    print()
    print("=" * 70)
    print("📊 Export Summary:")
    print(f"  Total materials: {stats['total']}")
    print(f"  ✅ Updated: {stats['updated']}")
    print(f"  ⏭️  Skipped: {stats['skipped']}")
    print(f"  ❌ Errors: {stats['errors']}")
    print()
    print(f"  📈 Properties sections updated: {stats['properties_updated']}")
    print(f"  ⚙️  Settings sections updated: {stats['settings_updated']}")
    print()
    
    if stats['errors'] == 0:
        print("🎉 Export completed successfully!")
    else:
        print(f"⚠️  Export completed with {stats['errors']} errors")


if __name__ == "__main__":
    export_frontmatter_with_ranges()
