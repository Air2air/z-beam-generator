"""
JSON-LD generator for application articles.
"""

import logging
from typing import Dict, Any
from components.jsonld.types.base_type_generator import BaseTypeGenerator

logger = logging.getLogger(__name__)

class ApplicationJsonldGenerator(BaseTypeGenerator):
    """Generator for application-specific JSON-LD."""
    
    def generate_jsonld(self, frontmatter: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate JSON-LD for application articles.
        
        Args:
            frontmatter: Article frontmatter data (override instance frontmatter if provided)
            
        Returns:
            JSON-LD structure for application articles
        """
        # Use provided frontmatter or instance frontmatter
        frontmatter = frontmatter or self.frontmatter
        
        # Get basic data
        name = self._get_frontmatter_value(frontmatter, "name", self.subject)
        slug = self._get_slug(frontmatter)
        description = self._get_frontmatter_value(
            frontmatter, 
            "description", 
            f"Information about {name} laser cleaning applications."
        )
        keywords = self._format_keywords(self._get_frontmatter_value(frontmatter, "keywords", []))
        today = self._get_current_date()
        
        # Build the JSON-LD structure
        return {
            "@context": "https://schema.org",
            "@type": "TechnicalArticle",
            "headline": name,
            "description": description,
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": self._build_url(slug, "application")
            },
            "author": {
                "@type": "Organization",
                "name": "Z-Beam"
            },
            "publisher": self._get_publisher(),
            "datePublished": today,
            "dateModified": today,
            "image": self._build_image_url(slug, "application"),
            "keywords": keywords,
            "technicalPlatform": "Laser Cleaning Technology"
        }