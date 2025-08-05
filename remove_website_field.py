#!/usr/bin/env python3
"""
Script to remove website field from frontmatter files.
"""

import os
import yaml
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def remove_website_field(frontmatter_path):
    """Remove website field from frontmatter files."""
    try:
        # Read the frontmatter file
        with open(frontmatter_path, 'r') as f:
            content = f.read()
        
        # Extract the YAML content between the first and last triple dashes
        yaml_content = None
        if '---' in content:
            parts = content.split('---')
            if len(parts) >= 3:
                yaml_content = parts[1]
                header = parts[0] + '---\n'
                footer = '---' + ''.join(parts[2:])
        
        if not yaml_content:
            logger.warning(f"Could not extract YAML content from {frontmatter_path}")
            return False
        
        # Parse the YAML content
        try:
            parsed = yaml.safe_load(yaml_content)
        except Exception as e:
            logger.error(f"Failed to parse YAML in {frontmatter_path}: {e}")
            return False
        
        # Check if there's a website field to remove
        if "website" not in parsed:
            logger.info(f"No website field in {frontmatter_path}")
            return False
        
        # Remove the website field
        del parsed["website"]
        logger.info(f"Removed website field from {frontmatter_path}")
        
        # Convert the parsed YAML back to string
        new_yaml_content = yaml.dump(parsed, default_flow_style=False, sort_keys=False)
        
        # Rebuild the file content
        new_content = header + new_yaml_content + footer
        
        # Write the updated content back to the file
        with open(frontmatter_path, 'w') as f:
            f.write(new_content)
        
        logger.info(f"Updated {frontmatter_path}")
        return True
    
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
