#!/usr/bin/env python3
"""
Simple script to fix image URLs with arrow characters in frontmatter files
"""

import os
import glob
import re

def fix_file(filepath):
    print(f"Processing: {os.path.basename(filepath)}")
    
    # Read the file content
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Store original content to check if changes were made
    original = content
    
    # Fix hero URLs with arrow characters
    content = re.sub(
        r'(url: /images/[^-]*)-+>+-*(laser-cleaning-hero\.jpg)', 
        r'\1-\2', 
        content
    )
    
    # Fix closeup URLs with arrow characters
    content = re.sub(
        r'(url: /images/[^-]*)-*>+-*(laser-cleaning-closeup\.jpg)', 
        r'\1-\2', 
        content
    )
    
    # Fix any other URLs with arrow characters
    content = re.sub(
        r'(url: /images/[^-]*)-*>+-*(laser-cleaning-[a-z]+\.jpg)', 
        r'\1-\2', 
        content
    )
    
    # Remove any remaining arrow characters just to be safe
    content = content.replace('--->-', '-')
    content = content.replace('>-', '-')
    
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
    
    if not os.path.exists(frontmatter_dir):
        print(f"❌ Directory not found: {frontmatter_dir}")
        return
    
    print("\n🔍 STARTING ARROW URL FIX PROCESS\n")
    
    # Get all markdown files
    md_files = glob.glob(os.path.join(frontmatter_dir, "*.md"))
    fixed_count = 0
    
    for file_path in md_files:
        if fix_file(file_path):
            fixed_count += 1
    
    print(f"\n🎉 PROCESS COMPLETE! Fixed URLs in {fixed_count} of {len(md_files)} files")

if __name__ == "__main__":
    main()