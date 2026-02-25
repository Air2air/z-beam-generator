#!/usr/bin/env python3
"""
Remove slug fields from all source data YAML files.

This script removes:
1. Top-level slug fields from material/contaminant/compound/settings entries
2. slug fields from relationship entries (related_materials, etc.)

Per FRONTMATTER_FORMATTING_SPECIFICATION.md Phase 1:
- slug fields should NOT exist in source data
- IDs are sufficient for identification
"""

import yaml
from pathlib import Path
from typing import Dict, Any


def remove_slugs_from_dict(data: Dict[str, Any], path: str = "") -> int:
    """
    Recursively remove all 'slug' fields from dictionary.
    
    Args:
        data: Dictionary to process
        path: Current path for logging
        
    Returns:
        Number of slug fields removed
    """
    count = 0
    
    if not isinstance(data, dict):
        return 0
    
    # Remove top-level slug if exists
    if 'slug' in data:
        del data['slug']
        count += 1
        print(f"  ✅ Removed slug from {path}")
    
    # Recursively process nested dictionaries
    for key, value in list(data.items()):
        new_path = f"{path}.{key}" if path else key
        
        if isinstance(value, dict):
            count += remove_slugs_from_dict(value, new_path)
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    count += remove_slugs_from_dict(item, f"{new_path}[{i}]")
    
    return count


def process_yaml_file(filepath: Path) -> int:
    """Process a single YAML file to remove slugs."""
    print(f"\n📄 Processing: {filepath.name}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data:
            print(f"  ⚠️  Empty file, skipping")
            return 0
        
        count = remove_slugs_from_dict(data)
        
        if count > 0:
            # Write back
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            print(f"  💾 Removed {count} slug fields, file updated")
        else:
            print(f"  ✅ No slug fields found")
        
        return count
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return 0


def main():
    """Remove slug fields from all source data files."""
    base_dir = Path(__file__).parent.parent / 'data'
    
    # Files to process
    files = [
        base_dir / 'materials' / 'Materials.yaml',
        base_dir / 'contaminants' / 'Contaminants.yaml',
        base_dir / 'compounds' / 'Compounds.yaml',
        base_dir / 'settings' / 'Settings.yaml',
    ]
    
    total_removed = 0
    files_modified = 0
    
    print("="*80)
    print("🧹 REMOVING SLUG FIELDS FROM SOURCE DATA")
    print("="*80)
    
    for filepath in files:
        if filepath.exists():
            removed = process_yaml_file(filepath)
            if removed > 0:
                files_modified += 1
                total_removed += removed
        else:
            print(f"\n⚠️  File not found: {filepath}")
    
    print("\n" + "="*80)
    print(f"✅ CLEANUP COMPLETE")
    print(f"   Files modified: {files_modified}")
    print(f"   Total slugs removed: {total_removed}")
    print("="*80)


if __name__ == '__main__':
    main()
