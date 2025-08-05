#!/usr/bin/env python3
"""
Script to fix image URLs with missing hyphens in frontmatter files
"""

import os
import glob
import re

def fix_file(filepath):
    # Read the file content
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Store original content to check if changes were made
    original = content
    
    # Extract the subject from the filename
    filename = os.path.basename(filepath)
    subject = filename.replace('-laser-cleaning.md', '').replace('-applications.md', '')
    subject_slug = subject.lower()
    
    # Fix missing hyphens between subject and "laser-cleaning"
    content = re.sub(r'(/images/[a-z0-9-]+)laser-cleaning', r'\1-laser-cleaning', content)
    
    # Ensure the correct subject name is used in the URL
    def replace_url(match):
        url_prefix = match.group(1)  # /images/
        image_type = match.group(2)  # -laser-cleaning-hero.jpg or similar
        
        # Construct the correct URL with the subject from the filename
        return f"{url_prefix}{subject_slug}{image_type}"
    
    # Find URLs that match the pattern but may have incorrect subject names
    content = re.sub(r'(url: /images/)[a-z0-9-]+(-laser-cleaning-(?:hero|closeup|detail|micrograph)\.jpg)', 
                    replace_url, content)
    
    # Only write if changes were made
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✅ Fixed URLs in {os.path.basename(filepath)}")
        return True
    else:
        print(f"⏭️ No changes needed in {os.path.basename(filepath)}")
        return False

def main():
    # Directory containing frontmatter files
    frontmatter_dir = "content/components/frontmatter"
    
    # Get all markdown files
    md_files = glob.glob(os.path.join(frontmatter_dir, "*.md"))
    fixed_count = 0
    
    print(f"\n🔧 Processing {len(md_files)} frontmatter files...\n")
    
    for file_path in md_files:
        if fix_file(file_path):
            fixed_count += 1
    
    print(f"\n🎉 Done! Fixed URLs in {fixed_count} of {len(md_files)} files")

if __name__ == "__main__":
    main()