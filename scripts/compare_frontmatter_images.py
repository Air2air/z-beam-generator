#!/usr/bin/env python3
"""
Compare frontmatter image references with actual images in Next.js public/images directory.
Identifies missing images and reports which materials have complete image sets.
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
        # Look for the images: section, then find hero and micro subsections
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

def compare_images():
    """Compare frontmatter image references with actual images."""
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
    print("🔍 Comparing frontmatter references with actual images...\n")
    
    results = {
        'complete': [],      # Both hero and micro images exist
        'partial': [],       # Only one image exists
        'missing': [],       # No images exist
        'errors': []         # Parsing errors
    }
    
    total_references = 0
    missing_references = []
    
    for md_file in sorted(frontmatter_dir.glob('*.md')):
        material_name = md_file.stem.replace('-laser-cleaning', '')
        
        hero_url, micro_url, error = extract_image_paths_from_frontmatter(md_file)
        
        if error:
            results['errors'].append((material_name, error))
            print(f"❌ {material_name}: {error}")
            continue
        
        if not hero_url or not micro_url:
            results['errors'].append((material_name, "Missing hero or micro URL in frontmatter"))
            print(f"❌ {material_name}: Missing hero or micro URL in frontmatter")
            continue
        
        # Check if images exist
        hero_exists = hero_url in actual_images
        micro_exists = micro_url in actual_images
        
        total_references += 2  # hero + micro
        
        if not hero_exists:
            missing_references.append(hero_url)
        if not micro_exists:
            missing_references.append(micro_url)
        
        if hero_exists and micro_exists:
            results['complete'].append(material_name)
            print(f"✅ {material_name}: Both images exist")
        elif hero_exists or micro_exists:
            results['partial'].append((material_name, hero_exists, micro_exists))
            missing_img = "micro" if hero_exists else "hero"
            print(f"⚠️  {material_name}: Missing {missing_img} image")
        else:
            results['missing'].append(material_name)
            print(f"❌ {material_name}: Both images missing")
    
    # Summary report
    print("\n" + "="*60)
    print("📊 IMAGE COMPARISON SUMMARY")
    print("="*60)
    
    total_materials = len(results['complete']) + len(results['partial']) + len(results['missing'])
    
    print(f"📁 Total materials checked: {total_materials}")
    print(f"✅ Complete (both images): {len(results['complete'])}")
    print(f"⚠️  Partial (one image): {len(results['partial'])}")
    print(f"❌ Missing (no images): {len(results['missing'])}")
    print(f"❌ Errors: {len(results['errors'])}")
    
    coverage = len(results['complete']) / total_materials * 100 if total_materials > 0 else 0
    print(f"📊 Complete coverage: {coverage:.1f}%")
    
    print(f"\n📈 IMAGE STATISTICS:")
    print(f"   Total image references: {total_references}")
    print(f"   Missing image files: {len(missing_references)}")
    print(f"   Actual images available: {len(actual_images)}")
    
    # List working materials (these should display in Next.js)
    if results['complete']:
        print(f"\n✅ MATERIALS WITH COMPLETE IMAGES ({len(results['complete'])}):")
        working_materials = sorted(results['complete'])
        for i, material in enumerate(working_materials):
            if i % 6 == 0:  # New line every 6 materials
                print()
            print(f"   {material:<20}", end="")
        print()
    
    # List missing images for debugging
    if missing_references:
        print(f"\n❌ MISSING IMAGE FILES (First 20):")
        for missing_img in sorted(set(missing_references))[:20]:
            filename = missing_img.split('/')[-1]
            print(f"   • {filename}")
        
        if len(set(missing_references)) > 20:
            print(f"   ... and {len(set(missing_references)) - 20} more")
    
    # Check if working materials match user's observation
    user_working = ['aluminum', 'bamboo', 'cobalt', 'copper', 'plywood', 'niobium', 'lead', 'iridium']
    confirmed_working = [m for m in user_working if m in results['complete']]
    not_working = [m for m in user_working if m not in results['complete']]
    
    print(f"\n🔍 USER REPORTED WORKING MATERIALS:")
    print(f"   ✅ Confirmed working: {confirmed_working}")
    if not_working:
        print(f"   ❌ Reported working but missing images: {not_working}")

if __name__ == "__main__":
    compare_images()
