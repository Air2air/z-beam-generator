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

logger = logging.getLogger(__name__)

class JsonLdGenerator(BaseComponent):
    """Generator for JSON-LD structured data."""
    
    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], ai_provider: str = "deepseek"):
        """Initialize the JSON-LD generator.
        
        Args:
            context: Context data including subject, article_type, etc.
            schema: Schema definition for JSON-LD generation
            ai_provider: The AI provider to use
        """
        super().__init__(context, schema, ai_provider)
        logger.info(f"JsonLdGenerator initialized for subject: {self.subject}")
    
    def generate(self) -> str:
        """Generate JSON-LD schema dynamically based on frontmatter."""
        try:
            frontmatter_data = self.get_frontmatter_data()
            if not frontmatter_data:
                logger.error("No frontmatter data available for JSON-LD generation")
                return ""
            
            # Dynamically determine schema type based on article_type in frontmatter or context
            article_type = frontmatter_data.get("article_type", self.article_type).lower()
            schema_type = "TechArticle"  # Default type
            
            if "product" in article_type:
                schema_type = "Product"
            elif "service" in article_type:
                schema_type = "Service"
            
            # Create base schema
            jsonld = {
                "@context": "https://schema.org/",
                "@type": schema_type
            }
            
            # Add common properties
            subject = frontmatter_data.get("name", self.subject)
            description = frontmatter_data.get("description", "")
            
            if schema_type == "Product":
                jsonld["name"] = subject
            else:
                jsonld["headline"] = f"{subject} Laser Cleaning Guide"
                
            if description:
                jsonld["description"] = description
                
            # Add author if available
            author_data = frontmatter_data.get("author", {})
            if author_data:
                jsonld["author"] = {
                    "@type": "Organization",
                    "name": author_data.get("name", "Z-Beam")
                }
                
            # Add publisher
            jsonld["publisher"] = {
                "@type": "Organization",
                "name": "Z-Beam",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://www.z-beam.com/logo.png"
                }
            }
            
            # Add URL
            website = frontmatter_data.get("website", "")
            if not website:
                website = f"https://www.z-beam.com/{subject.lower().replace(' ', '-')}-laser-cleaning"
                
            jsonld["url"] = website
            jsonld["mainEntityOfPage"] = {
                "@type": "WebPage",
                "@id": website
            }
            
            # Format as JSON string
            jsonld_str = json.dumps(jsonld, indent=2)
            return f"```json\n{jsonld_str}\n```"
            
        except Exception as e:
            logger.error(f"Error generating JSON-LD: {e}")
            return ""