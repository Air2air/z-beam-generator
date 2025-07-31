"""
Table generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
"""

import logging
from typing import Dict, Any
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class TableGenerator(BaseComponent):
    """Generator for table content with strict validation."""
    
    def generate(self) -> str:
        """Generate table content with strict validation.
        
        Returns:
            str: The generated table
            
        Raises:
            ValueError: If generation fails
        """
        # Strict validation - no fallbacks
        data = self._prepare_data()
        prompt = self._format_prompt(data)
        content = self._call_api(prompt)
        return self._post_process(content)
    
    def _prepare_data(self) -> Dict[str, Any]:
        """Prepare data for table generation with strict validation.
        
        Returns:
            Dict[str, Any]: Validated data for generation
            
        Raises:
            ValueError: If required data is missing
        """
        data = super()._prepare_data()
        
        # Get component configuration
        component_config = self.get_component_config()
        
        # Validate required configuration
        if "rows" not in component_config:
            raise ValueError("Required config 'rows' missing for table component")
        
        data.update({
            "rows": component_config["rows"],
            "all_frontmatter": "No frontmatter data available yet",  # Will be populated during generation pipeline
            "table_keys": ["specifications", "applications", "properties", "manufacturing"],  # Standard table data keys
            "title": f"{self.subject} Laser Cleaning Tables"
        })
        
        return data
    
    def _post_process(self, content: str) -> str:
        """Post-process the generated table.
        
        Args:
            content: Raw API response
            
        Returns:
            str: Processed table
            
        Raises:
            ValueError: If content is invalid
        """
        if not content or not content.strip():
            raise ValueError("API returned empty or invalid table")
        
        # Validate table format - look for pipe characters indicating markdown table
        lines = content.strip().split('\n')
        table_lines = [line for line in lines if '|' in line]
        
        if len(table_lines) < 2:  # Need at least header and separator
            raise ValueError("Generated content does not contain a valid markdown table")
        
        # Check for header separator line (contains dashes)
        separator_found = any('-' in line and '|' in line for line in table_lines)
        if not separator_found:
            raise ValueError("Table missing header separator row")
        
        expected_rows = self.get_component_config("rows")
        data_rows = len([line for line in table_lines if '|' in line and '-' not in line])
        
        if data_rows < expected_rows:
            raise ValueError(f"Generated {data_rows} table rows, expected {expected_rows}")
        
        return content.strip()