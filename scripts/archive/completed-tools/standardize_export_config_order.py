#!/usr/bin/env python3
"""
Export Config Field Order Standardization Script
=================================================

Reorders fields in export config files to match standard schema order.
Does not change functionality - only improves readability and consistency.

Standard field order (from export/config/schema.yaml):
  1. domain
  2. source_file
  3. output_path
  4. items_key
  5. id_field
  6. filename_suffix
  7. relationship_groups
  8. section_metadata
  9. tasks
  10. field_mapping
  11. field_ordering

Usage:
    python3 scripts/tools/standardize_export_config_order.py --check
    python3 scripts/tools/standardize_export_config_order.py --fix
"""

import argparse
from pathlib import Path
from typing import Any, Dict

import yaml

# Standard field order
FIELD_ORDER = [
    'domain',
    'source_file', 
    'output_path',
    'items_key',
    'id_field',
    'filename_suffix',
    'sluggify_filenames',
    'relationship_groups',
    'section_metadata',
    'tasks',
    'field_mapping',
    'field_ordering'
]


def reorder_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Reorder config fields according to standard."""
    ordered = {}
    
    # Add fields in standard order
    for field in FIELD_ORDER:
        if field in config:
            ordered[field] = config[field]
    
    # Add any remaining fields at the end
    for field, value in config.items():
        if field not in ordered:
            ordered[field] = value
    
    return ordered


def check_config(config_path: Path) -> bool:
    """Check if config follows standard field order."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Get actual field order
    actual_fields = [f for f in config.keys() if f in FIELD_ORDER]
    expected_fields = [f for f in FIELD_ORDER if f in config]
    
    if actual_fields == expected_fields:
        print(f"✅ {config_path.name}: Fields in standard order")
        return True
    else:
        print(f"⚠️  {config_path.name}: Fields NOT in standard order")
        print(f"   Expected: {expected_fields[:5]}...")
        print(f"   Actual:   {actual_fields[:5]}...")
        return False


def fix_config(config_path: Path, dry_run: bool = False) -> None:
    """Reorder config fields to match standard."""
    with open(config_path, 'r') as f:
        original_content = f.read()
        f.seek(0)
        config = yaml.safe_load(f)
    
    # Reorder
    ordered_config = reorder_config(config)
    
    # Generate new YAML
    new_content = yaml.dump(
        ordered_config,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False
    )
    
    # Check if changed
    if original_content.strip() == new_content.strip():
        print(f"✅ {config_path.name}: Already in standard order")
        return
    
    if dry_run:
        print(f"🔍 {config_path.name}: Would reorder fields (dry run)")
        return
    
    # Write reordered config
    with open(config_path, 'w') as f:
        f.write(new_content)
    
    print(f"✅ {config_path.name}: Fields reordered")


def main():
    parser = argparse.ArgumentParser(description='Standardize export config field order')
    parser.add_argument('--check', action='store_true', help='Check field order only')
    parser.add_argument('--fix', action='store_true', help='Fix field order')
    parser.add_argument('--dry-run', action='store_true', help='Show what would change')
    args = parser.parse_args()
    
    # Find export configs
    export_dir = Path('export/config')
    configs = list(export_dir.glob('*.yaml'))
    configs = [c for c in configs if c.name != 'schema.yaml']  # Skip schema
    
    if not configs:
        print("❌ No export config files found")
        return 1
    
    print(f"Found {len(configs)} export config files\n")
    
    if args.check:
        # Check all configs
        all_ok = True
        for config_path in sorted(configs):
            if not check_config(config_path):
                all_ok = False
        
        if all_ok:
            print("\n✅ All export configs in standard field order")
            return 0
        else:
            print("\n⚠️  Some export configs need field reordering")
            print("   Run with --fix to standardize")
            return 1
    
    elif args.fix or args.dry_run:
        # Fix all configs
        for config_path in sorted(configs):
            fix_config(config_path, dry_run=args.dry_run)
        
        if args.dry_run:
            print("\n🔍 Dry run complete - run without --dry-run to apply changes")
        else:
            print("\n✅ All export configs standardized")
        return 0
    
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    exit(main())
