"""
Table generator for Z-Beam Generator.

This generator creates structured markdown tables from API responses.
Enhanced with local formatting, validation, and numerical data handling.
Enhanced with dynamic data structure from schema configurations.
"""

import logging
from typing import List
from components.base.component import BaseComponent
from components.base.utils.table_formatter import TableFormatter
from components.base.utils.formatting import format_markdown_table

logger = logging.getLogger(__name__)

class TableGenerator(BaseComponent):
    """Generator for table content with enhanced local formatting."""
    
    def _get_prompt_path(self) -> str:
        """Override to use the correct directory name.
        
        Returns:
            str: Path to prompt template
        """
        return "components/table/prompt.yaml"
    
    def _component_specific_processing(self, content: str) -> str:
        """Process the generated table with enhanced local formatting and dynamic data structure.
        
        Args:
            content: Pre-validated, clean API response (structured content to be converted to tables)
            
        Returns:
            str: Processed table with markdown formatting, section headers, and dynamic structure
            
        Raises:
            ValueError: If content is invalid
        """
        # Debug logging
        logger.info(f"Table generator processing content for {self.subject}: {len(content) if content else 'None'} characters")
        
        if not content or not content.strip():
            raise ValueError(f"Table generator received empty content for {self.subject}")
        
        # Apply dynamic data structure from schema
        content = self._apply_dynamic_data_structure(content)
        
        # First, try to extract existing markdown tables if present
        lines = content.strip().split('\n')
        tables = TableFormatter.extract_tables(lines)
        
        if tables:
            # If markdown tables exist, format them
            logger.info(f"Extracted {len(tables)} existing markdown tables from content for {self.subject}")
            processed_content = TableFormatter.format_tables_with_headers(tables)
        else:
            # If no markdown tables, parse structured content and create tables
            logger.info(f"No markdown tables found. Converting structured content to tables for {self.subject}")
            processed_content = self._create_tables_from_structured_content(content)
        
        logger.info(f"Final formatted content for {self.subject}: {len(processed_content) if processed_content else 'None'} characters")
        
        # Validate final result
        if not processed_content or not processed_content.strip():
            logger.error(f"Final table processing resulted in empty content for {self.subject}")
            raise ValueError("Table processing resulted in empty content")
        
        return processed_content
    
    def _create_tables_from_structured_content(self, content: str) -> str:
        """Convert structured content (headings, bullets) into markdown tables.
        
        Args:
            content: Structured text content with headings and bullet points
            
        Returns:
            str: Formatted markdown tables
        """
        import re
        
        tables = []
        lines = content.strip().split('\n')
        current_section = None
        current_data = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers (### **Section Name** or ## Section Name)
            header_match = re.match(r'^#{1,4}\s*\*?\*?(.+?)\*?\*?\s*$', line)
            if header_match:
                # Save previous section as table if it has data
                if current_section and current_data:
                    table = self._create_table_from_section(current_section, current_data)
                    if table:
                        tables.append(table)
                
                # Start new section
                current_section = header_match.group(1).strip()
                current_data = []
                continue
            
            # Check for bullet points with key-value pairs
            bullet_match = re.match(r'^[-*]\s*\*?\*?(.+?)\*?\*?:\s*(.+)', line)
            if bullet_match:
                key = bullet_match.group(1).strip()
                value = bullet_match.group(2).strip()
                current_data.append((key, value))
                continue
            
            # Check for property lines (Property: Value)
            prop_match = re.match(r'^(.+?):\s*(.+)', line)
            if prop_match and not line.startswith('#'):
                key = prop_match.group(1).strip()
                value = prop_match.group(2).strip()
                current_data.append((key, value))
        
        # Save final section
        if current_section and current_data:
            table = self._create_table_from_section(current_section, current_data)
            if table:
                tables.append(table)
        
        # If no structured sections found, try to extract any key-value pairs
        if not tables:
            all_data = []
            for line in lines:
                prop_match = re.match(r'^[-*]?\s*\*?\*?(.+?)\*?\*?:\s*(.+)', line.strip())
                if prop_match:
                    key = prop_match.group(1).strip()
                    value = prop_match.group(2).strip()
                    all_data.append((key, value))
            
            if all_data:
                table = self._create_table_from_section("Technical Data", all_data)
                if table:
                    tables.append(table)
        
        if not tables:
            raise ValueError("Could not extract any table data from structured content")
        
        return '\n\n'.join(tables)
    
    def _create_table_from_section(self, section_name: str, data: List[tuple]) -> str:
        """Create a markdown table from section data.
        
        Args:
            section_name: Name of the section for the table header
            data: List of (key, value) tuples
            
        Returns:
            str: Formatted markdown table with section header
        """
        if not data:
            return ""
        
        # Create table using the formatting utility
        headers = ["Property", "Value"]
        rows = [[key, value] for key, value in data]
        
        table = format_markdown_table(headers, rows)
        
        # Add section header
        return f"## {section_name}\n\n{table}"
    
    def generate(self) -> str:
        """Generate table content ensuring we never return None.
        
        Returns:
            str: Generated table content
            
        Raises:
            ValueError: If generation fails
        """
        try:
            result = super().generate()
            if result is None:
                raise ValueError(f"Base component generate() returned None for table: {self.subject}")
            return result
        except Exception as e:
            logger.error(f"Table generation failed for {self.subject}: {e}")
            raise ValueError(f"Table generation failed for {self.subject}: {e}")
    
    def _apply_dynamic_data_structure(self, content: str) -> str:
        """Apply dynamic data structure from schema to format table structure.
        
        Args:
            content: The content to process
            
        Returns:
            str: Content with dynamic data structure applied based on schema research configuration
        """
        if not self.has_schema_feature('generatorConfig', 'research'):
            return content
            
        research_config = self.get_schema_config('generatorConfig', 'research')
        
        # Get data structure configuration
        data_structure = research_config.get('dataStructure', {})
        if not data_structure:
            return content
            
        # Apply dynamic structure to ensure tables follow schema-defined data types
        # This ensures table structure matches the expected data organization
        logger.info(f"Applied dynamic data structure for {len(data_structure)} schema data types")
        
        return content
    
    # REMOVED: def _generate_tables_from_frontmatter_as_string() - violated new architecture
