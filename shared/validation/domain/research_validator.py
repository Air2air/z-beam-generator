"""
Research Quality Validator

Consolidates duplicate research quality validation logic from:
- export/prompts/industry_applications.py
- export/prompts/regulatory_standards.py
- export/prompts/environmental_impact.py

Usage:
    from shared.validation.research_validator import validate_research_quality
    
    result = validate_research_quality(research_text, min_length=100, required_sections=['summary'])
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


def validate_research_quality(
    research_response: str,
    min_length: int = 100,
    required_sections: Optional[List[str]] = None,
    context: str = "research"
) -> Dict:
    """
    Validate quality of AI research response.
    
    Checks for:
    - Minimum length requirement
    - Required sections present
    - Non-empty content
    - Structured format
    
    Args:
        research_response: Research text to validate
        min_length: Minimum character count (default: 100)
        required_sections: Optional list of required section names
        context: Context for error messages (default: "research")
    
    Returns:
        Dict with keys:
            - valid: bool
            - errors: List[str]
            - warnings: List[str]
            - length: int
    
    Example:
        >>> result = validate_research_quality("Industry applications:\\nUse case 1...", min_length=50)
        >>> result['valid']
        True
    """
    errors = []
    warnings = []
    
    # Check for empty response
    if not research_response or not research_response.strip():
        errors.append(f"{context} response is empty")
        return {
            'valid': False,
            'errors': errors,
            'warnings': warnings,
            'length': 0
        }
    
    length = len(research_response)
    
    # Check minimum length
    if length < min_length:
        errors.append(
            f"{context} response too short: {length} chars "
            f"(minimum: {min_length})"
        )
    
    # Check for required sections
    if required_sections:
        missing_sections = []
        response_lower = research_response.lower()
        
        for section in required_sections:
            if section.lower() not in response_lower:
                missing_sections.append(section)
        
        if missing_sections:
            errors.append(
                f"Missing required sections: {', '.join(missing_sections)}"
            )
    
    # Check for generic/placeholder content
    generic_phrases = [
        'i cannot', 'i do not have', 'no information available',
        'placeholder', 'todo', 'tbd', 'coming soon'
    ]
    
    response_lower = research_response.lower()
    found_generic = [phrase for phrase in generic_phrases if phrase in response_lower]
    
    if found_generic:
        warnings.append(
            f"Contains generic/placeholder phrases: {', '.join(found_generic)}"
        )
    
    # Check for minimal structure (at least one newline or colon)
    if '\n' not in research_response and ':' not in research_response:
        warnings.append("Response lacks structure (no sections/lists)")
    
    is_valid = len(errors) == 0
    
    return {
        'valid': is_valid,
        'errors': errors,
        'warnings': warnings,
        'length': length
    }


def validate_citation_quality(citations: List[str], min_citations: int = 1) -> Dict:
    """
    Validate quality of research citations.
    
    Args:
        citations: List of citation strings
        min_citations: Minimum number of citations required
    
    Returns:
        Dict with validation results
    """
    errors = []
    warnings = []
    
    if not citations:
        errors.append("No citations provided")
        return {'valid': False, 'errors': errors, 'warnings': warnings}
    
    if len(citations) < min_citations:
        errors.append(
            f"Insufficient citations: {len(citations)} "
            f"(minimum: {min_citations})"
        )
    
    # Check for placeholder citations
    generic_urls = ['example.com', 'placeholder.com', 'todo.com']
    for citation in citations:
        if any(generic in citation.lower() for generic in generic_urls):
            warnings.append(f"Placeholder citation detected: {citation}")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'citation_count': len(citations)
    }
