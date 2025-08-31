#!/usr/bin/env python3
"""
Caption Component Validator

Component-specific validation logic for caption components.
"""

from typing import List, Dict, Any


def validate_caption_format(content: str, format_rules: Dict[str, Any] = None) -> List[str]:
    """
    Validate caption-specific format requirements.
    
    Args:
        content: The caption content to validate
        format_rules: Optional format rules dictionary
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Caption should be two lines with bold formatting
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    if len(lines) != 2:
        errors.append("Caption must have exactly 2 lines")
    else:
        for i, line in enumerate(lines):
            if not line.startswith('**') or '**' not in line[2:]:
                errors.append(f"Line {i+1} must start with bold formatting (**text**)")
    
    return errors


def validate_caption_content(content: str) -> List[str]:
    """
    Validate caption content requirements.
    
    Args:
        content: The caption content to validate
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Check for placeholder content
    if 'TBD' in content or 'TODO' in content or '[' in content and ']' in content:
        errors.append("Contains placeholder content (TBD, TODO, or [brackets])")
    
    # Basic content validation
    if not content.strip():
        errors.append("Caption component cannot be empty")
    
    return errors
