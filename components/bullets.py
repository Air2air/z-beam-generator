"""
MODULE DIRECTIVES FOR AI ASSISTANTS:
1. FRONTMATTER-DRIVEN: All content must be extracted from frontmatter
2. NO HARDCODED SECTIONS: Section structure must be derived from frontmatter
3. DYNAMIC FORMATTING: Format content based on article_type from frontmatter
4. ERROR HANDLING: Raise exceptions when required frontmatter fields are missing
5. SCHEMA AWARENESS: Be aware of the schema structure for different article types
"""

# Your imports and code

import logging
import json
from typing import Dict, Any

from components.base import BaseComponent

from api import get_client

logger = logging.getLogger(__name__)

class BulletsComponent(BaseComponent):
    """Generator for bullet points based on frontmatter data."""
    
    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], ai_provider: str = "deepseek"):
        """Initialize the bullets component.
        
        Args:
            context: Context data including subject, article_type, etc.
            schema: Schema definition for bullet generation
            ai_provider: The AI provider to use
        """
        super().__init__(context, schema, ai_provider)
        logger.info(f"BulletsComponent initialized for subject: {self.subject}")
        
        self.api_client = get_client(ai_provider)
    
    def generate(self) -> str:
        """Generate bullet points based on frontmatter data."""
        try:
            frontmatter_data = self.get_frontmatter_data()
            if not frontmatter_data:
                logger.warning("No frontmatter data available for bullet generation")
                return ""
            
            # Extract keywords and tags for bullet generation
            keywords = frontmatter_data.get("keywords", [])
            tags = frontmatter_data.get("tags", [])
            
            if not keywords and not tags:
                logger.info("No keywords or tags found for bullet generation")
                return ""
                
            # Create context for the AI prompt
            context = {
                "subject": self.subject,
                "article_type": self.article_type,
                "keywords": keywords[:5] if keywords else [],
                "tags": tags if tags else []
            }
            
            # Generate bullet points using AI
            prompt = (
                f"Based on these keywords and tags for {self.subject}:\n"
                f"{json.dumps(context, indent=2)}\n\n"
                f"Create 5 concise technical bullet points that highlight key aspects of {self.subject} laser cleaning.\n"
                "Each bullet point should be technical in nature and relevant to laser cleaning professionals.\n"
                "Format as proper markdown bullet points with bold emphasis on key terms.\n"
                "Each bullet point should be 15-25 words and focus on a unique technical aspect.\n"
                "Do not repeat information in multiple bullet points.\n"
            )
            
            bullet_content = self.api_client.generate_content(prompt)
            
            # Return the bullet points with a heading
            return f"## Key Technical Points\n\n{bullet_content}\n"
            
        except Exception as e:
            logger.error(f"Error generating bullet points: {e}")
            return ""
    
    def _generate_material_bullets(self, frontmatter_data: Dict[str, Any]) -> str:
        """Generate bullet points for material articles."""
        bullets = ["## Key Points"]
        
        # Add bullets based on frontmatter data
        # Implementation...
        
        return "\n\n".join(bullets)
    
    # Other bullet generation methods...