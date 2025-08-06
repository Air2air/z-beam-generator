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

def format_frontmatter_with_comment(yaml_content: str, category: str, article_type: str, subject: str) -> str:
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
    
    # Add or update metadata fields
    frontmatter_data['category'] = category
    frontmatter_data['article_type'] = article_type
    frontmatter_data['subject'] = subject
    
    # Convert back to YAML
    updated_yaml = yaml.dump(frontmatter_data, default_flow_style=False, sort_keys=False)
    
    # Format with YAML delimiters (no HTML comments)
    return f"---\n{updated_yaml}---"

def format_jsonld_as_script(jsonld_content: Dict[str, Any]) -> str:
    """Format JSON-LD content as HTML script tag.
    
    Args:
        jsonld_content: JSON-LD content as dictionary
        
    Returns:
        str: JSON-LD content as script tag
    """
    # Format JSON with pretty indentation
    json_str = json.dumps(jsonld_content, indent=2)
    
    # Wrap in script tag
    return f'<script type="application/ld+json">\n{json_str}\n</script>'

def format_jsonld_as_markdown(jsonld_content: Dict[str, Any]) -> str:
    """Format JSON-LD content as markdown code block.
    
    Args:
        jsonld_content: JSON-LD content as dictionary
        
    Returns:
        str: JSON-LD content as markdown code block
    """
    # Format JSON with pretty indentation
    json_str = json.dumps(jsonld_content, indent=2)
    
    # Wrap in markdown code block
    return f'```json\n{json_str}\n```'

def format_jsonld_as_yaml_markdown(jsonld_content: Dict[str, Any]) -> str:
    """Format JSON-LD content as YAML markdown code block.
    
    Args:
        jsonld_content: JSON-LD content as dictionary
        
    Returns:
        str: JSON-LD content as YAML markdown code block
    """
    # Format as YAML with pretty indentation
    yaml_str = yaml.dump(jsonld_content, default_flow_style=False, sort_keys=False)
    
    # Convert special characters to unicode representations
    yaml_str = (yaml_str
                .replace('\\u00b3', '³')
                .replace('\\u00b0', '°')
                .replace('\\u00b7', '·')
                .replace('\\u2013', '–')
                .replace('\\u2082', '₂')
                .replace('\\u2083', '₃')
                .replace('\\u00b1', '±'))
    
    # Wrap in markdown code block
    return f'```yaml\n{yaml_str}\n```'

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

def format_bullet_points(points: List[str]) -> str:
    """Format list as Markdown bullet points.
    
    Args:
        points: List of bullet points
        
    Returns:
        str: Formatted bullet points
    """
    return '\n'.join([f"- {point}" for point in points]) + '\n'

def format_yaml_object(data: Dict[str, Any]) -> str:
    """Format dictionary as YAML string.
    
    Args:
        data: Dictionary to format
        
    Returns:
        str: Formatted YAML string
    """
    return yaml.dump(data, default_flow_style=False, sort_keys=False)

# This function is now redundant with EnhancedBaseComponent._validate_links
# Keeping it for backward compatibility but using a simplified implementation
def normalize_markdown_links(content: str, max_links: int = None) -> str:
    """Normalize and potentially limit markdown links in content.
    
    Args:
        content: Markdown content with links
        max_links: Maximum number of links to keep (None for no limit)
        
    Returns:
        str: Content with normalized links
    """
    # If no limit specified, return content unchanged
    if max_links is None:
        return content
        
    # Extract all markdown links
    link_pattern = r'\[(.*?)\]\((.*?)\)'
    links = re.findall(link_pattern, content)
    
    # If under the limit, return as is
    if len(links) <= max_links:
        return content
    
    # Keep only the first max_links links
    links_to_keep = links[:max_links]
    
    # Remove excess links
    modified_content = content
    for text, url in links:
        link = f'[{text}]({url})'
        if (text, url) not in links_to_keep:
            modified_content = modified_content.replace(link, text)
    
    return modified_content

def add_section_headers_to_tables(content: str, skip_sections: List[str] = None) -> str:
    """Add Markdown section headers to tables based on content.
    
    Args:
        content: Markdown content with tables
        skip_sections: List of section names to skip
        
    Returns:
        str: Content with section headers added to tables
    """
    skip_sections = skip_sections or []
    lines = content.strip().split('\n')
    
    # Extract tables
    tables = []
    current_table = []
    for line in lines:
        if line.strip() and '|' in line:
            current_table.append(line)
        elif current_table:
            # End of a table
            if len(current_table) >= 2:  # Valid table has at least header and separator
                tables.append(current_table.copy())
            current_table = []
    
    # Add the last table if exists
    if current_table and len(current_table) >= 2:
        tables.append(current_table)
    
    # Process each table
    formatted_content = []
    for table in tables:
        # Determine table type based on header content
        header = table[0].lower()
        
        # Extract section name from header content
        section_name = None
        for column in header.split('|'):
            column = column.strip()
            if column and len(column) > 3:  # Reasonable column name
                potential_name = column.title()
                if potential_name not in skip_sections:
                    section_name = potential_name
                    break
        
        # Add section header if determined
        if section_name:
            formatted_content.append(f"\n## {section_name}\n")
            formatted_content.extend(table)
            formatted_content.append("")  # Blank line after table
    
    return '\n'.join(formatted_content)
