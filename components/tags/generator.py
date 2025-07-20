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
from typing import Dict, Any, List

from components.base import BaseComponent

logger = logging.getLogger(__name__)

class TagsGenerator(BaseComponent):
    """Generator for article tags section."""
    
    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], ai_provider: str = "deepseek"):
        """Initialize the tags generator.
        
        Args:
            context: Context data including subject, article_type, etc.
            schema: Schema definition for tags generation
            ai_provider: The AI provider to use
        """
        super().__init__(context, schema, ai_provider)
        logger.info(f"TagsGenerator initialized for subject: {self.subject}")
    
    def generate(self) -> str:
        """Generate tags section based on frontmatter data."""
        try:
            frontmatter_data = self.get_frontmatter_data()
            if not frontmatter_data:
                logger.warning("No frontmatter data available for tags generation")
                return ""
            
            # Extract tags from frontmatter
            tags = frontmatter_data.get("tags", [])
            if not tags:
                logger.info("No tags found in frontmatter")
                return ""
            
            # Create a bulleted list of tags
            tags_content = "## Tags\n\n"
            for tag in tags:
                tags_content += f"- {tag}\n"
            
            return tags_content + "\n"
            
        except Exception as e:
            logger.error(f"Error generating tags: {e}")
            return ""