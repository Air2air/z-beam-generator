#!/usr/bin/env python3
"""
Frontmatter Standardizer

Utility script to standardize frontmatter files to use consistent YAML formatting
with proper --- delimiters. Converts code block style YAML to standard frontmatter.
"""

import os
import re
import logging
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Set

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def list_frontmatter_files() -> List[Path]:
    """List all frontmatter files in the content directory"""
    frontmatter_dir = Path("content/components/frontmatter")
    if not frontmatter_dir.exists():
        logger.error(f"Frontmatter directory not found: {frontmatter_dir}")
        return []
    
    files = list(frontmatter_dir.glob("*.md"))
    logger.info(f"Found {len(files)} frontmatter files")
    return files

def parse_frontmatter(file_path: Path) -> Optional[Dict]:
    """Parse frontmatter from file in various formats"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        
        # Check for code block format (```yaml ... ```)
        if content.startswith("```yaml"):
            end_marker = content.find("```", 7)
            if end_marker != -1:
                yaml_content = content[7:end_marker].strip()
                data = yaml.safe_load(yaml_content)
                logger.debug(f"Parsed code block YAML from {file_path.name}")
                return data
        
        # Check for standard frontmatter format (--- ... ---)
        elif content.startswith("---"):
            end_marker = content.find("---", 3)
            if end_marker != -1:
                yaml_content = content[3:end_marker].strip()
                data = yaml.safe_load(yaml_content)
                logger.debug(f"Parsed standard frontmatter from {file_path.name}")
                return data
                
        # Try to parse the entire content as YAML
        try:
            data = yaml.safe_load(content)
            if isinstance(data, dict):
                logger.debug(f"Parsed entire file as YAML from {file_path.name}")
                return data
        except yaml.YAMLError:
            pass
            
        logger.warning(f"Could not parse frontmatter from {file_path.name}")
        return None
        
    except Exception as e:
        logger.error(f"Error parsing {file_path.name}: {e}")
        return None

def standardize_frontmatter(file_path: Path) -> bool:
    """Standardize frontmatter format to use proper --- delimiters"""
    try:
        # Parse the YAML content from whatever format it's in
        data = parse_frontmatter(file_path)
        if not data:
            logger.error(f"Failed to parse YAML from {file_path.name}")
            return False
            
        # Read the original file for version information
        with open(file_path, "r", encoding="utf-8") as f:
            original_content = f.read()
            
        # Extract version information if present
        version_info = ""
        version_match = re.search(r"<!--\s*Version.*?-->", original_content, re.DOTALL)
        if version_match:
            version_info = version_match.group(0)
            
        # Create standardized frontmatter with proper delimiters
        yaml_content = yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)
        standardized_content = f"---\n{yaml_content.strip()}\n---\n"
        
        # Add version information if present
        if version_info:
            standardized_content += f"\n{version_info}\n"
            
        # Write the standardized content back to the file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(standardized_content)
            
        logger.info(f"✅ Standardized frontmatter format for {file_path.name}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error standardizing {file_path.name}: {e}")
        return False

def main():
    """Main entry point for the script"""
    logger.info("Starting frontmatter standardization process")
    
    # Get all frontmatter files
    files = list_frontmatter_files()
    if not files:
        logger.error("No frontmatter files found")
        return
        
    # Track results
    successful = 0
    failed = 0
    
    # Process each file
    for file_path in files:
        if standardize_frontmatter(file_path):
            successful += 1
        else:
            failed += 1
            
    # Log summary
    logger.info(f"\n===== STANDARDIZATION SUMMARY =====")
    logger.info(f"Total files processed: {len(files)}")
    logger.info(f"Successfully standardized: {successful}")
    if failed > 0:
        logger.warning(f"Failed to standardize: {failed}")
    else:
        logger.info("All files standardized successfully!")
    
if __name__ == "__main__":
    main()
