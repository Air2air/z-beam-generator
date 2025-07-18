"""Output formatter - SCHEMA-DRIVEN ONLY."""

import logging
import json
import yaml
import re
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

def format_output(frontmatter, tags, jsonld, markdown_table, main_content):
    """Format all components into a final output string."""
    output_parts = []
    
    # Add frontmatter
    if frontmatter:
        output_parts.append(frontmatter)
    
    # Add tags, ensuring it's a string
    if tags:
        if isinstance(tags, list):
            tags_str = "\n".join([f"- {tag}" for tag in tags]) if tags else ""
            output_parts.append(f"tags:\n{tags_str}")
        else:
            output_parts.append(tags)
    
    # Add JSON-LD
    if jsonld:
        output_parts.append(jsonld)
    
    # Add markdown table
    if markdown_table:
        output_parts.append(markdown_table)
    
    # Add main content
    if main_content:
        output_parts.append(main_content)
    
    return "\n\n".join(output_parts)

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

def format_tags(tags):
    """Format tags as a proper YAML array."""
    if not tags:
        return "tags: []"
    
    # Make sure we have a list of tags, not a string
    if isinstance(tags, str):
        # Split by commas if it's a comma-separated string
        if ',' in tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
        # Split by spaces if it's a space-separated string
        elif ' ' in tags:
            tag_list = [tag.strip() for tag in tags.split()]
        # Otherwise just use the whole string as one tag
        else:
            tag_list = [tags.strip()]
    else:
        tag_list = tags
    
    # Create YAML formatted tag list
    formatted_tags = "tags:"
    for tag in tag_list:
        # Skip empty tags
        if not tag or tag.isspace():
            continue
        # Remove any internal newlines and normalize spacing
        clean_tag = tag.replace('\n', ' ').strip()
        if clean_tag:
            formatted_tags += f"\n- {clean_tag}"
    
    return formatted_tags

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