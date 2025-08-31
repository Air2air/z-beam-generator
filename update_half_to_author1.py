#!/usr/bin/env python3
"""
Script to change half of the frontmatter files to use author 1 (Yi-Chun Lin, Taiwan)
"""

import os
import glob
import re

def update_frontmatter_to_author1(filepath):
    """Update a frontmatter file to use author 1 (Yi-Chun Lin, Taiwan)"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if it's already Yi-Chun Lin
    if 'author: Yi-Chun Lin' in content:
        print(f"   ⏭️  {os.path.basename(filepath)} - already Yi-Chun Lin")
        return False
    
    # Replace author line
    content = re.sub(
        r'^author:\s*.*$', 
        'author: Yi-Chun Lin', 
        content, 
        flags=re.MULTILINE
    )
    
    # Replace authorCountry line
    content = re.sub(
        r'^authorCountry:\s*.*$', 
        'authorCountry: Taiwan', 
        content, 
        flags=re.MULTILINE
    )
    
    # Write back to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"   ✅ {os.path.basename(filepath)} - updated to Yi-Chun Lin (Taiwan)")
    return True

def main():
    print("🚀 UPDATING HALF OF FRONTMATTER FILES TO AUTHOR 1")
    print("=" * 50)
    
    # Find all frontmatter MD files
    frontmatter_files = sorted(glob.glob('content/components/frontmatter/*.md'))
    total_files = len(frontmatter_files)
    half_count = total_files // 2
    
    print(f"📁 Found {total_files} frontmatter files")
    print(f"🎯 Will update {half_count} files to Yi-Chun Lin (Taiwan)")
    print()
    
    # Update the first half of files (alphabetically)
    updated_count = 0
    for i, filepath in enumerate(frontmatter_files):
        if i < half_count:  # Update first half
            if update_frontmatter_to_author1(filepath):
                updated_count += 1
        else:
            print(f"   ⏭️  {os.path.basename(filepath)} - keeping current author")
    
    print()
    print("📊 SUMMARY:")
    print(f"   Total files: {total_files}")
    print(f"   Updated to Yi-Chun Lin: {updated_count}")
    print(f"   Kept existing authors: {total_files - updated_count}")
    print("✅ Done!")

if __name__ == "__main__":
    main()
