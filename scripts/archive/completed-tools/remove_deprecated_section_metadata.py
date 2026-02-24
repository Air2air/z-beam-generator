#!/usr/bin/env python3
"""
Remove deprecated sectionMetadata field from all data YAML files.

Per .github/copilot-instructions.md:
- sectionMetadata field is deprecated
- Source data should be complete (no enrichment at export)
- All metadata should be at _section level, not nested in sectionMetadata
"""

import yaml
import sys
from pathlib import Path

def remove_section_metadata(data):
    """Recursively remove sectionMetadata from data structure."""
    if isinstance(data, dict):
        # Remove sectionMetadata key if it exists
        if 'sectionMetadata' in data:
            del data['sectionMetadata']
        
        # Recursively process all values
        for key, value in list(data.items()):
            if isinstance(value, (dict, list)):
                remove_section_metadata(value)
    
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                remove_section_metadata(item)
    
    return data

def process_file(file_path):
    """Process a single YAML file to remove sectionMetadata."""
    if not file_path.exists():
        print(f"⚠️  File not found: {file_path}")
        return 0
    
    print(f"\n📖 Processing {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Count sectionMetadata occurrences before
    yaml_str = yaml.dump(data, default_flow_style=False, allow_unicode=True)
    before_count = yaml_str.count('sectionMetadata:')
    print(f"🔍 Found {before_count} sectionMetadata fields")
    
    if before_count == 0:
        print("✅ No sectionMetadata fields found - skipping")
        return 0
    
    # Remove sectionMetadata
    print("🗑️  Removing sectionMetadata fields...")
    remove_section_metadata(data)
    
    # Count after
    yaml_str_after = yaml.dump(data, default_flow_style=False, allow_unicode=True)
    after_count = yaml_str_after.count('sectionMetadata:')
    
    # Backup original
    backup_path = file_path.with_suffix(f'.yaml.backup')
    print(f"💾 Creating backup: {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(yaml_str)
    
    # Write cleaned data
    print(f"✍️  Writing cleaned data to {file_path}...")
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    removed = before_count - after_count
    print(f"✅ Removed {removed} sectionMetadata fields")
    
    return removed

def main():
    # Data files to process
    data_files = [
        Path('data/settings/Settings.yaml'),
        Path('data/materials/Materials.yaml'),
        Path('data/compounds/Compounds.yaml'),
        Path('data/contaminants/Contaminants.yaml')
    ]
    
    total_removed = 0
    total_processed = 0
    
    print("🚀 Starting sectionMetadata cleanup across all domains...")
    
    for file_path in data_files:
        removed = process_file(file_path)
        total_removed += removed
        if file_path.exists():
            total_processed += 1
    
    print(f"\n📊 CLEANUP SUMMARY:")
    print(f"   Files processed: {total_processed}/{len(data_files)}")
    print(f"   Total sectionMetadata removed: {total_removed}")
    print("\n✅ Cleanup complete! All deprecated sectionMetadata fields removed.")

if __name__ == '__main__':
    main()
