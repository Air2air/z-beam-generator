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
from typing import Dict, Any, List
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
        
        # Get component-specific configuration
        component_config = self.get_component_config()
        
        # Add content constraints
        data.update({
            "min_words": component_config.get("min_words", 500),
            "max_words": component_config.get("max_words", 1500),
            "tone": component_config.get("tone", "professional")
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
    
    def _format_prompt(self, data: Dict[str, Any]) -> str:
        """Build prompt for content generation."""
        # Get frontmatter data
        frontmatter = data.get("frontmatter", {})
        
        prompt = f"""
        Write a comprehensive article about {data['subject']} as a {data['article_type']}.
        
        Requirements:
        - Length: Between {data.get('min_words', 500)} and {data.get('max_words', 1500)} words
        - Tone: {data.get('tone', 'professional')}
        - Format: Markdown with proper headings and subheadings
        - Focus on accurate technical information
        """
        
        # Add frontmatter-derived information
        if "description" in frontmatter:
            prompt += f"\n\nDescription: {frontmatter['description']}"
            
        if "keywords" in frontmatter:
            keywords = frontmatter["keywords"]
            if isinstance(keywords, list):
                prompt += f"\n\nKeywords: {', '.join(keywords)}"
            else:
                prompt += f"\n\nKeywords: {keywords}"
        
        # Add article type-specific instructions
        if data['article_type'] == "material":
            prompt += """
            
            Include these sections:
            1. Introduction
            2. Properties
            3. Applications
            4. Manufacturing Process
            5. Advantages and Limitations
            """
        elif data['article_type'] == "thesaurus":
            prompt += """
            
            Include these sections:
            1. Definition
            2. Technical Context
            3. Related Concepts
            4. Applications
            """
        
        return prompt
    
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