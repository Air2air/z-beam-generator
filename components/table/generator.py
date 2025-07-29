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
import re
from typing import Dict, Any, List
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
        
        # Add table constraints
        data.update({
            "style": component_config.get("style", "technical"),
            "include_units": component_config.get("include_units", True)
        })
        
        # Get frontmatter data
        frontmatter = self.get_frontmatter_data()
        if frontmatter:
            # Extract article-type specific data for tables
            if self.article_type == "material":
                # Look for properties or specifications in frontmatter
                properties = frontmatter.get("properties", {})
                specs = frontmatter.get("technicalSpecifications", {})
                data["properties"] = properties
                data["specifications"] = specs
            elif self.article_type == "application":
                data["features"] = frontmatter.get("features", [])
                data["specifications"] = frontmatter.get("technicalSpecifications", {})
            elif self.article_type == "region":
                data["location"] = frontmatter.get("location", {})
                data["companies"] = frontmatter.get("companies", [])
        
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
        
        # Ensure content has a heading
        if not processed.lstrip().startswith("#"):
            processed = f"## {self.subject.capitalize()} Specifications\n\n{processed}"
        
        # Ensure content has a markdown table
        if "|" not in processed:
            logger.warning("Generated content does not contain a markdown table")
            processed = self._create_fallback_table() + "\n\n" + processed
        
        return processed
    
    def _create_fallback_table(self) -> str:
        """Create a fallback table when the API doesn't generate one.
        
        Returns:
            str: Markdown table
        """
        if self.article_type == "material":
            return f"""
| Property | Value | Description |
|----------|-------|-------------|
| Name | {self.subject.capitalize()} | Material |
| Type | {self.article_type.capitalize()} | Classification |
            """
        elif self.article_type == "application":
            return f"""
| Feature | Description |
|---------|-------------|
| Application | {self.subject.capitalize()} |
| Type | {self.article_type.capitalize()} |
            """
        else:
            return f"""
| Property | Value |
|----------|-------|
| Name | {self.subject.capitalize()} |
| Type | {self.article_type.capitalize()} |
            """