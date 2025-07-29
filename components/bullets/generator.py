"""
Bullets generator for Z-Beam Generator.

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

class BulletsGenerator(BaseComponent):
    """Generator for bullet point content."""
    
    def generate(self) -> str:
        """Generate bullet points content.
        
        Returns:
            str: The generated bullet points
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
            logger.error(f"Error generating bullets: {str(e)}")
            return self._create_error_markdown(str(e))
    
    def _prepare_data(self) -> Dict[str, Any]:
        """Prepare data for bullet points generation.
        
        Returns:
            Dict[str, Any]: Data for prompt formatting
        """
        data = super()._prepare_data()
        
        # Get component-specific configuration
        component_config = self.get_component_config()
        
        # Add bullet point constraints
        data.update({
            "count": component_config.get("count", 5),
            "style": component_config.get("style", "technical")
        })
        
        # Get frontmatter data
        frontmatter = self.get_frontmatter_data()
        if frontmatter:
            # Extract keywords if available
            keywords = frontmatter.get("keywords", [])
            if keywords:
                if isinstance(keywords, str):
                    keywords = [k.strip() for k in keywords.split(",")]
                data["keywords"] = keywords
            
            # Extract article-type specific data
            if self.article_type == "material":
                data["properties"] = frontmatter.get("properties", {})
                data["applications"] = frontmatter.get("applications", [])
            elif self.article_type == "application":
                data["industries"] = frontmatter.get("industries", [])
                data["features"] = frontmatter.get("features", [])
        
        return data
    
    def _post_process(self, content: str) -> str:
        """Post-process the bullet points content.
        
        Args:
            content: The API response content
            
        Returns:
            str: The processed bullet points
        """
        # Apply standard processing
        processed = super()._post_process(content)
        
        # Ensure content has a heading
        if not processed.lstrip().startswith("#"):
            processed = f"## Key Points about {self.subject.capitalize()}\n\n{processed}"
        
        # Ensure each non-heading line starts with a bullet point
        lines = processed.split("\n")
        result = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                result.append(line)
            elif stripped.startswith("#"):
                result.append(line)
            elif stripped.startswith("-") or stripped.startswith("*"):
                result.append(line)
            else:
                result.append(f"- {line}")
        
        return "\n".join(result)