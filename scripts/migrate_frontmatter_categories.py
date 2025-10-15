#!/usr/bin/env python3
"""
Migrate frontmatter YAML files from old categories to physics-based categories v3.0.0

This script updates materialProperties categories in-place without regenerating content.

Old Categories → New Physics-Based Categories:
- thermal → thermal_response
- mechanical → mechanical_response  
- optical_laser → laser_interaction
- physical_structural → material_characteristics
- surface → material_characteristics
- electrical → material_characteristics
- chemical → material_characteristics
- environmental → material_characteristics
- compositional → material_characteristics
- general → material_characteristics

Usage:
    python3 migrate_frontmatter_categories.py [--dry-run]
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, Any

# Category mapping: old → new
CATEGORY_MAPPING = {
    'thermal': 'thermal_response',
    'mechanical': 'mechanical_response',
    'optical_laser': 'laser_interaction',
    'physical_structural': 'material_characteristics',
    'surface': 'material_characteristics',
    'electrical': 'material_characteristics',
    'chemical': 'material_characteristics',
    'environmental': 'material_characteristics',
    'compositional': 'material_characteristics',
    'general': 'material_characteristics',
}

# Updated category metadata
CATEGORY_METADATA = {
    'laser_interaction': {
        'label': 'Laser Interaction Properties',
        'description': 'First-order photon coupling: how laser energy enters the material vs. reflects away',
        'percentage': 16.4,
        'physics_stage': 'Energy Absorption'
    },
    'thermal_response': {
        'label': 'Thermal Response Properties',
        'description': 'Heat propagation and dissipation: how absorbed energy distributes and when phase transitions occur',
        'percentage': 25.5,
        'physics_stage': 'Energy Dissipation'
    },
    'mechanical_response': {
        'label': 'Mechanical Response Properties',
        'description': 'Physical reaction to thermal stress: how material responds structurally to rapid heating',
        'percentage': 18.2,
        'physics_stage': 'Material Response'
    },
    'material_characteristics': {
        'label': 'Material Characteristics',
        'description': 'Intrinsic properties affecting secondary cleaning outcomes: surface finish, contaminant adhesion, and process efficiency',
        'percentage': 40.0,
        'physics_stage': 'Supporting Properties'
    }
}


def migrate_material_properties(material_props: Dict[str, Any]) -> Dict[str, Any]:
    """Migrate materialProperties from old to new category structure"""
    migrated = {}
    
    for old_cat, cat_data in material_props.items():
        # Skip 'other' category - keep as-is
        if old_cat == 'other':
            migrated[old_cat] = cat_data
            continue
            
        # Map to new category
        new_cat = CATEGORY_MAPPING.get(old_cat, old_cat)
        
        # If category already exists in migrated (merging multiple old cats), merge properties
        if new_cat in migrated:
            # Merge properties from this category into existing
            if 'properties' in cat_data and 'properties' in migrated[new_cat]:
                migrated[new_cat]['properties'].update(cat_data['properties'])
        else:
            # Create new category entry
            migrated[new_cat] = {
                'label': CATEGORY_METADATA[new_cat]['label'],
                'description': CATEGORY_METADATA[new_cat]['description'],
                'percentage': CATEGORY_METADATA[new_cat]['percentage'],
                'properties': cat_data.get('properties', {})
            }
    
    return migrated


def migrate_frontmatter_file(file_path: Path, dry_run: bool = False) -> bool:
    """Migrate a single frontmatter YAML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data or 'materialProperties' not in data:
            return False
        
        # Check if already migrated
        current_cats = set(data['materialProperties'].keys())
        old_cats = set(CATEGORY_MAPPING.keys())
        
        if not current_cats.intersection(old_cats):
            # Already migrated (no old categories present)
            return False
        
        # Migrate the categories
        data['materialProperties'] = migrate_material_properties(data['materialProperties'])
        
        if not dry_run:
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing {file_path.name}: {e}")
        return False


def main():
    dry_run = '--dry-run' in sys.argv
    
    if dry_run:
        print("🔍 DRY RUN MODE - No files will be modified\n")
    
    # Find all frontmatter YAML files
    frontmatter_dir = Path('content/components/frontmatter')
    
    if not frontmatter_dir.exists():
        print(f"❌ Directory not found: {frontmatter_dir}")
        return 1
    
    yaml_files = list(frontmatter_dir.glob('*-laser-cleaning.yaml'))
    
    print(f"📂 Found {len(yaml_files)} frontmatter files\n")
    
    migrated_count = 0
    skipped_count = 0
    
    for yaml_file in sorted(yaml_files):
        was_migrated = migrate_frontmatter_file(yaml_file, dry_run)
        
        if was_migrated:
            migrated_count += 1
            status = "🔄 Would migrate" if dry_run else "✅ Migrated"
            print(f"{status}: {yaml_file.name}")
        else:
            skipped_count += 1
    
    print(f"\n{'=' * 60}")
    print(f"📊 MIGRATION SUMMARY")
    print(f"{'=' * 60}")
    print(f"{'Would migrate' if dry_run else 'Migrated'}: {migrated_count} files")
    print(f"Skipped (already migrated): {skipped_count} files")
    print(f"Total: {len(yaml_files)} files")
    
    if dry_run:
        print(f"\n💡 Run without --dry-run to apply changes")
    else:
        print(f"\n✅ Migration complete!")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
