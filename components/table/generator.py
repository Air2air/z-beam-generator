"""
MODULE DIRECTIVES FOR AI ASSISTANTS:
1. FRONTMATTER-DRIVEN: All content must be extracted from frontmatter
2. NO HARDCODED SECTIONS: Section structure must be derived from frontmatter
3. DYNAMIC FORMATTING: Format content based on article_type from frontmatter
4. ERROR HANDLING: Raise exceptions when required frontmatter fields are missing
5. SCHEMA AWARENESS: Be aware of the schema structure for different article types
"""

# Your imports and code

import logging
import json
import re
from typing import Dict, Any

from components.base import BaseComponent

logger = logging.getLogger(__name__)

class TableGenerator(BaseComponent):
    """Generator for technical specification tables."""
    
    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], ai_provider: str = "deepseek"):
        """Initialize the table generator.
        
        Args:
            context: Context data including subject, article_type, etc.
            schema: Schema definition for table generation
            ai_provider: The AI provider to use
        """
        super().__init__(context, schema, ai_provider)
        logger.info(f"TableGenerator initialized for subject: {self.subject}")
    
    def generate(self) -> str:
        """Generate tables dynamically based on frontmatter structure."""
        try:
            frontmatter_data = self.get_frontmatter_data()
            if not frontmatter_data:
                logger.warning("No frontmatter data available for table generation")
                return ""
            
            # Look for table-worthy data in frontmatter
            tech_specs = frontmatter_data.get("technicalSpecifications", {})
            if not tech_specs:
                logger.info("No technical specifications found for table generation")
                return ""
            
            # Generate a markdown table dynamically
            table = "## Technical Specifications\n\n"
            table += "| Attribute | Value |\n"
            table += "|------------|-------|\n"
            
            # Add rows for each specification
            for key, value in tech_specs.items():
                # Format the property name using BaseComponent helper
                property_name = self.format_section_title(key)
                table += f"| {property_name} | {value} |\n"
            
            return table + "\n"
            
        except Exception as e:
            logger.error(f"Error generating tables: {e}")
            return ""