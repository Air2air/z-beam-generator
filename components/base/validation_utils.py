"""
Validation utilities for Z-Beam Generator components.

This module provides common validation functions used across different generators.
"""

import logging
import yaml
import json
import re
from typing import Dict, Any, List, Tuple, Optional, Union

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
    else:  # Default to char count
        length = len(text)
        
    if length < min_length:
        raise ValueError(f"{error_prefix} too short: {length} {length_type}, minimum required: {min_length}")
    
    if length > max_length:
        raise ValueError(f"{error_prefix} too long: {length} {length_type}, maximum allowed: {max_length}")
        
    return text

def validate_required_fields(data: Dict[str, Any], required_fields: List[str], 
                           context: str = "") -> None:
    """Validate that all required fields are present in a dictionary.
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        context: Context for error message
        
    Raises:
        ValueError: If any required fields are missing
    """
    if not isinstance(data, dict):
        raise ValueError(f"Expected dictionary for {context or 'data'}")
        
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        context_msg = f" in {context}" if context else ""
        raise ValueError(f"Missing required fields{context_msg}: {missing_fields}")

def validate_yaml_content(content: str) -> Dict[str, Any]:
    """Validate and parse YAML content.
    
    Args:
        content: YAML content to validate
        
    Returns:
        Dict: Parsed YAML content
        
    Raises:
        ValueError: If YAML is invalid
    """
    try:
        parsed = yaml.safe_load(content)
        if not isinstance(parsed, dict):
            raise ValueError("YAML content must be a dictionary")
        return parsed
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML: {e}")

def validate_json_content(content: str) -> Dict[str, Any]:
    """Validate and parse JSON content.
    
    Args:
        content: JSON content to validate
        
    Returns:
        Dict: Parsed JSON content
        
    Raises:
        ValueError: If JSON is invalid
    """
    try:
        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            raise ValueError("JSON content must be an object")
        return parsed
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")

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
    if len(lines) < min_count:
        raise ValueError(f"{error_prefix} {len(lines)} lines, minimum required: {min_count}")
    
    if max_count and len(lines) > max_count:
        # Truncate to max count
        return lines[:max_count]
        
    return lines

def extract_markdown_sections(content: str) -> Dict[str, str]:
    """Extract markdown sections based on headers.
    
    Args:
        content: Markdown content
        
    Returns:
        Dict: Dictionary mapping section headers to content
    """
    sections = {}
    lines = content.split('\n')
    current_section = None
    current_content = []
    
    for line in lines:
        if re.match(r'^#{1,6}\s+', line):  # Header line
            # Save previous section if exists
            if current_section is not None:
                sections[current_section] = '\n'.join(current_content).strip()
            
            # Start new section
            current_section = line.lstrip('#').strip()
            current_content = []
        elif current_section is not None:
            current_content.append(line)
    
    # Save the last section
    if current_section is not None:
        sections[current_section] = '\n'.join(current_content).strip()
    
    return sections

def validate_category_consistency(content: str, category: str, article_type: str, subject: str) -> bool:
    """Validate that category information is consistent throughout the content.
    
    Args:
        content: Content to validate
        category: Expected category
        article_type: Expected article type
        subject: Expected subject
        
    Returns:
        bool: True if consistent
        
    Raises:
        ValueError: If inconsistencies are detected
    """
    # Extract frontmatter
    frontmatter_pattern = r'---\s+(.*?)\s+---'
    frontmatter_match = re.search(frontmatter_pattern, content, re.DOTALL)
    
    if not frontmatter_match:
        raise ValueError("Missing YAML frontmatter")
    
    frontmatter_text = frontmatter_match.group(1)
    
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in frontmatter: {e}")
    
    # Check consistency
    if 'category' not in frontmatter:
        raise ValueError("Missing 'category' in frontmatter")
    
    if frontmatter['category'].lower() != category.lower():
        raise ValueError(f"Category mismatch: '{frontmatter['category']}' in frontmatter vs '{category}' expected")
    
    if 'article_type' not in frontmatter:
        raise ValueError("Missing 'article_type' in frontmatter")
    
    if frontmatter['article_type'].lower() != article_type.lower():
        raise ValueError(f"Article type mismatch: '{frontmatter['article_type']}' in frontmatter vs '{article_type}' expected")
    
    if 'subject' not in frontmatter:
        raise ValueError("Missing 'subject' in frontmatter")
    
    if frontmatter['subject'].lower() != subject.lower():
        raise ValueError(f"Subject mismatch: '{frontmatter['subject']}' in frontmatter vs '{subject}' expected")
    
    return True

def strip_markdown_code_blocks(content: str) -> str:
    """Remove markdown code block markers from content.
    
    Args:
        content: Content that may contain code blocks
        
    Returns:
        str: Content with code block markers removed
    """
    content = content.strip()
    
    # Comprehensive patterns for various code block formats
    code_block_patterns = [
        r'^```(?:yaml|text|json|python|javascript|css|html)?\s*\n(.*?)```\s*$',  # With language specifier + newline
        r'^```(?:yaml|text|json|python|javascript|css|html)?\s*(.*?)```\s*$',    # With language specifier, no newline
        r'^```\s*\n(.*?)```\s*$',                                                # Plain ``` with newline
        r'^```(.*?)```$',                                                        # Simple ``` wrapper
    ]
    
    for pattern in code_block_patterns:
        match = re.match(pattern, content, re.DOTALL)
        if match:
            extracted = match.group(1).strip()
            if extracted:
                return extracted
    
    # No legacy fallbacks - if patterns don't match, content is returned as-is
    return content

def extract_yaml_from_content(content: str) -> str:
    """Extract YAML content from a string that may contain frontmatter delimiters.
    
    Args:
        content: Content that may contain YAML frontmatter
        
    Returns:
        str: Extracted YAML content
    """
    content = strip_markdown_code_blocks(content)
    
    # If content has YAML frontmatter delimiters, extract the content between them
    if "---" in content:
        # Split by --- to get the content between delimiters
        parts = content.split("---", 2)
        if len(parts) >= 2:
            return parts[1].strip()
    
    return content
