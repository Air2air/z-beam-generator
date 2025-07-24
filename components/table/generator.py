"""
Module for generating tables from frontmatter data.

MODULE DIRECTIVES FOR AI ASSISTANTS:
1. DATA-DRIVEN CONTENT: Generate tables ONLY based on keys present in frontmatter
2. PROMPT-DRIVEN FORMATTING: All formatting directives must come from prompt.yaml
3. NO HARDCODED SECTIONS: Table sections must be derived from frontmatter structure
4. FORMAT DELEGATION: Header styles, descriptions, and table structure from prompt config
5. DYNAMIC ADAPTATION: Adapt to changes in frontmatter schema without code changes
6. NO CONTENT GENERATION: Don't generate content not in frontmatter
7. CONSISTENT NAMING: Use frontmatter key names consistently
8. NUMERICAL RANGE PROCESSING: Process numerical ranges in frontmatter to create interpolated tables
9. RANGE-BASED FILTERING: Use prompt config to determine which tables should be generated
10. OPTIMAL VALUE HIGHLIGHTING: Apply highlighting to optimal values as specified in prompt
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple, Union

from ..base import BaseComponent
from .numerical_detector import NumericalFieldDetector  # Add this import

logger = logging.getLogger(__name__)


class TableGenerator(BaseComponent):
    """Generates tables from frontmatter data based on prompt configuration."""

    def __init__(self, *args, **kwargs):
        """Initialize the table generator with flexible argument handling.
        
        Args:
            *args: Positional arguments, expecting subject and component_name
            **kwargs: Keyword arguments that may include subject or component_name
        """
        logger.info(f"TableGenerator initialized with args={args}, kwargs={kwargs}")
        
        # Extract subject from either positional or keyword arguments
        subject = None
        component_name = "table"
        
        # Handle different argument patterns
        if args:
            if isinstance(args[0], str):
                subject = args[0]
            
            if len(args) > 1 and isinstance(args[1], str):
                component_name = args[1]
        
        # Override with kwargs if provided
        if 'subject' in kwargs:
            subject = kwargs['subject']
        if 'component_name' in kwargs:
            component_name = kwargs['component_name']
            
        # Initialize the base component
        super().__init__(component_name=component_name)
        
        # Store the subject
        self.subject = subject or ""
        # Cache for configuration
        self._config = None
        
        logger.info(f"TableGenerator initialized for {self.subject} with component_name: {component_name}")

    def generate(self) -> str:
        """Generate tables dynamically for frontmatter fields containing numerical data."""
        try:
            # Step 1: Get frontmatter data
            frontmatter_data = self.get_frontmatter_data()
            if not frontmatter_data:
                logger.warning("No frontmatter data available")
                return ""
                
            # Step 2: Initialize the numerical field detector (if needed)
            if not hasattr(self, 'field_detector'):
                self.field_detector = NumericalFieldDetector()
                
            # Step 3: Score and identify fields likely to contain numerical data
            numerical_scores = self.field_detector.identify_numerical_fields(frontmatter_data)
            logger.info(f"Field numerical scores: {numerical_scores}")
            
            # Step 4: Sort fields by their numerical relevance score (highest first)
            sorted_fields = sorted(numerical_scores.items(), key=lambda x: x[1], reverse=True)
            logger.info(f"Fields sorted by numerical relevance: {[f[0] for f in sorted_fields]}")
            
            # Step 5: Process fields in order of relevance
            table_sections = []
            
            for field, score in sorted_fields:
                # Skip fields with low scores
                if score < 0.5:
                    logger.info(f"Skipping low-scoring field: {field} (score: {score})")
                    continue
                    
                logger.info(f"Processing field: {field} (score: {score})")
                value = frontmatter_data[field]
                
                # Step 6: Determine the appropriate table type for each field
                table_type = self.field_detector.suggest_table_type(field, value)
                logger.info(f"Suggested table type for {field}: {table_type}")
                
                # Step 7: Generate the appropriate table based on type
                table = ""
                if table_type == 'range' and isinstance(value, dict):
                    table = self._generate_range_table(field, value)
                elif table_type == 'percentage' and isinstance(value, list):
                    table = self._generate_percentage_table(field, value)
                elif table_type == 'metrics' and isinstance(value, list):
                    table = self._generate_metrics_table(field, value)
                elif table_type == 'standards' and isinstance(value, list):
                    table = self._generate_standards_table(field, value)
                    
                # Step 8: Add the generated table to the list if not empty
                if table:
                    logger.info(f"Generated {table_type} table for {field}: {len(table)} chars")
                    table_sections.append(table)
                else:
                    logger.info(f"No table generated for {field}")
            
            # Step 9: Combine all tables and return the result
            if table_sections:
                result = "\n\n".join(table_sections)
                logger.info(f"Generated {len(table_sections)} tables with total {len(result)} characters")
                return result
            else:
                logger.warning("No tables generated")
                return ""
                
        except Exception as e:
            logger.error(f"Error generating tables: {str(e)}", exc_info=True)
            return f"<!-- Error generating tables: {str(e)} -->"

    def _contains_range(self, text: str) -> bool:
        """Check if a string contains a numerical range."""
        if not isinstance(text, str):
            return False
            
        # Check for Unicode dashes and other range indicators
        normalized = text.replace('\u2013', '-').replace('\u2014', '-').replace('\u2015', '-')
        
        # Check for range patterns
        range_patterns = [
            r'\d+\s*[-–—]\s*\d+',  # e.g., "50-500"
            r'\d+\s*to\s*\d+',     # e.g., "50 to 500"
            r'\d+\s*±\s*\d+'       # e.g., "50 ± 5"
        ]
        
        for pattern in range_patterns:
            if re.search(pattern, normalized):
                return True
                
        return False

    def _generate_range_table(self, field: str, data: Dict[str, Any]) -> str:
        """Generate a table for dictionary data containing numerical ranges."""
        if not data:
            return ""
        
        # Create the table structure
        lines = []
        title = f"## {self._format_name(field)} for {self.subject.title()}"
        lines.append(title)
        lines.append("")
        
        # Add description
        description = f"Numerical ranges for {self.subject.lower()} {field.lower().replace('specifications', '')}:"
        lines.append(description)
        lines.append("")
        
        # Create header row
        lines.append("| **Parameter** | **Minimum** | **Low** | **Optimal** | **High** | **Maximum** |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        
        # Track if we found any valid ranges
        found_ranges = False
        
        # Process each item
        for key, value in data.items():
            # Skip non-string values
            if not isinstance(value, str):
                continue
            
            # Format the parameter name
            param_name = self._format_name(key)
            
            # Extract range info
            range_info = self._extract_range(value)
            
            if range_info:
                found_ranges = True
                min_val, max_val, unit = range_info
                
                # Create interpolated values
                step = (max_val - min_val) / 4  # 5 columns
                
                # Format values with appropriate precision
                if min_val.is_integer() and max_val.is_integer():
                    # For integer values
                    values = [
                        f"{int(min_val)}{unit}",
                        f"{int(min_val + step)}{unit}",
                        f"**{int(min_val + 2*step)}{unit}**",  # Optimal value in bold
                        f"{int(min_val + 3*step)}{unit}",
                        f"{int(max_val)}{unit}"
                    ]
                else:
                    # For decimal values
                    values = [
                        f"{min_val:.1f}{unit}",
                        f"{(min_val + step):.1f}{unit}",
                        f"**{(min_val + 2*step):.1f}{unit}**",  # Optimal value in bold
                        f"{(min_val + 3*step):.1f}{unit}",
                        f"{max_val:.1f}{unit}"
                    ]
                
                # Add row
                row = f"| {param_name} | {values[0]} | {values[1]} | {values[2]} | {values[3]} | {values[4]} |"
                lines.append(row)
        
        # If no ranges were found, return empty string
        if not found_ranges:
            return ""
        
        return "\n".join(lines)

    def _generate_percentage_table(self, field: str, data: List[Dict[str, Any]]) -> str:
        """Generate a table for list data containing percentage values."""
        if not data:
            return ""
        
        # Create the table structure
        lines = []
        title = f"## {self._format_name(field)} of {self.subject.title()}"
        lines.append(title)
        lines.append("")
        
        # Add description
        description = f"Percentage breakdown for {self.subject.lower()} {field.lower()}:"
        lines.append(description)
        lines.append("")
        
        # Determine columns
        first_item = data[0]
        columns = []
        
        # Look for component/name field
        component_field = None
        for field_name in ['component', 'name', 'material', 'element']:
            if field_name in first_item:
                component_field = field_name
                columns.append(component_field)
                break
        
        # Look for type field
        type_field = None
        for field_name in ['type', 'category', 'classification']:
            if field_name in first_item:
                type_field = field_name
                columns.append(type_field)
                break
        
        # Look for percentage field
        percentage_field = None
        for field_name in ['percentage', 'percent', 'ratio', 'composition']:
            if field_name in first_item:
                percentage_field = field_name
                columns.append(field_name)
                break
        
        # If we don't have essential fields, return empty
        if not component_field or not percentage_field:
            return ""
        
        # Create header row
        header = "| " + " | ".join(f"**{self._format_name(col)}**" for col in columns) + " |"
        lines.append(header)
        lines.append("| " + " | ".join(["---"] * len(columns)) + " |")
        
        # Process each item
        for item in data:
            values = []
            for col in columns:
                values.append(str(item.get(col, "")))
            
            # Add row
            row = "| " + " | ".join(values) + " |"
            lines.append(row)
        
        return "\n".join(lines)

    def _generate_metrics_table(self, field: str, data: List[Dict[str, Any]]) -> str:
        """Generate a table for metrics/results data."""
        if not data:
            return ""
        
        # Create the table structure
        lines = []
        title = f"## {self._format_name(field)} for {self.subject.title()}"
        lines.append(title)
        lines.append("")
        
        # Add description
        description = f"Performance metrics for {self.subject.lower()}:"
        lines.append(description)
        lines.append("")
        
        # Determine columns
        metric_field = None
        result_field = None
        
        # Check first item for field names
        if data and isinstance(data[0], dict):
            for field_name in ['metric', 'measurement', 'test', 'parameter']:
                if field_name in data[0]:
                    metric_field = field_name
                    break
            
            for field_name in ['result', 'value', 'outcome', 'performance']:
                if field_name in data[0]:
                    result_field = field_name
                    break
        
        # If we don't have both fields, return empty
        if not metric_field or not result_field:
            return ""
        
        # Create header row
        lines.append(f"| **{self._format_name(metric_field)}** | **{self._format_name(result_field)}** |")
        lines.append("| --- | --- |")
        
        # Process each item
        for item in data:
            metric = item.get(metric_field, "")
            result = item.get(result_field, "")
            
            # Add row
            row = f"| {metric} | {result} |"
            lines.append(row)
        
        return "\n".join(lines)

    def _generate_standards_table(self, field: str, data: List[Dict[str, Any]]) -> str:
        """Generate a table for standards/codes data."""
        if not data:
            return ""
        
        # Create the table structure
        lines = []
        title = f"## {self._format_name(field)} for {self.subject.title()}"
        lines.append(title)
        lines.append("")
        
        # Add description
        description = f"Applicable standards and codes for {self.subject.lower()}:"
        lines.append(description)
        lines.append("")
        
        # Determine columns
        code_field = None
        description_field = None
        
        # Check first item for field names
        if data and isinstance(data[0], dict):
            for field_name in ['code', 'standard', 'regulation', 'id']:
                if field_name in data[0]:
                    code_field = field_name
                    break
            
            for field_name in ['description', 'details', 'info', 'text']:
                if field_name in data[0]:
                    description_field = field_name
                    break
        
        # If we don't have both fields, return empty
        if not code_field or not description_field:
            return ""
        
        # Create header row
        lines.append(f"| **{self._format_name(code_field)}** | **{self._format_name(description_field)}** |")
        lines.append("| --- | --- |")
        
        # Process each item
        for item in data:
            code = item.get(code_field, "")
            description = item.get(description_field, "")
            
            # Add row
            row = f"| {code} | {description} |"
            lines.append(row)
        
        return "\n".join(lines)

    def _extract_range(self, value: str) -> Optional[Tuple[float, float, str]]:
        """Extract numerical range from a string value."""
        if not isinstance(value, str):
            return None
        
        # Unicode dash characters commonly used in specifications
        normalized = value.replace('\u2013', '-')  # en dash
        normalized = normalized.replace('\u2014', '-')  # em dash
        normalized = normalized.replace('\u2015', '-')  # horizontal bar
        
        # Remove parenthetical content but keep the units
        normalized = re.sub(r'\([^)]*\)', '', normalized)
        normalized = normalized.replace('modular', '').replace('adjustable', '').strip()
        normalized = normalized.replace('diameter', '').strip()
        
        # Common patterns for ranges
        patterns = [
            r'(\d+\.?\d*)\s*[-–—]\s*(\d+\.?\d*)\s*([a-zA-Z°%µ]+)?',  # e.g. 50-500W
            r'(\d+\.?\d*)\s*to\s*(\d+\.?\d*)\s*([a-zA-Z°%µ]+)?'       # e.g. 50 to 500W
        ]
        
        for pattern in patterns:
            match = re.search(pattern, normalized)
            if match:
                try:
                    min_val = float(match.group(1))
                    max_val = float(match.group(2))
                    unit = match.group(3) or ""
                    return (min_val, max_val, unit)
                except (ValueError, TypeError):
                    continue
        
        # Handle special case for temperature ranges with ±
        plus_minus_pattern = r'(\d+\.?\d*)\s*[±]\s*(\d+\.?\d*)\s*([a-zA-Z°%µ]+)?'
        match = re.search(plus_minus_pattern, normalized)
        if match:
            try:
                center_val = float(match.group(1))
                variation = float(match.group(2))
                min_val = center_val - variation
                max_val = center_val + variation
                unit = match.group(3) or ""
                return (min_val, max_val, unit)
            except (ValueError, TypeError):
                pass
        
        return None

    def _format_name(self, name: str) -> str:
        """Format a camelCase name as Title Case with spaces."""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1)
        return s2.title()