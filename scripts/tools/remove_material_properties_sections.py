#!/usr/bin/env python3
"""
Remove materialProperties sections from frontmatter files.

This script consolidates materialProperties data into properties
and removes the redundant materialProperties sections.
"""

import yaml
from pathlib import Path


def merge_material_properties_to_properties(data):
    """Merge materialProperties into properties structure"""
    if 'materialProperties' not in data:
        return False
    
    material_props = data.pop('materialProperties')
    
    # Initialize properties if it doesn't exist
    if 'properties' not in data:
        data['properties'] = {}
    
    properties = data['properties']
    
    # Merge chemical properties
    if 'chemical' in material_props:
        chemical = material_props['chemical']
        if 'formula' in chemical:
            properties['formula'] = chemical['formula']
        if 'symbol' in chemical:
            properties['symbol'] = chemical['symbol']
    
    # Merge physical properties
    if 'physical' in material_props:
        physical = material_props['physical']
        if 'density' in physical:
            properties['density'] = physical['density']
        if 'densityUnit' in physical:
            properties['densityUnit'] = physical['densityUnit']
    
    # Merge thermal properties
    if 'thermal' in material_props:
        thermal = material_props['thermal']
        if 'thermalConductivity' in thermal:
            properties['thermalConductivity'] = thermal['thermalConductivity']
        if 'thermalConductivityUnit' in thermal:
            properties['thermalConductivityUnit'] = thermal['thermalConductivityUnit']
    
    return True


def process_frontmatter_file(file_path):
    """Process a single frontmatter file to remove materialProperties section"""
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
        
        # Check if materialProperties exists and merge it
        if not merge_material_properties_to_properties(data):
            print("  ✅ No materialProperties section found")
            return False
        
        print("  🔄 Merged materialProperties into properties")
        
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