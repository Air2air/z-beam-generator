#!/usr/bin/env python3
"""
Migrate operational.industry_applications from flat list to relationship section format.
COMPLIANCE: Core Principle 0.6 - Fix source data (Materials.yaml), NOT frontmatter.

Run: python3 scripts/migrations/migrate_industry_applications_source.py
"""

import os
import re
import yaml
from pathlib import Path
import shutil

def slugify(text):
    """Convert display name to slug ID."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)  # Remove special chars
    text = re.sub(r'[-\s]+', '-', text)    # Replace spaces/dashes
    return text.strip('-')

def migrate_materials_yaml():
    """Migrate industry_applications in Materials.yaml source data."""
    
    source_file = Path('data/materials/Materials.yaml')
    backup_file = Path('data/materials/Materials.yaml.backup-industry-apps')
    
    # Create backup
    shutil.copy2(source_file, backup_file)
    print(f"✅ Backup created: {backup_file}")
    
    # Load source data
    with open(source_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    migrated_count = 0
    skipped_count = 0
    
    # Process each material
    for material_name, material_data in data['materials'].items():
        if 'relationships' not in material_data:
            continue
        
        if 'operational' not in material_data['relationships']:
            continue
        
        industry_apps = material_data['relationships']['operational'].get('industry_applications')
        
        # Already migrated (has presentation key)
        if isinstance(industry_apps, dict) and 'presentation' in industry_apps:
            skipped_count += 1
            continue
        
        # Old flat list format
        if isinstance(industry_apps, list):
            # Convert to relationship structure
            items = [{'id': slugify(name)} for name in industry_apps]
            
            material_data['relationships']['operational']['industry_applications'] = {
                'presentation': 'card',
                'items': items,
                '_section': {
                    'sectionTitle': 'Industry Applications',
                    'sectionDescription': 'Industries and sectors where this material is commonly processed with laser cleaning',
                    'icon': 'building',
                    'order': 1,
                    'variant': 'default'
                }
            }
            
            print(f"✅ Migrated: {material_name}")
            migrated_count += 1
        else:
            skipped_count += 1
    
    # Write back to source
    with open(source_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"\n📊 Migration Summary:")
    print(f"   ✅ Migrated: {migrated_count} materials")
    print(f"   ⏭️  Skipped: {skipped_count} materials")
    print(f"   📁 Total: {migrated_count + skipped_count} materials")
    print(f"\n💾 Backup: {backup_file}")
    print(f"📝 Source updated: {source_file}")
    print(f"\n⚠️  NEXT STEP: Re-export materials to generate frontmatter")
    print(f"   Command: python3 run.py --export --domain materials")

def main():
    print("🔧 Industry Applications Migration (Source Data)")
    print("=" * 60)
    print("Migrating: data/materials/Materials.yaml")
    print("Policy: Core Principle 0.6 - Fix source data, not frontmatter")
    print("=" * 60)
    print()
    
    migrate_materials_yaml()
    
    print("\n✅ Migration Complete!")

if __name__ == '__main__':
    main()
