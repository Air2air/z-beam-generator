#!/usr/bin/env python3
"""
Fix Null/Empty Relationship Items in Source Data

Problem: Many relationship fields have items with null ids or empty arrays.
This script removes these invalid entries from source YAML files.

Usage:
    python3 scripts/tools/fix_null_relationship_items.py --dry-run
    python3 scripts/tools/fix_null_relationship_items.py
"""

import argparse
import yaml
from pathlib import Path
from typing import Dict, Any, List


def clean_relationship_items(data: Dict[str, Any], path: str = "") -> tuple[int, int]:
    """
    Remove null items and empty arrays from relationship fields.
    
    Returns:
        (items_removed, arrays_removed) counts
    """
    items_removed = 0
    arrays_removed = 0
    
    if not isinstance(data, dict):
        return items_removed, arrays_removed
    
    # Check if this dict has 'items' field
    if 'items' in data:
        items = data['items']
        if items is None:
            # Remove null items field entirely
            del data['items']
            arrays_removed += 1
            print(f"  Removed null items field: {path}")
        elif isinstance(items, list):
            if len(items) == 0:
                # Remove empty items array
                del data['items']
                arrays_removed += 1
                print(f"  Removed empty items array: {path}")
            else:
                # Filter out null items or items with null id
                original_count = len(items)
                filtered = []
                for item in items:
                    if item is None:
                        items_removed += 1
                    elif isinstance(item, dict) and item.get('id') is None:
                        items_removed += 1
                    else:
                        filtered.append(item)
                
                if len(filtered) < original_count:
                    if len(filtered) == 0:
                        # All items were null, remove the array
                        del data['items']
                        arrays_removed += 1
                        print(f"  Removed empty items (all null): {path}")
                    else:
                        data['items'] = filtered
                        print(f"  Cleaned {original_count - len(filtered)} null items: {path}")
    
    # Recursively process nested dicts
    for key, value in list(data.items()):
        if isinstance(value, dict):
            removed, empty = clean_relationship_items(value, f"{path}.{key}" if path else key)
            items_removed += removed
            arrays_removed += empty
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    removed, empty = clean_relationship_items(item, f"{path}.{key}[{i}]" if path else f"{key}[{i}]")
                    items_removed += removed
                    arrays_removed += empty
    
    return items_removed, arrays_removed


def process_source_file(file_path: Path, dry_run: bool = False) -> tuple[int, int]:
    """Process a single source YAML file."""
    print(f"\n📄 Processing: {file_path.name}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Get the main items key (materials, contaminants, settings, compounds)
    items_key = None
    for key in ['materials', 'contaminants', 'settings', 'compounds']:
        if key in data:
            items_key = key
            break
    
    if not items_key:
        print("  ⚠️  No recognized items key found")
        return 0, 0
    
    total_items_removed = 0
    total_arrays_removed = 0
    
    # Process each item
    items = data[items_key]
    for item_id, item_data in items.items():
        if 'relationships' in item_data:
            removed, empty = clean_relationship_items(item_data['relationships'], f"{item_id}.relationships")
            total_items_removed += removed
            total_arrays_removed += empty
    
    # Save if changes were made and not dry-run
    if (total_items_removed > 0 or total_arrays_removed > 0) and not dry_run:
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=1000)
        print(f"  ✅ Saved changes")
    
    return total_items_removed, total_arrays_removed


def main():
    parser = argparse.ArgumentParser(description='Fix null/empty relationship items in source data')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without saving')
    args = parser.parse_args()
    
    # Source data files
    source_files = [
        Path('data/materials/Materials.yaml'),
        Path('data/contaminants/Contaminants.yaml'),
        Path('data/settings/Settings.yaml'),
        Path('data/compounds/Compounds.yaml'),
    ]
    
    print("="*80)
    print("FIX NULL/EMPTY RELATIONSHIP ITEMS")
    print("="*80)
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be saved\n")
    
    total_items = 0
    total_arrays = 0
    
    for file_path in source_files:
        if file_path.exists():
            items, arrays = process_source_file(file_path, args.dry_run)
            total_items += items
            total_arrays += arrays
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Null items removed: {total_items}")
    print(f"Empty arrays removed: {total_arrays}")
    print(f"Total fixes: {total_items + total_arrays}")
    
    if args.dry_run:
        print("\n🔍 This was a dry run. Run without --dry-run to apply changes.")
    else:
        print("\n✅ Changes saved to source files.")
        print("📦 Run --export for each domain to regenerate frontmatter.")


if __name__ == '__main__':
    main()
