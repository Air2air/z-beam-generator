"""Utility functions for frontmatter generation."""

import logging
from typing import Dict, Any
from utils.frontmatter_utils import extract_frontmatter

logger = logging.getLogger(__name__)

def extract_yaml_content(frontmatter: str) -> str:
    """Extract YAML content from frontmatter.
    
    This is a legacy method. New code should use utils.frontmatter_utils.extract_frontmatter instead.
    
    Args:
        frontmatter: String containing frontmatter with delimiters
        
    Returns:
        YAML content without delimiters
    """
    if frontmatter.startswith('---'):
        second_marker = frontmatter.find('---', 3)
        if second_marker != -1:
            yaml_content = frontmatter[3:second_marker].strip()
        else:
            yaml_content = frontmatter[3:].strip()
    else:
        yaml_content = frontmatter
    
    return yaml_content

def get_frontmatter_data(frontmatter: str) -> Dict[str, Any]:
    """Get frontmatter data from string.
    
    This is a wrapper around utils.frontmatter_utils.extract_frontmatter for backwards compatibility.
    
    Args:
        frontmatter: String containing frontmatter with delimiters
        
    Returns:
        Dictionary containing frontmatter data
    """
    return extract_frontmatter(frontmatter)