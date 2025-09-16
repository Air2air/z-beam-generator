#!/usr/bin/env python3
"""
Update Frontmatter Image Paths Script

Updates all existing frontmatter files to use the exact image format requirements:
- Structured images: hero: url: format
- Consistent alt text format
- Proper kebab-case filename matching
- Both hero AND micro image references
"""

import os
import re
import yaml
import frontmatter
from pathlib import Path


def extract_material_name_from_filename(filename):
    """Extract material name from filename for consistent image paths"""
    # Remove .md extension and -laser-cleaning suffix
    base_name = filename.replace('.md', '').replace('-laser-cleaning', '')
    return base_name


def create_standardized_alt_text(material_name, image_type):
    """Create standardized alt text according to the new requirements"""
    if image_type == 'hero':
        return f"{material_name} surface undergoing laser cleaning showing precise contamination removal"
    elif image_type == 'micro':
        return f"Microscopic view of {material_name} surface after laser cleaning showing detailed surface structure"
    else:
        return f"{material_name} laser cleaning {image_type} image"


def update_frontmatter_images(file_path):
    """Update a single frontmatter file with standardized image format"""
    try:
        # Load the frontmatter file
        with open(file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        # Extract material name from filename
        filename = os.path.basename(file_path)
        material_slug = extract_material_name_from_filename(filename)
        
        # Get material name from frontmatter for alt text
        material_name = post.metadata.get('name', material_slug.replace('-', ' ').title())
        
        # Update images section with standardized format
        post.metadata['images'] = {
            'hero': {
                'alt': create_standardized_alt_text(material_name, 'hero'),
                'url': f'/images/{material_slug}-laser-cleaning-hero.jpg'
            },
            'micro': {
                'alt': create_standardized_alt_text(material_name, 'micro'),
                'url': f'/images/{material_slug}-laser-cleaning-micro.jpg'
            }
        }
        
        # Write back the updated file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        
        return True, f"✅ Updated {filename}"
        
    except Exception as e:
        return False, f"❌ Error updating {filename}: {str(e)}"


def main():
    """Main function to update all frontmatter files"""
    print("🔄 UPDATING FRONTMATTER IMAGE PATHS")
    print("=" * 50)
    
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
        success, message = update_frontmatter_images(file_path)
        print(message)
        
        if success:
            success_count += 1
        else:
            error_count += 1
    
    print()
    print("📊 SUMMARY:")
    print(f"✅ Successfully updated: {success_count} files")
    print(f"❌ Errors: {error_count} files")
    print(f"📁 Total processed: {len(md_files)} files")
    
    if error_count == 0:
        print("\n🎯 ALL FILES UPDATED SUCCESSFULLY!")
        print("\n📋 STANDARDIZED FORMAT APPLIED:")
        print("   - Structured images: hero: url: format ✓")
        print("   - Consistent alt text for accessibility ✓") 
        print("   - Kebab-case filename matching ✓")
        print("   - Both hero AND micro images ✓")
    else:
        print(f"\n⚠️  {error_count} files had errors and need manual review")


if __name__ == "__main__":
    main()
