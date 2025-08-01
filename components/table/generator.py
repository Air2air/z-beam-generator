"""
Table generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
"""

import logging
from typing import Dict, Any
from components.base.enhanced_component import EnhancedBaseComponent

logger = logging.getLogger(__name__)

class TableGenerator(EnhancedBaseComponent):
    """Generator for table content with strict validation."""
    
    def _post_process(self, content: str) -> str:
        """Post-process the generated table.
        
        Args:
            content: Raw API response
            
        Returns:
            str: Processed table
            
        Raises:
            ValueError: If content is invalid
        """
        # Validate and clean input
        content = self._validate_non_empty(content, "API returned empty or invalid table")
        
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