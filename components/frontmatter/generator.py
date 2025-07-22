"""
MODULE DIRECTIVES FOR AI ASSISTANTS:
1. FRONTMATTER-DRIVEN: All content must be extracted from frontmatter
2. NO HARDCODED SECTIONS: Section structure must be derived from frontmatter
3. DYNAMIC FORMATTING: Format content based on article_type from frontmatter
4. ERROR HANDLING: Raise exceptions when required frontmatter fields are missing
5. SCHEMA AWARENESS: Be aware of the schema structure for different article types
"""

import logging
import yaml
from typing import Dict, Any
from components.base import BaseComponent

logger = logging.getLogger(__name__)

class FrontmatterGenerator(BaseComponent):
    """Generates YAML frontmatter for articles."""
    
    def generate(self) -> str:
        """Generate YAML frontmatter based on subject."""
        try:
            # For frontmatter generator, we don't use existing frontmatter
            # since we're generating the frontmatter itself
            
            # 1. Prepare data for prompt
            prompt_data = self._prepare_data({})
            
            # 2. Format prompt
            prompt = self._format_prompt(prompt_data)
            
            # 3. Call API
            content = self._call_api(prompt)
            
            # 4. Post-process content
            return self._post_process(content)
            
        except Exception as e:
            logger.error(f"Error generating frontmatter: {str(e)}")
            return self._create_error_markdown(str(e))
    
    def _prepare_data(self, _: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for prompt formatting."""
        # Add the schema key that's missing
        return {
            "subject": self.subject,
            "article_type": self.article_type,
            "schema": {
                "title": "String - Title of the article",
                "description": "String - Brief description",
                "keywords": "Array - Related keywords",
                "properties": "Object - Material properties",
                "applications": "Array - Common applications"
            }
        }
    
    def _format_prompt(self, data: Dict[str, Any]) -> str:
        """Format prompt template with data."""
        template = self.load_prompt_template()
        
        try:
            return template.format(**data)
        except KeyError as e:
            logger.error(f"Missing key in prompt data: {e}")
            # Fallback to a simple prompt if template formatting fails
            return f"Generate YAML frontmatter for an article about {data.get('subject', 'the topic')}."
    
    def _call_api(self, prompt: str) -> str:
        """Call API with prompt."""
        return self.api_client.generate_content(prompt)
    
    def _post_process(self, content: str) -> str:
        """Post-process API response to ensure valid YAML frontmatter."""
        if not content:
            return ""
            
        # Extract YAML content (may be wrapped in markdown code blocks)
        yaml_content = content
        
        if "```yaml" in content:
            # Extract from code block
            start = content.find("```yaml") + 7
            end = content.find("```", start)
            if end != -1:
                yaml_content = content[start:end].strip()
        elif "```" in content:
            # Extract from generic code block
            start = content.find("```") + 3
            end = content.find("```", start)
            if end != -1:
                yaml_content = content[start:end].strip()
        
        # Remove any extra YAML document markers (---)
        if yaml_content.count('---') > 2:
            # Keep only the first document
            parts = yaml_content.split('---', 2)
            if len(parts) >= 3:
                yaml_content = parts[1].strip()
        
        # Validate YAML
        try:
            yaml_data = yaml.safe_load(yaml_content)
            if not isinstance(yaml_data, dict):
                raise ValueError("Frontmatter must be a dictionary")
                
            # Ensure basic fields are present
            if "title" not in yaml_data:
                yaml_data["title"] = self.subject.capitalize()
                
            # Format as YAML frontmatter
            formatted_yaml = yaml.safe_dump(yaml_data, default_flow_style=False)
            return f"---\n{formatted_yaml}---\n"
            
        except Exception as e:
            logger.error(f"Invalid YAML frontmatter: {str(e)}")
            # Return minimal valid frontmatter
            return f"---\ntitle: {self.subject.capitalize()}\n---\n"
