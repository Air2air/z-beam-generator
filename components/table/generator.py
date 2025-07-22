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
from typing import Dict, Any

from components.base import BaseComponent

logger = logging.getLogger(__name__)

class TableGenerator(BaseComponent):
    """Generates tables for articles based on frontmatter data."""
    
    def generate(self) -> str:
        """Generate tables dynamically based on frontmatter structure."""
        try:
            # 1. Get frontmatter data using standard method
            frontmatter_data = self.get_frontmatter_data()
            
            if not frontmatter_data:
                logger.warning("No frontmatter data available for table generation")
                return ""
            
            # 2. Prepare data for tables
            tables_data = self._prepare_data(frontmatter_data)
            
            if not tables_data:
                logger.info("No table-worthy data found in frontmatter")
                return ""
            
            # 3. Format prompt (not needed for tables)
            # Tables are generated directly from frontmatter, no API call needed
            
            # 4. Post-process content
            return self._post_process(tables_data)
            
        except Exception as e:
            logger.error(f"Error generating tables: {str(e)}")
            return self._create_error_markdown(str(e))
    
    def _prepare_data(self, frontmatter_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Extract table-worthy data from frontmatter."""
        tables_data = {}
        
        # Look for standard table-worthy sections
        table_sections = [
            "technicalSpecifications",
            "properties",
            "specifications",
            "dimensions"
        ]
        
        for section in table_sections:
            if section in frontmatter_data and frontmatter_data[section]:
                if isinstance(frontmatter_data[section], dict):
                    tables_data[section] = frontmatter_data[section]
        
        return tables_data
    
    def _format_prompt(self, data: Dict[str, Any]) -> str:
        """Format prompt template with data (not used in TableGenerator)."""
        # This method is not used for tables, but included for standard conformance
        return ""
    
    def _call_api(self, prompt: str) -> str:
        """Call API with prompt (not used in TableGenerator)."""
        # This method is not used for tables, but included for standard conformance
        return ""
    
    def _post_process(self, tables_data: Dict[str, Dict[str, Any]]) -> str:
        """Generate tables from prepared data."""
        if not tables_data:
            return ""
        
        tables_content = []
        for section_key, section_data in tables_data.items():
            section_title = self.format_section_title(section_key)
            tables_content.append(f"## {section_title}")
            tables_content.append(self._format_table(section_data))
        
        return "\n\n".join(tables_content)