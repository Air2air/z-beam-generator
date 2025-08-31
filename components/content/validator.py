#!/usr/bin/env python3
"""
Content Component Validator

Component-specific validation logic for content components.
"""

from typing import List, Dict, Any


def validate_content_format(content: str, format_rules: Dict[str, Any] = None) -> List[str]:
    """
    Validate content-specific format requirements.
    
    Args:
        content: The content to validate
        format_rules: Optional format rules dictionary
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Content should be properly structured paragraphs
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    if len(paragraphs) < 2:
        errors.append("Content should have at least 2 paragraphs")
    
    return errors


def validate_content_structure(content: str) -> List[str]:
    """
    Validate content structure requirements.
    
    Args:
        content: The content to validate
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Check for placeholder content
    if 'TBD' in content or 'TODO' in content or '[' in content and ']' in content:
        errors.append("Contains placeholder content (TBD, TODO, or [brackets])")
    
    # Basic content validation
    if not content.strip():
        errors.append("Content component cannot be empty")
    
    return errors


def validate_content_quality(content: str) -> List[str]:
    """
    Validate content quality requirements.
    
    Args:
        content: The content to validate
        
    Returns:
        List of validation warnings (empty if acceptable)
    """
    warnings = []
    
    # Check minimum length
    if len(content) < 200:
        warnings.append("Content may be too short for comprehensive coverage")
    
    # Check for technical content indicators
    technical_indicators = ['laser', 'cleaning', 'material', 'surface', 'process']
    found_indicators = sum(1 for indicator in technical_indicators if indicator.lower() in content.lower())
    if found_indicators < 3:
        warnings.append("Content may lack sufficient technical detail")
    
    return warnings
