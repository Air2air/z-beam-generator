"""
Author component post-processor for content cleanup and enhancement.
"""
import re
import json
import logging

logger = logging.getLogger(__name__)


def post_process_author(content: str, material_name: str = "") -> str:
    """
    Post-process author content for consistency and quality.
    
    Args:
        content: Generated author content
        material_name: Name of the material being processed
        
    Returns:
        str: Post-processed author content
    """
    if not content or not content.strip():
        return content
    
    try:
        # Try to parse as JSON if it looks like JSON
        if content.strip().startswith(('{', '[')):
            json_data = json.loads(content)
            cleaned_data = clean_author_json(json_data)
            return json.dumps(cleaned_data, indent=2, ensure_ascii=False)
    except json.JSONDecodeError:
        pass
    
    # Clean as text content
    return clean_author_text(content, material_name)


def clean_author_json(data):
    """Clean author JSON data structure."""
    if isinstance(data, dict):
        cleaned = {}
        for key, value in data.items():
            if isinstance(value, str):
                cleaned[key] = clean_author_string_value(value, key)
            else:
                cleaned[key] = clean_author_json(value)
        return cleaned
    elif isinstance(data, list):
        return [clean_author_json(item) for item in data]
    else:
        return data


def clean_author_string_value(value: str, field_name: str = "") -> str:
    """Clean individual string values in author data."""
    if not value:
        return value
    
    # Normalize whitespace
    cleaned = re.sub(r'\s+', ' ', value.strip())
    
    # Field-specific cleaning
    if field_name.lower() in ['name', 'author', 'display_name']:
        cleaned = clean_author_name(cleaned)
    elif field_name.lower() in ['email']:
        cleaned = clean_author_email(cleaned)
    elif field_name.lower() in ['url', 'website', 'homepage']:
        cleaned = clean_author_url(cleaned)
    elif field_name.lower() in ['bio', 'description', 'about']:
        cleaned = clean_author_bio(cleaned)
    elif field_name.lower() in ['organization', 'company', 'affiliation']:
        cleaned = clean_author_organization(cleaned)
    
    return cleaned


def clean_author_text(content: str, material_name: str = "") -> str:
    """Clean author content as text."""
    lines = content.strip().split('\n')
    processed_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            processed_lines.append('')
            continue
        
        # Clean up author information lines
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            if key.lower() in ['name', 'author']:
                value = clean_author_name(value)
            elif key.lower() == 'email':
                value = clean_author_email(value)
            elif key.lower() in ['url', 'website']:
                value = clean_author_url(value)
            elif key.lower() in ['bio', 'description']:
                value = clean_author_bio(value)
            elif key.lower() in ['organization', 'company']:
                value = clean_author_organization(value)
            
            line = f"{key}: {value}"
        
        processed_lines.append(line)
    
    return '\n'.join(processed_lines)


def clean_author_name(name: str) -> str:
    """Clean author name."""
    # Remove extra whitespace and normalize
    name = re.sub(r'\s+', ' ', name.strip())
    
    # Capitalize properly (First Last format)
    parts = name.split()
    cleaned_parts = []
    for part in parts:
        if part and not part.startswith(('(', ')')):
            cleaned_parts.append(part.capitalize())
        else:
            cleaned_parts.append(part)
    
    return ' '.join(cleaned_parts)


def clean_author_email(email: str) -> str:
    """Clean author email."""
    email = email.strip().lower()
    
    # Basic email validation and cleanup
    if '@' in email and '.' in email.split('@')[1]:
        return email
    else:
        return email  # Return as-is if not a valid email format


def clean_author_url(url: str) -> str:
    """Clean author URL."""
    url = url.strip()
    
    # Ensure proper URL format
    if url and not url.startswith(('http://', 'https://')):
        if url.startswith('www.'):
            url = 'https://' + url
        elif '.' in url:
            url = 'https://' + url
    
    return url


def clean_author_bio(bio: str) -> str:
    """Clean author biography."""
    bio = re.sub(r'\s+', ' ', bio.strip())
    
    # Ensure proper sentence structure
    if bio and bio[0].islower():
        bio = bio[0].upper() + bio[1:]
    
    if bio and not bio.endswith(('.', '!', '?')):
        bio += '.'
    
    return bio


def clean_author_organization(org: str) -> str:
    """Clean author organization."""
    org = re.sub(r'\s+', ' ', org.strip())
    
    # Capitalize appropriately
    # Handle common organization types
    if org.lower().endswith((' inc', ' inc.', ' corp', ' corp.', ' ltd', ' ltd.', ' llc')):
        parts = org.split()
        cleaned_parts = [part.capitalize() if not part.endswith('.') else part.upper() for part in parts]
        return ' '.join(cleaned_parts)
    else:
        # Standard title case
        return org.title()
    
    return org
