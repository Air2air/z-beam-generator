"""
Caption component post-processor for content cleanup and enhancement.
"""
import re
import logging

logger = logging.getLogger(__name__)


def post_process_caption(content: str, material_name: str = "") -> str:
    """
    Post-process caption content for consistency and quality.
    
    Args:
        content: Generated caption content
        material_name: Name of the material being processed
        
    Returns:
        str: Post-processed caption content
    """
    if not content or not content.strip():
        return content
    
    # Clean up common formatting issues
    processed = content.strip()
    
    # Ensure proper sentence structure
    processed = re.sub(r'\s+', ' ', processed)  # Normalize whitespace
    processed = re.sub(r'\.{2,}', '.', processed)  # Remove multiple periods
    
    # Capitalize first letter if not already
    if processed and processed[0].islower():
        processed = processed[0].upper() + processed[1:]
    
    # Ensure ends with period if it's a complete sentence
    if processed and not processed.endswith(('.', '!', '?')):
        processed += '.'
    
    # Clean up technical terms
    technical_replacements = {
        'laser cleaning': 'laser cleaning',
        'contaminant': 'contaminant',
        'substrate': 'substrate',
        'surface': 'surface'
    }
    
    for old_term, new_term in technical_replacements.items():
        processed = re.sub(rf'\b{re.escape(old_term)}\b', new_term, processed, flags=re.IGNORECASE)
    
    # Material-specific enhancements
    if material_name:
        material_lower = material_name.lower()
        if material_lower in processed.lower() and material_name not in processed:
            processed = re.sub(rf'\b{re.escape(material_lower)}\b', material_name, processed, flags=re.IGNORECASE)
    
    return processed
