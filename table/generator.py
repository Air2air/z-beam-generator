"""Enhanced table generator for new schema structures."""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
import re

logger = logging.getLogger(__name__)

class TableGenerator:
    """Generates markdown tables for technical articles from schema-driven frontmatter."""

    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], frontmatter_dict: Dict[str, Any]):
        self.context = context
        self.schema = schema
        self.frontmatter_dict = frontmatter_dict
        # No hardcoded assumptions about frontmatter structure

    def generate(self) -> Optional[str]:
        """Generate tables based on available frontmatter data."""
        tables = []
        
        # Dynamically identify table-worthy data in frontmatter
        for key, value in self.frontmatter_dict.items():
            if self._is_table_candidate(key, value):
                table = self._create_table_from_data(key, value)
                if table:
                    tables.append(table)
        
        return "\n\n".join(tables) if tables else ""
        
    def _is_table_candidate(self, key, value):
        """Determine if a frontmatter field is suitable for table representation."""
        # Tables work well for structured collections of data
        if isinstance(value, list) and len(value) > 1:
            # Check if items have consistent structure (good for tables)
            if all(isinstance(item, dict) for item in value):
                return True
                
        # Technical specifications are usually good table candidates
        elif key in ['technicalSpecifications', 'specifications', 'parameters'] and isinstance(value, dict):
            return True
            
        # Process parameters often work well as tables
        elif 'parameters' in key.lower() and (isinstance(value, dict) or isinstance(value, list)):
            return True
            
        return False
        
    def _create_table_from_data(self, key, value):
        """Create appropriate table format based on data structure."""
        if isinstance(value, list) and all(isinstance(item, dict) for item in value):
            return self._create_table_from_dict_list(key, value)
            
        elif isinstance(value, dict):
            return self._create_table_from_dict(key, value)
            
        return None
        
    def _create_table_from_dict_list(self, key, items):
        """Create table from list of dictionaries."""
        if not items:
            return None
            
        # Get all possible column headers from all items
        headers = set()
        for item in items:
            headers.update(item.keys())
        
        headers = sorted(list(headers))
        
        # Format the table title based on the key
        title = f"## {self._format_title(key)}\n\n"
        
        # Create table header
        table = "| " + " | ".join(self._format_column_name(h) for h in headers) + " |\n"
        table += "|" + "|".join(["----" for _ in headers]) + "|\n"
        
        # Create table rows
        for item in items:
            row = "| " + " | ".join(str(item.get(h, "")) for h in headers) + " |"
            table += row + "\n"
            
        return title + table
        
    def _create_table_from_dict(self, key, data):
        """Create two-column table from dictionary."""
        # Format the table title based on the key
        title = f"## {self._format_title(key)}\n\n"
        
        # Create table header
        table = "| Parameter | Value |\n|-----------|-------|\n"
        
        # Create table rows
        for param, value in data.items():
            table += f"| {self._format_column_name(param)} | {value} |\n"
            
        return title + table
        
    def _format_title(self, key):
        """Convert camelCase or snake_case to Title Case."""
        # Replace camelCase with spaces
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', key)
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1)
        # Replace underscores with spaces
        s3 = s2.replace('_', ' ')
        # Title case
        return s3.title()
        
    def _format_column_name(self, name):
        """Format column name for readability."""
        # Similar to _format_title but may have different requirements
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1)
        s3 = s2.replace('_', ' ')
        return s3.title()