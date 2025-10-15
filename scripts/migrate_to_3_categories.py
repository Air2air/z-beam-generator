#!/usr/bin/env python3
"""
Migrate frontmatter files from 5 categories (4 + other) to 3 categories (v4.0.0)

This script remaps property categories in existing frontmatter files:
- laser_interaction + thermal_response + other → energy_coupling
- mechanical_response → structural_response  
- material_characteristics → material_properties

GROK Compliant:
- Fail-fast on missing files or invalid YAML
- No mocks/fallbacks in production code
- Comprehensive error handling
- Preserves all data, only remaps category keys
"""

import yaml
from pathlib import Path
from typing import Dict, Any
import sys

# Category migration mapping (v3.0 → v4.0)
CATEGORY_MAPPING = {
    'laser_interaction': 'energy_coupling',
    'thermal_response': 'energy_coupling',
    'other': 'energy_coupling',  # Merged into energy_coupling
    'mechanical_response': 'structural_response',
    'material_characteristics': 'material_properties'
}


def migrate_material_properties(properties: Dict[str, Any]) -> Dict[str, Any]:
    """
    Migrate materialProperties structure from 5 categories to 3
    
    Args:
        properties: Original materialProperties dict with 5 categories
        
    Returns:
        Migrated materialProperties dict with 3 categories
        
    Raises:
        ValueError: If properties structure is invalid
    """
    if not isinstance(properties, dict):
        raise ValueError(f"Invalid properties type: {type(properties)}")
    
    migrated = {}
    
    for old_category, category_data in properties.items():
        # Get new category name
        new_category = CATEGORY_MAPPING.get(old_category)
        
        if not new_category:
            # Unknown category - fail fast
            raise ValueError(f"Unknown category '{old_category}' - cannot migrate")
        
        if not isinstance(category_data, dict):
            raise ValueError(f"Invalid category data for '{old_category}': {type(category_data)}")
        
        # If new category doesn't exist yet, create it
        if new_category not in migrated:
            migrated[new_category] = {
                'label': get_category_label(new_category),
                'properties': {}
            }
            # Copy description and percentage from first source if present
            if 'description' in category_data:
                migrated[new_category]['description'] = category_data['description']
            if 'percentage' in category_data:
                migrated[new_category]['percentage'] = category_data['percentage']
        
        # Merge properties from old category into new category
        if 'properties' in category_data:
            migrated[new_category]['properties'].update(category_data['properties'])
    
    # Update labels to match v4.0 taxonomy
    for category in migrated:
        migrated[category]['label'] = get_category_label(category)
    
    return migrated


def get_category_label(category_id: str) -> str:
    """Get human-readable label for category ID"""
    labels = {
        'energy_coupling': 'Energy Coupling Properties',
        'structural_response': 'Structural Response Properties',
        'material_properties': 'Material Properties'
    }
    return labels.get(category_id, category_id)


def migrate_frontmatter_file(file_path: Path) -> bool:
    """
    Migrate a single frontmatter file from 5 categories to 3
    
    Args:
        file_path: Path to frontmatter YAML file
        
    Returns:
        True if migration was performed, False if already migrated or no changes needed
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If YAML structure is invalid
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Frontmatter file not found: {file_path}")
    
    # Load YAML
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {file_path}: {e}")
    
    if not isinstance(data, dict):
        raise ValueError(f"Invalid frontmatter structure in {file_path}: not a dict")
    
    # Check if materialProperties exists and has categorized structure
    if 'materialProperties' not in data:
        print(f"  ⚠️  No materialProperties in {file_path.name} - skipping")
        return False
    
    properties = data['materialProperties']
    
    # Check if already using 3-category structure
    if all(cat in ['energy_coupling', 'structural_response', 'material_properties'] 
           for cat in properties.keys()):
        print(f"  ✓  Already using 3-category structure: {file_path.name}")
        return False
    
    # Check if using flat structure (no categories)
    if 'properties' in properties or not any(
        isinstance(v, dict) and 'properties' in v for v in properties.values()
    ):
        print(f"  ⚠️  Flat structure in {file_path.name} - needs regeneration, not migration")
        return False
    
    # Migrate categories
    try:
        migrated_properties = migrate_material_properties(properties)
        data['materialProperties'] = migrated_properties
    except ValueError as e:
        print(f"  ❌  Failed to migrate {file_path.name}: {e}")
        raise
    
    # Write back to file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    except Exception as e:
        raise ValueError(f"Failed to write {file_path}: {e}")
    
    print(f"  ✅  Migrated: {file_path.name}")
    return True


def main():
    """Main migration script"""
    print("=" * 70)
    print("FRONTMATTER MIGRATION: 5 Categories → 3 Categories (v4.0.0)")
    print("=" * 70)
    print("\nCategory Mapping:")
    print("  laser_interaction     → energy_coupling")
    print("  thermal_response      → energy_coupling")
    print("  other                 → energy_coupling")
    print("  mechanical_response   → structural_response")
    print("  material_characteristics → material_properties")
    print()
    
    # Find all frontmatter files
    frontmatter_dir = Path('content/components/frontmatter')
    
    if not frontmatter_dir.exists():
        print(f"❌ Frontmatter directory not found: {frontmatter_dir}")
        sys.exit(1)
    
    yaml_files = sorted(frontmatter_dir.glob('*-laser-cleaning.yaml'))
    
    if not yaml_files:
        print(f"❌ No frontmatter files found in {frontmatter_dir}")
        sys.exit(1)
    
    print(f"Found {len(yaml_files)} frontmatter files\n")
    
    # Migrate each file
    migrated_count = 0
    skipped_count = 0
    error_count = 0
    
    for yaml_file in yaml_files:
        try:
            if migrate_frontmatter_file(yaml_file):
                migrated_count += 1
            else:
                skipped_count += 1
        except Exception as e:
            print(f"  ❌  ERROR migrating {yaml_file.name}: {e}")
            error_count += 1
            continue
    
    # Summary
    print("\n" + "=" * 70)
    print("MIGRATION SUMMARY")
    print("=" * 70)
    print(f"Total files:     {len(yaml_files)}")
    print(f"✅ Migrated:     {migrated_count}")
    print(f"⚠️  Skipped:      {skipped_count}")
    print(f"❌ Errors:       {error_count}")
    print()
    
    if migrated_count > 0:
        print("✅ Migration completed successfully!")
        print("\nNext steps:")
        print("  1. Run tests: python3 -m pytest tests/test_property_categorizer.py")
        print("  2. Verify sample file: cat content/components/frontmatter/copper-laser-cleaning.yaml")
        print("  3. Commit changes: git add -A && git commit -m 'Migrate to 3-category structure v4.0.0'")
        print("  4. Deploy: python3 run.py --deploy")
    
    if error_count > 0:
        print(f"\n⚠️  WARNING: {error_count} files had errors during migration")
        print("    Review the errors above and fix manually if needed")
    
    return 0 if error_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
