"""
JSON-LD component post-processor for content cleanup and enhancement.
"""
import re
import json
import logging

logger = logging.getLogger(__name__)


def post_process_jsonld(content: str, material_name: str = "") -> str:
    """
    Post-process JSON-LD content for consistency and quality.
    
    Args:
        content: Generated JSON-LD content
        material_name: Name of the material being processed
        
    Returns:
        str: Post-processed JSON-LD content
    """
    if not content or not content.strip():
        return content
    
    try:
        # Try to parse as JSON to validate structure
        json_data = json.loads(content)
        
        # Clean up the JSON structure
        cleaned_data = clean_jsonld_structure(json_data, material_name)
        
        # Return formatted JSON
        return json.dumps(cleaned_data, indent=2, ensure_ascii=False)
        
    except json.JSONDecodeError:
        # If not valid JSON, clean as text
        return clean_jsonld_text(content, material_name)


def clean_jsonld_structure(data, material_name: str = ""):
    """Clean JSON-LD data structure."""
    if isinstance(data, dict):
        cleaned = {}
        for key, value in data.items():
            # Clean string values
            if isinstance(value, str):
                cleaned[key] = clean_jsonld_string_value(value, material_name)
            else:
                cleaned[key] = clean_jsonld_structure(value, material_name)
        return cleaned
    elif isinstance(data, list):
        return [clean_jsonld_structure(item, material_name) for item in data]
    else:
        return data


def clean_jsonld_string_value(value: str, material_name: str = "") -> str:
    """Clean individual string values in JSON-LD."""
    if not value:
        return value
    
    # Normalize whitespace
    cleaned = re.sub(r'\s+', ' ', value.strip())
    
    # Clean up technical terms
    technical_replacements = {
        'laser cleaning': 'laser cleaning',
        'surface treatment': 'surface treatment',
        'industrial processing': 'industrial processing',
        'contaminant removal': 'contaminant removal'
    }
    
    for old_term, new_term in technical_replacements.items():
        cleaned = re.sub(rf'\b{re.escape(old_term)}\b', new_term, cleaned, flags=re.IGNORECASE)
    
    # Material-specific enhancements
    if material_name:
        material_lower = material_name.lower()
        if material_lower in cleaned.lower() and material_name not in cleaned:
            cleaned = re.sub(rf'\b{re.escape(material_lower)}\b', material_name, cleaned, flags=re.IGNORECASE)
    
    # Ensure proper sentence structure for descriptions
    if len(cleaned) > 50 and not cleaned.startswith(('http', 'https', 'www')):
        if cleaned and cleaned[0].islower():
            cleaned = cleaned[0].upper() + cleaned[1:]
        if not cleaned.endswith(('.', '!', '?')) and not cleaned.endswith(('/', '#')):
            cleaned += '.'
    
    return cleaned


def clean_jsonld_text(content: str, material_name: str = "") -> str:
    """Clean JSON-LD as text if JSON parsing fails."""
    lines = content.strip().split('\n')
    processed_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            processed_lines.append('')
            continue
        
        # Clean up string values in JSON-like text
        if ':' in line and ('"' in line or "'" in line):
            # Extract and clean the value part
            parts = line.split(':', 1)
            if len(parts) == 2:
                key_part = parts[0].strip()
                value_part = parts[1].strip()
                
                # If value is quoted, clean the content
                quote_match = re.search(r'["\']([^"\']*)["\']', value_part)
                if quote_match:
                    original_value = quote_match.group(1)
                    cleaned_value = clean_jsonld_string_value(original_value, material_name)
                    value_part = value_part.replace(original_value, cleaned_value)
                
                line = key_part + ': ' + value_part
        
        processed_lines.append(line)
    
    return '\n'.join(processed_lines)
