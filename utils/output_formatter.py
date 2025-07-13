"""Output formatter - SCHEMA-DRIVEN ONLY."""

import logging
import json
import yaml
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

def assemble_markdown(metadata: Dict[str, Any], tags: List[str], jsonld: Dict[str, Any]) -> str:
    """Assemble final markdown output - NO FALLBACKS."""
    
    if not metadata:
        logger.error("Metadata is required for output assembly")
        return None
    
    if not tags:
        logger.error("Tags are required for output assembly")
        return None
    
    if not jsonld:
        logger.error("JSON-LD is required for output assembly")
        return None
    
    try:
        output_parts = []
        
        # Add YAML frontmatter
        output_parts.append("---")
        output_parts.append(yaml.dump(metadata, default_flow_style=False, sort_keys=False))
        output_parts.append("---")
        output_parts.append("")
        
        # Add tags section (separate from frontmatter for compatibility)
        output_parts.append(f"Tags: {', '.join(tags)}")
        output_parts.append("")
        
        # Add JSON-LD structured data
        output_parts.append('<script type="application/ld+json">')
        output_parts.append(json.dumps(jsonld, indent=2))
        output_parts.append('</script>')
        
        return "\n".join(output_parts)
        
    except Exception as e:
        logger.error(f"Failed to assemble markdown: {e}", exc_info=True)
        return None

def format_output(metadata: str, tags: str, jsonld: str) -> Optional[str]:
    """
    Format the complete markdown output with proper formatting.
    
    Args:
        metadata_content: YAML frontmatter content
        tags_content: Tag string content
        json_ld_content: JSON-LD content
        
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
    """Convert character-by-character tags to proper format."""
    if not tags:
        return ""
        
    # Fix the character-by-character tag format
    # Original format: r, u, s, t, -, r, e, m, o, v, a, l, ,, ...
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
    
    return content