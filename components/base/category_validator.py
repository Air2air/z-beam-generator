"""
Category validation utility for Z-Beam Generator.

Ensures consistency in frontmatter metadata.
"""

import re
import yaml
import logging

logger = logging.getLogger(__name__)

def validate_category_consistency(file_content: str) -> bool:
    """
    Validates that category information is consistent within frontmatter.
    
    Args:
        file_content: String content of the file to validate
        
    Returns:
        bool: True if consistent, False otherwise
        
    Raises:
        ValueError: If inconsistencies are detected
    """
    # Extract frontmatter
    frontmatter_pattern = r'---\s+(.*?)\s+---'
    frontmatter_match = re.search(frontmatter_pattern, file_content, re.DOTALL)
    
    if not frontmatter_match:
        raise ValueError("Missing or invalid YAML frontmatter")
    
    frontmatter_text = frontmatter_match.group(1)
    
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in frontmatter: {e}")
    
    # Check for required fields
    errors = []
    
    # Check required fields exist
    if 'category' not in frontmatter:
        errors.append("Missing required 'category' field in frontmatter")
    
    if 'article_type' not in frontmatter:
        errors.append("Missing required 'article_type' field in frontmatter")
    
    if 'subject' not in frontmatter:
        errors.append("Missing required 'subject' field in frontmatter")
    
    # Validate name/subject consistency
    if 'name' in frontmatter and 'subject' in frontmatter and frontmatter['name'] != frontmatter['subject']:
        errors.append(f"Frontmatter 'name' ({frontmatter['name']}) doesn't match 'subject' ({frontmatter['subject']})")
    
    # Validate title format
    if 'title' in frontmatter and 'subject' in frontmatter:
        expected_title_prefix = f"{frontmatter['subject']} "
        if not frontmatter['title'].startswith(expected_title_prefix):
            errors.append(f"Title '{frontmatter['title']}' should start with '{expected_title_prefix}'")
    
    # If there are any inconsistencies, raise an error
    if errors:
        raise ValueError("Category validation errors:\n" + "\n".join(errors))
    
    return True
