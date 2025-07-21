"""
Centralized utilities for working with frontmatter across the Z-Beam system.
"""

import logging
import yaml
import re
from typing import Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)

def extract_frontmatter(content: str) -> Dict[str, Any]:
    """Extract frontmatter data from markdown content.
    
    Args:
        content: Markdown content with frontmatter
        
    Returns:
        Dictionary containing frontmatter data, or empty dict if extraction fails
    """
    try:
        # Basic validation
        if not content or "---" not in content:
            logger.warning("No frontmatter delimiters found")
            return {}
            
        # Extract content between first two --- markers
        parts = content.split('---', 2)
        if len(parts) < 3:
            logger.warning("Invalid frontmatter format (missing closing delimiter)")
            return {}
            
        # The middle part is the YAML content
        yaml_content = parts[1].strip()
        
        if not yaml_content:
            logger.warning("Empty frontmatter content")
            return {}
            
        # Parse the YAML content
        try:
            parsed_data = yaml.safe_load(yaml_content)
            
            # Handle the case when frontmatter is a list instead of a dict
            if isinstance(parsed_data, list):
                # Wrap the list in a dictionary with a "providers" key
                frontmatter_data = {"providers": parsed_data}
                logger.info("Converted list frontmatter to dictionary with providers key")
            elif isinstance(parsed_data, dict):
                frontmatter_data = parsed_data
            else:
                logger.warning(f"Unexpected frontmatter type: {type(parsed_data)}")
                frontmatter_data = {"content": str(parsed_data)}
                
            logger.info(f"Extracted frontmatter with {len(frontmatter_data)} fields")
            return frontmatter_data
            
        except yaml.YAMLError as e:
            logger.error(f"Error parsing frontmatter YAML: {e}")
            return {}
            
    except Exception as e:
        logger.error(f"Error extracting frontmatter: {e}")
        return {}

def extract_frontmatter_from_file(file_path: str) -> Dict[str, Any]:
    """Extract frontmatter from a markdown file.
    
    Args:
        file_path: Path to the markdown file
        
    Returns:
        Dictionary containing frontmatter data, or empty dict if extraction fails
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return extract_frontmatter(content)
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return {}

def create_frontmatter(data: Dict[str, Any]) -> str:
    """Create frontmatter string from data.
    
    Args:
        data: Dictionary containing frontmatter fields
        
    Returns:
        Formatted frontmatter string with delimiters
    """
    try:
        if not data:
            return ""
            
        yaml_content = yaml.safe_dump(data, default_flow_style=False, sort_keys=False)
        return f"---\n{yaml_content}---\n"
        
    except Exception as e:
        logger.error(f"Error creating frontmatter: {e}")
        return ""

def validate_frontmatter(data: Dict[str, Any], required_fields: list = None) -> bool:
    """Validate frontmatter data against required fields.
    
    Args:
        data: Frontmatter data dictionary
        required_fields: List of required field names
        
    Returns:
        True if valid, False otherwise
    """
    if not data:
        logger.warning("Empty frontmatter data")
        return False
        
    if required_fields:
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            logger.warning(f"Missing required frontmatter fields: {', '.join(missing_fields)}")
            return False
            
    return True