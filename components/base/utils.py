"""
Utility classes for working with frontmatter and markdown formatting.

This module provides reusable utilities for frontmatter extraction, validation,
and markdown formatting to ensure consistent handling across components.
"""

import logging
import yaml
from typing import Dict, Any, List

from utils.string_utils import StringUtils

logger = logging.getLogger(__name__)

class FrontmatterUtils:
    """Utility methods for working with frontmatter."""
    
    @staticmethod
    def extract_frontmatter(content: str) -> Dict[str, Any]:
        """Extract frontmatter data from markdown content."""
        try:
            # Basic validation
            if not content or "---" not in content:
                logger.warning("No frontmatter delimiters found")
                return {}
                
            # Extract content between first two --- markers
            parts = content.split('---', 2)
            if len(parts) < 3:
                logger.warning("Invalid frontmatter format (missing closing delimiter)")
                return {}
                
            # The middle part is the YAML content
            yaml_content = parts[1].strip()
            
            if not yaml_content:
                logger.warning("Empty frontmatter content")
                return {}
                
            # Parse the YAML content
            try:
                parsed_data = yaml.safe_load(yaml_content)
                
                # Handle the case when frontmatter is a list instead of a dict
                if isinstance(parsed_data, list):
                    # Wrap the list in a dictionary with a "providers" key
                    frontmatter_data = {"providers": parsed_data}
                    logger.info("Converted list frontmatter to dictionary with providers key")
                elif isinstance(parsed_data, dict):
                    frontmatter_data = parsed_data
                else:
                    logger.warning(f"Unexpected frontmatter type: {type(parsed_data)}")
                    frontmatter_data = {"content": str(parsed_data)}
                    
                logger.info(f"Extracted frontmatter with {len(frontmatter_data)} fields")
                return frontmatter_data
                
            except yaml.YAMLError as e:
                logger.error(f"Error parsing frontmatter YAML: {e}")
                return {}
                
        except Exception as e:
            logger.error(f"Error extracting frontmatter: {e}")
            return {}

    @staticmethod
    def extract_frontmatter_from_file(file_path: str) -> Dict[str, Any]:
        """Extract frontmatter from a markdown file."""
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            return FrontmatterUtils.extract_frontmatter(content)
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return {}

    @staticmethod
    def create_frontmatter(data: Dict[str, Any]) -> str:
        """Create frontmatter string from data."""
        try:
            if not data:
                return ""
                
            yaml_content = yaml.safe_dump(data, default_flow_style=False, sort_keys=False)
            return f"---\n{yaml_content}---\n"
            
        except Exception as e:
            logger.error(f"Error creating frontmatter: {e}")
            return ""

    @staticmethod
    def validate_frontmatter(data: Dict[str, Any], required_fields: list = None) -> bool:
        """Validate frontmatter data against required fields."""
        if not data:
            logger.warning("Empty frontmatter data")
            return False
            
        if required_fields:
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                logger.warning(f"Missing required frontmatter fields: {', '.join(missing_fields)}")
                return False
                
        return True


class MarkdownUtils:
    """Utility methods for markdown formatting."""
    
    @staticmethod
    def format_section_title(key: str) -> str:
        """Convert a camelCase or snake_case key to Title Case."""
        # Handle non-string inputs
        if not isinstance(key, str):
            logger.warning(f"Non-string key passed to format_section_title: {type(key)}")
            try:
                # Try to convert to string
                key = str(key)
            except:
                return "Section"  # Fallback title

        # Remove underscores and handle camelCase
        if '_' in key:
            words = key.split('_')
        else:
            import re
            # Insert space before uppercase letters that follow lowercase
            words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', key)

        # Title case each word
        return ' '.join(word.capitalize() for word in words)
    
    @staticmethod
    def format_list_items(items: List[str], prefix: str = "*") -> str:
        """Format a list of items as markdown bullets."""
        if not items:
            return ""
            
        return "\n".join(f"{prefix} {item}" for item in items)

    @staticmethod
    def format_table(data: Dict[str, Any], headers: List[str] = None, 
                     format_key_func=None) -> str:
        """Format data as a markdown table."""
        if not data:
            return ""
            
        # Use provided headers or format keys as headers
        if not headers:
            headers = ["Property", "Value"]
            
        table_rows = [
            f"| {headers[0]} | {headers[1]} |",
            f"|{'-'*10}|{'-'*10}|"
        ]
        
        # Use the provided format function or fallback to the static method
        if format_key_func is None:
            format_key_func = MarkdownUtils.format_section_title
            
        for key, value in data.items():
            key_formatted = format_key_func(key)
            
            # Handle different value types
            if isinstance(value, list):
                value_str = ", ".join(str(v) for v in value)
            elif isinstance(value, dict):
                value_str = ", ".join(f"{k}: {v}" for k, v in value.items())
            else:
                value_str = str(value)
                
            table_rows.append(f"| {key_formatted} | {value_str} |")
            
        return "\n".join(table_rows)

    @staticmethod
    def generate_section(section_key: str, frontmatter_data: Dict[str, Any],
                         format_title_func=None, format_list_func=None, 
                         format_table_func=None) -> str:
        """Generate content for a specific frontmatter section."""
        section_data = frontmatter_data.get(section_key)
        if not section_data:
            return ""
        
        # Use provided formatting functions or fallback to static methods
        if format_title_func is None:
            format_title_func = MarkdownUtils.format_section_title
            
        if format_list_func is None:
            format_list_func = MarkdownUtils.format_list_items
            
        if format_table_func is None:
            format_table_func = MarkdownUtils.format_table
            
        title = format_title_func(section_key)
        content = [f"## {title}"]
        
        if isinstance(section_data, list):
            content.append(format_list_func(section_data))
        elif isinstance(section_data, dict):
            content.append(format_table_func(section_data))
        else:
            content.append(str(section_data))
            
        return "\n\n".join(content)