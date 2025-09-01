#!/usr/bin/env python3
"""
Tags component post-processor for content cleanup and enhancement.
"""
import re
import logging

logger = logging.getLogger(__name__)


def post_process_tags(content: str, material_name: str = "") -> str:
    """
    Post-process tags content for consistency and quality.
    
    Args:
        content: Generated tags content
        material_name: Name of the material being processed
        
    Returns:
        str: Post-processed tags content
    """
    if not content or not content.strip():
        return content
    
    # Split and clean tags
    tags = [tag.strip() for tag in content.split(',') if tag.strip()]
    processed_tags = []
    
    for tag in tags:
        # Convert to lowercase
        tag = tag.lower()
        
        # Replace spaces with hyphens
        tag = re.sub(r'\s+', '-', tag)
        
        # Remove special characters except hyphens
        tag = re.sub(r'[^a-z0-9-]', '', tag)
        
        # Remove multiple consecutive hyphens
        tag = re.sub(r'-+', '-', tag)
        
        # Remove leading/trailing hyphens
        tag = tag.strip('-')
        
        # Skip empty tags
        if not tag:
            continue
        
        # Skip duplicates
        if tag not in processed_tags:
            processed_tags.append(tag)
    
    # Material-specific enhancements
    if material_name:
        material_tag = material_name.lower().replace(' ', '-')
        material_tag = re.sub(r'[^a-z0-9-]', '', material_tag)
        if material_tag and material_tag not in processed_tags:
            processed_tags.insert(0, material_tag)
    
    # Ensure essential tags are present
    essential_tags = ['laser-cleaning']
    for essential in essential_tags:
        if essential not in processed_tags:
            processed_tags.append(essential)
    
    # Sort tags for consistency
    priority_tags = ['laser-cleaning', 'industrial', 'precision']
    priority_found = [tag for tag in processed_tags if tag in priority_tags]
    other_tags = sorted([tag for tag in processed_tags if tag not in priority_tags])
    
    # Combine priority and other tags
    final_tags = priority_found + other_tags
    
    # Remove duplicates while preserving order
    seen = set()
    unique_tags = []
    for tag in final_tags:
        if tag not in seen:
            seen.add(tag)
            unique_tags.append(tag)
    
    return ', '.join(unique_tags)
