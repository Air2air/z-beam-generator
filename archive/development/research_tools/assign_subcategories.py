#!/usr/bin/env python3
"""
Assign subcategories to materials in Materials.yaml

This script reads the subcategory material lists from Categories.yaml and
assigns the appropriate subcategory field to each material in Materials.yaml.

Usage:
    python3 scripts/research_tools/assign_subcategories.py
    python3 scripts/research_tools/assign_subcategories.py --dry-run
"""

import sys
import yaml
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def assign_subcategories(dry_run=False):
    """Assign subcategories to all materials based on Categories.yaml definitions"""
    
    materials_path = project_root / "data" / "Materials.yaml"
    categories_path = project_root / "data" / "Categories.yaml"
    
    print("🔄 Assigning Subcategories to Materials")
    print("=" * 80)
    
    # Load both files
    print("\n📂 Loading files...")
    with open(materials_path, 'r') as f:
        materials_data = yaml.safe_load(f)
    print(f"  ✅ Materials.yaml: {len(materials_data['materials'])} materials")
    
    with open(categories_path, 'r') as f:
        categories_data = yaml.safe_load(f)
    print(f"  ✅ Categories.yaml: {len(categories_data['categories'])} categories")
    
    # Build subcategory mapping: {material_name: (category, subcategory)}
    subcategory_map = {}
    
    for cat_name, cat_data in categories_data['categories'].items():
        subcats = cat_data.get('subcategories', {})
        for subcat_name, subcat_data in subcats.items():
            materials_list = subcat_data.get('materials', [])
            for material_name in materials_list:
                subcategory_map[material_name] = (cat_name, subcat_name)
    
    print(f"\n📊 Subcategory mapping created: {len(subcategory_map)} materials")
    
    # Assign subcategories
    print("\n🔧 Assigning subcategories...")
    
    stats = {
        'assigned': 0,
        'skipped_already_assigned': 0,
        'skipped_no_subcategory': 0,
        'updated': 0,
        'errors': 0
    }
    
    for material_name, material_data in materials_data['materials'].items():
        current_subcat = material_data.get('subcategory')
        
        if material_name in subcategory_map:
            category, expected_subcat = subcategory_map[material_name]
            
            if current_subcat == expected_subcat:
                stats['skipped_already_assigned'] += 1
                continue
            elif current_subcat and current_subcat != expected_subcat:
                print(f"  🔄 {material_name}: {current_subcat} → {expected_subcat}")
                material_data['subcategory'] = expected_subcat
                stats['updated'] += 1
            else:
                print(f"  ✅ {material_name}: → {expected_subcat}")
                material_data['subcategory'] = expected_subcat
                stats['assigned'] += 1
        else:
            stats['skipped_no_subcategory'] += 1
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 ASSIGNMENT SUMMARY")
    print("=" * 80)
    print(f"  ✅ Newly assigned: {stats['assigned']}")
    print(f"  🔄 Updated: {stats['updated']}")
    print(f"  ⏭️  Already assigned: {stats['skipped_already_assigned']}")
    print(f"  ⚠️  No subcategory available: {stats['skipped_no_subcategory']}")
    print(f"  ❌ Errors: {stats['errors']}")
    print("")
    
    total_changes = stats['assigned'] + stats['updated']
    
    if dry_run:
        print("🔍 DRY RUN - No changes written to file")
        print(f"   Would have made {total_changes} changes")
        return 0
    
    # Write back to file
    if total_changes > 0:
        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = materials_path.parent / f"Materials.yaml.backup.{timestamp}"
        
        print(f"💾 Creating backup: {backup_path.name}")
        with open(backup_path, 'w') as f:
            yaml.dump(materials_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        # Write updated data
        print(f"✍️  Writing changes to Materials.yaml...")
        with open(materials_path, 'w') as f:
            yaml.dump(materials_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        print(f"✅ Successfully updated {total_changes} materials")
    else:
        print("ℹ️  No changes needed")
    
    return 0


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Assign subcategories to materials based on Categories.yaml'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    
    args = parser.parse_args()
    
    exit_code = assign_subcategories(dry_run=args.dry_run)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
