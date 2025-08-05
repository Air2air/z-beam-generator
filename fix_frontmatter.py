#!/usr/bin/env python3
"""
Script to fix frontmatter structure issues in markdown files
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
    
    # 1. Fix incomplete HTML comments (replace "- " or "-" at the end with "-->")
    content = re.sub(r'(<!--[^>]*)-\s*\n', r'\1-->\n', content)
    
    # 2. Fix the standalone dash before the frontmatter
    content = re.sub(r'\n-\nname:', '\n---\nname:', content)
    
    # 3. Ensure proper frontmatter formatting with three dashes
    if '---' not in content[:100]:
        # If no triple dash yet, add it after the comments
        content = re.sub(r'(<!--.*?-->)\s*\n(<!--.*?-->)\s*\n', r'\1\n\2\n---\n', content, flags=re.DOTALL)
    
    # Only write if changes were made
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✅ Fixed frontmatter in {os.path.basename(filepath)}")
        return True
    else:
        print(f"⏭️ No fixes needed in {os.path.basename(filepath)}")
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
    
    print(f"\n🎉 Done! Fixed frontmatter in {fixed_count} of {len(md_files)} files")

if __name__ == "__main__":
    main()