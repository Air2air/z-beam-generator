#!/usr/bin/env python3
"""
Verify frontmatter structure across all generated files.
Identifies files with flat image structure vs structured hero/micro layout.
"""
import os
import yaml
import re
from pathlib import Path

def load_frontmatter(file_path):
    """Extract YAML frontmatter from markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract frontmatter between --- markers
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return None, "No frontmatter found"
        
        frontmatter_content = match.group(1)
        try:
            data = yaml.safe_load(frontmatter_content)
            return data, None
        except yaml.YAMLError as e:
            return None, f"YAML parsing error: {e}"
    except Exception as e:
        return None, f"File reading error: {e}"

def check_image_structure(data):
    """Check if images follow structured hero/micro format."""
    if not data or 'images' not in data:
        return 'missing', "No images section found"
    
    images = data['images']
    
    # Check for flat structure (direct url/alt at images level)
    if 'url' in images or 'alt' in images:
        return 'flat', "Images section has direct url/alt fields (flat structure)"
    
    # Check for structured format
    if 'hero' in images and 'micro' in images:
        hero = images['hero']
        micro = images['micro']
        
        # Verify hero structure
        if not isinstance(hero, dict) or 'url' not in hero or 'alt' not in hero:
            return 'malformed', "Hero section missing url or alt fields"
        
        # Verify micro structure  
        if not isinstance(micro, dict) or 'url' not in micro or 'alt' not in micro:
            return 'malformed', "Micro section missing url or alt fields"
        
        return 'structured', "Properly structured with hero/micro layout"
    
    return 'unknown', "Unknown image structure format"

def main():
    """Verify structure of all frontmatter files."""
    frontmatter_dir = Path('content/components/frontmatter')
    
    if not frontmatter_dir.exists():
        print(f"❌ Directory not found: {frontmatter_dir}")
        return
    
    print("🔍 Verifying frontmatter structure across all files...\n")
    
    results = {
        'structured': [],
        'flat': [],
        'malformed': [],
        'missing': [],
        'errors': []
    }
    
    for md_file in sorted(frontmatter_dir.glob('*.md')):
        print(f"📄 Checking: {md_file.name}")
        
        data, error = load_frontmatter(md_file)
        if error:
            results['errors'].append((md_file.name, error))
            print(f"   ❌ Error: {error}")
            continue
        
        structure_type, message = check_image_structure(data)
        results[structure_type].append((md_file.name, message))
        
        if structure_type == 'structured':
            print(f"   ✅ {message}")
        elif structure_type == 'flat':
            print(f"   ⚠️  {message}")
        else:
            print(f"   ❌ {message}")
    
    # Summary report
    print("\n" + "="*60)
    print("📊 STRUCTURE VERIFICATION SUMMARY")
    print("="*60)
    
    total_files = sum(len(files) for files in results.values())
    
    print(f"✅ Structured (hero/micro): {len(results['structured'])} files")
    print(f"⚠️  Flat structure: {len(results['flat'])} files")
    print(f"❌ Malformed: {len(results['malformed'])} files")  
    print(f"❌ Missing images: {len(results['missing'])} files")
    print(f"❌ Errors: {len(results['errors'])} files")
    print(f"📊 Total: {total_files} files")
    
    # Detailed issue reports
    if results['flat']:
        print("\n🔍 FILES WITH FLAT STRUCTURE:")
        for filename, message in results['flat']:
            print(f"   • {filename}: {message}")
    
    if results['malformed']:
        print("\n🔍 FILES WITH MALFORMED STRUCTURE:")
        for filename, message in results['malformed']:
            print(f"   • {filename}: {message}")
    
    if results['missing']:
        print("\n🔍 FILES WITH MISSING IMAGES:")
        for filename, message in results['missing']:
            print(f"   • {filename}: {message}")
    
    if results['errors']:
        print("\n🔍 FILES WITH ERRORS:")
        for filename, error in results['errors']:
            print(f"   • {filename}: {error}")
    
    # Recommend action
    issues_found = len(results['flat']) + len(results['malformed']) + len(results['missing']) + len(results['errors'])
    
    if issues_found == 0:
        print("\n🎉 All frontmatter files have correct structured image format!")
    else:
        print(f"\n⚠️  Found {issues_found} files that need attention.")
        print("   Consider running the frontmatter update script to fix these issues.")

if __name__ == "__main__":
    main()
