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
from typing import Dict, Any, List, Optional
from ..base import BaseComponent

logger = logging.getLogger(__name__)

class TableGenerator(BaseComponent):
    """Generates tables from frontmatter data."""

    def __init__(self, *args, **kwargs):
        """Initialize the table generator with flexible argument handling."""
        logger.info(f"TableGenerator initialized with args={args}, kwargs={kwargs}")
        
        # Extract subject from either positional or keyword arguments
        subject = None
        component_name = "table"
        
        if len(args) >= 1:
            subject = args[0]
        elif 'subject' in kwargs:
            subject = kwargs['subject']
            
        if len(args) >= 2:
            if isinstance(args[1], str):
                component_name = args[1]
            
        # Initialize the base component
        super().__init__(component_name=component_name)
        
        # Store the subject
        self.subject = subject or ""
        logger.info(f"TableGenerator initialized for {self.subject} with component_name: {component_name}")

    def generate(self) -> str:
        """Generate tables only for numerical range data in frontmatter."""
        try:
            # Get frontmatter data
            frontmatter_data = self.get_frontmatter_data()
            if not frontmatter_data:
                logger.warning("No frontmatter data available")
                return ""
            
            # Process the technical specifications - this will always be shown if it has ranges
            table_sections = []
            
            # Check if technical specifications exist and contain ranges
            if "technicalSpecifications" in frontmatter_data:
                tech_specs_table = self._generate_tech_specs_table(frontmatter_data["technicalSpecifications"])
                if tech_specs_table:
                    table_sections.append(tech_specs_table)
                    
            # Look for other sections that might contain numerical ranges
            other_sections = [
                "composition", 
                "outcomes", 
                "environmentalImpact",
                "compatibility",
                "regulatoryStandards"
            ]
            
            # Skip sections with detailed text descriptions
            skip_sections = ["applications"]
            
            # Return the combined table content
            if table_sections:
                return "\n\n".join(table_sections)
            else:
                logger.warning("No tables with numerical ranges were generated")
                return ""
                
        except Exception as e:
            logger.error(f"Error generating tables: {str(e)}", exc_info=True)
            return f"<!-- Error generating tables: {str(e)} -->"

    def _load_prompt_config(self) -> Dict[str, Any]:
        """Load prompt configuration safely."""
        try:
            # Use built-in method from BaseComponent to load configuration
            config = self.load_prompt_config()
            return config
        except Exception as e:
            logger.error(f"Error loading table configuration: {str(e)}")
            return {}

    def _get_default_config(self) -> Dict[str, Any]:
        """Return a default minimal configuration."""
        return {
            "format": {
                "header_style": "bold",
                "include_descriptions": True,
                "section_title_format": "## {title}"
            }
        }

    def _process_section(self, section_name: str, data: Any) -> str:
        """Process a section of the frontmatter data."""
        if section_name == "technicalSpecifications":
            return self._generate_tech_specs_table(data)
        elif section_name == "composition" and isinstance(data, list):
            return self._generate_composition_table(data)
        elif section_name == "applications" and isinstance(data, list):
            return self._generate_applications_table(data)
        elif section_name == "outcomes" and isinstance(data, list):
            return self._generate_outcomes_table(data)
        elif section_name == "environmentalImpact" and isinstance(data, list):
            return self._generate_environmental_table(data)
        elif section_name == "compatibility" and isinstance(data, list):
            return self._generate_compatibility_table(data)
        elif section_name == "regulatoryStandards" and isinstance(data, list):
            return self._generate_regulatory_table(data)
        return ""

    def _generate_tech_specs_table(self, data: Dict[str, Any]) -> str:
        """Generate a table for technical specifications with focus on numerical ranges."""
        if not data:
            return ""
        
        lines = []
        lines.append(f"## Technical Specifications for Laser Cleaning {self.subject.title()}")
        lines.append("")
        lines.append("Comprehensive parameters for optimal laser cleaning:")
        lines.append("")
        
        # Create header row
        lines.append("| **Parameter** | **Minimum** | **Low** | **Optimal** | **High** | **Maximum** |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        
        # Track if we found any valid ranges
        found_ranges = False
        
        # Process each specification
        for key, value in data.items():
            # Format the parameter name
            param_name = self._format_name(key)
            
            # Check if it's a range
            range_info = self._extract_range(value)
            
            if range_info:
                found_ranges = True
                min_val, max_val, unit = range_info
                # Create interpolated values
                step = (max_val - min_val) / 4  # 5 columns
                
                # Format values with appropriate precision
                # Use the most appropriate format based on the values
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
                        f"{min_val + step:.1f}{unit}",
                        f"**{min_val + 2*step:.1f}{unit}**",  # Optimal value in bold
                        f"{min_val + 3*step:.1f}{unit}",
                        f"{max_val:.1f}{unit}"
                    ]
                
                # Add row
                row = f"| {param_name} | {values[0]} | {values[1]} | {values[2]} | {values[3]} | {values[4]} |"
                lines.append(row)
    
        # If no ranges were found, add a note
        if not found_ranges:
            lines.append("| No numerical ranges found in technical specifications | | | | | |")
    
        return "\n".join(lines)

    def _generate_composition_table(self, data: List[Dict[str, Any]]) -> str:
        """Generate a table for composition data."""
        if not data:
            return ""
        
        lines = []
        lines.append(f"## Composition of {self.subject.title()}")
        lines.append("")
        lines.append(f"{self.subject.title()}'s mineral composition affecting laser cleaning performance:")
        lines.append("")
        
        # Create header row
        lines.append("| **Component** | **Type** | **Percentage** |")
        lines.append("| --- | --- | --- |")
        
        # Process each component
        for item in data:
            component = item.get("component", "")
            comp_type = item.get("type", "")
            percentage = item.get("percentage", "")
            
            row = f"| {component} | {comp_type} | {percentage} |"
            lines.append(row)
        
        return "\n".join(lines)

    def _generate_applications_table(self, data: List[Dict[str, Any]]) -> str:
        """Generate a table for applications data."""
        if not data:
            return ""
        
        lines = []
        lines.append(f"## Applications for {self.subject.title()} Laser Cleaning")
        lines.append("")
        lines.append("Key use cases with detailed implementation:")
        lines.append("")
        
        # Create header row
        lines.append("| **Application** | **Description** |")
        lines.append("| --- | --- |")
        
        # Process each application
        for item in data:
            name = item.get("name", "")
            description = item.get("description", "")
            
            row = f"| {name} | {description} |"
            lines.append(row)
        
        return "\n".join(lines)

    def _generate_outcomes_table(self, data: List[Dict[str, Any]]) -> str:
        """Generate a table for outcomes data."""
        if not data:
            return ""
        
        lines = []
        lines.append(f"## Performance Metrics for {self.subject.title()} Laser Cleaning")
        lines.append("")
        lines.append("Verified cleaning results and quality measurements:")
        lines.append("")
        
        # Create header row
        lines.append("| **Metric** | **Result** |")
        lines.append("| --- | --- |")
        
        # Process each outcome
        for item in data:
            metric = item.get("metric", "")
            result = item.get("result", "")
            
            row = f"| {metric} | {result} |"
            lines.append(row)
        
        return "\n".join(lines)

    def _generate_environmental_table(self, data: List[Dict[str, Any]]) -> str:
        """Generate a table for environmental impact data."""
        if not data:
            return ""
        
        lines = []
        lines.append(f"## Environmental Benefits of {self.subject.title()} Laser Cleaning")
        lines.append("")
        lines.append("Quantifiable environmental advantages compared to traditional methods:")
        lines.append("")
        
        # Create header row
        lines.append("| **Benefit** | **Impact** |")
        lines.append("| --- | --- |")
        
        # Process each benefit
        for item in data:
            benefit = item.get("benefit", "")
            description = item.get("description", "")
            
            row = f"| {benefit} | {description} |"
            lines.append(row)
        
        return "\n".join(lines)

    def _generate_compatibility_table(self, data: List[Dict[str, Any]]) -> str:
        """Generate a table for compatibility data."""
        if not data:
            return ""
        
        lines = []
        lines.append(f"## Material Compatibility with {self.subject.title()}")
        lines.append("")
        lines.append("Other materials compatible with similar laser cleaning techniques:")
        lines.append("")
        
        # Create header row
        lines.append("| **Material** | **Application** |")
        lines.append("| --- | --- |")
        
        # Process each compatibility item
        for item in data:
            material = item.get("material", "")
            application = item.get("application", "")
            
            row = f"| {material} | {application} |"
            lines.append(row)
        
        return "\n".join(lines)

    def _generate_regulatory_table(self, data: List[Dict[str, Any]]) -> str:
        """Generate a table for regulatory standards data."""
        if not data:
            return ""
        
        lines = []
        lines.append(f"## Regulatory Standards for {self.subject.title()} Laser Cleaning")
        lines.append("")
        lines.append("Applicable codes and compliance requirements:")
        lines.append("")
        
        # Create header row
        lines.append("| **Code** | **Description** |")
        lines.append("| --- | --- |")
        
        # Process each standard
        for item in data:
            code = item.get("code", "")
            description = item.get("description", "")
            
            row = f"| {code} | {description} |"
            lines.append(row)
        
        return "\n".join(lines)

    def _extract_range(self, value: str) -> Optional[tuple]:
        """Extract numerical range from a string value."""
        if not isinstance(value, str):
            return None
        
        # Unicode dash characters commonly used in specifications
        value = value.replace('\u2013', '-')  # en dash
        value = value.replace('\u2014', '-')  # em dash
        value = value.replace('\u2015', '-')  # horizontal bar
        
        # Remove parenthetical content but keep the units
        value = re.sub(r'\([^)]*\)', '', value)
        value = value.replace('modular', '').replace('adjustable', '').strip()
        
        # Common patterns for ranges
        patterns = [
            r'(\d+\.?\d*)\s*[-–—]\s*(\d+\.?\d*)\s*([a-zA-Z°%µ]+)?',  # e.g. 50-500W
            r'(\d+\.?\d*)\s*to\s*(\d+\.?\d*)\s*([a-zA-Z°%µ]+)?'       # e.g. 50 to 500W
        ]
        
        for pattern in patterns:
            match = re.search(pattern, value)
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
        match = re.search(plus_minus_pattern, value)
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