"""
Frontmatter generator for Z-Beam Generator.

MODULE DIRECTIVES FOR AI ASSISTANTS:
1. FRONTMATTER-DRIVEN: All content must be extracted from frontmatter
2. NO HARDCODEED SECTIONS: Section structure must be derived from frontmatter
3. DYNAMIC FORMATTING: Format content based on article_type from frontmatter
4. ERROR HANDLING: Raise exceptions when required frontmatter fields are missing
5. SCHEMA AWARENESS: Be aware of the schema structure for different article types
"""

"""Frontmatter generator component."""

import logging
import re
import yaml
from typing import Dict, Any
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class FrontmatterGenerator(BaseComponent):
    """Generator for article frontmatter."""
    
    def generate(self) -> str:
        """Generate frontmatter content.
        
        Returns:
            str: The generated frontmatter
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
            logger.error(f"Error generating frontmatter: {str(e)}")
            return self._create_error_markdown(str(e))
    
    def _prepare_data(self) -> Dict[str, Any]:
        """Prepare data for frontmatter generation.
        
        Returns:
            Dict[str, Any]: Data for prompt formatting
        """
        data = super()._prepare_data()
        
        # Get component-specific configuration
        component_config = self.get_component_config()
        
        # Set frontmatter fields based on article type
        if self.article_type == "material":
            data["required_fields"] = ["title", "description", "date", "author", "properties", "applications"]
        elif self.article_type == "application":
            data["required_fields"] = ["title", "description", "date", "author", "industries", "features"]
        elif self.article_type == "region":
            data["required_fields"] = ["title", "description", "date", "author", "location", "industries"]
        elif self.article_type == "thesaurus":
            data["required_fields"] = ["title", "description", "date", "author", "alternateNames", "relatedTerms"]
        else:
            data["required_fields"] = ["title", "description", "date", "author"]
        
        # Add website inclusion flag
        data["include_website"] = component_config.get("include_website", True)
        
        return data
    
    def _post_process(self, content: str) -> str:
        """Post-process the frontmatter content.
        
        Args:
            content: The API response content
            
        Returns:
            str: The processed frontmatter
        """
        # Process API response to extract YAML frontmatter
        processed = super()._post_process(content)
        
        # Ensure content has proper frontmatter format (between triple dashes)
        if "---" in processed:
            # Extract everything between first and second '---'
            parts = processed.split("---", 2)
            if len(parts) >= 3:
                yaml_content = parts[1].strip()
                
                # Validate YAML content
                try:
                    frontmatter = yaml.safe_load(yaml_content)
                    if not isinstance(frontmatter, dict):
                        frontmatter = {"title": self.subject.capitalize()}
                        yaml_content = yaml.dump(frontmatter, default_flow_style=False)
                except Exception:
                    # If YAML is invalid, create minimal valid frontmatter
                    frontmatter = {"title": self.subject.capitalize()}
                    yaml_content = yaml.dump(frontmatter, default_flow_style=False)
                
                return f"---\n{yaml_content}\n---\n"
        else:
            # Extract YAML from code blocks if present
            yaml_content = self._extract_yaml_from_code_blocks(processed)
            if yaml_content:
                return f"---\n{yaml_content}\n---\n"
            
            # If no valid YAML found, create minimal frontmatter
            minimal = {
                "title": self.subject.capitalize(),
                "description": f"Information about {self.subject}",
                "date": self._get_current_date(),
                "author": "Z-Beam Technical Writer"
            }
            yaml_content = yaml.dump(minimal, default_flow_style=False)
            return f"---\n{yaml_content}\n---\n"
    
    def _extract_yaml_from_code_blocks(self, content: str) -> str:
        """Extract YAML content from code blocks.
        
        Args:
            content: Content that might contain YAML code blocks
            
        Returns:
            str: Extracted YAML content or empty string
        """
        # Look for YAML in code blocks
        pattern = r"```ya?ml\s*([\s\S]*?)\s*```"
        match = re.search(pattern, content)
        if match:
            return match.group(1).strip()
        return ""
    
    def _get_current_date(self) -> str:
        """Get current date in YYYY-MM-DD format.
        
        Returns:
            str: Current date
        """
        import datetime
        return datetime.date.today().isoformat()
