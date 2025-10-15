#!/usr/bin/env python3
"""
Update missing min/max range values in frontmatter files from materials.yaml.

This script:
1. Reads range values from materials.yaml for each material
2. Updates frontmatter files where min/max are null but exist in materials.yaml
3. Preserves all other content unchanged
4. Provides detailed reporting of updates
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple


def load_materials_data() -> Dict[str, Any]:
    """Load materials.yaml database"""
    materials_file = Path('data/materials.yaml')
    if not materials_file.exists():
        raise FileNotFoundError("data/materials.yaml not found")
    
    with open(materials_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    return data.get('materials', {})


def find_frontmatter_file(material_name: str) -> Optional[Path]:
    """Find the frontmatter file for a material"""
    frontmatter_dir = Path('content/components/frontmatter')
    
    # Try direct slug match
    base_slug = material_name.lower().replace(' ', '-')
    files = list(frontmatter_dir.glob(f"*{base_slug[:20]}*laser-cleaning.yaml"))
    
    if files:
        return files[0]
    
    # Try abbreviation if material name has one
    if '(' in material_name and ')' in material_name:
        abbrev = material_name.split('(')[-1].replace(')', '').strip()
        files = list(frontmatter_dir.glob(f"*{abbrev.lower()}*laser-cleaning.yaml"))
        if files:
            return files[0]
    
    return None


def update_property_ranges(
    frontmatter_data: Dict[str, Any],
    material_properties: Dict[str, Any],
    replace_category_ranges: bool = False
) -> Tuple[int, List[str]]:
    """
    Update min/max values in frontmatter from materials.yaml.
    
    Args:
        frontmatter_data: Frontmatter data to update
        material_properties: Material properties from materials.yaml
        replace_category_ranges: If True, replace category ranges with material-specific ranges
    
    Returns:
        Tuple of (number of properties updated, list of updated property names)
    """
    updates_count = 0
    updated_props = []
    
    if 'materialProperties' not in frontmatter_data:
        return 0, []
    
    # Iterate through all categories in materialProperties
    for category_name, category_data in frontmatter_data['materialProperties'].items():
        if not isinstance(category_data, dict) or 'properties' not in category_data:
            continue
        
        for prop_name, prop_data in category_data['properties'].items():
            if not isinstance(prop_data, dict):
                continue
            
            # Check if materials.yaml has ranges for this property
            mat_prop = material_properties.get(prop_name)
            if not mat_prop or not isinstance(mat_prop, dict):
                continue
            
            mat_min = mat_prop.get('min')
            mat_max = mat_prop.get('max')
            
            # Skip if materials.yaml doesn't have ranges
            if mat_min is None and mat_max is None:
                continue
            
            # Check current frontmatter values
            fm_min = prop_data.get('min')
            fm_max = prop_data.get('max')
            
            # Determine if update is needed
            updated = False
            
            if replace_category_ranges:
                # Replace any existing ranges with material-specific ones
                if mat_min is not None and fm_min != mat_min:
                    prop_data['min'] = mat_min
                    updated = True
                if mat_max is not None and fm_max != mat_max:
                    prop_data['max'] = mat_max
                    updated = True
            else:
                # Only update null ranges
                if fm_min is None and mat_min is not None:
                    prop_data['min'] = mat_min
                    updated = True
                if fm_max is None and mat_max is not None:
                    prop_data['max'] = mat_max
                    updated = True
            
            if updated:
                updates_count += 1
                updated_props.append(f"{category_name}.{prop_name}")
    
    return updates_count, updated_props


def process_material(
    material_name: str,
    material_data: Dict[str, Any],
    dry_run: bool = False,
    replace_category_ranges: bool = False
) -> Tuple[bool, int, str]:
    """
    Process a single material's frontmatter file.
    
    Args:
        material_name: Name of the material
        material_data: Material data from materials.yaml
        dry_run: If True, don't write changes
        replace_category_ranges: If True, replace category ranges with material-specific ones
    
    Returns:
        Tuple of (success, updates_count, status_message)
    """
    # Find frontmatter file
    fm_file = find_frontmatter_file(material_name)
    if not fm_file:
        return False, 0, "Frontmatter file not found"
    
    # Load frontmatter
    try:
        with open(fm_file, 'r', encoding='utf-8') as f:
            fm_data = yaml.safe_load(f)
    except Exception as e:
        return False, 0, f"Failed to load: {e}"
    
    # Get material properties from materials.yaml
    material_properties = material_data.get('properties', {})
    if not material_properties:
        return False, 0, "No properties in materials.yaml"
    
    # Update ranges
    updates_count, updated_props = update_property_ranges(
        fm_data, 
        material_properties,
        replace_category_ranges
    )
    
    if updates_count == 0:
        return True, 0, "No missing ranges found"
    
    # Write back if not dry run
    if not dry_run:
        try:
            with open(fm_file, 'w', encoding='utf-8') as f:
                yaml.dump(fm_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            return True, updates_count, f"Updated {updates_count} properties"
        except Exception as e:
            return False, 0, f"Failed to write: {e}"
    else:
        return True, updates_count, f"Would update {updates_count} properties: {', '.join(updated_props[:3])}{'...' if len(updated_props) > 3 else ''}"


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Update missing min/max ranges in frontmatter from materials.yaml'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be updated without making changes'
    )
    parser.add_argument(
        '--material',
        type=str,
        help='Process only a specific material'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of materials to process'
    )
    parser.add_argument(
        '--replace-category-ranges',
        action='store_true',
        help='Replace category-wide ranges with material-specific ranges from materials.yaml'
    )
    
    args = parser.parse_args()
    
    print("🔧 Missing Range Value Updater")
    print("=" * 80)
    
    if args.dry_run:
        print("⚠️  DRY RUN MODE - No files will be modified")
        print("=" * 80)
    
    # Load materials data
    try:
        materials = load_materials_data()
        print(f"✅ Loaded {len(materials)} materials from materials.yaml\n")
    except Exception as e:
        print(f"❌ Failed to load materials.yaml: {e}")
        return 1
    
    # Filter materials if specific one requested
    if args.material:
        if args.material in materials:
            materials = {args.material: materials[args.material]}
            print(f"🎯 Processing only: {args.material}\n")
        else:
            print(f"❌ Material '{args.material}' not found in materials.yaml")
            return 1
    
    # Apply limit if specified
    if args.limit:
        materials = dict(list(materials.items())[:args.limit])
        print(f"📊 Limited to first {len(materials)} materials\n")
    
    # Process materials
    print("Processing materials...")
    print("-" * 80)
    
    total_processed = 0
    total_updated = 0
    total_failed = 0
    total_updates = 0
    
    for material_name, material_data in materials.items():
        success, updates_count, message = process_material(
            material_name, 
            material_data, 
            args.dry_run,
            args.replace_category_ranges
        )
        
        total_processed += 1
        
        if success:
            if updates_count > 0:
                total_updated += 1
                total_updates += updates_count
                print(f"✅ {material_name:40s} - {message}")
            # Skip printing materials with no updates unless verbose
        else:
            total_failed += 1
            print(f"❌ {material_name:40s} - {message}")
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"Materials processed:     {total_processed}")
    print(f"Files updated:           {total_updated}")
    print(f"Properties updated:      {total_updates}")
    print(f"Failures:                {total_failed}")
    
    if args.dry_run:
        print("\n⚠️  DRY RUN - No changes were made. Run without --dry-run to apply updates.")
    else:
        print(f"\n✅ Successfully updated {total_updates} property ranges in {total_updated} files")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
