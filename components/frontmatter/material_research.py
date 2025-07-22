"""Material research submodule for dynamic material information retrieval.

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

class MaterialResearch(BaseComponent):
    """Generates research information about materials based on frontmatter data."""
    
    def generate(self) -> str:
        """Generate research-focused content about a material."""
        try:
            # 1. Get frontmatter data using standard method
            frontmatter_data = self.get_frontmatter_data()
            
            if not frontmatter_data:
                logger.warning("No frontmatter data available for material research")
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
            logger.error(f"Error generating material research: {str(e)}")
            return self._create_error_markdown(str(e))
    
    def _prepare_data(self, frontmatter_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for prompt formatting."""
        return {
            "subject": self.subject,
            "material_name": frontmatter_data.get("name", self.subject),
            "research_fields": ", ".join(frontmatter_data.get("researchFields", [])),
            "recent_developments": ", ".join(frontmatter_data.get("recentDevelopments", [])),
            "innovation_areas": ", ".join(frontmatter_data.get("innovationAreas", []))
        }
    
    def _format_prompt(self, data: Dict[str, Any]) -> str:
        """Format prompt template with data."""
        template = self.load_prompt_template()
        return template.format(**data)
    
    def _call_api(self, prompt: str) -> str:
        """Call API with prompt."""
        return self.api_client.generate_content(prompt)
    
    def _post_process(self, content: str) -> str:
        """Post-process API response."""
        if not content:
            return ""
        
        # Ensure content has a research section header if not present
        if not any(line.strip().lower().startswith(('# research', '## research')) for line in content.split('\n')):
            content = f"## Research & Development\n\n{content}"
        
        return content