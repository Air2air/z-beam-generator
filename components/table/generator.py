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
        
        # Add table constraints
        data.update({
            "style": self.get_component_config("style", "technical"),
            "include_units": self.get_component_config("include_units", True)
        })
        
        # Get frontmatter data and extract ALL available fields dynamically
        frontmatter = self.get_frontmatter_data()
        if frontmatter:
            # Define table-worthy data types (objects and lists of objects)
            table_worthy_keys = []
            
            for key, value in frontmatter.items():
                # Skip simple metadata
                if key in ['name', 'description', 'website', 'author', 'tags', 'countries']:
                    continue
                    
                # Include structured data that can be tabulated
                if isinstance(value, dict) and value:  # Non-empty objects
                    table_worthy_keys.append(key)
                    data[key] = value
                elif isinstance(value, list) and value:  # Non-empty lists
                    # Check if it's a list of objects (good for tables)
                    if isinstance(value[0], dict):
                        table_worthy_keys.append(key)
                        data[key] = value
                    # Or a list of simple values that can be converted to tables
                    elif len(value) > 1:
                        table_worthy_keys.append(key)
                        data[key] = value
            
            # Store the dynamically discovered table-worthy keys
            data["table_keys"] = table_worthy_keys
            
            # Also pass all frontmatter for template flexibility as formatted YAML
            import yaml
            data["all_frontmatter"] = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
        else:
            data["table_keys"] = []
            data["all_frontmatter"] = "No frontmatter data available"
        
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