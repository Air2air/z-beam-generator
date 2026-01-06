#!/usr/bin/env python3
"""
Remove Materials Duplication - Fix Source Data

Eliminates duplicate section data from Materials.yaml by removing top-level keys
that duplicate data already present in relationships structure.

Problem:
- ALL 153 materials have 'operational' at top level (duplicates relationships.operational)
- 150/153 materials have 'regulatory_standards' at top level (duplicates relationships.safety.regulatory_standards)

Solution:
- Remove top-level 'operational' key (data preserved in relationships.operational)
- Remove top-level 'regulatory_standards' key (data preserved in relationships.safety.regulatory_standards)
- Keep relationships structure (has _section metadata)

Compliance: Core Principle 0.6 - Fix source data, NOT frontmatter files
"""

import yaml
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


def verify_relationships_complete(material: Dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Verify that relationships structure has all data before removing top-level keys.
    
    Returns:
        (is_complete, missing_sections): True if relationships has all data, list of missing sections
    """
    missing = []
    
    # Check for relationships.operational
    if 'operational' in material:
        if 'relationships' not in material:
            missing.append('relationships block missing')
        elif 'operational' not in material.get('relationships', {}):
            missing.append('relationships.operational missing')
        else:
            # Verify has _section metadata
            rel_operational = material['relationships']['operational']
            for section_key in rel_operational.keys():
                section = rel_operational[section_key]
                if isinstance(section, dict) and '_section' not in section:
                    missing.append(f'relationships.operational.{section_key}._section missing')
    
    # Check for relationships.safety.regulatory_standards
    if 'regulatory_standards' in material:
        if 'relationships' not in material:
            missing.append('relationships block missing')
        elif 'safety' not in material.get('relationships', {}):
            missing.append('relationships.safety missing')
        elif 'regulatory_standards' not in material.get('relationships', {}).get('safety', {}):
            missing.append('relationships.safety.regulatory_standards missing')
        else:
            # Verify has _section metadata
            reg_standards = material['relationships']['safety']['regulatory_standards']
            if isinstance(reg_standards, dict) and '_section' not in reg_standards:
                missing.append('relationships.safety.regulatory_standards._section missing')
    
    return (len(missing) == 0, missing)


def remove_duplicate_keys(material_id: str, material: Dict[str, Any], dry_run: bool = False) -> tuple[bool, list[str]]:
    """
    Remove duplicate top-level keys from a single material.
    
    If relationships structure is missing, MIGRATE data there first.
    
    Returns:
        (success, keys_removed): True if successful, list of keys removed
    """
    keys_removed = []
    keys_migrated = []
    
    # Ensure relationships block exists
    if 'relationships' not in material:
        if not dry_run:
            material['relationships'] = {}
        print(f"   ℹ️  {material_id}: Created relationships block")
    
    # Handle operational data
    if 'operational' in material:
        # Check if relationships.operational exists
        if 'operational' not in material.get('relationships', {}):
            # MIGRATE data to relationships
            if not dry_run:
                material['relationships']['operational'] = material['operational']
            keys_migrated.append('operational → relationships.operational')
            print(f"   🔄 {material_id}: Migrated operational data to relationships.operational")
        
        # Now safe to remove top-level key
        if not dry_run:
            del material['operational']
        keys_removed.append('operational')
    
    # Handle regulatory_standards data
    if 'regulatory_standards' in material:
        # Ensure safety block exists
        if 'safety' not in material.get('relationships', {}):
            if not dry_run:
                material['relationships']['safety'] = {}
        
        # Check if relationships.safety.regulatory_standards exists
        if 'regulatory_standards' not in material.get('relationships', {}).get('safety', {}):
            # MIGRATE data to relationships.safety
            if not dry_run:
                material['relationships']['safety']['regulatory_standards'] = {
                    'items': material['regulatory_standards'],
                    'presentation': 'card'
                }
            keys_migrated.append('regulatory_standards → relationships.safety.regulatory_standards')
            print(f"   🔄 {material_id}: Migrated regulatory_standards to relationships.safety")
        
        # Now safe to remove top-level key
        if not dry_run:
            del material['regulatory_standards']
        keys_removed.append('regulatory_standards')
    
    return (True, keys_removed)


def main():
    """Remove duplicate keys from all materials"""
    import sys
    
    # Parse args
    dry_run = '--dry-run' in sys.argv
    
    # File paths
    materials_file = Path('data/materials/Materials.yaml')
    backup_file = Path('data/materials/Materials.yaml.backup-duplicates')
    
    if not materials_file.exists():
        print(f"❌ ERROR: {materials_file} not found")
        return 1
    
    print("="*80)
    print("🧹 REMOVE MATERIALS DUPLICATION")
    print("="*80)
    print(f"Mode: {'DRY RUN (preview only)' if dry_run else 'LIVE (will modify files)'}")
    print()
    
    # Load Materials.yaml
    print(f"📖 Loading {materials_file}...")
    with open(materials_file) as f:
        data = yaml.safe_load(f)
    
    materials = data.get('materials', {})
    total = len(materials)
    print(f"   ✅ Loaded {total} materials\n")
    
    # Create backup (if not dry run)
    if not dry_run:
        print(f"💾 Creating backup: {backup_file.name}...")
        shutil.copy2(materials_file, backup_file)
        print(f"   ✅ Backup created\n")
    
    # Process each material
    print("🔄 Processing materials...\n")
    
    success_count = 0
    error_count = 0
    operational_removed = 0
    regulatory_removed = 0
    
    for material_id, material in materials.items():
        success, keys_removed = remove_duplicate_keys(material_id, material, dry_run)
        
        if success:
            if keys_removed:
                success_count += 1
                if 'operational' in keys_removed:
                    operational_removed += 1
                if 'regulatory_standards' in keys_removed:
                    regulatory_removed += 1
                
                mode_prefix = "[DRY RUN] " if dry_run else ""
                print(f"   {mode_prefix}✅ {material_id}: Removed {', '.join(keys_removed)}")
            # else: No duplicates to remove (skip silently)
        else:
            error_count += 1
    
    print()
    
    # Save updated file (if not dry run and no errors)
    if not dry_run:
        if error_count == 0:
            print(f"💾 Saving updated {materials_file.name}...")
            with open(materials_file, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)
            print(f"   ✅ File saved\n")
        else:
            print(f"⚠️  Skipping save due to {error_count} errors\n")
    
    # Summary
    print("="*80)
    print("📊 SUMMARY")
    print("="*80)
    print(f"   Total materials: {total}")
    print(f"   ✅ Successfully processed: {success_count}")
    print(f"   ❌ Errors: {error_count}")
    print(f"   🗑️  'operational' removed: {operational_removed}")
    print(f"   🗑️  'regulatory_standards' removed: {regulatory_removed}")
    print()
    
    if dry_run:
        print("ℹ️  This was a DRY RUN. No files were modified.")
        print("   Run without --dry-run to apply changes.")
    else:
        if error_count == 0:
            print("✅ Migration complete! All duplicate keys removed from source data.")
            print(f"   Backup available at: {backup_file}")
            print()
            print("📋 Next steps:")
            print("   1. Re-export materials domain: python3 run.py --export --domain materials")
            print("   2. Verify frontmatter files have no duplicate top-level keys")
            print("   3. Check file size reduction (~10-15% expected)")
        else:
            print(f"❌ Migration failed with {error_count} errors.")
            print("   Please review errors above and fix relationships structure first.")
    
    print("="*80)
    
    return 0 if error_count == 0 else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
