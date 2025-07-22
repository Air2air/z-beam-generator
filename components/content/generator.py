"""
MODULE DIRECTIVES FOR AI ASSISTANTS:
1. FRONTMATTER-DRIVEN: All content must be extracted from frontmatter
2. NO HARDCODED SECTIONS: Section structure must be derived from frontmatter
3. DYNAMIC FORMATTING: Format content based on article_type from frontmatter
4. ERROR HANDLING: Raise exceptions when required frontmatter fields are missing
5. SCHEMA AWARENESS: Be aware of the schema structure for different article types
"""

import logging
from typing import Dict, Any, List
from components.base import BaseComponent

logger = logging.getLogger(__name__)

class ContentGenerator(BaseComponent):
    """Generates main article content based on frontmatter data."""
    
    def generate(self) -> str:
        """Generate main content for the article."""
        try:
            # 1. Get frontmatter data using standard method
            frontmatter_data = self.get_frontmatter_data()
            
            if not frontmatter_data:
                logger.warning("No frontmatter data available for content generation")
                return self._create_error_markdown("Missing frontmatter data")
                
            # 2. Prepare data for prompt
            prompt_data = self._prepare_data(frontmatter_data)
            
            # 3. Format prompt
            prompt = self._format_prompt(prompt_data)
            
            # 4. Call API
            content = self._call_api(prompt)
            
            # 5. Post-process content
            return self._post_process(content)
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            return self._create_error_markdown(str(e))
    
    def _prepare_data(self, frontmatter_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for prompt formatting."""
        # Extract essential data from frontmatter
        title = frontmatter_data.get("title", self.subject)
        description = frontmatter_data.get("description", "")
        keywords = frontmatter_data.get("keywords", [])
        properties = frontmatter_data.get("properties", {})
        applications = frontmatter_data.get("applications", [])
        tech_specs = frontmatter_data.get("technicalSpecifications", {})
        
        # Determine structure based on article_type
        article_type = frontmatter_data.get("articleType", "informational")
        
        # Build prompt data dictionary
        return {
            "subject": self.subject,
            "title": title,
            "description": description,
            "keywords": ", ".join(keywords) if keywords else "",
            "article_type": article_type,
            "has_properties": bool(properties),
            "has_applications": bool(applications),
            "has_tech_specs": bool(tech_specs),
            # Include any additional context from frontmatter
            "context": frontmatter_data.get("context", ""),
            "tone": frontmatter_data.get("tone", "informative")
        }
    
    def _format_prompt(self, data: Dict[str, Any]) -> str:
        """Format prompt template with data."""
        template = self.load_prompt_template()
        
        try:
            return template.format(**data)
        except KeyError as e:
            logger.error(f"Missing key in prompt data: {e}")
            # Fallback to a simple prompt if template formatting fails
            return f"Write a detailed article about {data.get('subject', 'the topic')}."
    
    def _call_api(self, prompt: str) -> str:
        """Call API with prompt."""
        return self.api_client.generate_content(prompt)
    
    def _post_process(self, content: str) -> str:
        """Post-process API response."""
        if not content:
            return ""
            
        # Ensure content starts with a header if not already
        if not content.strip().startswith("#"):
            frontmatter_data = self.get_frontmatter_data()
            title = frontmatter_data.get("title", self.subject.capitalize())
            content = f"# {title}\n\n{content}"
        
        return content