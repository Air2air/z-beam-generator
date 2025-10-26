#!/usr/bin/env python3
"""
Add longName field to all regulatory standards in frontmatter files.
"""

import yaml
from pathlib import Path

# Organization name mappings
ORG_LONG_NAMES = {
    'FDA': 'Food and Drug Administration',
    'ANSI': 'American National Standards Institute',
    'IEC': 'International Electrotechnical Commission',
    'OSHA': 'Occupational Safety and Health Administration',
    'ISO': 'International Organization for Standardization',
    'EN': 'European Committee for Standardization',
    'ASTM': 'American Society for Testing and Materials',
    'EPA': 'Environmental Protection Agency',
    'Unknown': 'Unknown Organization'
}

def add_long_names_to_file(file_path: Path):
    """Add longName field to regulatory standards in a frontmatter file."""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    if not data or 'regulatoryStandards' not in data:
        return False
    
    modified = False
    for standard in data['regulatoryStandards']:
        if 'name' in standard and 'longName' not in standard:
            org_name = standard['name']
            if org_name in ORG_LONG_NAMES:
                standard['longName'] = ORG_LONG_NAMES[org_name]
                modified = True
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        return True
    
    return False

def main():
    frontmatter_dir = Path('/Users/todddunning/Desktop/Z-Beam/z-beam-generator/content/frontmatter')
    
    if not frontmatter_dir.exists():
        print(f"❌ Directory not found: {frontmatter_dir}")
        return
    
    files_updated = 0
    files_skipped = 0
    
    for yaml_file in sorted(frontmatter_dir.glob('*.yaml')):
        try:
            if add_long_names_to_file(yaml_file):
                print(f"✅ Updated: {yaml_file.name}")
                files_updated += 1
            else:
                files_skipped += 1
        except Exception as e:
            print(f"❌ Error processing {yaml_file.name}: {e}")
    
    print("\n📊 Summary:")
    print(f"  ✅ Updated: {files_updated} files")
    print(f"  ⏭️  Skipped: {files_skipped} files")

if __name__ == '__main__':
    main()
