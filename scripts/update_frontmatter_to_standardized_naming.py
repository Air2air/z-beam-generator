#!/usr/bin/env python3
"""
Update Existing Frontmatter Files to Use Standardized Image Naming

Updates all existing frontmatter files to use the standardized naming convention
that matches the resolved image conflicts.
"""

import os
import yaml
import frontmatter
from pathlib import Path


def apply_standardized_naming(material_name_lower: str) -> str:
    """Apply the same standardized naming convention used in image resolution"""
    # Basic kebab-case conversion
    slug = material_name_lower.replace(" ", "-")
    
    # Apply specific naming standardizations that match the image resolution
    naming_mappings = {
        "carbon-steel": "steel",
        "galvanized-steel": "steel", 
        "tool-steel": "steel",
        "cast-iron": "iron",
        "terra-cotta": "terracotta",
        "indium-glass": "indium"
    }
    
    # Apply standardization if material matches known conflicts
    if slug in naming_mappings:
        slug = naming_mappings[slug]
        
    # Remove wood- prefix if present (matching image resolution strategy)
    if slug.startswith("wood-"):
        slug = slug[5:]  # Remove "wood-" prefix
        
    return slug


def extract_material_name_from_filename(filename):
    """Extract material name from filename for consistent image paths"""
    # Remove .md extension and -laser-cleaning suffix
    base_name = filename.replace('.md', '').replace('-laser-cleaning', '')
    
    # Convert to title case for material name
    return base_name.replace('-', ' ').title()


def update_frontmatter_file(file_path):
    """Update a single frontmatter file with standardized image naming"""
    try:
        # Load the frontmatter file
        with open(file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        # Extract material name from filename
        filename = os.path.basename(file_path)
        base_material_name = extract_material_name_from_filename(filename)
        
        # Get the original material name from frontmatter (if available)
        frontmatter_name = post.metadata.get('name', base_material_name)
        
        # Apply standardized naming to get the correct slug
        material_slug = apply_standardized_naming(frontmatter_name.lower())
        
        # Update images section with standardized naming
        if 'images' in post.metadata:
            if 'hero' in post.metadata['images']:
                post.metadata['images']['hero']['url'] = f'/images/{material_slug}-laser-cleaning-hero.jpg'
                post.metadata['images']['hero']['alt'] = f"{frontmatter_name} surface undergoing laser cleaning showing precise contamination removal"
            
            if 'micro' in post.metadata['images']:
                post.metadata['images']['micro']['url'] = f'/images/{material_slug}-laser-cleaning-micro.jpg'
                post.metadata['images']['micro']['alt'] = f"Microscopic view of {frontmatter_name} surface after laser cleaning showing detailed surface structure"
        
        # Write back the updated file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        
        return True, f"✅ Updated {filename}: {frontmatter_name} -> {material_slug}"
        
    except Exception as e:
        return False, f"❌ Error updating {filename}: {str(e)}"


def main():
    """Main function to update all frontmatter files"""
    print("🔄 UPDATING FRONTMATTER FILES TO STANDARDIZED NAMING")
    print("=" * 60)
    
    # Path to frontmatter files
    frontmatter_dir = Path("content/components/frontmatter")
    
    if not frontmatter_dir.exists():
        print(f"❌ Frontmatter directory not found: {frontmatter_dir}")
        return
    
    # Get all .md files
    md_files = list(frontmatter_dir.glob("*.md"))
    print(f"📁 Found {len(md_files)} frontmatter files to update")
    print()
    
    success_count = 0
    error_count = 0
    
    # Update each file
    for file_path in sorted(md_files):
        success, message = update_frontmatter_file(file_path)
        print(message)
        
        if success:
            success_count += 1
        else:
            error_count += 1
    
    print()
    print("📊 SUMMARY:")
    print(f"✅ Successfully updated: {success_count} files")
    if error_count > 0:
        print(f"❌ Errors encountered: {error_count} files")
    print(f"📈 Success rate: {(success_count/(success_count+error_count)*100):.1f}%")


if __name__ == "__main__":
    main()
