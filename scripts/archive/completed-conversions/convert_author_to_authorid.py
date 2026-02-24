#!/usr/bin/env python3
"""
Convert full author objects to authorId in all domain YAML files.
V6 Schema Normalization.
"""

import argparse
import yaml
from pathlib import Path

def convert_file(filepath):
    """Convert author objects to authorId in a YAML file."""
    print(f"Processing {filepath}...")
    
    with open(filepath, 'r') as f:
        data = yaml.safe_load(f)
    
    changes = 0
    domain_key = filepath.stem.lower().replace('s', '')  # Materials -> material
    if domain_key not in data:
        domain_key = filepath.stem.lower()  # Try plural form
    
    if domain_key not in data:
        print(f"  ⚠️  Could not find domain key in {filepath}")
        return 0
    
    items = data[domain_key]
    
    for item_id, item_data in items.items():
        if 'author' in item_data and isinstance(item_data['author'], dict):
            author_id = item_data['author'].get('id')
            if author_id:
                item_data['authorId'] = author_id
                del item_data['author']
                changes += 1
    
    if changes > 0:
        with open(filepath, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        print(f"  ✅ Converted {changes} items")
    else:
        print(f"  ℹ️  No changes needed")
    
    return changes

def main():
    parser = argparse.ArgumentParser(
        description="Convert author objects to authorId in domain YAML files"
    )
    parser.add_argument(
        '--domain',
        choices=['materials', 'contaminants', 'compounds', 'settings', 'applications', 'all'],
        default='all',
        help='Domain to convert (default: all)'
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    base_dir = repo_root / 'data'
    domain_files = {
        'materials': base_dir / 'materials' / 'Materials.yaml',
        'contaminants': base_dir / 'contaminants' / 'Contaminants.yaml',
        'compounds': base_dir / 'compounds' / 'Compounds.yaml',
        'settings': base_dir / 'settings' / 'Settings.yaml',
        'applications': base_dir / 'applications' / 'Applications.yaml',
    }

    if args.domain == 'all':
        files = list(domain_files.values())
    else:
        files = [domain_files[args.domain]]

    total_changes = 0
    for filepath in files:
        if filepath.exists():
            total_changes += convert_file(filepath)
        else:
            print(f"⚠️  File not found: {filepath}")

    print(f"\n✅ Total conversions: {total_changes}")
    print("📋 V6 Schema normalization complete")

if __name__ == '__main__':
    main()
