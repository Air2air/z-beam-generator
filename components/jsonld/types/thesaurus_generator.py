"""
JSON-LD generator for thesaurus articles.
"""

import logging
from typing import Dict, Any, List
from components.jsonld.types.base_type_generator import BaseTypeGenerator

logger = logging.getLogger(__name__)

class ThesaurusJsonldGenerator(BaseTypeGenerator):
    """Generator for thesaurus-specific JSON-LD."""
    
    def generate_jsonld(self, frontmatter: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate JSON-LD for thesaurus articles.
        
        Args:
            frontmatter: Article frontmatter data (override instance frontmatter if provided)
            
        Returns:
            JSON-LD structure for thesaurus articles
        """
        # Use provided frontmatter or instance frontmatter
        frontmatter = frontmatter or self.frontmatter
        
        # Get basic data
        name = self._get_frontmatter_value(frontmatter, "name", self.subject)
        slug = self._get_slug(frontmatter)
        description = self._get_frontmatter_value(frontmatter, "description", 
                                                 f"Definition and information about {name} in laser cleaning context.")
        today = self._get_current_date()
        
        # Get keywords and related terms
        keywords = self._format_keywords(self._get_frontmatter_value(frontmatter, "keywords", []))
        related_terms = self._get_frontmatter_value(frontmatter, "relatedTerms", [])
        
        # Process related terms into links if present
        related_links = []
        if related_terms and isinstance(related_terms, list):
            for term in related_terms:
                if isinstance(term, str):
                    term_slug = term.lower().replace(" ", "-")
                    related_links.append(self._build_url(term_slug, "thesaurus"))
                elif isinstance(term, dict) and "name" in term:
                    term_slug = term["name"].lower().replace(" ", "-")
                    related_links.append(self._build_url(term_slug, "thesaurus"))
        
        # Build the JSON-LD structure
        jsonld = {
            "@context": "https://schema.org",
            "@type": "DefinedTerm",
            "name": name,
            "description": description,
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": self._build_url(slug, "thesaurus")
            },
            "datePublished": today,
            "dateModified": today,
            "image": self._build_image_url(slug, "thesaurus"),
            "keywords": keywords,
            "inDefinedTermSet": {
                "@type": "DefinedTermSet",
                "name": "Z-Beam Laser Cleaning Glossary"
            }
        }
        
        # Add related links if available
        if related_links:
            jsonld["relatedLink"] = related_links
            
        return jsonld