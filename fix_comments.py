#!/usr/bin/env python3
"""
Script to fix malformed HTML comments in frontmatter files
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
    
    # Fix incomplete HTML comments (replace "- " or "-" at the end with "-->")
    content = re.sub(r'(<!--[^>]*)-\s*\n', r'\1-->\n', content)
    
    # Only write if changes were made
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Fixed comments in {os.path.basename(filepath)}")
        return True
    else:
        print(f"No comment fixes needed in {os.path.basename(filepath)}")
        return False

def main():
    # Directory containing frontmatter files
    frontmatter_dir = "content/components/frontmatter"
    
    # Get all markdown files
    md_files = glob.glob(os.path.join(frontmatter_dir, "*.md"))
    fixed_count = 0
    
    print(f"Processing {len(md_files)} files...")
    
    for file_path in md_files:
        if fix_file(file_path):
            fixed_count += 1
    
    print(f"Done! Fixed comments in {fixed_count} of {len(md_files)} files")

if __name__ == "__main__":
    main()