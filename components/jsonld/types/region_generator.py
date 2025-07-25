"""
JSON-LD generator for region articles.
"""

import logging
from typing import Dict, Any
from components.jsonld.types.base_type_generator import BaseTypeGenerator

logger = logging.getLogger(__name__)

class RegionJsonldGenerator(BaseTypeGenerator):
    """Generator for region-specific JSON-LD."""
    
    def generate_jsonld(self, frontmatter: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate JSON-LD for region articles.
        
        Args:
            frontmatter: Article frontmatter data (override instance frontmatter if provided)
            
        Returns:
            JSON-LD structure for region articles
        """
        # Use provided frontmatter or instance frontmatter
        frontmatter = frontmatter or self.frontmatter
        
        # Get basic data
        name = self._get_frontmatter_value(frontmatter, "name", self.subject)
        slug = self._get_slug(frontmatter)
        description = self._get_frontmatter_value(frontmatter, "description", 
                                                 f"Information about {name} laser cleaning services.")
        today = self._get_current_date()
        
        # Get keywords
        keywords = self._format_keywords(self._get_frontmatter_value(frontmatter, "keywords", []))
        
        # Get author information with proper fallbacks
        author = self._get_frontmatter_value(frontmatter, "author", {})
        author_id = self._get_nested_value(author, "author_id", 1)
        author_name = self._get_nested_value(author, "author_name", "")
        author_country = self._get_nested_value(author, "author_country", "")
        author_credentials = self._get_nested_value(author, "credentials", 
                                                   "Industry Leader in Laser Cleaning Technology")
        organization_name = self._get_nested_value(author, "name", "Laser Technology Institute")
        
        # Build the JSON-LD structure
        return {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": name,
            "description": description,
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": self._build_url(slug, "region")
            },
            "author": {
                "@type": "Person",
                "identifier": author_id,
                "name": author_name,
                "nationality": author_country,
                "description": author_credentials,
                "affiliation": {
                    "@type": "Organization",
                    "name": organization_name
                }
            },
            "publisher": self._get_publisher(),
            "datePublished": today,
            "dateModified": today,
            "image": self._build_image_url(slug, "region"),
            "keywords": keywords
        }