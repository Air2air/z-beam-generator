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
        
        # Add content constraints using normalized method
        data.update({
            "min_words": self.get_component_config("min_words"),
            "max_words": self.get_component_config("max_words"),
            "tone": self.get_component_config("tone", "professional")
        })
        
        # Get frontmatter data
        frontmatter = self.get_frontmatter_data()
        if frontmatter:
            # Extract title and description
            data["title"] = frontmatter.get("title", self.subject.capitalize())
            data["description"] = frontmatter.get("description", "")
            
            # Extract article-type specific data
            if self.article_type == "material":
                data["properties"] = frontmatter.get("properties", {})
                data["applications"] = frontmatter.get("applications", [])
            elif self.article_type == "application":
                data["industries"] = frontmatter.get("industries", [])
                data["features"] = frontmatter.get("features", [])
            elif self.article_type == "region":
                data["location"] = frontmatter.get("location", {})
                data["industries"] = frontmatter.get("industries", [])
            elif self.article_type == "thesaurus":
                data["alternateNames"] = frontmatter.get("alternateNames", [])
                data["relatedTerms"] = frontmatter.get("relatedTerms", [])
        
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