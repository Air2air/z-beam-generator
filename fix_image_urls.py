#!/usr/bin/env python3
"""
Script to fix image URLs in frontmatter files.
"""

import os
import yaml
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_image_urls(frontmatter_path):
    """Fix image URLs in frontmatter files to start with /images/."""
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
        
        # Check if there are image URLs to fix
        if "images" not in parsed:
            logger.info(f"No images in {frontmatter_path}")
            return False
        
        # Track if any URLs were changed
        changed = False
        
        # Fix hero image URL
        if "hero" in parsed["images"] and isinstance(parsed["images"]["hero"], dict):
            if "url" in parsed["images"]["hero"]:
                old_url = parsed["images"]["hero"]["url"]
                url = old_url.lower()
                
                # Remove domain if present
                if "://" in url:
                    url = "/" + "/".join(url.split("/")[3:])
                
                # Ensure URL starts with /images/
                if not url.startswith("/images/"):
                    url = "/images/" + url.split("/")[-1]
                
                # Update URL if changed
                if url != old_url:
                    parsed["images"]["hero"]["url"] = url
                    changed = True
                    logger.info(f"Updated hero URL in {frontmatter_path}: {old_url} -> {url}")
        
        # Fix closeup image URL
        if "closeup" in parsed["images"] and isinstance(parsed["images"]["closeup"], dict):
            if "url" in parsed["images"]["closeup"]:
                old_url = parsed["images"]["closeup"]["url"]
                url = old_url.lower()
                
                # Remove domain if present
                if "://" in url:
                    url = "/" + "/".join(url.split("/")[3:])
                
                # Ensure URL starts with /images/
                if not url.startswith("/images/"):
                    url = "/images/" + url.split("/")[-1]
                
                # Update URL if changed
                if url != old_url:
                    parsed["images"]["closeup"]["url"] = url
                    changed = True
                    logger.info(f"Updated closeup URL in {frontmatter_path}: {old_url} -> {url}")
        
        # If no changes were made, return
        if not changed:
            logger.info(f"No URL changes needed in {frontmatter_path}")
            return False
        
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
        logger.error(f"Error fixing URLs in {frontmatter_path}: {e}")
        return False

def main():
    """Update all frontmatter files."""
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
            if fix_image_urls(file_path):
                updated_files += 1
    
    logger.info(f"Processed {total_files} files, updated {updated_files} files.")

if __name__ == "__main__":
    main()
