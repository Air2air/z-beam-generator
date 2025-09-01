#!/usr/bin/env python3
"""
Content Component Post-Processor

Component-specific post-processing logic for content components.
"""

import re
import logging

logger = logging.getLogger(__name__)


def post_process_content(content: str, material_name: str = None) -> str:
    """
    Apply content-specific post-processing.
    
    Args:
        content: Raw content text
        material_name: Name of the material (optional)
        
    Returns:
        Post-processed content
    """
    try:
        # Clean up content formatting
        content = _fix_paragraph_structure(content)
        content = _improve_technical_language(content)
        content = _standardize_terminology(content)
        
        return content
        
    except Exception as e:
        logger.error(f"Error in content post-processing: {e}")
        return content


def _fix_paragraph_structure(content: str) -> str:
    """Fix paragraph structure and spacing."""
    # Remove excessive line breaks
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Ensure proper paragraph separation
    lines = content.split('\n')
    cleaned_lines = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped:
            cleaned_lines.append(stripped)
        elif i > 0 and i < len(lines) - 1:  # Not first or last line
            # Keep paragraph breaks
            if lines[i-1].strip() and lines[i+1].strip():
                cleaned_lines.append('')
    
    return '\n'.join(cleaned_lines)


def _improve_technical_language(content: str) -> str:
    """Improve technical language consistency."""
    # Standardize laser terminology
    replacements = {
        r'\blaser\s+clean(ing)?\b': 'laser cleaning',
        r'\bablat(ion|e)\b': 'ablation',
        r'\bfiber\s+laser\b': 'fiber laser',
        r'\bpulse(d)?\s+laser\b': 'pulsed laser',
        r'\bwave\s*length\b': 'wavelength',
        r'\bfluence\b': 'fluence',
        r'\bthreshold\b': 'ablation threshold'
    }
    
    for pattern, replacement in replacements.items():
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    
    return content


def _standardize_terminology(content: str) -> str:
    """Standardize technical terminology."""
    # Material property terminology
    property_terms = {
        r'\bdensity\s+value\b': 'density',
        r'\bmelting\s+temp(erature)?\b': 'melting point',
        r'\bthermal\s+conduct(ivity|ion)\b': 'thermal conductivity',
        r'\btensile\s+strength\b': 'tensile strength',
        r'\bYoung\'?s\s+modulus\b': 'Young\'s modulus'
    }
    
    for pattern, replacement in property_terms.items():
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    
    return content


def validate_content_quality(content: str) -> dict:
    """
    Validate content quality metrics.
    
    Args:
        content: Content to validate
        
    Returns:
        Dictionary with quality metrics
    """
    metrics = {
        "word_count": len(content.split()),
        "paragraph_count": len([p for p in content.split('\n\n') if p.strip()]),
        "technical_terms": 0,
        "readability_score": 0.0,
        "quality_issues": []
    }
    
    # Count technical terms
    technical_terms = [
        'laser', 'cleaning', 'ablation', 'wavelength', 'fluence',
        'material', 'surface', 'processing', 'thermal', 'optical'
    ]
    
    content_lower = content.lower()
    metrics["technical_terms"] = sum(1 for term in technical_terms if term in content_lower)
    
    # Basic readability assessment
    sentences = len(re.split(r'[.!?]+', content))
    if sentences > 0:
        avg_words_per_sentence = metrics["word_count"] / sentences
        # Simple readability score (lower is more readable)
        metrics["readability_score"] = min(10.0, avg_words_per_sentence / 20.0 * 10.0)
    
    # Quality checks
    if metrics["word_count"] < 150:
        metrics["quality_issues"].append("Content may be too short")
    
    if metrics["paragraph_count"] < 2:
        metrics["quality_issues"].append("Content should have multiple paragraphs")
    
    if metrics["technical_terms"] < 5:
        metrics["quality_issues"].append("Content may lack sufficient technical detail")
    
    return metrics
