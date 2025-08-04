"""
Validation utilities for Z-Beam Generator components.

This module provides common validation functions used across different generators.
"""

import logging
import yaml
import json
import re
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

def validate_non_empty(content: str, error_message: str = "Content cannot be empty") -> str:
    """Validate that content is not empty.
    
    Args:
        content: Content to validate
        error_message: Custom error message
        
    Returns:
        str: Trimmed content
        
    Raises:
        ValueError: If content is empty
    """
    if not content or not content.strip():
        raise ValueError(error_message)
    return content.strip()

def validate_length(text: str, min_length: int = 0, max_length: int = float('inf'),
                   error_prefix: str = "Text", length_type: str = "chars") -> str:
    """Validate text length is within specified bounds.
    
    Args:
        text: Text to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length
        error_prefix: Prefix for error message
        length_type: Type of length (chars, words, etc.)
        
    Returns:
        str: The validated text
        
    Raises:
        ValueError: If length is outside allowed bounds
    """
    if length_type == "words":
        length = len(text.split())
    else:
        length = len(text)
        
    if length < min_length:
        raise ValueError(f"{error_prefix} too short: {length} {length_type}, minimum required: {min_length}")
        
    if length > max_length:
        raise ValueError(f"{error_prefix} too long: {length} {length_type}, maximum allowed: {max_length}")
        
    return text

def validate_line_count(lines: List[str], min_count: int, 
                     max_count: Optional[int] = None, 
                     error_prefix: str = "Generated") -> List[str]:
    """Validate that the number of lines meets requirements.
    
    Args:
        lines: List of content lines
        min_count: Minimum required line count
        max_count: Maximum allowed line count (optional)
        error_prefix: Prefix for error message
        
    Returns:
        List[str]: Original or truncated lines
        
    Raises:
        ValueError: If line count is below minimum
    """
    line_count = len(lines)
    
    if line_count < min_count:
        raise ValueError(f"{error_prefix} content too short: {line_count} lines, minimum required: {min_count}")
        
    if max_count and line_count > max_count:
        logger.warning(f"{error_prefix} content too long: {line_count} lines, truncating to {max_count}")
        return lines[:max_count]
        
    return lines

def strip_markdown_code_blocks(content: str) -> str:
    """Remove markdown code block delimiters if present.
    
    Args:
        content: Content that may contain markdown code blocks
        
    Returns:
        str: Content with code block markers removed
    """
    # Remove code block markers if the content starts and ends with them
    content = content.strip()
    if content.startswith('```') and content.endswith('```'):
        # Find the first newline after the opening marker
        first_newline = content.find('\n', 3)
        if first_newline != -1:
            # Check if there's a language specifier
            if content[3:first_newline].strip():
                # Remove opening line with language and closing line
                content = content[first_newline+1:-3].strip()
            else:
                # Remove just the markers
                content = content[4:-3].strip()
        else:
            # No newline, just remove markers
            content = content[3:-3].strip()
            
    return content

def validate_required_fields(data: Dict[str, Any], 
                          required_fields: List[str], 
                          data_name: str = "Data") -> None:
    """Validate that a dictionary contains all required fields.
    
    Args:
        data: Dictionary to validate
        required_fields: List of required fields
        data_name: Name of the data structure for error messages
        
    Raises:
        ValueError: If any required field is missing
    """
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValueError(f"{data_name} is missing required fields: {', '.join(missing_fields)}")

def validate_json(content: str) -> Dict[str, Any]:
    """Validate and parse JSON content.
    
    Args:
        content: JSON content to validate
        
    Returns:
        Dict[str, Any]: Parsed JSON
        
    Raises:
        ValueError: If content is not valid JSON
    """
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")

def validate_yaml(content: str) -> Dict[str, Any]:
    """Validate and parse YAML content.
    
    Args:
        content: YAML content to validate
        
    Returns:
        Dict[str, Any]: Parsed YAML
        
    Raises:
        ValueError: If content is not valid YAML
    """
    try:
        result = yaml.safe_load(content)
        if not isinstance(result, dict):
            raise ValueError("YAML must parse to a dictionary")
        return result
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML: {e}")

def validate_category_consistency(file_content: str, category: str, article_type: str, subject: str) -> bool:
    """
    Validates that category information is consistent within frontmatter.
    
    Args:
        file_content: String content of the file to validate
        category: Expected category
        article_type: Expected article type
        subject: Expected subject
        
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
    
    # Check field values match expected values
    if 'category' in frontmatter and category and frontmatter['category'] != category:
        errors.append(f"Category mismatch in frontmatter: expected '{category}', got '{frontmatter['category']}'")
    
    if 'article_type' in frontmatter and frontmatter['article_type'] != article_type:
        errors.append(f"Article type mismatch in frontmatter: expected '{article_type}', got '{frontmatter['article_type']}'")
    
    if 'subject' in frontmatter and frontmatter['subject'] != subject:
        errors.append(f"Subject mismatch in frontmatter: expected '{subject}', got '{frontmatter['subject']}'")
    
    if errors:
        raise ValueError("\n".join(errors))
    
    return True
