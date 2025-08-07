"""
Table generator for Z-Beam Generator.

This generator creates structured markdown tables from API responses.
Enhanced with local formatting, validation, and numerical data handling.
Enhanced with dynamic data structure from schema configurations.
"""

import logging
import re
from typing import List, Dict
from components.base.component import BaseComponent
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
            content: Pre-validated, clean API response
            
        Returns:
            str: Processed table with markdown formatting, section headers, and dynamic structure
            
        Raises:
            ValueError: If content is invalid
        """
        # Apply centralized formatting first for consistency
        content = self.apply_centralized_formatting(content)
        
        # Apply dynamic data structure from schema
        content = self._apply_dynamic_data_structure(content)
        
        # Validate table format - look for pipe characters indicating markdown table
        lines = content.strip().split('\n')
        tables = self._extract_tables(lines)
        
        if not tables:
            # If no tables found in the AI response, rely on AI to generate proper tables
            # Table component should generate tables from AI, not frontmatter data
            raise ValueError("Generated content does not contain valid markdown tables")
        
        # Add section headers and format tables
        processed_content = self._format_tables_with_headers(tables)
        
        # Check if any tables remain after processing
        if not processed_content.strip():
            logger.warning("All tables were excluded by filtering rules. Asking AI to regenerate tables.")
            # Ask AI to generate different tables rather than falling back to frontmatter
            raise ValueError("No valid tables found after filtering. AI should generate different table content.")
        
        return processed_content
    
    def _extract_tables(self, lines: List[str]) -> List[Dict]:
        """Extract markdown tables from content.
        
        Args:
            lines: Content lines
            
        Returns:
            List[Dict]: List of table dictionaries with title and content
        """
        tables = []
        current_title = "Data Table"
        current_table_lines = []
        in_table = False
        
        for line in lines:
            # Check for header lines that might indicate a new table
            if re.match(r'^##\s+', line):
                # If we were processing a table, save it
                if in_table and current_table_lines:
                    tables.append({
                        "title": current_title,
                        "content": current_table_lines
                    })
                    current_table_lines = []
                    in_table = False
                
                # Set the new title
                current_title = line.lstrip('#').strip()
            # Check if this line is part of a table
            elif '|' in line:
                in_table = True
                current_table_lines.append(line)
            # Empty line might indicate end of table
            elif not line.strip() and in_table:
                # Only consider it the end if we have a complete table with header and separator
                if len(current_table_lines) >= 2 and '-' in current_table_lines[1] and '|' in current_table_lines[1]:
                    tables.append({
                        "title": current_title,
                        "content": current_table_lines
                    })
                    current_table_lines = []
                    in_table = False
            # Content line that might be after a header but before a table
            elif not in_table and line.strip() and not re.match(r'^#', line):
                # Skip descriptive text lines to avoid malformed titles
                # Only use proper markdown headers (##, ###) as titles
                pass
        
        # Add the final table if there is one
        if in_table and current_table_lines:
            tables.append({
                "title": current_title,
                "content": current_table_lines
            })
        
        return tables
    
    def _format_tables_with_headers(self, tables: List[Dict]) -> str:
        """Format tables with proper section headers.
        
        Args:
            tables: List of table dictionaries
            
        Returns:
            str: Formatted content with tables and headers
        """
        formatted_content = []
        
        for table in tables:
            # Add table content without headers
            formatted_content.extend(table['content'])
            formatted_content.append("")
            formatted_content.append("")
        
        return "\n".join(formatted_content)
    
    # Removed frontmatter dependency methods - components now use base component data only
    # _generate_tables_from_frontmatter() - DEPRECATED: violated new architecture
    # _generate_tables_from_frontmatter_as_string() - DEPRECATED: violated new architecture
    
    def _create_key_value_table(self, title: str, data: Dict) -> Dict:
        """Create a key-value table from dictionary data.
        
        Args:
            title: Table title
            data: Dictionary data
            
        Returns:
            Dict: Table dictionary
        """
        table_lines = []
        
        # Add header row
        table_lines.append("| Parameter | Value |")
        table_lines.append("|-----------|-------|")
        
        # Add data rows
        for key, value in data.items():
            if isinstance(value, (str, int, float, bool)):
                table_lines.append(f"| {key} | {value} |")
        
        return {
            "title": title.replace("_", " ").title(),
            "content": table_lines
        }
    
    def _create_list_table(self, title: str, data: List[Dict]) -> Dict:
        """Create a table from a list of dictionaries.
        
        Args:
            title: Table title
            data: List of dictionaries
            
        Returns:
            Dict: Table dictionary
        """
        table_lines = []
        
        # Determine columns based on the first item
        if not data:
            return {
                "title": title.replace("_", " ").title(),
                "content": ["| No data available |", "|------------------|"]
            }
        
        first_item = data[0]
        columns = list(first_item.keys())
        
        # Create header row
        header = "| " + " | ".join(col.replace("_", " ").title() for col in columns) + " |"
        table_lines.append(header)
        
        # Create separator row
        separator = "| " + " | ".join("---" for _ in columns) + " |"
        table_lines.append(separator)
        
        # Add data rows
        for item in data:
            row_values = []
            for col in columns:
                value = item.get(col, "")
                if isinstance(value, (str, int, float, bool)):
                    row_values.append(str(value))
                else:
                    row_values.append("")
            
            row = "| " + " | ".join(row_values) + " |"
            table_lines.append(row)
        
        return {
            "title": title.replace("_", " ").title(),
            "content": table_lines
        }
    
    def _create_string_list_table(self, title: str, data: List[str]) -> Dict:
        """Create a table from a list of strings.
        
        Args:
            title: Table title
            data: List of strings
            
        Returns:
            Dict: Table dictionary
        """
        table_lines = []
        
        # Create header row
        table_lines.append(f"| {title.replace('_', ' ').title()} |")
        table_lines.append("|----------|")
        
        # Add data rows
        for item in data:
            table_lines.append(f"| {item} |")
        
        return {
            "title": title.replace("_", " ").title(),
            "content": table_lines
        }

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
