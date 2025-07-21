"""
MODULE DIRECTIVES FOR AI ASSISTANTS:
1. FRONTMATTER-DRIVEN: All content must be extracted from frontmatter
2. NO HARDCODED SECTIONS: Section structure must be derived from frontmatter
3. DYNAMIC FORMATTING: Format content based on article_type from frontmatter
4. ERROR HANDLING: Raise exceptions when required frontmatter fields are missing
5. SCHEMA AWARENESS: Be aware of the schema structure for different article types
"""

import logging
import json
import re
from typing import Dict, Any

from components.base import BaseComponent

logger = logging.getLogger(__name__)

class ContentGenerator(BaseComponent):
    """Generates dynamic article content based on frontmatter data."""
    
    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], ai_provider: str = "deepseek"):
        """Initialize the content generator.
        
        Args:
            context: Context data including subject, article_type, etc.
            schema: Schema definition for content generation
            ai_provider: The AI provider to use
        """
        super().__init__(context, schema, ai_provider)
        logger.info(f"ContentGenerator initialized for subject: {self.subject}")
    
    def generate(self) -> str:
        """Generate content based on the template method pattern."""
        try:
            # 1. Prepare data
            data = self._prepare_data()
            
            # 2. Create prompt
            prompt = self._create_prompt(data)
            
            # 3. Generate content via API
            content = self._generate_content(prompt)
            
            # 4. Post-process content
            return self._post_process(content)
            
        except Exception as e:
            from utils.error_handler import ErrorHandler
            return ErrorHandler.handle_component_error("ContentGenerator", e, strict_mode=False)
    
    def _prepare_data(self):
        """Prepare data for prompt creation."""
        # Get frontmatter data
        frontmatter_data = self.get_frontmatter_data()
        
        # Get component-specific configuration
        config = self.get_component_config()
        
        # Prepare context data
        return {
            "subject": self.subject,
            "article_type": self.article_type,
            "frontmatter": frontmatter_data,
            "max_words": config.get("max_words", 500),
            "min_words": config.get("min_words", 300),
            "paragraphs": config.get("paragraphs", 3)
        }

    def _create_prompt(self, data):
        """Create dynamic prompt based on prepared data."""
        # Format as JSON for consistency
        context_json = json.dumps(data, indent=2)
        
        # Create dynamic prompt with clear instructions
        prompt = (
            f"Generate the introduction section ONLY for an article about {data['subject']} laser cleaning.\n\n"
            f"CONTEXT (use only this data as your information source):\n{context_json}\n\n"
            "IMPORTANT INSTRUCTIONS:\n"
            "1. Generate ONLY an introduction/overview section\n"
            "2. DO NOT include any other sections (technical specs, applications, etc.)\n"
            "3. DO NOT create a table of contents or section previews\n"
            "4. DO NOT use any hardcoded section titles or structures\n"
            "5. DO NOT add any content that would be better handled by separate components\n"
            "6. Your content should be focused only on introducing the subject\n"
            "7. Format as proper markdown\n"
            f"8. Be concise but informative ({data['min_words']}-{data['max_words']} words)\n"
            "9. Ensure your content is based ONLY on the provided frontmatter data\n"
            "10. DO NOT invent facts or specifications not present in the frontmatter\n"
            "11. DO NOT include markdown headlines (# or ##) in your response\n"
        )
        
        return prompt
    
    def _generate_content(self, prompt):
        """Generate content using the API client from BaseComponent."""
        return self.api_client.generate_content(prompt)
    
    def _post_process(self, content):
        """Post-process the generated content."""
        # Remove any HTML comments
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        
        # Remove any markdown headers
        content = re.sub(r'^#{1,6}\s+.*$', '', content, flags=re.MULTILINE)
        
        # Remove excessive blank lines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Ensure content ends with a newline
        if not content.endswith('\n'):
            content += '\n'
            
        return content.strip()