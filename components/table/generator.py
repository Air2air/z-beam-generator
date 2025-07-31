"""
Table generator for Z-Beam Generator.

MODULE DIRECTIVES FOR AI ASSISTANTS:
1. FRONTMATTER-DRIVEN: All content must be extracted from frontmatter
2. NO HARDCODED SECTIONS: Section structure must be derived from frontmatter
3. DYNAMIC FORMATTING: Format content based on article_type from frontmatter
4. ERROR HANDLING: Raise exceptions when required frontmatter fields are missing
5. SCHEMA AWARENESS: Be aware of the schema structure for different article types
"""

import logging
from typing import Dict, Any
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class TableGenerator(BaseComponent):
    """Generator for table content."""
    
    def generate(self) -> str:
        """Generate table content.
        
        Returns:
            str: The generated table
        """
        try:
            # 1. Prepare data for prompt
            data = self._prepare_data()
            
            # 2. Format prompt
            prompt = self._format_prompt(data)
            
            # 3. Call API
            content = self._call_api(prompt)
            
            # 4. Post-process content
            return self._post_process(content)
        except Exception as e:
            logger.error(f"Error generating table: {str(e)}")
            return self._create_error_markdown(str(e))
    
    def _prepare_data(self) -> Dict[str, Any]:
        """Prepare data for table generation.
        
        Returns:
            Dict[str, Any]: Data for prompt formatting
        """
        data = super()._prepare_data()
        
        # Get component-specific configuration
        component_config = self.get_component_config()
        
        # Add table-specific configuration
        data.update({
            "table_type": component_config.get("table_type", "comparison"),
            "max_rows": component_config.get("max_rows", 10),
            "include_units": component_config.get("include_units", True)
        })
        
        # Get frontmatter data and include ALL available structured data
        frontmatter = self.get_frontmatter_data()
        if frontmatter:
            # Include all frontmatter data dynamically
            for key, value in frontmatter.items():
                if value:  # Only include non-empty values
                    data[key] = value
            
            # Store list of available keys for template iteration
            data["available_keys"] = [k for k, v in frontmatter.items() if v]
            
            # Also provide the complete frontmatter as formatted YAML
            import yaml
            data["all_frontmatter"] = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
            
            logger.info(f"Using frontmatter data with {len(frontmatter)} fields for table generation")
        else:
            data["all_frontmatter"] = "No frontmatter data available"
            logger.warning("No frontmatter data available for table generation")
        
        return data
    
    def _post_process(self, content: str) -> str:
        """Post-process the table content.
        
        Args:
            content: The API response content
            
        Returns:
            str: The processed table
        """
        # Apply standard processing
        processed = super()._post_process(content)
        
        # Ensure content is formatted as a proper markdown table
        if '|' not in processed:
            # Convert to table format if not already
            lines = [line.strip() for line in processed.split('\n') if line.strip()]
            if lines:
                # Create a simple two-column table
                table_lines = ["| Property | Value |", "|----------|-------|"]
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        table_lines.append(f"| {key.strip()} | {value.strip()} |")
                processed = '\n'.join(table_lines)
        
        return processed