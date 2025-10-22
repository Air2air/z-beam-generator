#!/usr/bin/env python3
"""
Placeholder Content Validator

Validates content to ensure no placeholder text remains in generated content.
"""

import re
from typing import List


def validate_placeholder_content(content: str) -> List[str]:
    """
    Validate that content doesn't contain placeholder text.
    
    Args:
        content: The content to validate
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    if not content or not content.strip():
        return errors
    
    # Common placeholder patterns
    placeholder_patterns = [
        r'\[.*?\]',  # [placeholder text]
        r'\{.*?\}',  # {placeholder text}
        r'TODO:',    # TODO markers
        r'FIXME:',   # FIXME markers  
        r'XXX',      # XXX markers
        r'TBD',      # To Be Determined
        r'placeholder',  # literal "placeholder"
        r'example',      # literal "example" (context-dependent)
        r'sample',       # literal "sample" (context-dependent)
    ]
    
    for pattern in placeholder_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            errors.append(f"Found placeholder content: {matches}")
    
    return errors


def has_placeholder_content(content: str) -> bool:
    """
    Check if content contains placeholder text.
    
    Args:
        content: The content to check
        
    Returns:
        True if placeholder content is found, False otherwise
    """
    return len(validate_placeholder_content(content)) > 0