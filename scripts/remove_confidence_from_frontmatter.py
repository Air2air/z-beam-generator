#!/usr/bin/env python3
"""
Remove confidence fields from all existing frontmatter YAML files.

This script:
1. Finds all frontmatter/*.yaml files
2. Removes all 'confidence:' fields
3. Preserves all other structure and formatting
4. Creates backups before modification
"""

import re
import shutil
from pathlib import Path
from datetime import datetime

def remove_confidence_fields(yaml_content: str) -> tuple[str, int]:
    """
    Remove all confidence: lines from YAML content.
    
    Returns:
        tuple: (modified_content, count_removed)
    """
    # Pattern to match confidence field with any indentation
    pattern = r'^(\s*)confidence:\s*\d+\s*$'
    
    lines = yaml_content.split('\n')
    modified_lines = []
    removed_count = 0
    
    for line in lines:
        if re.match(pattern, line):
            removed_count += 1
            continue  # Skip this line
        modified_lines.append(line)
    
    return '\n'.join(modified_lines), removed_count

def process_frontmatter_files():
    """Process all frontmatter YAML files."""
    
    # Get frontmatter directory
    root_dir = Path(__file__).parent.parent
    frontmatter_dir = root_dir / 'frontmatter'
    
    if not frontmatter_dir.exists():
        print(f"❌ Frontmatter directory not found: {frontmatter_dir}")
        return
    
    # Find all YAML files recursively
    yaml_files = list(frontmatter_dir.rglob('*.yaml'))
    
    if not yaml_files:
        print(f"⚠️  No YAML files found in {frontmatter_dir}")
        return
    
    print(f"🔍 Found {len(yaml_files)} frontmatter YAML files")
    print(f"📂 Processing files in: {frontmatter_dir}")
    print()
    
    total_removed = 0
    files_modified = 0
    
    # Create backup directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = root_dir / f'frontmatter_backup_{timestamp}'
    
    for yaml_file in yaml_files:
        # Read file
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Error reading {yaml_file.name}: {e}")
            continue
        
        # Remove confidence fields
        modified_content, removed_count = remove_confidence_fields(content)
        
        if removed_count > 0:
            # Create backup on first modification
            if files_modified == 0:
                print(f"💾 Creating backup: {backup_dir}")
                shutil.copytree(frontmatter_dir, backup_dir)
                print()
            
            # Write modified content
            try:
                with open(yaml_file, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                
                print(f"✅ {yaml_file.relative_to(frontmatter_dir)}: removed {removed_count} confidence fields")
                total_removed += removed_count
                files_modified += 1
            except Exception as e:
                print(f"❌ Error writing {yaml_file.name}: {e}")
    
    print()
    print("=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Files processed: {len(yaml_files)}")
    print(f"✅ Files modified: {files_modified}")
    print(f"✅ Confidence fields removed: {total_removed}")
    if files_modified > 0:
        print(f"💾 Backup created: {backup_dir}")
    print()

if __name__ == "__main__":
    print("🚀 Removing confidence fields from frontmatter YAML files")
    print("=" * 60)
    print()
    process_frontmatter_files()
