#!/usr/bin/env python3
"""
Frontmatter Component Post-Processor

Component-specific post-processing logic for frontmatter components.
"""

from typing import Dict, Any
import logging
from .utils import validate_frontmatter_properties_completeness

logger = logging.getLogger(__name__)


def post_process_frontmatter(content: str, material_name: str = None, category: str = None) -> str:
    """
    Apply frontmatter-specific post-processing.
    
    Args:
        content: Raw frontmatter content
        material_name: Name of the material (optional)
        category: Material category for enhancement (required)
        
    Returns:
        Post-processed frontmatter content
    """
    # Apply property enhancement - category is required
    from utils.property_enhancer import enhance_generated_frontmatter
    content = enhance_generated_frontmatter(content, category)
    
    # Apply frontmatter-specific cleanup
    content = _cleanup_frontmatter_formatting(content)
    content = _validate_frontmatter_structure(content)
    
    return content


def _cleanup_frontmatter_formatting(content: str) -> str:
    """Clean up frontmatter formatting issues."""
    # Remove duplicate YAML delimiters
    if content.startswith('---\n---'):
        content = content.replace('---\n---', '---', 1)
    
    # Remove empty object placeholders
    content = content.replace(': {}', ': ""')
    
    # Fix common YAML formatting issues
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Fix duplicate field names
        if ':' in line and line.count(':') > 1:
            parts = line.split(':', 1)
            if len(parts) == 2:
                line = f"{parts[0].strip()}: {parts[1].strip()}"
        
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)


def _validate_frontmatter_structure(content: str) -> str:
    """Validate and fix frontmatter structure."""
    # Ensure proper YAML delimiters
    if not content.startswith('---'):
        content = f"---\n{content}"
    
    # Ensure closing delimiter exists
    yaml_end = content.find('---', 3)
    if yaml_end == -1:
        # Find the end of YAML content and add delimiter
        lines = content.split('\n')
        yaml_lines = []
        for i, line in enumerate(lines[1:], 1):  # Skip first ---
            if line.strip() and not line.startswith(' ') and ':' not in line:
                # This might be the start of markdown content
                yaml_lines = lines[:i]
                remaining_lines = lines[i:]
                content = '\n'.join(yaml_lines + ['---'] + remaining_lines)
                break
        else:
            # No markdown content found, just add closing delimiter
            content = f"{content}\n---"
    
    return content


def generate_frontmatter_summary(content: str) -> Dict[str, Any]:
    """
    Generate a summary of frontmatter completeness and quality.
    
    Args:
        content: Frontmatter content to analyze
        
    Returns:
        Dictionary with analysis results
    """
    try:
        import yaml
        
        # Extract YAML content
        if not content.startswith('---'):
            return {"error": "Not valid frontmatter format"}
        
        yaml_end = content.find('---', 3)
        if yaml_end == -1:
            return {"error": "Frontmatter not properly closed"}
        
        yaml_content = content[3:yaml_end].strip()
        frontmatter_data = yaml.safe_load(yaml_content)
        
        if not frontmatter_data:
            return {"error": "Empty frontmatter data"}
        
        # Get completeness analysis
        completeness = validate_frontmatter_properties_completeness(frontmatter_data)
        
        # Add additional metrics
        summary = {
            "total_fields": len(frontmatter_data),
            "has_properties": "properties" in frontmatter_data,
            "has_chemical_props": "chemicalProperties" in frontmatter_data,
            "has_category": "category" in frontmatter_data,
            "completeness_score": completeness["completeness"],
            "missing_sections": completeness["missing_sections"],
            "missing_properties": completeness["missing_properties"],
            "recommendations": completeness["recommendations"]
        }
        
        return summary
        
    except Exception as e:
        return {"error": f"Analysis failed: {e}"}
