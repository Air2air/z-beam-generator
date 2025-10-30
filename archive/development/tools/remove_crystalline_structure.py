#!/usr/bin/env python3
"""
Remove crystallineStructure property from the entire system.

Removes from:
1. Categories.yaml - propertyCategories
2. Any category_ranges that might have it (though none currently exist)
"""

import yaml
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parents[2]
CATEGORIES_FILE = ROOT_DIR / "data" / "Categories.yaml"
BACKUP_FILE = ROOT_DIR / "data" / f"Categories.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"


def remove_crystalline_structure(data: dict) -> dict:
    """Remove crystallineStructure from Categories.yaml."""
    
    removed_count = 0
    
    # Remove from propertyCategories
    for cat_name, cat_data in data['propertyCategories']['categories'].items():
        if 'properties' in cat_data and 'crystallineStructure' in cat_data['properties']:
            cat_data['properties'].remove('crystallineStructure')
            removed_count += 1
            print(f'  ✅ Removed from propertyCategories.{cat_name}.properties')
    
    # Remove from category_ranges (if it exists anywhere)
    for category in data['categories'].values():
        if 'category_ranges' in category and 'crystallineStructure' in category['category_ranges']:
            del category['category_ranges']['crystallineStructure']
            removed_count += 1
            print(f'  ✅ Removed from {category}.category_ranges')
    
    return data, removed_count


def main():
    print(f"\n{'=' * 70}")
    print("Remove crystallineStructure Property")
    print(f"{'=' * 70}\n")
    
    # Load data
    print("📂 Loading Categories.yaml...")
    with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    print(f"  ✅ Loaded\n")
    
    # Backup
    print("💾 Creating backup...")
    with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"  ✅ Backup saved: {BACKUP_FILE}\n")
    
    # Remove crystallineStructure
    print("🗑️  Removing crystallineStructure...")
    updated_data, removed_count = remove_crystalline_structure(data)
    
    # Save
    print("\n📝 Updating Categories.yaml...")
    with open(CATEGORIES_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(updated_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"\n{'=' * 70}")
    print(f"Summary: Removed crystallineStructure from {removed_count} locations")
    print(f"{'=' * 70}\n")
    print("✅ Categories.yaml updated successfully")
    print("\n⚠️  Next step: Regenerate frontmatter with `python3 run.py --deploy`\n")
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
