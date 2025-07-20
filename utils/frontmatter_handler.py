# Create a new file: utils/frontmatter_handler.py
"""Frontmatter parsing and handling utilities."""

import re
import yaml
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def parse_frontmatter(markdown_content: str) -> Dict[str, Any]:
    """
    Extract and parse YAML frontmatter from markdown content.
    
    Args:
        markdown_content: String containing markdown with frontmatter
        
    Returns:
        Dictionary of parsed frontmatter data
    """
    if not markdown_content:
        return {}
        
    frontmatter_match = re.search(r'---\s*(.*?)\s*---', markdown_content, re.DOTALL)
    if not frontmatter_match:
        return {}
        
    try:
        return yaml.safe_load(frontmatter_match.group(1)) or {}
    except Exception as e:
        logger.error(f"Failed to parse frontmatter YAML: {e}")
        return {}

def format_frontmatter(data: Dict[str, Any]) -> str:
    """
    Format data as YAML frontmatter.
    
    Args:
        data: Dictionary to convert to frontmatter
        
    Returns:
        Formatted frontmatter string
    """
    if not data:
        return ""
        
    try:
        yaml_str = yaml.dump(data, sort_keys=False)
        return f"---\n{yaml_str}---\n\n"
    except Exception as e:
        logger.error(f"Failed to format frontmatter: {e}")
        return ""