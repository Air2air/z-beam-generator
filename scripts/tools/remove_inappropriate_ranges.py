#!/usr/bin/env python3
"""
Remove category ranges that are not physically appropriate for material categories.

For example:
- oxidationResistance doesn't apply to ceramics/glass (already oxides)
- corrosionResistance doesn't apply to wood (wood rots, doesn't corrode)
- flexuralStrength less relevant for brittle semiconductors
"""

import yaml
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parents[2]
CATEGORIES_FILE = ROOT_DIR / "data" / "Categories.yaml"
BACKUP_FILE = ROOT_DIR / "data" / f"Categories.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"

# Define which properties should be removed from which categories
INAPPROPRIATE_RANGES = {
    'ceramic': ['oxidationResistance'],
    'glass': ['oxidationResistance'],
    'stone': ['corrosionResistance', 'oxidationResistance'],
    'masonry': ['corrosionResistance', 'oxidationResistance'],
    'wood': ['corrosionResistance', 'oxidationResistance'],
    'composite': ['oxidationResistance'],
    'plastic': ['oxidationResistance'],
    'semiconductor': ['flexuralStrength', 'compressiveStrength', 'corrosionResistance', 'oxidationResistance']
}


def remove_inappropriate_ranges(data: dict) -> tuple:
    """Remove inappropriate property ranges from categories."""
    removed_count = 0
    removal_log = []
    
    for category, props_to_remove in INAPPROPRIATE_RANGES.items():
        if category not in data['categories']:
            continue
        
        category_ranges = data['categories'][category].get('category_ranges', {})
        
        for prop in props_to_remove:
            if prop in category_ranges:
                # Check if it was auto-generated
                is_auto = category_ranges[prop].get('auto_generated', False)
                sample_count = category_ranges[prop].get('sample_count', 0)
                
                # Remove it
                del category_ranges[prop]
                removed_count += 1
                
                removal_log.append({
                    'category': category,
                    'property': prop,
                    'auto_generated': is_auto,
                    'sample_count': sample_count
                })
    
    return data, removed_count, removal_log


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Remove inappropriate category ranges',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without modifying files')
    parser.add_argument('--no-backup', action='store_true', help='Skip creating backup')
    
    args = parser.parse_args()
    
    print(f"\n{'=' * 70}")
    print("Remove Inappropriate Category Ranges")
    print(f"{'=' * 70}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE UPDATE'}")
    print(f"{'=' * 70}\n")
    
    # Load data
    print("📂 Loading Categories.yaml...")
    with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    print(f"  ✅ Loaded {len(data['categories'])} categories\n")
    
    # Show what will be removed
    print("🔍 Properties to be removed:\n")
    for category, props in sorted(INAPPROPRIATE_RANGES.items()):
        print(f"{category}:")
        for prop in props:
            ranges = data['categories'][category].get('category_ranges', {})
            if prop in ranges:
                is_auto = ranges[prop].get('auto_generated', False)
                sample_count = ranges[prop].get('sample_count', 0)
                status = '🤖 AUTO-GENERATED' if is_auto else '👤 MANUAL'
                print(f"  ❌ {prop} {status} (n={sample_count})")
            else:
                print(f"  ⏭️  {prop} (not present)")
        print()
    
    # Remove inappropriate ranges
    updated_data, removed_count, removal_log = remove_inappropriate_ranges(data)
    
    if not args.dry_run:
        # Backup
        if not args.no_backup:
            print("💾 Creating backup...")
            with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            print(f"  ✅ Backup saved: {BACKUP_FILE}\n")
        
        # Save
        print("📝 Updating Categories.yaml...")
        with open(CATEGORIES_FILE, 'w', encoding='utf-8') as f:
            yaml.dump(updated_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        print(f"\n{'=' * 70}")
        print("Removal Summary")
        print(f"{'=' * 70}")
        print(f"Properties removed: {removed_count} ✅\n")
        
        print("Detailed removal log:")
        for entry in removal_log:
            status = '🤖' if entry['auto_generated'] else '👤'
            print(f"  {status} {entry['category']}.{entry['property']} (n={entry['sample_count']})")
        
        print(f"\n{'=' * 70}")
        print("✅ Categories.yaml updated successfully\n")
    else:
        print(f"⚠️  DRY RUN - No files were modified")
        print(f"   Would remove {removed_count} inappropriate property ranges\n")
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
