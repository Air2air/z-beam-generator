#!/usr/bin/env python3
"""
Add 'name' field to industry_applications items (Phase 2 migration).
Converts slugified IDs back to display names.

COMPLIANCE: docs/INDUSTRY_APPLICATIONS_MIGRATION_JAN5_2026.md (updated requirements)
Run: python3 scripts/migrations/add_name_to_industry_applications.py
"""

import yaml
from pathlib import Path
import shutil

def id_to_display_name(slug_id):
    """Convert slugified ID back to display name."""
    # Replace hyphens with spaces and title case each word
    return ' '.join(word.capitalize() for word in slug_id.split('-'))

def add_names_to_materials_yaml():
    """Add 'name' field to all industry_applications items."""
    
    source_file = Path('data/materials/Materials.yaml')
    backup_file = Path('data/materials/Materials.yaml.backup-add-names')
    
    # Create backup
    shutil.copy2(source_file, backup_file)
    print(f"✅ Backup created: {backup_file}")
    
    # Load source data
    with open(source_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    updated_count = 0
    skipped_count = 0
    
    # Process each material
    for material_name, material_data in data['materials'].items():
        if 'relationships' not in material_data:
            continue
        
        if 'operational' not in material_data['relationships']:
            continue
        
        industry_apps = material_data['relationships']['operational'].get('industry_applications')
        
        # Check if it's the relationship structure format
        if not isinstance(industry_apps, dict) or 'items' not in industry_apps:
            skipped_count += 1
            continue
        
        # Check if items already have 'name' field
        if industry_apps['items'] and 'name' in industry_apps['items'][0]:
            skipped_count += 1
            continue
        
        # Add 'name' field to each item
        for item in industry_apps['items']:
            if 'id' in item and 'name' not in item:
                item['name'] = id_to_display_name(item['id'])
        
        print(f"✅ Added names: {material_name}")
        updated_count += 1
    
    # Write back to source
    with open(source_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"\n📊 Migration Summary:")
    print(f"   ✅ Updated: {updated_count} materials")
    print(f"   ⏭️  Skipped: {skipped_count} materials")
    print(f"   📁 Total: {updated_count + skipped_count} materials")
    print(f"\n💾 Backup: {backup_file}")
    print(f"📝 Source updated: {source_file}")
    print(f"\n⚠️  NEXT STEP: Re-export materials to regenerate frontmatter")
    print(f"   Command: python3 run.py --export --domain materials")

def main():
    print("🔧 Industry Applications Phase 2: Add Display Names")
    print("=" * 60)
    print("Adding 'name' field to all items in data/materials/Materials.yaml")
    print("Requirement: Each item needs both 'id' (slug) AND 'name' (display)")
    print("=" * 60)
    print()
    
    add_names_to_materials_yaml()
    
    print("\n✅ Phase 2 Migration Complete!")

if __name__ == '__main__':
    main()
