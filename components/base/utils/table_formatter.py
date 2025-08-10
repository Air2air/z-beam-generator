"""Table formatting utilities for extracting and formatting markdown tables."""

import re
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class TableFormatter:
    """Utilities for processing and formatting markdown tables."""
    
    @staticmethod
    def extract_tables(lines: List[str]) -> List[Dict]:
        """Extract tables from lines of text.
        
        Args:
            lines: List of text lines that may contain markdown tables
            
        Returns:
            List[Dict]: List of extracted table data
        """
        tables = []
        current_table = []
        in_table = False
        
        for line in lines:
            line = line.strip()
            
            # Check if this line looks like a table row (contains |)
            if '|' in line and line.count('|') >= 2:
                if not in_table:
                    in_table = True
                    current_table = []
                current_table.append(line)
            else:
                # End of table or no table content
                if in_table and current_table:
                    table_data = TableFormatter._parse_table_lines(current_table)
                    if table_data:
                        tables.append(table_data)
                    current_table = []
                in_table = False
        
        # Handle case where table is at the end of content
        if in_table and current_table:
            table_data = TableFormatter._parse_table_lines(current_table)
            if table_data:
                tables.append(table_data)
        
        return tables
    
    @staticmethod
    def _parse_table_lines(lines: List[str]) -> Dict:
        """Parse a list of table lines into structured data.
        
        Args:
            lines: Lines that make up a single table
            
        Returns:
            Dict: Parsed table data with headers and rows
        """
        if len(lines) < 2:
            return {}
        
        # Clean and split first line for headers
        header_line = lines[0].strip('|').strip()
        headers = [cell.strip() for cell in header_line.split('|')]
        
        # Skip separator line (usually contains dashes)
        data_lines = lines[2:] if len(lines) > 2 else []
        
        rows = []
        for line in data_lines:
            # Clean and split data line
            data_line = line.strip('|').strip()
            cells = [cell.strip() for cell in data_line.split('|')]
            
            # Ensure we have the right number of cells
            while len(cells) < len(headers):
                cells.append('')
            
            # Create row dict
            row = {}
            for i, header in enumerate(headers):
                if i < len(cells):
                    row[header] = cells[i]
                else:
                    row[header] = ''
            
            rows.append(row)
        
        return {
            'headers': headers,
            'rows': rows,
            'column_count': len(headers)
        }
    
    @staticmethod
    def format_tables_with_headers(tables: List[Dict]) -> str:
        """Format extracted tables back into markdown with proper headers.
        
        Args:
            tables: List of table data dictionaries
            
        Returns:
            str: Formatted markdown tables
        """
        if not tables:
            return ""
        
        formatted_tables = []
        
        for table in tables:
            if not table.get('headers') or not table.get('rows'):
                continue
            
            headers = table['headers']
            rows = table['rows']
            
            # Create header row
            header_row = '| ' + ' | '.join(headers) + ' |'
            
            # Create separator row
            separator_row = '|' + ''.join([' --- |' for _ in headers])
            
            # Create data rows
            data_rows = []
            for row in rows:
                cells = []
                for header in headers:
                    cell_value = row.get(header, '').strip()
                    cells.append(cell_value)
                data_row = '| ' + ' | '.join(cells) + ' |'
                data_rows.append(data_row)
            
            # Combine all rows
            table_lines = [header_row, separator_row] + data_rows
            formatted_table = '\n'.join(table_lines)
            formatted_tables.append(formatted_table)
        
        return '\n\n'.join(formatted_tables)
    
    @staticmethod
    def validate_table_structure(content: str) -> bool:
        """Validate that table content has proper markdown table structure.
        
        Args:
            content: Content to validate
            
        Returns:
            bool: True if content contains valid table structure
        """
        lines = content.split('\n')
        table_lines = [line for line in lines if '|' in line and line.count('|') >= 2]
        
        if len(table_lines) < 2:
            return False
        
        # Check if we have at least a header and separator
        header_line = table_lines[0]
        separator_line = table_lines[1] if len(table_lines) > 1 else ""
        
        # Basic validation: separator should contain dashes
        if not re.search(r'[-:]+', separator_line):
            return False
        
        # Check header and separator have similar column counts
        header_cols = header_line.count('|')
        separator_cols = separator_line.count('|')
        
        return abs(header_cols - separator_cols) <= 1
