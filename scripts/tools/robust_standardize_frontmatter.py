#!/usr/bin/env python3
"""
Frontmatter Standardizer - Robust Version

Utility script to standardize frontmatter files to use consistent YAML formatting
with proper --- delimiters. Handles even broken YAML by extracting valid content.
"""

import os
import re
import logging
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

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

def extract_yaml_content(file_path: Path) -> Tuple[Dict, bool]:
    """
    Extract YAML content from file using multiple strategies
    
    Returns:
        Tuple of (parsed_data, success_flag)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Strategy 1: Try to extract content between code block markers
        if "```yaml" in content:
            yaml_pattern = r"```yaml\s*(.*?)\s*```"
            yaml_match = re.search(yaml_pattern, content, re.DOTALL)
            if yaml_match:
                yaml_content = yaml_match.group(1).strip()
                try:
                    data = yaml.safe_load(yaml_content)
                    if isinstance(data, dict):
                        logger.info(f"Successfully extracted YAML from code block in {file_path.name}")
                        return data, True
                except Exception as e:
                    logger.debug(f"Failed to parse code block YAML: {e}")
            
        # Strategy 2: Try to extract content between standard frontmatter markers
        if "---" in content:
            yaml_pattern = r"---\s*(.*?)\s*---"
            yaml_match = re.search(yaml_pattern, content, re.DOTALL)
            if yaml_match:
                yaml_content = yaml_match.group(1).strip()
                try:
                    data = yaml.safe_load(yaml_content)
                    if isinstance(data, dict):
                        logger.info(f"Successfully extracted YAML from standard frontmatter in {file_path.name}")
                        return data, True
                except Exception as e:
                    logger.debug(f"Failed to parse standard frontmatter: {e}")
        
        # Strategy 3: Try to extract all lines up to the first version information comment
        version_info_pattern = r"# Version Information"
        if version_info_pattern in content:
            lines = content.split('\n')
            yaml_lines = []
            for line in lines:
                if line.strip().startswith("# Version Information"):
                    break
                yaml_lines.append(line)
            
            yaml_content = '\n'.join(yaml_lines).strip()
            
            # If it starts with ```yaml, strip that
            if yaml_content.startswith("```yaml"):
                yaml_content = yaml_content[7:].strip()
            
            # If it ends with ```, strip that
            if yaml_content.endswith("```"):
                yaml_content = yaml_content[:-3].strip()
                
            try:
                data = yaml.safe_load(yaml_content)
                if isinstance(data, dict):
                    logger.info(f"Successfully extracted YAML up to version info in {file_path.name}")
                    return data, True
            except Exception as e:
                logger.debug(f"Failed to parse YAML up to version info: {e}")
        
        # Strategy 4: Try to parse line by line and extract key-value pairs
        # This is a more aggressive approach for broken YAML
        lines = content.split('\n')
        yaml_dict = {}
        current_key = None
        current_list = None
        
        for line in lines:
            # Skip comment lines and version info
            if line.strip().startswith('#') or "Version Information" in line:
                continue
                
            # Stop at the end of YAML content
            if "```" in line and not line.strip().startswith("```yaml"):
                break
            
            # Skip YAML code block markers
            if line.strip() == "```yaml" or line.strip() == "```":
                continue
                
            # Try to parse key-value pairs
            kv_match = re.match(r'^\s*(\w+):\s*(.+)$', line)
            if kv_match:
                key, value = kv_match.groups()
                yaml_dict[key] = value.strip('"\'')
                current_key = key
                current_list = None
            
            # Try to parse nested objects
            nested_match = re.match(r'^\s+(\w+):\s*(.+)$', line)
            if nested_match and current_key:
                if not isinstance(yaml_dict.get(current_key), dict):
                    yaml_dict[current_key] = {}
                key, value = nested_match.groups()
                yaml_dict[current_key][key] = value.strip('"\'')
            
            # Try to parse list items
            list_match = re.match(r'^\s*-\s*(.+)$', line)
            if list_match:
                item = list_match.group(1).strip()
                if current_key:
                    if not isinstance(yaml_dict.get(current_key), list):
                        yaml_dict[current_key] = []
                    yaml_dict[current_key].append(item)
                    current_list = current_key
        
        if yaml_dict:
            logger.info(f"Successfully extracted {len(yaml_dict)} key-value pairs from {file_path.name} using line-by-line parsing")
            return yaml_dict, True
            
        # If we got here, we couldn't extract any valid YAML
        logger.error(f"Could not extract YAML content from {file_path.name}")
        return {}, False
        
    except Exception as e:
        logger.error(f"Error reading/processing {file_path.name}: {e}")
        return {}, False

def extract_version_info(file_path: Path) -> str:
    """Extract version information from the file if it exists"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Look for version info comments
        version_match = re.search(r'# Version Information.*?# Operation: \w+', content, re.DOTALL)
        if version_match:
            return version_match.group(0)
            
        # Look for version log blocks
        version_log_match = re.search(r'---\s*Version Log.*?---', content, re.DOTALL)
        if version_log_match:
            return version_log_match.group(0)
            
        return ""
    except Exception as e:
        logger.error(f"Error extracting version info from {file_path.name}: {e}")
        return ""

def standardize_frontmatter_file(filepath: Path, dry_run: bool = False) -> bool:
    """
    Standardize a single frontmatter file.
    
    Args:
        filepath: Path to the file
        dry_run: If True, don't write changes
        
    Returns:
        True if changes were made (or would be made in dry run)
    """
    try:
        # Extract YAML data
        yaml_data, success = extract_yaml_content(filepath)
        if not success or not yaml_data:
            logger.error(f"Failed to extract YAML data from {filepath.name}")
            return False
            
        # Extract version information if present
        version_info = extract_version_info(filepath)
            
        # Create standardized frontmatter with proper delimiters
        yaml_content = yaml.dump(yaml_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
        standardized_content = f"---\n{yaml_content.strip()}\n---\n"
        
        # Add version information if present
        if version_info:
            standardized_content += f"\n{version_info}\n"
            
        # Write the standardized content back to the file
        if not dry_run:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(standardized_content)
                
            logger.info(f"✅ Standardized frontmatter format for {filepath.name}")
        else:
            logger.info(f"Would standardize frontmatter format for {filepath.name} (dry run)")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Error standardizing {filepath.name}: {e}")
        return False

def main():
    """Main entry point for the script"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Standardize frontmatter files")
    parser.add_argument("--dry-run", action="store_true", help="Don't make changes, just report what would be done")
    parser.add_argument("--file", help="Process a specific file instead of all files")
    args = parser.parse_args()
    
    if args.dry_run:
        logger.info("Running in dry-run mode - no changes will be made")
    
    # Get files to process
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return
        files = [file_path]
    else:
        # Find all frontmatter files
        files = list_frontmatter_files()
        
    if not files:
        logger.error("No frontmatter files found to process")
        return
        
    # Track results
    successful = 0
    failed = 0
    
    # Process each file
    for file_path in files:
        if standardize_frontmatter_file(file_path, args.dry_run):
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
    
    if args.dry_run and successful > 0:
        logger.info("Run without --dry-run to apply these changes")
    
if __name__ == "__main__":
    main()
