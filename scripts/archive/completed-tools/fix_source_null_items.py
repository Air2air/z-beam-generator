#!/usr/bin/env python3
"""
Fix Null/Empty Items in Source Data

Removes:
- items: [null]
- items: []

From source YAML files (data/*.yaml)
"""

import yaml
from pathlib import Path
from typing import Any, Dict, List, Tuple
import argparse


def clean_relationship_items(data: Dict[str, Any], path: str = "") -> Tuple[int, int]:
    """
    Recursively clean null and empty items from relationship structures.
    If items is removed, remove the entire field.
    
    Returns:
        (items_with_null_removed, empty_arrays_removed)
    """
    items_removed = 0
    arrays_removed = 0
    keys_to_delete = []
    
    if isinstance(data, dict):
        for key, value in list(data.items()):
            new_path = f"{path}.{key}" if path else key
            
            # Check if this is an items field
            if key == 'items':
                parent_path = path
                if value is None or (isinstance(value, list) and (len(value) == 0 or (len(value) == 1 and value[0] is None))):
                    # items is null/empty/[null] - remove the PARENT field entirely
                    # Mark the parent for deletion by returning a signal
                    keys_to_delete.append(key)
                    if value is None or (isinstance(value, list) and len(value) == 0):
                        arrays_removed += 1
                        print(f"  Removed field with empty items at {path}")
                    else:
                        items_removed += 1
                        print(f"  Removed field with items: [null] at {path}")
                    # Signal to remove parent
                    return items_removed, arrays_removed, True  # True = remove parent
            elif isinstance(value, dict):
                # Recurse into nested structures
                removed, empty, should_delete = clean_relationship_items(value, new_path)
                items_removed += removed
                arrays_removed += empty
                if should_delete:
                    # Child dict had null items, so remove this entire key
                    keys_to_delete.append(key)
        
        # Remove marked keys
        for key in keys_to_delete:
            del data[key]
    
    return items_removed, arrays_removed, False  # False = don't remove parent


def process_source_file(file_path: Path, dry_run: bool = True) -> Tuple[int, int]:
    """Process a single source data file."""
    print(f"\n📄 Processing: {file_path.name}")
    
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)
    
    # Determine domain key
    if 'materials' in data:
        domain_key = 'materials'
    elif 'contaminants' in data:
        domain_key = 'contaminants'
    elif 'settings' in data:
        domain_key = 'settings'
    elif 'compounds' in data:
        domain_key = 'compounds'
    else:
        print(f"  ⚠️  No recognized domain key found")
        return 0, 0
    
    items_dict = data[domain_key]
    total_items = 0
    total_arrays = 0
    
    for item_id, item_data in items_dict.items():
        if 'relationships' not in item_data:
            continue
        
        items, arrays, _ = clean_relationship_items(item_data['relationships'], f"{item_id}.relationships")
        total_items += items
        total_arrays += arrays
    
    if total_items > 0 or total_arrays > 0:
        print(f"  ✅ Cleaned: {total_items} null items, {total_arrays} empty arrays")
        
        if not dry_run:
            # Save the cleaned data
            with open(file_path, 'w') as f:
                yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            print(f"  💾 Saved changes to {file_path.name}")
    else:
        print(f"  ✅ No issues found")
    
    return total_items, total_arrays


def main():
    parser = argparse.ArgumentParser(description='Fix null/empty items in source data files')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without saving')
    args = parser.parse_args()
    
    print("=" * 80)
    print("FIX NULL/EMPTY ITEMS IN SOURCE DATA")
    print("=" * 80)
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be saved")
    else:
        print("⚠️  LIVE MODE - Changes will be applied to source files")
    print()
    
    source_files = [
        Path('data/compounds/Compounds.yaml'),
        Path('data/settings/Settings.yaml'),
    ]
    
    grand_total_items = 0
    grand_total_arrays = 0
    
    for file_path in source_files:
        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue
        
        items, arrays = process_source_file(file_path, args.dry_run)
        grand_total_items += items
        grand_total_arrays += arrays
    
    print()
    print("=" * 80)
    print(f"✅ TOTAL: {grand_total_items} null items + {grand_total_arrays} empty arrays fixed")
    print("=" * 80)
    
    if args.dry_run:
        print("\nTo apply these changes, run:")
        print("  python3 scripts/tools/fix_source_null_items.py")
    else:
        print("\n✅ Changes saved! Next steps:")
        print("  1. Re-export affected domains:")
        print("     python3 run.py --export --domain compounds")
        print("     python3 run.py --export --domain settings")
        print("  2. Verify fixes with null scan")
        print("  3. Commit changes")


if __name__ == '__main__':
    main()
