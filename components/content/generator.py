"""
Content generator for Z-Beam Generator.

MODULE DIRECTIVES FOR AI ASSISTANTS:
1. FRONTMATTER-DRIVEN: All content must be extracted from frontmatter
2. NO HARDCODEED SECTIONS: Section structure must be derived from frontmatter
3. DYNAMIC FORMATTING: Format content based on article_type from frontmatter
4. ERROR HANDLING: Raise exceptions when required frontmatter fields are missing
5. SCHEMA AWARENESS: Be aware of the schema structure for different article types
"""

"""Content generator component."""

import logging
from typing import Dict, Any
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class ContentGenerator(BaseComponent):
    """Generator for main article content."""
    
    def generate(self) -> str:
        """Generate main article content.
        
        Returns:
            str: The generated content
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
            logger.error(f"Error generating content: {str(e)}")
            return self._create_error_markdown(str(e))
    
    def _prepare_data(self) -> Dict[str, Any]:
        """Prepare data for content generation.
        
        Returns:
            Dict[str, Any]: Data for prompt formatting
        """
        data = super()._prepare_data()
        
        # Add content constraints from config
        data.update({
            "min_words": self.get_component_config("min_words", 300),
            "max_words": self.get_component_config("max_words", 800),
            "tone": self.get_component_config("tone", "professional"),
            "style": self.get_component_config("style", "technical"),
            "audience": self.get_component_config("audience", "professionals")
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
        else:
            data["all_frontmatter"] = "No frontmatter data available"
        
        return data
    
    def _post_process(self, content: str) -> str:
        """Post-process the main content.
        
        Args:
            content: The API response content
            
        Returns:
            str: The processed content
        """
        # Apply standard processing
        processed = super()._post_process(content)
        
        # Ensure content has a top-level heading
        if not processed.lstrip().startswith("#"):
            title = self.get_frontmatter_data().get("title", self.subject.capitalize())
            processed = f"# {title}\n\n{processed}"
        
        return processed