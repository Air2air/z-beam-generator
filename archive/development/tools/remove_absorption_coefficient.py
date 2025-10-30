#!/usr/bin/env python3
"""
Remove absorptionCoefficient property completely from the system.

This removes it from:
1. Categories.yaml (propertyCategories)
2. All frontmatter files
3. Any category ranges (if present)
"""

import yaml
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parents[2]
CATEGORIES_FILE = ROOT_DIR / "data" / "Categories.yaml"
FRONTMATTER_DIR = ROOT_DIR / "content" / "components" / "frontmatter"
BACKUP_DIR = ROOT_DIR / "backups" / f"remove_absorption_coefficient_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def backup_files(files_to_backup):
    """Create backups of files before modification."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    for file_path in files_to_backup:
        if file_path.exists():
            backup_path = BACKUP_DIR / file_path.name
            import shutil
            shutil.copy2(file_path, backup_path)
    
    print(f"✅ Backed up {len(files_to_backup)} files to {BACKUP_DIR}")


def remove_from_categories():
    """Remove absorptionCoefficient from Categories.yaml."""
    with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    removed_from = []
    
    # Remove from propertyCategories
    prop_cats = data.get('propertyCategories', {}).get('categories', {})
    for cat_name, cat_data in prop_cats.items():
        if 'properties' in cat_data and 'absorptionCoefficient' in cat_data['properties']:
            cat_data['properties'].remove('absorptionCoefficient')
            removed_from.append(f'propertyCategories.{cat_name}')
    
    # Remove from category_ranges (if exists)
    for cat_name, cat_data in data.get('categories', {}).items():
        if 'category_ranges' in cat_data and 'absorptionCoefficient' in cat_data['category_ranges']:
            del cat_data['category_ranges']['absorptionCoefficient']
            removed_from.append(f'categories.{cat_name}.category_ranges')
    
    # Save
    with open(CATEGORIES_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    return removed_from


def remove_from_frontmatter():
    """Remove absorptionCoefficient from all frontmatter files."""
    removed_count = 0
    files_modified = []
    
    for fm_file in FRONTMATTER_DIR.glob('*.yaml'):
        with open(fm_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        modified = False
        
        # Check materialProperties
        for cat_name, cat_data in data.get('materialProperties', {}).items():
            if 'properties' in cat_data and 'absorptionCoefficient' in cat_data['properties']:
                del cat_data['properties']['absorptionCoefficient']
                modified = True
                removed_count += 1
        
        if modified:
            with open(fm_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            files_modified.append(fm_file.name)
    
    return removed_count, files_modified


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Remove absorptionCoefficient from entire system'
    )
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without modifying files')
    parser.add_argument('--no-backup', action='store_true', help='Skip creating backup')
    
    args = parser.parse_args()
    
    print(f"\n{'=' * 70}")
    print("Remove absorptionCoefficient from System")
    print(f"{'=' * 70}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE UPDATE'}")
    print(f"{'=' * 70}\n")
    
    # Preview what will be removed from Categories.yaml
    print("📂 Checking Categories.yaml...\n")
    
    with open(CATEGORIES_FILE, 'r') as f:
        categories_data = yaml.safe_load(f)
    
    prop_cats = categories_data.get('propertyCategories', {}).get('categories', {})
    found_in_cats = []
    for cat_name, cat_data in prop_cats.items():
        if 'properties' in cat_data and 'absorptionCoefficient' in cat_data['properties']:
            found_in_cats.append(cat_name)
    
    if found_in_cats:
        print(f"Found in propertyCategories: {', '.join(found_in_cats)}")
    else:
        print("Not found in propertyCategories")
    
    # Check category_ranges
    found_in_ranges = []
    for cat_name, cat_data in categories_data.get('categories', {}).items():
        if 'category_ranges' in cat_data and 'absorptionCoefficient' in cat_data['category_ranges']:
            found_in_ranges.append(cat_name)
    
    if found_in_ranges:
        print(f"Found in category_ranges: {', '.join(found_in_ranges)}")
    else:
        print("Not found in category_ranges")
    
    print()
    
    # Preview frontmatter files
    print("📂 Checking frontmatter files...\n")
    
    fm_count = 0
    for fm_file in FRONTMATTER_DIR.glob('*.yaml'):
        with open(fm_file, 'r') as f:
            data = yaml.safe_load(f)
        
        for cat_name, cat_data in data.get('materialProperties', {}).items():
            if 'properties' in cat_data and 'absorptionCoefficient' in cat_data['properties']:
                fm_count += 1
                break
    
    print(f"Found in {fm_count} frontmatter files")
    print()
    
    if not args.dry_run:
        # Create backups
        if not args.no_backup:
            print("💾 Creating backups...\n")
            files_to_backup = [CATEGORIES_FILE] + list(FRONTMATTER_DIR.glob('*.yaml'))
            backup_files(files_to_backup)
            print()
        
        # Remove from Categories.yaml
        print("🗑️  Removing from Categories.yaml...")
        removed_from_cats = remove_from_categories()
        if removed_from_cats:
            for location in removed_from_cats:
                print(f"  ✅ Removed from {location}")
        else:
            print("  ⏭️  Not found in Categories.yaml")
        print()
        
        # Remove from frontmatter
        print("🗑️  Removing from frontmatter files...")
        removed_count, files_modified = remove_from_frontmatter()
        print(f"  ✅ Removed from {removed_count} frontmatter files")
        print()
        
        # Summary
        print(f"{'=' * 70}")
        print("Removal Summary")
        print(f"{'=' * 70}")
        print(f"Categories.yaml locations: {len(removed_from_cats)}")
        print(f"Frontmatter files modified: {len(files_modified)}")
        print(f"Total removals: {len(removed_from_cats) + removed_count}")
        print(f"{'=' * 70}\n")
        print("✅ absorptionCoefficient completely removed from system\n")
        
    else:
        print("⚠️  DRY RUN - No files were modified")
        print(f"   Would remove from {len(found_in_cats)} propertyCategories")
        print(f"   Would remove from {len(found_in_ranges)} category_ranges")
        print(f"   Would remove from {fm_count} frontmatter files\n")
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
