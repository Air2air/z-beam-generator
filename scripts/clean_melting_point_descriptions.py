#!/usr/bin/env python3
"""
Clean Melting Point Descriptions Script

This script removes descriptive text from meltingPoint fields in frontmatter files,
keeping only the temperature values and units.
"""

import os
import re
import glob

def clean_melting_point(melting_point_value):
    """
    Clean melting point value by removing descriptive text in parentheses
    and standardizing format to keep only temperature and unit.
    """
    # Remove content in parentheses
    cleaned = re.sub(r'\s*\([^)]+\)', '', melting_point_value)
    
    # Handle special cases that start with descriptive text
    if cleaned.lower().startswith('decomposes at'):
        # Extract temperature from "Decomposes at ~280°C" and format as just the temperature
        temp_match = re.search(r'(\d+(?:\.\d+)?)\s*[°×]\s*C', cleaned, re.IGNORECASE)
        if temp_match:
            cleaned = f"{temp_match.group(1)}°C"
    
    # Clean up extra spaces and tildes
    cleaned = re.sub(r'~\s*', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = cleaned.strip()
    
    return cleaned

def process_frontmatter_file(file_path):
    """Process a single frontmatter file to clean melting point descriptions."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find and replace meltingPoint lines with descriptive text
        pattern = r'(\s*meltingPoint:\s*["\']?)([^"\'\n]+?)(["\']?\s*(?:\n|$))'
        
        def replace_melting_point(match):
            indent = match.group(1)
            original_value = match.group(2)
            ending = match.group(3)
            
            # Only clean if there are parentheses or starts with "Decomposes"
            if '(' in original_value or original_value.strip().lower().startswith('decomposes'):
                cleaned_value = clean_melting_point(original_value)
                return f"{indent}{cleaned_value}{ending}"
            else:
                return match.group(0)  # Return unchanged
        
        new_content = re.sub(pattern, replace_melting_point, content)
        
        # Only write if content changed
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False
    
    return False

def main():
    """Main function to process all frontmatter files."""
    frontmatter_dir = 'content/components/frontmatter'
    
    if not os.path.exists(frontmatter_dir):
        print(f"Error: Directory {frontmatter_dir} does not exist")
        return
    
    # Find all frontmatter files
    pattern = os.path.join(frontmatter_dir, '*-laser-cleaning.md')
    files = glob.glob(pattern)
    
    if not files:
        print(f"No frontmatter files found in {frontmatter_dir}")
        return
    
    print(f"Processing {len(files)} frontmatter files...")
    
    updated_count = 0
    for file_path in files:
        if process_frontmatter_file(file_path):
            filename = os.path.basename(file_path)
            print(f"✅ Updated: {filename}")
            updated_count += 1
    
    print("\n📊 Summary:")
    print(f"   Files processed: {len(files)}")
    print(f"   Files updated: {updated_count}")
    print(f"   Files unchanged: {len(files) - updated_count}")

if __name__ == "__main__":
    main()
