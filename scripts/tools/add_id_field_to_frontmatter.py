#!/usr/bin/env python3
"""
Add 'id' field to all frontmatter YAML files based on filename.

The id field will be set to the filename without extension.
This provides a consistent, file-based identifier for each item.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any


def add_id_to_yaml_file(filepath: Path) -> bool:
    """Add id field to a YAML file based on its filename."""
    try:
        # Get filename without extension as the id
        file_id = filepath.stem
        
        # Read the YAML file
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not isinstance(data, dict):
            print(f"⚠️  {filepath.name}: Not a dict, skipping")
            return False
        
        # Check if id already exists
        if 'id' in data:
            if data['id'] == file_id:
                print(f"✓  {filepath.name}: Already has correct id")
                return False
            else:
                print(f"🔄 {filepath.name}: Updating id from '{data['id']}' to '{file_id}'")
        else:
            print(f"➕ {filepath.name}: Adding id '{file_id}'")
        
        # Add/update the id field at the top level
        data['id'] = file_id
        
        # Write back to file
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, 
                     default_flow_style=False,
                     allow_unicode=True,
                     sort_keys=False,
                     width=120)
        
        return True
        
    except Exception as e:
        print(f"❌ {filepath.name}: Error - {e}")
        return False


def process_domain(domain_path: Path) -> Dict[str, int]:
    """Process all YAML files in a domain directory."""
    stats = {
        'total': 0,
        'updated': 0,
        'skipped': 0,
        'errors': 0
    }
    
    if not domain_path.exists():
        print(f"⚠️  Domain not found: {domain_path}")
        return stats
    
    yaml_files = sorted(domain_path.glob('*.yaml'))
    
    print(f"\n{'='*80}")
    print(f"Processing: {domain_path.name}")
    print(f"{'='*80}")
    
    for filepath in yaml_files:
        stats['total'] += 1
        
        try:
            if add_id_to_yaml_file(filepath):
                stats['updated'] += 1
            else:
                stats['skipped'] += 1
        except Exception as e:
            print(f"❌ {filepath.name}: {e}")
            stats['errors'] += 1
    
    return stats


def main():
    """Process all frontmatter domains."""
    frontmatter_dir = Path(__file__).parent.parent.parent / 'frontmatter'
    
    domains = ['materials', 'contaminants', 'compounds', 'settings']
    
    total_stats = {
        'total': 0,
        'updated': 0,
        'skipped': 0,
        'errors': 0
    }
    
    print("🔄 Adding 'id' fields to all frontmatter YAML files")
    print(f"Base directory: {frontmatter_dir}")
    
    for domain in domains:
        domain_path = frontmatter_dir / domain
        stats = process_domain(domain_path)
        
        for key in total_stats:
            total_stats[key] += stats[key]
        
        print(f"\n📊 {domain.capitalize()} Summary:")
        print(f"   Total files: {stats['total']}")
        print(f"   Updated: {stats['updated']}")
        print(f"   Skipped: {stats['skipped']}")
        print(f"   Errors: {stats['errors']}")
    
    print(f"\n{'='*80}")
    print("📊 OVERALL SUMMARY")
    print(f"{'='*80}")
    print(f"Total files processed: {total_stats['total']}")
    print(f"Files updated: {total_stats['updated']}")
    print(f"Files skipped (already correct): {total_stats['skipped']}")
    print(f"Errors: {total_stats['errors']}")
    print(f"\n✅ Complete!")


if __name__ == '__main__':
    main()
