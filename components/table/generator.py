"""
Table generator for Z-Beam Generator.

This module provides a TableGenerator component that:
1. Generates Markdown tables with validation
2. Maintains clean Markdown format for Next.js processing
3. Performs validation to ensure table quality
4. Adds section headers to tables for better organization

Configuration options:
- rows: Number of expected rows (int)
"""

import logging
import re
from typing import List
from components.base.enhanced_component import EnhancedBaseComponent

logger = logging.getLogger(__name__)

class TableGenerator(EnhancedBaseComponent):
    """Generator for table content with strict validation."""
    
    def _get_prompt_path(self) -> str:
        """Override to use the correct directory name.
        
        Returns:
            str: Path to prompt template
        """
        return "components/table/prompt.yaml"
    
    def _post_process(self, content: str) -> str:
        """Post-process the generated table.
        
        Args:
            content: Raw API response
            
        Returns:
            str: Processed table with markdown formatting and section headers
            
        Raises:
            ValueError: If content is invalid
        """
        # Validate and clean input
        content = self._validate_non_empty(content, "API returned empty or invalid table")
        
        # Validate table format - look for pipe characters indicating markdown table
        lines = content.strip().split('\n')
        original_table_lines = [line for line in lines if '|' in line]
        
        if len(original_table_lines) < 2:  # Need at least header and separator
            raise ValueError("Generated content does not contain a valid markdown table")
        
        # Check for header separator line (contains dashes)
        separator_found = any('-' in line and '|' in line for line in original_table_lines)
        if not separator_found:
            raise ValueError("Table missing header separator row")
        
        expected_rows = self.get_component_config("rows", 3)
        original_data_rows = len([line for line in original_table_lines if '|' in line and '-' not in line])
        
        if original_data_rows < expected_rows:
            raise ValueError(f"Generated {original_data_rows} table rows, expected {expected_rows}")
        
        # Split into tables and add headers, potentially excluding some tables
        processed_content = self._add_section_headers(lines)
        
        # Check if any tables remain after filtering
        if not processed_content.strip():
            logger.warning("All tables were excluded by filtering rules. Returning empty content.")
        
        return processed_content
    
    def _add_section_headers(self, lines: List[str]) -> str:
        """Add Markdown section headers to tables based on their content.
        
        Args:
            lines: List of content lines
            
        Returns:
            str: Content with added section headers
        """
        # Get sections to exclude from component config
        skip_sections = self.get_component_config("skip_sections", [
            # Default sections to skip if not specified in config
            "Keywords",
            "Author Information",
            "Application Examples",
            "Benefits",
            "Geographic Distribution", 
            "Location Details",
            "Compatible Materials"
        ])
        
        # Extract tables
        tables = []
        current_table = []
        for line in lines:
            if line.strip() and '|' in line:
                current_table.append(line)
            elif current_table:
                tables.append(current_table)
                current_table = []
            # Skip empty lines
        
        if current_table:
            tables.append(current_table)
        
        # Process each table and add headers
        result_lines = []
        for table in tables:
            if not table:
                continue
                
            # Generate appropriate header based on table content
            header = self._generate_section_header(table)
            
            # Skip this table entirely if its type is in the exclude list
            if header in skip_sections:
                logger.info(f"Skipping table with header: {header}")
                continue
            
            # Add header for included tables
            if header:
                result_lines.append("")
                result_lines.append(f"### {header}")
                result_lines.append("")
            
            # Format table
            formatted_table = self._ensure_consistent_formatting(table)
            result_lines.append(formatted_table)
            result_lines.append("")
        
        return "\n".join(result_lines)
    
    def _generate_section_header(self, table_lines: List[str]) -> str:
        """Generate an appropriate section header based on table content.
        
        Args:
            table_lines: List of table lines
            
        Returns:
            str: Section header
        """
        # Extract header row
        if not table_lines or len(table_lines) < 2:
            return "Data Table"
        
        header_row = table_lines[0]
        columns = [col.strip() for col in header_row.split('|') if col.strip()]
        
        # Common mapping patterns
        header_mappings = {
            "Field": "Author Information",      # Will be excluded
            "Parameter": "Technical Parameters",
            "Property": "Technical Properties",
            "Component": "Material Composition",
            "Name": "Application Examples",      # Will be excluded
            "Benefit": "Benefits",               # Will be excluded
            "Code": "Compliance Standards",
            "Metric": "Quality Metrics",
            "Material": "Compatible Materials",  # Will be excluded
            "Country": "Geographic Distribution", # Will be excluded
            "Location": "Location Details",      # Will be excluded
            "Keyword": "Keywords"                # Will be excluded
        }
        
        # Check for specific patterns
        for key, header in header_mappings.items():
            if any(key in col for col in columns):
                return header
                
        # Check for Parameter + Value pattern specifically for Laser Parameters
        if "Parameter" in columns and "Value" in columns:
            # Check if any parameter contains "laser", "power", "pulse", etc.
            for line in table_lines[2:]:  # Skip header and separator
                cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                if cells and any(term in cells[0].lower() for term in ["power", "pulse", "wavelength", "laser"]):
                    return "Laser Parameters"
        
        # Default
        return "Data Table"
    
    def _ensure_consistent_formatting(self, table_lines: list) -> str:
        """Ensure consistent table formatting.
        
        Args:
            table_lines: List of markdown table lines
            
        Returns:
            str: Consistently formatted markdown table
        """
        # Find the separator line index
        separator_idx = 0
        for i, line in enumerate(table_lines):
            if '-' in line and '|' in line:
                separator_idx = i
                break
        
        # Count the number of columns
        max_columns = 0
        for line in table_lines:
            pipe_count = line.count('|')
            # Adjust count for border pipes
            if line.strip().startswith('|'):
                pipe_count -= 1
            if line.strip().endswith('|'):
                pipe_count -= 1
            max_columns = max(max_columns, pipe_count + 1)
        
        # Format the table with consistent spacing
        formatted_lines = []
        
        # Process each line
        for i, line in enumerate(table_lines):
            cells = [cell.strip() for cell in line.split('|')]
            
            # Remove empty first/last elements if present
            if cells and not cells[0]:
                cells = cells[1:]
            if cells and not cells[-1]:
                cells = cells[:-1]
            
            # Ensure all rows have the same number of columns
            while len(cells) < max_columns:
                cells.append('')
            
            # Format based on whether this is the separator line
            if i == separator_idx:
                formatted_cells = ['---' for _ in cells]
                formatted_lines.append('| ' + ' | '.join(formatted_cells) + ' |')
            # Format the first row (table headers) normally
            elif i == 0:
                formatted_lines.append('| ' + ' | '.join(cells) + ' |')
            # For data rows, format keys to title case with spaces if first column
            elif i > separator_idx and len(cells) > 0:
                # Convert first cell (key) to title case with spaces
                if self._is_likely_camel_case(cells[0]):
                    cells[0] = self._camel_to_title_case(cells[0])
                formatted_lines.append('| ' + ' | '.join(cells) + ' |')
            else:
                formatted_lines.append('| ' + ' | '.join(cells) + ' |')
        
        return '\n'.join(formatted_lines)
    
    def _is_likely_camel_case(self, text: str) -> bool:
        """Check if a string is likely in camelCase format.
        
        Args:
            text: String to check
            
        Returns:
            bool: True if likely camelCase
        """
        # Simple heuristic: contains lowercase followed by uppercase
        if not text:
            return False
        
        return any(prev.islower() and current.isupper() 
                  for prev, current in zip(text[:-1], text[1:]))
    
    def _camel_to_title_case(self, text: str) -> str:
        """Convert camelCase to Title Case With Spaces.
        
        Args:
            text: camelCase text
            
        Returns:
            str: Title Case With Spaces
        """
        # Use regex to insert space before uppercase letters
        s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1 \2', text)
        s2 = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', s1)
        
        # Title case the result
        return s2.title()