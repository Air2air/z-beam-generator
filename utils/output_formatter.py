"""Output formatter - SCHEMA-DRIVEN ONLY."""

import logging
import json
import yaml
import re
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

def format_output(metadata: str, tags: str, jsonld: str, table: str = "") -> Optional[str]:
    """
    Format the complete markdown output with proper formatting.
    
    Args:
        metadata: YAML frontmatter content as string
        tags: Tag string content
        jsonld: JSON-LD content as string
        
    Returns:
        Properly formatted complete markdown string
    """
    try:
        # Clean up metadata (YAML)
        clean_metadata = format_yaml(metadata)
        
        # Clean up tags
        clean_tags = format_tags(tags)
        
        # Clean up JSON-LD
        clean_jsonld = format_jsonld(jsonld)
        
        # Assemble the markdown
        markdown = "---\n"
        markdown += clean_metadata
        markdown += "\n---\n\n"
        markdown += f"Tags: {clean_tags}\n\n"
        markdown += "<script type=\"application/ld+json\">\n"
        markdown += clean_jsonld
        markdown += "\n</script>"
        
        if table:
            markdown += table + "\n\n"
        
        logger.info(f"Successfully formatted output: {len(markdown)} characters")
        return markdown
    except Exception as e:
        logger.error(f"Output formatting failed: {e}", exc_info=True)
        return None

def format_yaml(content: str) -> str:
    """Remove excessive escape characters from YAML output."""
    if not content:
        return ""
    
    # Remove the wrapping quotes if they exist
    if content.startswith('"') and content.endswith('"'):
        content = content[1:-1]
    
    # Replace escaped newlines with actual newlines
    content = content.replace('\\n', '\n')
    
    # Replace escaped quotes with regular quotes
    content = content.replace('\\"', '"')
    
    # Fix special characters
    content = content.replace('\\xB2', '²')
    content = content.replace('\\u03BCm', 'μm')
    content = content.replace('\\xC2\\xB0', '°')
    
    return content

def format_tags(tags: str) -> str:
    """Format tags with proper separators."""
    if not tags:
        return ""
    
    # If tags contain kebab-case format
    if "-" in tags:
        # Case 1: Tags are running together without separators
        if "," not in tags:
            # Improved regex to catch kebab-case words properly
            pattern = r'([a-z0-9]+-[a-z0-9-]+)(?=[a-z])'
            formatted = re.sub(pattern, r'\1, ', tags)
            # Handle case where regex didn't add a comma at the end
            if not formatted.endswith(", ") and formatted != tags:
                return formatted
        
        # Case 2: Tags may already be separated by commas
        if "," in tags:
            parts = [p.strip() for p in tags.split(",")]
            return ", ".join(parts)
    
    # Case 3: Character-by-character format (r, u, s, t, -, r, e, m, o, v, a, l)
    formatted_tags = []
    current_tag = ""
    
    # Split by commas
    parts = tags.split(',')
    for part in parts:
        part = part.strip()
        if part:
            # Skip the spaces that were added as individual characters
            if part == " ":
                current_tag += "-" if current_tag else ""
            else:
                current_tag += part
        else:
            # Empty part after comma indicates end of tag
            if current_tag:
                formatted_tags.append(current_tag)
                current_tag = ""
    
    # Add the last tag if there is one
    if current_tag:
        formatted_tags.append(current_tag)
    
    # Remove duplicate tags and join with commas
    unique_tags = list(dict.fromkeys(formatted_tags))
    return ", ".join(unique_tags)

def format_jsonld(content: str) -> str:
    """Fix JSON-LD formatting by removing extra quotes."""
    if not content:
        return "{}"
    
    # Remove extra quotes at the beginning if they exist
    if content.startswith('"'):
        content = content[1:]
    
    # Remove extra quotes at the end if they exist
    if content.endswith('"') and not content.endswith('\\\"'):
        content = content[:-1]
    
    # Try to format as valid JSON with pretty-printing
    try:
        json_obj = json.loads(content)
        return json.dumps(json_obj, indent=2)
    except json.JSONDecodeError:
        # If parsing fails, return as is
        logger.warning("Could not parse JSON-LD as valid JSON, returning as-is")
        return content

def force_write_output(directory, filename, content):
    """Force write content to file with extensive error checking."""
    import os
    import logging
    
    logger = logging.getLogger("z-beam")
    
    # Ensure directory exists
    os.makedirs(directory, exist_ok=True)
    
    # Create full path
    full_path = os.path.join(directory, filename)
    
    # Try to write the file
    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Verify file was written
        if os.path.exists(full_path):
            file_size = os.path.getsize(full_path)
            logger.info(f"✅ File successfully written to {full_path} (size: {file_size} bytes)")
            return True
        else:
            logger.error(f"❌ File does not exist after writing: {full_path}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error writing file to {full_path}: {str(e)}")
        return False