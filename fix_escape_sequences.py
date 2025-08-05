#!/usr/bin/env python3
"""
Script to fix escape sequences in frontmatter files.
"""

import os
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_escape_sequences(frontmatter_path):
    """Fix escape sequences in frontmatter files."""
    try:
        # Read the frontmatter file
        with open(frontmatter_path, 'r') as f:
            content = f.read()
        
        # Find all instances of backslash followed by space
        pattern = r'\\[ ]'
        if not re.search(pattern, content):
            logger.info(f"No problematic escape sequences found in {frontmatter_path}")
            return False
        
        # Replace backslash+space with just space
        content = content.replace('\\ ', ' ')
        
        # Write the updated content back to the file
        with open(frontmatter_path, 'w') as f:
            f.write(content)
        
        logger.info(f"Fixed escape sequences in {frontmatter_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error fixing escape sequences in {frontmatter_path}: {e}")
        return False

def main():
    """Fix escape sequences in all frontmatter files."""
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
            if fix_escape_sequences(file_path):
                updated_files += 1
    
    logger.info(f"Processed {total_files} files, updated {updated_files} files.")

if __name__ == "__main__":
    main()
