"""
Tags generator for Z-Beam Generator.

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

class TagsGenerator(BaseComponent):
    """Generator for article tags."""
    
    def generate(self) -> str:
        """Generate tags content.
        
        Returns:
            str: The generated tags
        """
        try:
            # Check if frontmatter already has keywords
            frontmatter = self.get_frontmatter_data()
            if frontmatter and "keywords" in frontmatter:
                keywords = frontmatter["keywords"]
                if keywords:
                    if isinstance(keywords, list):
                        tags = keywords
                    elif isinstance(keywords, str):
                        tags = [k.strip() for k in keywords.split(",")]
                    else:
                        tags = [str(keywords)]
                        
                    if tags:
                        return self._format_tags(tags)
            
            # No keywords in frontmatter, generate tags
            # 1. Prepare data for prompt
            data = self._prepare_data()
            
            # 2. Format prompt
            prompt = self._format_prompt(data)
            
            # 3. Call API
            content = self._call_api(prompt)
            
            # 4. Post-process content
            return self._post_process(content)
        except Exception as e:
            logger.error(f"Error generating tags: {str(e)}")
            return self._create_error_markdown(str(e))
    
    def _prepare_data(self) -> Dict[str, Any]:
        """Prepare data for tags generation.
        
        Returns:
            Dict[str, Any]: Data for prompt formatting
        """
        data = super()._prepare_data()
        
        # Get component-specific configuration
        component_config = self.get_component_config()
        
        # Add tag constraints
        data["max_count"] = component_config.get("count", 10)  # Use 'count' from config, fallback to 10
        
        # Add subject-with-dashes for template
        data["subject-with-dashes"] = data["subject"].replace(" ", "-").replace("_", "-")
        
        # Get frontmatter data
        frontmatter = self.get_frontmatter_data()
        if frontmatter:
            # Extract title and description for better tag generation
            data["title"] = frontmatter.get("title", "")
            data["description"] = frontmatter.get("description", "")
            
            # Add article-type specific content for better tag generation
            if self.article_type == "material":
                data["properties"] = frontmatter.get("properties", {})
                data["applications"] = frontmatter.get("applications", [])
            elif self.article_type == "application":
                data["industries"] = frontmatter.get("industries", [])
                data["features"] = frontmatter.get("features", [])
            elif self.article_type == "thesaurus":
                data["alternateNames"] = frontmatter.get("alternateNames", [])
        
        return data
    
    def _post_process(self, content: str) -> str:
        """Post-process the tags content.
        
        Args:
            content: The API response content
            
        Returns:
            str: The processed tags
        """
        # Apply standard processing
        processed = super()._post_process(content)
        
        # Extract tags from content
        tags = self._extract_tags(processed)
        
        # Format the tags
        return self._format_tags(tags)
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract tags from content.
        
        Args:
            content: Content with tags
            
        Returns:
            List[str]: List of tags
        """
        # Get max tag count
        max_count = self.get_component_config("max_count", 10)
        
        # Split by commas, new lines, or bullet points
        tags = []
        
        # Try comma-separated list first
        if "," in content:
            tag_list = content.split(",")
            tags = [t.strip() for t in tag_list if t.strip()]
        else:
            # Try line-by-line or bullet points
            lines = content.split("\n")
            for line in lines:
                # Remove bullet points, dashes, and other markers
                clean_line = re.sub(r'^[-*•#\s]+', '', line.strip())
                if clean_line:
                    tags.append(clean_line)
        
        # Normalize tags (lowercase, remove special characters)
        normalized_tags = []
        for tag in tags:
            # Convert to kebab case (lowercase with hyphens)
            kebab = tag.lower().strip()
            kebab = re.sub(r'[^a-z0-9\-]+', '-', kebab)  # Replace non-alphanumeric with hyphens
            kebab = re.sub(r'-+', '-', kebab)  # Replace multiple hyphens with single hyphen
            kebab = kebab.strip('-')  # Remove leading/trailing hyphens
            
            if kebab and kebab not in normalized_tags:
                normalized_tags.append(kebab)
        
        # Limit to max count
        return normalized_tags[:max_count]
    
    def _format_tags(self, tags: List[str]) -> str:
        """Format tags as HTML spans.
        
        Args:
            tags: List of tags
            
        Returns:
            str: Formatted tags
        """
        # Add heading
        result = "## Tags\n\n"
        
        # Add tags as HTML spans
        if tags:
            tag_spans = [f'<span class="tag">{tag}</span>' for tag in tags]
            result += " ".join(tag_spans)
        else:
            result += "<!-- No tags available -->"
        
        return result