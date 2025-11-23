#!/usr/bin/env python3
"""Add active: true field to all frontmatter YAML files."""

import yaml
from pathlib import Path

def add_active_field(file_path):
    """Add active: true field after schema_version in YAML file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Parse YAML
        data = yaml.safe_load(content)
        
        # Check if active field already exists
        if 'active' in data:
            return False  # Already has active field
        
        # Add active field after schema_version
        lines = content.split('\n')
        new_lines = []
        added = False
        
        for line in lines:
            new_lines.append(line)
            if not added and line.startswith('schema_version:'):
                new_lines.append('active: true')
                added = True
        
        # Write back
        with open(file_path, 'w') as f:
            f.write('\n'.join(new_lines))
        
        return True
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

# Find all frontmatter YAML files
frontmatter_dir = Path('frontmatter')
yaml_files = list(frontmatter_dir.rglob('*.yaml'))

print(f"Found {len(yaml_files)} frontmatter files")
print()

updated = 0
skipped = 0

for yaml_file in sorted(yaml_files):
    if add_active_field(yaml_file):
        print(f"✅ Updated: {yaml_file}")
        updated += 1
    else:
        print(f"⏭️  Skipped: {yaml_file}")
        skipped += 1

print()
print(f"📊 Summary:")
print(f"   Updated: {updated}")
print(f"   Skipped: {skipped}")
print(f"   Total: {len(yaml_files)}")
