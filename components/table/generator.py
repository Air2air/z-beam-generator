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
from components.base.component import BaseComponent
from components.base.utils.formatting import format_markdown_table

logger = logging.getLogger(__name__)

class TableGenerator(BaseComponent):
    """Generator for table content with strict validation."""
    
    def _get_prompt_path(self) -> str:
        """Override to use the correct directory name.
        
        Returns:
            str: Path to prompt template
        """
        return "components/table/prompt.yaml"
    
    def _component_specific_processing(self, content: str) -> str:
        """Process the generated table.
        
        Args:
            content: Pre-validated, clean API response
            
        Returns:
            str: Processed table with markdown formatting and section headers
            
        Raises:
            ValueError: If content is invalid
        """
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
        
        # Extract headers and data
        headers = []
        rows = []
        
        # Process header row
        if len(table_lines) > 0:
            header_cells = self._extract_cells(table_lines[0])
            headers = [cell for cell in header_cells]
        
        # Process data rows (skip separator)
        for i, line in enumerate(table_lines):
            if i != 0 and i != separator_idx and i < len(table_lines):
                cells = self._extract_cells(line)
                
                # Title case the first column if it exists
                if cells and len(cells) > 0:
                    cells[0] = self._convert_to_title_case(cells[0])
                
                if cells:
                    rows.append(cells)
        
        # Use the formatting utility to create a clean markdown table
        return format_markdown_table(headers, rows)
    
    def _extract_cells(self, line: str) -> List[str]:
        """Extract and clean cells from a markdown table line.
        
        Args:
            line: Table line with pipe separators
            
        Returns:
            List[str]: List of cleaned cell values
        """
        cells = [cell.strip() for cell in line.split('|')]
        
        # Remove empty first/last elements if present (border pipes)
        if cells and not cells[0]:
            cells = cells[1:]
        if cells and not cells[-1]:
            cells = cells[:-1]
            
        return cells
            
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
    
    def _convert_to_title_case(self, text: str) -> str:
        """Convert any text to Title Case With Spaces.
        
        Args:
            text: Input text
            
        Returns:
            str: Text in Title Case With Spaces format
        """
        # First check if it's camelCase and convert it appropriately
        if self._is_likely_camel_case(text):
            # Use regex to insert space before uppercase letters
            s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1 \2', text)
            s2 = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', s1)
            text = s2
        
        # Split by spaces, underscores, or hyphens
        words = re.split(r'[ _-]+', text)
        # Title case each word and join with spaces
        return ' '.join(word.capitalize() for word in words)
    
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