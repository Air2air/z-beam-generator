#!/usr/bin/env python3
"""
Comprehensive image mismatch analysis.
Identifies all naming convention issues between frontmatter and actual images.
"""
import os
import re
from pathlib import Path

def extract_image_paths_from_frontmatter(file_path):
    """Extract hero and micro image paths from frontmatter file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract frontmatter between --- markers
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return None, None, "No frontmatter found"
        
        frontmatter_content = match.group(1)
        
        # Extract hero and micro image URLs with better regex to handle multiline YAML
        images_section = re.search(r'images:\s*\n(.*?)(?=\n\w|\Z)', frontmatter_content, re.DOTALL)
        if not images_section:
            return None, None, "No images section found"
        
        images_content = images_section.group(1)
        
        # Extract URLs from hero and micro sections
        hero_match = re.search(r'hero:\s*\n.*?url:\s*([^\n]+)', images_content, re.DOTALL)
        micro_match = re.search(r'micro:\s*\n.*?url:\s*([^\n]+)', images_content, re.DOTALL)
        
        hero_url = hero_match.group(1).strip() if hero_match else None
        micro_url = micro_match.group(1).strip() if micro_match else None
        
        return hero_url, micro_url, None
    except Exception as e:
        return None, None, f"Error reading file: {e}"

def get_actual_images(images_dir):
    """Get list of actual image files in the public/images directory."""
    images_path = Path(images_dir)
    if not images_path.exists():
        return set(), f"Images directory not found: {images_dir}"
    
    # Get all .jpg files
    image_files = set()
    for img_file in images_path.glob("*.jpg"):
        # Convert to the path format used in frontmatter (/images/filename.jpg)
        image_files.add(f"/images/{img_file.name}")
    
    return image_files, None

def find_similar_images(missing_image, actual_images):
    """Find images with similar names that might be the correct match."""
    missing_filename = missing_image.split('/')[-1]
    material_name = missing_filename.replace('-laser-cleaning-hero.jpg', '').replace('-laser-cleaning-micro.jpg', '')
    image_type = 'hero' if 'hero' in missing_filename else 'micro'
    
    # Look for variations
    possible_matches = []
    
    for actual_image in actual_images:
        actual_filename = actual_image.split('/')[-1]
        
        # Check if it contains the material name and image type
        if material_name in actual_filename and image_type in actual_filename:
            possible_matches.append(actual_image)
        
        # Check for category-prefixed versions (e.g., wood-walnut, carbon-steel)
        if material_name in actual_filename and image_type in actual_filename:
            possible_matches.append(actual_image)
    
    return possible_matches

def analyze_comprehensive():
    """Comprehensive analysis of image mismatches."""
    frontmatter_dir = Path('content/components/frontmatter')
    images_dir = '/Users/todddunning/Desktop/Z-Beam/z-beam-test-push/public/images'
    
    if not frontmatter_dir.exists():
        print(f"❌ Frontmatter directory not found: {frontmatter_dir}")
        return
    
    actual_images, images_error = get_actual_images(images_dir)
    if images_error:
        print(f"❌ {images_error}")
        return
    
    print(f"📁 Found {len(actual_images)} actual images in {images_dir}")
    print("🔍 Comprehensive image mismatch analysis...\n")
    
    results = {
        'exact_match': [],
        'missing_with_alternatives': [],
        'completely_missing': [],
        'errors': []
    }
    
    for md_file in sorted(frontmatter_dir.glob('*.md')):
        material_name = md_file.stem.replace('-laser-cleaning', '')
        
        hero_url, micro_url, error = extract_image_paths_from_frontmatter(md_file)
        
        if error:
            results['errors'].append((material_name, error))
            continue
        
        if not hero_url or not micro_url:
            results['errors'].append((material_name, "Missing hero or micro URL in frontmatter"))
            continue
        
        # Check exact matches
        hero_exists = hero_url in actual_images
        micro_exists = micro_url in actual_images
        
        if hero_exists and micro_exists:
            results['exact_match'].append(material_name)
            print(f"✅ {material_name}: Perfect match")
            continue
        
        # Check for alternative names
        missing_images = []
        if not hero_exists:
            missing_images.append(hero_url)
        if not micro_exists:
            missing_images.append(micro_url)
        
        found_alternatives = False
        for missing_image in missing_images:
            alternatives = find_similar_images(missing_image, actual_images)
            if alternatives:
                found_alternatives = True
                image_type = 'hero' if 'hero' in missing_image else 'micro'
                print(f"⚠️  {material_name}: Missing {image_type}, but found alternatives:")
                for alt in alternatives:
                    print(f"   → {alt}")
        
        if found_alternatives:
            results['missing_with_alternatives'].append((material_name, missing_images))
        else:
            results['completely_missing'].append((material_name, missing_images))
            print(f"❌ {material_name}: No alternatives found for missing images")
    
    # Summary
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE MISMATCH ANALYSIS")
    print("="*80)
    
    total = len(results['exact_match']) + len(results['missing_with_alternatives']) + len(results['completely_missing'])
    
    print(f"✅ Exact matches: {len(results['exact_match'])}")
    print(f"⚠️  Missing with alternatives: {len(results['missing_with_alternatives'])}")
    print(f"❌ Completely missing: {len(results['completely_missing'])}")
    print(f"❌ Errors: {len(results['errors'])}")
    print(f"📊 Total materials: {total}")
    
    # Show specific issues that can be fixed
    if results['missing_with_alternatives']:
        print(f"\n🔧 FIXABLE NAMING ISSUES:")
        for material, missing_imgs in results['missing_with_alternatives']:
            print(f"\n   {material}:")
            for missing_img in missing_imgs:
                alternatives = find_similar_images(missing_img, actual_images)
                missing_filename = missing_img.split('/')[-1]
                print(f"     Missing: {missing_filename}")
                for alt in alternatives:
                    alt_filename = alt.split('/')[-1]
                    print(f"     Available: {alt_filename}")

if __name__ == "__main__":
    analyze_comprehensive()
