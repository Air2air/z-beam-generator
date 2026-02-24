#!/usr/bin/env python3
"""
Add _section metadata to materialCharacteristics and laserMaterialInteraction
sections for all materials that are missing it.

This transforms the legacy 'description' field into proper _section metadata
with sectionTitle, sectionDescription, icon, order, and variant.

Usage:
    python3 scripts/backfill/add_material_properties_section_metadata.py [--dry-run]
"""

import yaml
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def generate_section_title(material_name: str, section_type: str) -> str:
    """Generate a descriptive section title."""
    if section_type == 'materialCharacteristics':
        return f"{material_name}'s Core Properties"
    elif section_type == 'laserMaterialInteraction':
        return "Laser Interaction Behavior"
    return section_type.replace('_', ' ').title()


def add_section_metadata(materials_data: dict, dry_run: bool = False) -> dict:
    """Add _section metadata to materials missing it."""
    
    updated_count = 0
    skipped_count = 0
    
    for material_id, material in materials_data['materials'].items():
        properties = material.get('properties', {})
        if not properties:
            print(f"⚠️  {material_id}: No properties section")
            continue
        
        material_name = material.get('name', material_id.replace('-laser-cleaning', '').replace('-', ' ').title())
        
        # Process materialCharacteristics
        mat_chars = properties.get('materialCharacteristics', {})
        if mat_chars and isinstance(mat_chars, dict):
            if '_section' not in mat_chars:
                description = mat_chars.get('description', f"Core physical properties of {material_name}")
                
                mat_chars['_section'] = {
                    'sectionTitle': generate_section_title(material_name, 'materialCharacteristics'),
                    'sectionDescription': description,
                    'icon': 'wrench',
                    'order': 50,
                    'variant': 'default'
                }
                
                updated_count += 1
                if not dry_run:
                    print(f"✅ {material_id}: Added _section to materialCharacteristics")
                else:
                    print(f"🔍 [DRY-RUN] {material_id}: Would add _section to materialCharacteristics")
                    print(f"   Title: {mat_chars['_section']['sectionTitle']}")
                    print(f"   Description: {description[:80]}...")
            else:
                skipped_count += 1
        
        # Process laserMaterialInteraction
        laser_interaction = properties.get('laserMaterialInteraction', {})
        if laser_interaction and isinstance(laser_interaction, dict):
            if '_section' not in laser_interaction:
                description = laser_interaction.get('description', f"How {material_name} responds to laser cleaning")
                
                laser_interaction['_section'] = {
                    'sectionTitle': generate_section_title(material_name, 'laserMaterialInteraction'),
                    'sectionDescription': description,
                    'icon': 'zap',
                    'order': 60,
                    'variant': 'default'
                }
                
                if not dry_run:
                    print(f"✅ {material_id}: Added _section to laserMaterialInteraction")
                else:
                    print(f"🔍 [DRY-RUN] {material_id}: Would add _section to laserMaterialInteraction")
    
    return materials_data, updated_count, skipped_count


def main():
    dry_run = '--dry-run' in sys.argv
    
    materials_file = project_root / 'data' / 'materials' / 'Materials.yaml'
    
    print("=" * 80)
    print("ADD _SECTION METADATA TO MATERIAL PROPERTIES")
    print("=" * 80)
    print(f"Source: {materials_file}")
    print(f"Mode: {'DRY-RUN' if dry_run else 'LIVE UPDATE'}")
    print()
    
    # Load materials data
    print("📖 Loading materials data...")
    with open(materials_file, 'r', encoding='utf-8') as f:
        materials_data = yaml.safe_load(f)
    
    print(f"✅ Loaded {len(materials_data['materials'])} materials")
    print()
    
    # Add _section metadata
    print("🔧 Adding _section metadata...")
    materials_data, updated_count, skipped_count = add_section_metadata(materials_data, dry_run)
    
    # Save if not dry-run
    if not dry_run and updated_count > 0:
        print()
        print(f"💾 Saving updated data to {materials_file}...")
        with open(materials_file, 'w', encoding='utf-8') as f:
            yaml.dump(materials_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print("✅ Saved successfully")
    
    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Materials updated: {updated_count}")
    print(f"Materials skipped (already had _section): {skipped_count}")
    print(f"Total materials: {len(materials_data['materials'])}")
    
    if dry_run:
        print()
        print("ℹ️  This was a dry-run. Run without --dry-run to apply changes.")
    
    return 0 if updated_count > 0 or dry_run else 1


if __name__ == '__main__':
    sys.exit(main())
