"""Utility functions for frontmatter generation."""

import re
import logging

logger = logging.getLogger(__name__)

def extract_yaml_content(frontmatter: str) -> str:
    """Extract YAML content from frontmatter."""
    if frontmatter.startswith('---'):
        second_marker = frontmatter.find('---', 3)
        if second_marker > 0:
            yaml_content = frontmatter[3:second_marker].strip()
        else:
            yaml_content = frontmatter[3:].strip()
    else:
        yaml_content = frontmatter
        
    # Clean any potential embedded document markers
    yaml_content = re.sub(r'---+', '\n', yaml_content)
    return yaml_content