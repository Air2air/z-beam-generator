#!/usr/bin/env python3
"""
Remove laserProcessing sections from frontmatter files.

This script consolidates laserProcessing data into machineSettings
and removes the redundant laserProcessing sections.
"""

import yaml
from pathlib import Path


def process_frontmatter_file(file_path):
    """Process a single frontmatter file to remove laserProcessing section"""
    print(f"Processing {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into frontmatter and markdown content
        parts = content.split('---', 2)
        if len(parts) < 3:
            print(f"  ⚠️  No frontmatter found in {file_path}")
            return False
            
        before_yaml = parts[0]
        yaml_content = parts[1]
        after_yaml = parts[2]
        
        # Parse YAML
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            print(f"  ❌ YAML parsing error in {file_path}: {e}")
            return False
        
        # Check if laserProcessing exists
        if 'laserProcessing' not in data:
            print("  ✅ No laserProcessing section found")
            return False
        
        # Remove laserProcessing section
        data.pop('laserProcessing')
        print("  🗑️  Removed laserProcessing section")
        
        # Write back the updated file
        new_yaml_content = yaml.dump(data, default_flow_style=False, allow_unicode=True, width=120, indent=2)
        new_content = f"{before_yaml}---\n{new_yaml_content.strip()}\n---{after_yaml}"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        print(f"  ✅ Updated {file_path}")
        return True
        
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")
        return False


def main():
    """Main function to process all frontmatter files"""
    frontmatter_dir = Path("content/components/frontmatter")
    
    if not frontmatter_dir.exists():
        print(f"❌ Frontmatter directory not found: {frontmatter_dir}")
        return
    
    # Find all markdown files
    md_files = list(frontmatter_dir.glob("*.md"))
    print(f"Found {len(md_files)} frontmatter files")
    
    updated_count = 0
    
    for file_path in md_files:
        if process_frontmatter_file(file_path):
            updated_count += 1
    
    print("\n🎉 Processing complete!")
    print(f"✅ Updated {updated_count} files")
    print(f"📁 Total files processed: {len(md_files)}")


if __name__ == "__main__":
    main()