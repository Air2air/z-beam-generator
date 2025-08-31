"""
Metatags component post-processor for content cleanup and enhancement.
"""
import re
import logging

logger = logging.getLogger(__name__)


def post_process_metatags(content: str, material_name: str = "") -> str:
    """
    Post-process metatags content for consistency and quality.
    
    Args:
        content: Generated metatags content
        material_name: Name of the material being processed
        
    Returns:
        str: Post-processed metatags content
    """
    if not content or not content.strip():
        return content
    
    lines = content.strip().split('\n')
    processed_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            processed_lines.append('')
            continue
        
        # Clean up meta tag formatting
        if line.startswith('<meta'):
            line = clean_meta_tag(line)
        
        processed_lines.append(line)
    
    processed = '\n'.join(processed_lines)
    
    # Material-specific enhancements
    if material_name:
        material_lower = material_name.lower()
        if material_lower in processed.lower() and material_name not in processed:
            processed = re.sub(rf'\b{re.escape(material_lower)}\b', material_name, processed, flags=re.IGNORECASE)
    
    return processed


def clean_meta_tag(tag: str) -> str:
    """Clean individual meta tag."""
    # Normalize whitespace
    tag = re.sub(r'\s+', ' ', tag)
    
    # Ensure proper attribute quoting
    tag = re.sub(r'(\w+)=([^"\s]+)', r'\1="\2"', tag)
    
    # Clean up content attribute values
    if 'content=' in tag:
        # Extract content value and clean it
        content_match = re.search(r'content="([^"]*)"', tag)
        if content_match:
            content_value = content_match.group(1)
            cleaned_content = clean_meta_content(content_value)
            tag = tag.replace(content_match.group(0), f'content="{cleaned_content}"')
    
    return tag


def clean_meta_content(content: str) -> str:
    """Clean meta tag content values."""
    # Normalize whitespace
    content = re.sub(r'\s+', ' ', content.strip())
    
    # Clean up technical terms
    technical_replacements = {
        'laser cleaning': 'laser cleaning',
        'surface treatment': 'surface treatment',
        'industrial processing': 'industrial processing',
        'contaminant removal': 'contaminant removal'
    }
    
    for old_term, new_term in technical_replacements.items():
        content = re.sub(rf'\b{re.escape(old_term)}\b', new_term, content, flags=re.IGNORECASE)
    
    # Ensure proper sentence structure for descriptions
    if len(content) > 50:  # Likely a description
        if content and content[0].islower():
            content = content[0].upper() + content[1:]
        if not content.endswith('.'):
            content += '.'
    
    return content
