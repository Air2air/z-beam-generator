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
        """Generate content for the article."""
        # Get frontmatter data
        frontmatter_data = self.get_frontmatter_data()
        
        if not frontmatter_data:
            logger.warning("No frontmatter data available for content generation")
            # Generate minimal content even without frontmatter
            return f"""
# {self.subject.title()}

Content generation could not proceed normally because frontmatter data was not available.
This could be due to an error in the frontmatter component.

## Basic Information

This article is about {self.subject}, which is a {self.article_type}.

## Please Fix Frontmatter Generation

Once the frontmatter component is working correctly, this content will be properly generated.
"""
        
        try:
            # Get article type from frontmatter or context
            article_type = frontmatter_data.get("article_type", self.article_type)
            subject = frontmatter_data.get("name", self.subject)
            
            # Create prompt for fully dynamic content
            prompt = self._create_dynamic_prompt(subject, article_type, frontmatter_data)
            
            # Generate content using the API client from BaseComponent
            content = self.api_client.generate_content(prompt)
            
            # Return the generated content
            return content
            
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return f"<!-- Error generating content: {str(e)} -->\n\n"
    
    def _create_dynamic_prompt(self, subject: str, article_type: str, frontmatter_data: Dict[str, Any]) -> str:
        """Create a prompt that results in fully dynamic content.
        
        Args:
            subject: The subject of the article
            article_type: The type of article
            frontmatter_data: Frontmatter data from BaseComponent
        
        Returns:
            A prompt string for the AI
        """
        # Basic contextual info about the request
        context = {
            "subject": subject,
            "article_type": article_type,
            "frontmatter": frontmatter_data,
        }
        
        # The prompt instructs the AI to create fully dynamic content
        # with no hardcoded sections or structures
        prompt = (
            f"Generate the introduction section ONLY for an article about {subject} laser cleaning.\n\n"
            f"CONTEXT (use only this data as your information source):\n{json.dumps(context, indent=2)}\n\n"
            "IMPORTANT INSTRUCTIONS:\n"
            "1. Generate ONLY an introduction/overview section\n"
            "2. DO NOT include any other sections (technical specs, applications, etc.)\n"
            "3. DO NOT create a table of contents or section previews\n"
            "4. DO NOT use any hardcoded section titles or structures\n"
            "5. DO NOT add any content that would be better handled by separate components\n"
            "6. Your content should be focused only on introducing the subject\n"
            "7. Format as proper markdown\n"
            "8. Be concise but informative (200-300 words)\n"
            "9. Ensure your content is based ONLY on the provided frontmatter data\n"
            "10. DO NOT invent facts or specifications not present in the frontmatter\n"
            "11. DO NOT include markdown headlines (# or ##) in your response\n"
        )
        
        return prompt