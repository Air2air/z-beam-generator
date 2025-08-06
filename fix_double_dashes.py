#!/usr/bin/env python3
"""
Script to find and fix double dashes in image URLs across all content files.
"""

import os
import re
import glob
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fix_double_dashes_in_file(file_path):
    """Fix double dashes in image URLs within a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for image URLs with double dashes
    pattern = r'((?:url|src):\s*"/images/[a-z0-9]+)--([a-z0-9-]+\.jpg")'
    updated_content = re.sub(pattern, r'\1-\2', content)
    
    # Check if content changed
    if content != updated_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        logger.info(f"Fixed double dashes in {file_path}")
        return True
    return False

def main():
    """Find and fix double dashes in image URLs."""
    # Get all markdown files in the content directory
    content_path = os.path.join(os.getcwd(), 'content')
    md_files = glob.glob(os.path.join(content_path, '**', '*.md'), recursive=True)
    
    # Also check the specific components directories
    components_path = os.path.join(os.getcwd(), 'components')
    md_files.extend(glob.glob(os.path.join(components_path, '**', '*.md'), recursive=True))
    
    fixed_count = 0
    total_files = len(md_files)
    
    logger.info(f"Checking {total_files} files for double dashes in image URLs...")
    
    for file_path in md_files:
        if fix_double_dashes_in_file(file_path):
            fixed_count += 1
    
    logger.info(f"Fixed double dashes in {fixed_count} of {total_files} files.")

if __name__ == "__main__":
    main()
