#!/usr/bin/env python3
"""
Migrate Data YAML IDs to Slug Format
=====================================

Converts Materials.yaml and Contaminants.yaml to use slug-based IDs
that match frontmatter filenames.

BEFORE:
    Materials.yaml:     "Aluminum" → material data
    Contaminants.yaml:  "carbon-buildup" → contaminant data
    
AFTER:
    Materials.yaml:     "aluminum-laser-cleaning" → material data
    Contaminants.yaml:  "carbon-buildup-contamination" → contaminant data

This aligns data file IDs with frontmatter file IDs for consistency.
"""

import yaml
import re
from pathlib import Path
from typing import Dict, Any


def title_to_slug(title: str) -> str:
    """Convert title case to slug format"""
    # Convert to lowercase
    slug = title.lower()
    # Replace spaces with hyphens
    slug = slug.replace(' ', '-')
    # Remove special characters except hyphens
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    # Remove multiple consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    return slug


def migrate_materials_yaml(materials_file: Path, backup: bool = True) -> Dict[str, str]:
    """
    Migrate Materials.yaml to use slug-based IDs.
    
    Returns:
        Dict mapping old IDs to new IDs
    """
    print(f"📖 Reading {materials_file}...")
    with open(materials_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Create backup
    if backup:
        backup_file = materials_file.with_suffix('.yaml.backup')
        print(f"💾 Creating backup: {backup_file}")
        with open(backup_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    # Migrate IDs
    id_mapping = {}
    old_materials = data['materials']
    new_materials = {}
    
    print(f"🔄 Migrating {len(old_materials)} material IDs...")
    
    for old_id, material_data in old_materials.items():
        # Generate new slug-based ID
        new_id = title_to_slug(old_id) + '-laser-cleaning'
        id_mapping[old_id] = new_id
        
        # Update the id field within the material data
        if 'id' in material_data:
            material_data['id'] = new_id
        
        # Store with new key
        new_materials[new_id] = material_data
        
        print(f"  ✓ '{old_id}' → '{new_id}'")
    
    # Replace materials dict
    data['materials'] = new_materials
    
    # Write updated file
    print(f"💾 Writing updated {materials_file}...")
    with open(materials_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"✅ Materials.yaml migration complete!")
    return id_mapping


def migrate_contaminants_yaml(contaminants_file: Path, backup: bool = True) -> Dict[str, str]:
    """
    Migrate Contaminants.yaml to use slug-based IDs with -contamination suffix.
    
    Returns:
        Dict mapping old IDs to new IDs
    """
    print(f"\n📖 Reading {contaminants_file}...")
    with open(contaminants_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Create backup
    if backup:
        backup_file = contaminants_file.with_suffix('.yaml.backup')
        print(f"💾 Creating backup: {backup_file}")
        with open(backup_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    # Migrate IDs
    id_mapping = {}
    old_contaminants = data['contamination_patterns']
    new_contaminants = {}
    
    print(f"🔄 Migrating {len(old_contaminants)} contaminant IDs...")
    
    for old_id, contaminant_data in old_contaminants.items():
        # Add -contamination suffix if not already present
        if old_id.endswith('-contamination'):
            new_id = old_id
        else:
            new_id = old_id + '-contamination'
        
        id_mapping[old_id] = new_id
        
        # Update the id field within the contaminant data
        if 'id' in contaminant_data:
            contaminant_data['id'] = new_id
        
        # Store with new key
        new_contaminants[new_id] = contaminant_data
        
        if old_id != new_id:
            print(f"  ✓ '{old_id}' → '{new_id}'")
    
    # Replace contamination_patterns dict
    data['contamination_patterns'] = new_contaminants
    
    # Write updated file
    print(f"💾 Writing updated {contaminants_file}...")
    with open(contaminants_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"✅ Contaminants.yaml migration complete!")
    return id_mapping


def main():
    """Run the migration"""
    base_dir = Path(__file__).parent.parent.parent
    
    print("=" * 80)
    print("DATA YAML ID MIGRATION TO SLUG FORMAT")
    print("=" * 80)
    print()
    print("This script will:")
    print("  1. Backup Materials.yaml and Contaminants.yaml")
    print("  2. Convert IDs to match frontmatter filename format")
    print("  3. Update all internal id fields")
    print()
    
    # Migrate materials
    materials_file = base_dir / 'data' / 'materials' / 'Materials.yaml'
    materials_mapping = migrate_materials_yaml(materials_file)
    
    # Migrate contaminants
    contaminants_file = base_dir / 'data' / 'contaminants' / 'Contaminants.yaml'
    contaminants_mapping = migrate_contaminants_yaml(contaminants_file)
    
    print()
    print("=" * 80)
    print("MIGRATION SUMMARY")
    print("=" * 80)
    print(f"✅ Materials:     {len(materials_mapping)} IDs migrated")
    print(f"✅ Contaminants:  {len(contaminants_mapping)} IDs migrated")
    print()
    print("📝 Backups created:")
    print(f"   • {materials_file.with_suffix('.yaml.backup')}")
    print(f"   • {contaminants_file.with_suffix('.yaml.backup')}")
    print()
    print("🎯 Next steps:")
    print("   1. Run tests: pytest tests/test_centralized_architecture.py -v")
    print("   2. Verify: All 17 tests should pass")
    print("   3. Update any code that references old IDs")
    print()


if __name__ == '__main__':
    main()
