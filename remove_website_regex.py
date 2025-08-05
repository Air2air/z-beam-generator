#!/usr/bin/env python3
"""
Script to remove website field from frontmatter files.
"""

import os
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def remove_website_field(frontmatter_path):
    """Remove website field from frontmatter files using regex."""
    try:
        # Read the frontmatter file
        with open(frontmatter_path, 'r') as f:
            content = f.read()
        
        # Use regex to remove the website line
        website_pattern = re.compile(r'^website:.*?$', re.MULTILINE)
        if website_pattern.search(content):
            new_content = website_pattern.sub('', content)
            
            # Write the updated content back to the file
            with open(frontmatter_path, 'w') as f:
                f.write(new_content)
            
            logger.info(f"Removed website field from {frontmatter_path}")
            return True
        else:
            logger.info(f"No website field found in {frontmatter_path}")
            return False
    
    except Exception as e:
        logger.error(f"Error removing website field in {frontmatter_path}: {e}")
        return False

def main():
    """Remove website field from all frontmatter files."""
    frontmatter_dir = os.path.join("content", "components", "frontmatter")
    
    if not os.path.exists(frontmatter_dir):
        logger.error(f"Directory not found: {frontmatter_dir}")
        return
    
    # Process all frontmatter files
    total_files = 0
    updated_files = 0
    
    for filename in os.listdir(frontmatter_dir):
        if filename.endswith(".md"):
            total_files += 1
            file_path = os.path.join(frontmatter_dir, filename)
            if remove_website_field(file_path):
                updated_files += 1
    
    logger.info(f"Processed {total_files} files, updated {updated_files} files.")

if __name__ == "__main__":
    main()
