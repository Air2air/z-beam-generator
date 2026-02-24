#!/usr/bin/env python3
"""
Normalize all YAML field names to camelCase convention.

This script converts snake_case field names to camelCase throughout the source data,
excluding special fields that start with underscore (like _section).

Usage:
    python3 scripts/tools/normalize_yaml_field_names.py --dry-run  # Preview changes
    python3 scripts/tools/normalize_yaml_field_names.py           # Apply changes
"""

import yaml
import re
from pathlib import Path
import tempfile
import shutil
import argparse


def snake_to_camel(snake_str):
    """Convert snake_case to camelCase."""
    components = snake_str.split('_')
    # Keep first component lowercase, capitalize the rest
    return components[0] + ''.join(x.title() for x in components[1:])


def should_normalize(key):
    """Check if a field name should be normalized."""
    # Skip fields starting with _ (like _section)
    if key.startswith('_'):
        return False
    # Only normalize if contains underscore
    if '_' not in key:
        return False
    return True


def normalize_dict_keys(obj, changes_log):
    """Recursively normalize dictionary keys from snake_case to camelCase."""
    if not isinstance(obj, dict):
        return obj
    
    new_dict = {}
    for key, value in obj.items():
        # Normalize the key if needed
        new_key = key
        if should_normalize(key):
            new_key = snake_to_camel(key)
            if new_key != key:
                changes_log.append(f"  {key} → {new_key}")
        
        # Recursively process the value
        if isinstance(value, dict):
            new_dict[new_key] = normalize_dict_keys(value, changes_log)
        elif isinstance(value, list):
            new_dict[new_key] = [
                normalize_dict_keys(item, changes_log) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            new_dict[new_key] = value
    
    return new_dict


def normalize_yaml_file(file_path, dry_run=False):
    """Normalize field names in a YAML file."""
    print(f"\nProcessing: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    changes_log = []
    normalized_data = normalize_dict_keys(data, changes_log)
    
    # Remove duplicates and sort
    unique_changes = sorted(set(changes_log))
    
    if unique_changes:
        print(f"  Found {len(unique_changes)} field name changes:")
        for change in unique_changes[:20]:  # Show first 20
            print(change)
        if len(unique_changes) > 20:
            print(f"  ... and {len(unique_changes) - 20} more")
    else:
        print("  ✅ No snake_case fields found")
        return 0
    
    if not dry_run:
        # Create backup
        backup_path = f"{file_path}.backup"
        shutil.copy2(file_path, backup_path)
        print(f"  📦 Backup created: {backup_path}")
        
        # Save atomically
        temp_fd, temp_path = tempfile.mkstemp(
            suffix='.yaml',
            dir=Path(file_path).parent,
            text=True
        )
        try:
            with open(temp_fd, 'w', encoding='utf-8') as f:
                yaml.dump(
                    normalized_data,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                    width=1000  # Prevent line wrapping
                )
            shutil.move(temp_path, file_path)
            print(f"  ✅ Saved: {file_path}")
        except Exception as e:
            Path(temp_path).unlink(missing_ok=True)
            raise e
    
    return len(unique_changes)


def main():
    parser = argparse.ArgumentParser(description='Normalize YAML field names to camelCase')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without applying')
    args = parser.parse_args()
    
    # Files to process
    files = [
        'data/materials/Materials.yaml',
        'data/contaminants/Contaminants.yaml',
        'data/compounds/Compounds.yaml',
        'data/settings/Settings.yaml'
    ]
    
    print('=' * 80)
    if args.dry_run:
        print('DRY RUN - PREVIEW MODE (no changes will be saved)')
    else:
        print('NORMALIZING YAML FIELD NAMES TO CAMELCASE')
    print('=' * 80)
    
    total_changes = 0
    for file_path in files:
        if Path(file_path).exists():
            changes = normalize_yaml_file(file_path, args.dry_run)
            total_changes += changes
        else:
            print(f"\n⚠️  File not found: {file_path}")
    
    print('\n' + '=' * 80)
    if args.dry_run:
        print(f'PREVIEW COMPLETE: {total_changes} total field names would be normalized')
        print('Run without --dry-run to apply changes')
    else:
        print(f'✅ NORMALIZATION COMPLETE: {total_changes} field names normalized')
    print('=' * 80)


if __name__ == '__main__':
    main()
