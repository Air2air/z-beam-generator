"""Bullet points component for Z-Beam articles."""

import logging
from typing import Dict, Any, List

from components.base import BaseComponent

logger = logging.getLogger(__name__)

class BulletsComponent(BaseComponent):
    """Generator for bullet points based on frontmatter data."""
    
    def generate(self) -> str:
        """Generate bullet points for article."""
        try:
            # 1. Get frontmatter data using standard method
            frontmatter_data = self.get_frontmatter_data()
            
            if not frontmatter_data:
                logger.warning("No frontmatter data available for bullet generation")
                return ""
                
            # 2. Prepare data for prompt
            prompt_data = self._prepare_data(frontmatter_data)
            
            # 3. Format prompt
            prompt = self._format_prompt(prompt_data)
            
            # 4. Call API
            content = self._call_api(prompt)
            
            # 5. Post-process content
            return self._post_process(content)
            
        except Exception as e:
            logger.error(f"Error generating bullets: {str(e)}")
            return self._create_error_markdown(str(e))
    
    def _prepare_data(self, frontmatter_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for prompt formatting."""
        # Extract relevant data from frontmatter
        keywords = frontmatter_data.get("keywords", [])
        tags = frontmatter_data.get("tags", [])
        applications = frontmatter_data.get("applications", [])
        tech_specs = frontmatter_data.get("technicalSpecifications", {})
        safety_info = frontmatter_data.get("safetyConsiderations", [])
        
        # Format data for prompt
        return {
            "subject": self.subject,
            "article_type": self.article_type,
            "keywords": ", ".join(keywords),
            "tags": ", ".join(tags),
            "applications": ", ".join(applications),
            "has_tech_specs": bool(tech_specs),
            "safety_info": ", ".join(safety_info) if safety_info else ""
        }
    
    def _format_prompt(self, data: Dict[str, Any]) -> str:
        """Format prompt template with data."""
        # Get prompt template
        template = self.load_prompt_template()
        
        # Format template with data
        try:
            return template.format(**data)
        except KeyError as e:
            logger.error(f"Missing key in prompt data: {e}")
            return f"Generate bullet points for {data.get('subject', 'the topic')}."
    
    def _call_api(self, prompt: str) -> str:
        """Call API with prompt."""
        return self.api_client.generate_content(prompt)
    
    def _post_process(self, content: str) -> str:
        """Post-process API response."""
        if not content:
            return ""
            
        # Ensure content starts with a header
        if not content.startswith("#"):
            content = "## Key Points\n\n" + content
            
        return content