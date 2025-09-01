#!/usr/bin/env python3
"""
Content Component Validator

Component-specific validation logic for content components.
"""

from typing import List, Dict, Any
import re


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
    
    # Content should have a title starting with #
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    if not lines:
        errors.append("Content component cannot be empty")
        return errors
    
    # Check for main title
    has_main_title = any(line.startswith('# ') for line in lines[:5])  # Check first 5 lines
    if not has_main_title:
        errors.append("Content must start with a main title (# Title)")
    
    # Check for author byline
    byline_pattern = r'\*\*.*,\s*Ph\.D\.\s*-\s*.*\*\*'
    has_byline = any(re.search(byline_pattern, line) for line in lines[:10])
    if not has_byline:
        errors.append("Content must include author byline with format **Name, Ph.D. - Country**")
    
    # Check for section headers
    section_headers = [line for line in lines if line.startswith('## ')]
    if len(section_headers) < 2:
        errors.append("Content should have at least 2 section headers (## Section)")
    
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
    
    # Check minimum word count
    word_count = len(content.split())
    if word_count < 100:
        errors.append(f"Content too short ({word_count} words, minimum 100)")
    elif word_count > 600:
        errors.append(f"Content too long ({word_count} words, maximum 600)")
    
    # Check for technical keywords
    technical_keywords = ['laser', 'cleaning', 'wavelength', 'material', 'surface']
    found_keywords = sum(1 for keyword in technical_keywords if keyword.lower() in content.lower())
    if found_keywords < 3:
        errors.append("Content should include relevant technical keywords")
    
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
    
    # Check paragraph structure
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    if len(paragraphs) < 3:
        warnings.append("Content may benefit from more paragraph structure")
    
    # Check for repetitive content
    sentences = re.split(r'[.!?]+', content)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    
    if len(sentences) != len(set(sentences)):
        warnings.append("Content may contain repetitive sentences")
    
    # Check for appropriate technical depth
    technical_terms = ['parameters', 'specifications', 'applications', 'properties', 'process']
    found_terms = sum(1 for term in technical_terms if term.lower() in content.lower())
    if found_terms < 2:
        warnings.append("Content may benefit from more technical depth")
    
    return warnings
