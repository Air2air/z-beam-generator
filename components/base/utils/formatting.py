"""
Formatting utilities for Z-Beam Generator components.

This module provides common formatting functions used across different generators.
"""

import logging
import re
import json
import yaml
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def configure_yaml_formatting():
    """Configure YAML dumper to use proper formatting for strings.
    
    This applies the following formatting rules:
    1. Use literal style (|) for multiline strings to prevent backslash escaping
    2. Use quoted style (") for strings with special characters
    
    Call this function before using yaml.dump() to ensure consistent formatting.
    """
    def str_presenter(dumper, data):
        """Present strings with appropriate YAML style based on content.
        
        Args:
            dumper: YAML dumper instance
            data: String data to format
            
        Returns:
            YAML scalar node with appropriate style
        """
        # Convert data to string if it's not already
        if not isinstance(data, str):
            data = str(data)
            
        # Strip quotes if they're enclosing the entire string
        if data.startswith('"') and data.endswith('"') and len(data) > 1:
            data = data[1:-1]
            
        # Handle newlines within the string
        if '\n' in data or len(data.splitlines()) > 1:
            # Always use literal block style for multiline strings
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        
        # Use double-quoted style for strings with special characters
        if any(char in data for char in "{}[]:#,&*!|>'\"%-@\\"):
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')
            
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)
    
    # Register the presenter for string types
    yaml.add_representer(str, str_presenter)
    
    return True  # Return success flag

def format_frontmatter_with_comment(yaml_content: str, category: str = "", article_type: str = "", subject: str = "") -> str:
    """Format YAML content as frontmatter with metadata included in the YAML.
    
    Args:
        yaml_content: YAML content for frontmatter
        category: Category for metadata
        article_type: Article type for metadata
        subject: Subject for metadata
        
    Returns:
        str: Formatted frontmatter with metadata and delimiters
    """
    # Strip any existing code block markers (``` or ```) that might cause YAML parsing issues
    if yaml_content.startswith('```') and yaml_content.endswith('```'):
        yaml_content = yaml_content[3:-3].strip()
    
    # Parse the YAML content
    try:
        frontmatter_data = yaml.safe_load(yaml_content)
        if frontmatter_data is None:
            frontmatter_data = {}
        elif not isinstance(frontmatter_data, dict):
            logger.warning("Frontmatter YAML did not parse as a dictionary, creating new dictionary")
            frontmatter_data = {}
    except yaml.YAMLError:
        logger.warning("Could not parse frontmatter YAML, creating new dictionary")
        frontmatter_data = {}
    
    # Add or update metadata fields if provided
    if category:
        frontmatter_data['category'] = category
    if article_type:
        frontmatter_data['article_type'] = article_type
    if subject:
        frontmatter_data['subject'] = subject
    
    # Configure YAML for consistent formatting
    configure_yaml_formatting()
    
    # Convert back to YAML
    updated_yaml = yaml.dump(frontmatter_data, default_flow_style=False, sort_keys=False, width=float('inf'))
    
    # Add delimiters (no HTML comments)
    delimited_yaml = f"---\n{updated_yaml}---\n"
    
    # Final cleanup for any remaining backslash line continuations
    delimited_yaml = re.sub(r'"\\\s*\n\s*\\?"', '"', delimited_yaml)
    delimited_yaml = re.sub(r'\\\s*\n\s*\\', '\n', delimited_yaml)
    
    return delimited_yaml

def format_jsonld_as_yaml_markdown(jsonld: Dict[str, Any]) -> str:
    """Format JSON-LD as YAML markdown code block.
    
    Args:
        jsonld: JSON-LD data
        
    Returns:
        str: Formatted YAML markdown
        
    Raises:
        ValueError: If JSON-LD cannot be serialized
    """
    try:
        # Configure YAML for consistent formatting
        configure_yaml_formatting()
        
        yaml_str = yaml.dump(jsonld, default_flow_style=False, sort_keys=False, width=float('inf'))
        
        # Clean up any backslash line continuations
        yaml_str = re.sub(r'"\\\s*\n\s*\\?"', '"', yaml_str)
        yaml_str = re.sub(r'\\\s*\n\s*\\', '\n', yaml_str)
        
        # Convert special characters to unicode representations
        yaml_str = (yaml_str
                    .replace('\\u00b3', '³')
                    .replace('\\u00b0', '°')
                    .replace('\\u00b7', '·')
                    .replace('\\u2013', '–')
                    .replace('\\u2082', '₂')
                    .replace('\\u2083', '₃')
                    .replace('\\u00b1', '±'))
                    
        return f'```yaml\n{yaml_str}\n```'
    except (TypeError, ValueError) as e:
        raise ValueError(f"Failed to serialize JSON-LD as YAML: {e}")

def format_script_tag(json_content: str, content_type: str = "application/ld+json") -> str:
    """Format JSON content as a script tag.
    
    Args:
        json_content: JSON content
        content_type: Content type for script tag
        
    Returns:
        str: JSON content wrapped in script tag
        
    Raises:
        ValueError: If JSON content is invalid
    """
    try:
        # If the content is a dictionary, serialize it to JSON
        if isinstance(json_content, dict):
            json_content = json.dumps(json_content, indent=2)
        # If it's already a string, make sure it's valid JSON
        else:
            json.loads(json_content)
            
        script_tag = f'<script type="{content_type}">\n{json_content}\n</script>'
        return script_tag
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON content: {e}")

def format_metatags(meta_data: Dict[str, str]) -> str:
    """Format meta data as HTML meta tags.
    
    Args:
        meta_data: Dictionary of meta name/content pairs
        
    Returns:
        str: HTML meta tags
    """
    meta_tags = []
    for name, content in meta_data.items():
        # Handle property vs name attributes
        if name.startswith('og:') or name.startswith('twitter:'):
            meta_tags.append(f'<meta property="{name}" content="{content}" />')
        else:
            meta_tags.append(f'<meta name="{name}" content="{content}" />')
            
    return '\n'.join(meta_tags)

def format_markdown_table(headers: List[str], rows: List[List[str]]) -> str:
    """Format data as markdown table.
    
    Args:
        headers: List of column headers
        rows: List of rows, each row being a list of values
        
    Returns:
        str: Formatted markdown table
    """
    if not headers or not rows:
        return ""
    
    # Create header row
    table = [f"| {' | '.join(headers)} |"]
    
    # Create separator row
    separator = [f"| {' | '.join(['---' for _ in headers])} |"]
    
    # Create data rows
    data_rows = [f"| {' | '.join(row)} |" for row in rows]
    
    # Combine all rows
    return '\n'.join(table + separator + data_rows)

def format_bullet_points(items: List[str], bullet_char: str = '*') -> str:
    """Format a list of items as markdown bullet points.
    
    Args:
        items: List of items to format
        bullet_char: Character to use for bullets
        
    Returns:
        str: Formatted bullet points
    """
    return '\n'.join([f"{bullet_char} {item}" for item in items])

def format_yaml_object(data: Dict[str, Any]) -> str:
    """Format dictionary as YAML string with consistent formatting.
    
    Automatically configures YAML formatting to use proper string styles
    including literal style (|) for multiline strings.
    
    Args:
        data: Dictionary to format
        
    Returns:
        str: Formatted YAML string
        
    Raises:
        ValueError: If serialization fails
    """
    try:
        # Always configure YAML formatting before dumping
        configure_yaml_formatting()
        yaml_str = yaml.dump(data, default_flow_style=False, sort_keys=False, width=float('inf'))
        return yaml_str
    except Exception as e:
        raise ValueError(f"Failed to serialize as YAML: {e}")

def clean_html(content: str) -> str:
    """Remove HTML tags from content.
    
    Args:
        content: Content that may contain HTML tags
        
    Returns:
        str: Content with HTML tags removed
    """
    # Simple HTML tag removal using regex
    clean = re.sub(r'<[^>]*>', '', content)
    
    # Replace HTML entities
    html_entities = {
        '&nbsp;': ' ',
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&#39;': "'"
    }
    
    for entity, replacement in html_entities.items():
        clean = clean.replace(entity, replacement)
        
    return clean
