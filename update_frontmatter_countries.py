#!/usr/bin/env python3
"""
Script to add authorCountry field to existing frontmatter MD files
"""

import os
import json
import glob
import re

def load_authors():
    """Load authors data from authors.json"""
    with open('components/author/authors.json', 'r') as f:
        data = json.load(f)
    
    # Create name -> country mapping
    author_map = {}
    for author in data['authors']:
        name = author['name']
        country = author['country']
        
        # Normalize country names for consistency
        if country == "United States (California)":
            country = "United States"
        
        author_map[name] = country
    
    return author_map

def update_frontmatter_file(filepath, author_map):
    """Update a single frontmatter file to add authorCountry"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if authorCountry already exists
    if 'authorCountry:' in content:
        print(f"   ⏭️  {os.path.basename(filepath)} - already has authorCountry")
        return False
    
    # Extract author name using regex
    author_match = re.search(r'^author:\s*(.+)$', content, re.MULTILINE)
    if not author_match:
        print(f"   ❌ {os.path.basename(filepath)} - no author field found")
        return False
    
    author_name = author_match.group(1).strip()
    
    # Get country for this author
    country = author_map.get(author_name)
    if not country:
        print(f"   ❓ {os.path.basename(filepath)} - unknown author: {author_name}")
        return False
    
    # Insert authorCountry right after author line
    author_line = author_match.group(0)
    new_content = content.replace(
        author_line,
        f"{author_line}\nauthorCountry: {country}"
    )
    
    # Write back to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"   ✅ {os.path.basename(filepath)} - added authorCountry: {country}")
    return True

def main():
    print("🚀 UPDATING FRONTMATTER FILES WITH AUTHOR COUNTRIES")
    print("=" * 55)
    
    # Load author mapping
    print("📖 Loading authors from components/author/authors.json...")
    author_map = load_authors()
    
    print(f"👥 Found {len(author_map)} authors:")
    for name, country in author_map.items():
        print(f"   • {name} → {country}")
    print()
    
    # Find all frontmatter MD files
    frontmatter_files = glob.glob('content/components/frontmatter/*.md')
    print(f"📁 Found {len(frontmatter_files)} frontmatter files")
    print()
    
    # Update each file
    updated_count = 0
    for filepath in sorted(frontmatter_files):
        if update_frontmatter_file(filepath, author_map):
            updated_count += 1
    
    print()
    print("📊 SUMMARY:")
    print(f"   Total files: {len(frontmatter_files)}")
    print(f"   Updated: {updated_count}")
    print(f"   Skipped: {len(frontmatter_files) - updated_count}")
    print("✅ Done!")

if __name__ == "__main__":
    main()
