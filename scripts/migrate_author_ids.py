#!/usr/bin/env python3
"""
Migrate Materials.yaml author fields from full objects to ID-only

Replaces:
  author:
    country: Italy
    expertise: Laser-Based Additive Manufacturing
    id: 2
    image: /images/author/alessandro-moretti.jpg
    name: Alessandro Moretti
    sex: m
    title: Ph.D.

With:
  author:
    id: 2

This makes authors_registry.py the single source of truth.
"""

import yaml
from pathlib import Path
import sys

def migrate_materials_yaml():
    """Slim down author fields to just ID in Materials.yaml"""
    
    materials_file = Path(__file__).resolve().parents[1] / "materials" / "data" / "Materials.yaml"
    
    print(f"🔄 Loading {materials_file}")
    with open(materials_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    materials = data.get('materials', {})
    migrated_count = 0
    
    for material_name, material_data in materials.items():
        if 'author' in material_data:
            author_field = material_data['author']
            
            # If author is already just an ID or {id: N}, skip
            if isinstance(author_field, int):
                print(f"  ✓ {material_name}: already migrated (int)")
                continue
            elif isinstance(author_field, dict):
                if len(author_field) == 1 and 'id' in author_field:
                    print(f"  ✓ {material_name}: already migrated (dict with id only)")
                    continue
                elif 'id' in author_field:
                    # Has ID plus other fields - slim it down
                    author_id = author_field['id']
                    material_data['author'] = {'id': author_id}
                    migrated_count += 1
                    print(f"  ✅ {material_name}: slimmed to ID {author_id}")
                else:
                    print(f"  ⚠️  {material_name}: author has no 'id' field - SKIPPING")
            else:
                print(f"  ⚠️  {material_name}: unexpected author type {type(author_field)} - SKIPPING")
    
    if migrated_count > 0:
        # Backup original
        backup_file = materials_file.parent / f"Materials_backup_before_author_migration.yaml"
        print(f"\n💾 Creating backup: {backup_file}")
        with open(backup_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        # Write migrated version
        print(f"📝 Writing migrated Materials.yaml")
        with open(materials_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        print(f"\n✅ Migration complete!")
        print(f"   Migrated: {migrated_count} materials")
        print(f"   Backup saved: {backup_file}")
        print(f"\n📋 Next steps:")
        print(f"   1. Run: python3 run.py --deploy")
        print(f"   2. Verify frontmatter has full author data from registry")
    else:
        print(f"\n✅ No migration needed - all materials already using ID-only format")
    
    return migrated_count

if __name__ == "__main__":
    try:
        count = migrate_materials_yaml()
        sys.exit(0 if count >= 0 else 1)
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
