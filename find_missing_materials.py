#!/usr/bin/env python3
"""
Find Missing Materials in Index
Identifies which frontmatter files don't have corresponding index entries
"""

import yaml
from pathlib import Path

def find_missing_materials():
    """Find materials that have frontmatter files but no index entries"""
    materials_path = Path("data/Materials.yaml")
    frontmatter_dir = Path("content/components/frontmatter")
    
    # Load Materials.yaml
    with open(materials_path, 'r') as f:
        data = yaml.safe_load(f)
    
    # Get materials from index
    index_materials = set(data.get('material_index', {}).keys())
    print(f"Materials in index: {len(index_materials)}")
    
    # Get materials from frontmatter files
    frontmatter_files = list(frontmatter_dir.glob("*.md"))
    frontmatter_materials = set()
    
    for file_path in frontmatter_files:
        # Extract material name from filename
        filename = file_path.name
        if filename.endswith('-laser-cleaning.md'):
            material_name = filename.replace('-laser-cleaning.md', '').replace('-', ' ').title()
            frontmatter_materials.add(material_name)
    
    print(f"Materials in frontmatter: {len(frontmatter_materials)}")
    
    # Find missing materials
    missing_from_index = frontmatter_materials - index_materials
    missing_from_frontmatter = index_materials - frontmatter_materials
    
    print(f"\n🔍 ANALYSIS:")
    print(f"Missing from index ({len(missing_from_index)} materials):")
    for material in sorted(missing_from_index):
        print(f"  - {material}")
    
    print(f"\nMissing from frontmatter ({len(missing_from_frontmatter)} materials):")
    for material in sorted(missing_from_frontmatter):
        print(f"  - {material}")
    
    return missing_from_index, missing_from_frontmatter

if __name__ == "__main__":
    missing_from_index, missing_from_frontmatter = find_missing_materials()