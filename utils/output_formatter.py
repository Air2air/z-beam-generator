"""Output formatter - SCHEMA-DRIVEN ONLY."""

import logging
from typing import Union, List

logger = logging.getLogger(__name__)

def format_output(frontmatter, tags, jsonld, markdown_table, main_content):
    """
    Format components into final output with proper triple backtick formatting.
    """
    try:
        # Convert any list type objects to strings
        def ensure_string(content):
            if isinstance(content, list):
                return "\n".join(content)
            elif content is None:
                return ""
            else:
                return str(content)
                
        # Format each component
        frontmatter_str = ensure_string(frontmatter).strip()
        tags_str = ensure_string(tags).strip()
        jsonld_str = ensure_string(jsonld).strip()
        table_str = ensure_string(markdown_table).strip()
        content_str = ensure_string(main_content).strip()
        
        # Start with frontmatter
        parts = []
        
        # Add frontmatter with proper formatting if it exists
        if frontmatter_str:
            # Convert from triple hyphen to triple backtick format if needed
            if frontmatter_str.startswith('---'):
                # Extract YAML content
                yaml_content = frontmatter_str.split('---', 2)[1].strip()
                parts.append(f"```yaml\n{yaml_content}\n```")
            elif not frontmatter_str.startswith('```yaml'):
                # Add triple backticks if not already present
                parts.append(f"```yaml\n{frontmatter_str}\n```")
            else:
                # Already properly formatted
                parts.append(frontmatter_str)
        
        # Add content
        if content_str:
            parts.append(content_str)
            
        # Add tags
        if tags_str:
            parts.append(tags_str)
            
        # Add JSON-LD with proper formatting if it exists
        if jsonld_str:
            # Ensure JSON-LD has proper formatting
            if jsonld_str.startswith('{') and not jsonld_str.startswith('```json'):
                parts.append(f"```json\n{jsonld_str}\n```")
            else:
                parts.append(jsonld_str)
                
        # Add tables
        if table_str:
            parts.append(table_str)
            
        # Join everything with double newlines
        return "\n\n".join(parts)
        
    except Exception as e:
        logger.error(f"Error formatting output: {e}")
        return None

def force_write_output(output_path, content):
    """
    Force write content to file, ensuring directory exists.
    """
    import os
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Error writing output: {e}")
        return False