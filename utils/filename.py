"""Filename utilities for safe filesystem operations."""
import re


def generate_safe_filename(material_name: str) -> str:
    """
    Generate a safe, lowercase, hyphenated filename from a material name.
    
    Args:
        material_name: The material name to convert
        
    Returns:
        A filesystem-safe filename slug
        
    Examples:
        >>> generate_safe_filename("Stainless Steel")
        'stainless-steel'
        >>> generate_safe_filename("ABS Plastic")
        'abs-plastic'
    """
    # Convert to lowercase
    safe_name = material_name.lower()
    
    # Replace spaces and underscores with hyphens
    safe_name = re.sub(r'[\s_]+', '-', safe_name)
    
    # Remove any characters that aren't alphanumeric or hyphens
    safe_name = re.sub(r'[^a-z0-9-]', '', safe_name)
    
    # Remove multiple consecutive hyphens
    safe_name = re.sub(r'-+', '-', safe_name)
    
    # Strip leading/trailing hyphens
    safe_name = safe_name.strip('-')
    
    return safe_name
