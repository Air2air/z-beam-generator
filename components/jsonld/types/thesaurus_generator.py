"""
JSON-LD generator for thesaurus/glossary articles.
"""

import logging
from typing import Dict, Any, List
from components.jsonld.types.base_type_generator import BaseTypeGenerator

logger = logging.getLogger(__name__)

class ThesaurusJsonldGenerator(BaseTypeGenerator):
    """Generator for thesaurus-specific JSON-LD."""
    
    def generate_jsonld(self, frontmatter: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate JSON-LD for thesaurus/glossary articles.
        
        Args:
            frontmatter: Optional frontmatter data
            
        Returns:
            Dict[str, Any]: Generated JSON-LD
        """
        # Use provided frontmatter or instance frontmatter
        frontmatter = frontmatter or self.frontmatter
        
        # Get basic data
        name = self._get_frontmatter_value(frontmatter, "name", self.subject)
        # Capitalize first letter of name
        name = name[0].upper() + name[1:] if name else ""
        slug = self._get_slug(frontmatter)
        description = self._get_frontmatter_value(frontmatter, "description", 
                                                f"Definition and technical details about {name} in laser cleaning.")
        keywords = self._format_keywords(self._get_frontmatter_value(frontmatter, "keywords", []))
        today = self._get_current_date()
        website_url = self._get_frontmatter_value(frontmatter, "website", 
                                                self._build_url(slug, "thesaurus"))
        
        # Get author information
        author = self._get_frontmatter_value(frontmatter, "author", {})
        
        # Build basic JSON-LD structure
        jsonld = {
            "@context": "https://schema.org",
            "@type": "DefinedTerm",
            "name": name,
            "description": description,
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": website_url
            },
            "author": {
                "@type": "Person",
                "identifier": self._get_nested_value(author, "author_id", 1),
                "name": self._get_nested_value(author, "author_name", ""),
                "description": self._get_nested_value(author, "credentials", 
                                                    "Laser Technology Expert")
            },
            "datePublished": today,
            "dateModified": today,
            "image": f"https://www.z-beam.com/images/glossary/{slug}.jpg",
            "keywords": keywords,
            "inDefinedTermSet": {
                "@type": "DefinedTermSet",
                "name": "Laser Cleaning Glossary",
                "description": "Comprehensive glossary of laser cleaning terminology and techniques"
            }
        }
        
        # Add term type if available
        term_type = self._get_frontmatter_value(frontmatter, "termType", "")
        if term_type:
            jsonld["termCode"] = term_type
        
        # Add alternate names if available
        alt_names = self._get_frontmatter_value(frontmatter, "alternateNames", [])
        if alt_names and isinstance(alt_names, list) and len(alt_names) > 0:
            jsonld["alternateName"] = alt_names
        
        # Add subject of field
        jsonld["subjectOf"] = {
            "@type": "Article",
            "name": f"{name} - Laser Cleaning Technical Reference",
            "description": description,
            "isPartOf": {
                "@type": "DefinedTermSet",
                "name": "Laser Cleaning Encyclopedia"
            }
        }
        
        # Add about section with related concepts
        about_items = self._get_about_items(frontmatter, name)
        if about_items:
            jsonld["about"] = about_items
        
        return jsonld
    
    def _get_about_items(self, frontmatter: Dict[str, Any], name: str) -> List[Dict[str, Any]]:
        """Get about items for the term.
        
        Args:
            frontmatter: Frontmatter data
            name: Term name
            
        Returns:
            List[Dict[str, Any]]: About items
        """
        items = []
        
        # Add related terms
        related_terms = self._get_frontmatter_value(frontmatter, "relatedTerms", [])
        if related_terms:
            term_items = []
            for term in related_terms:
                if isinstance(term, dict):
                    term_name = term.get("name", "")
                    relation = term.get("relationship", "")
                    
                    if term_name:
                        term_item = {
                            "@type": "DefinedTerm",
                            "name": self._normalize_text(term_name)
                        }
                        if relation:
                            term_item["description"] = self._normalize_text(f"{relation} of {name}")
                        term_items.append(term_item)
                elif isinstance(term, str):
                    term_items.append({
                        "@type": "DefinedTerm",
                        "name": self._normalize_text(term)
                    })
            
            if term_items:
                items.append({
                    "@type": "Thing",
                    "name": "Related Terms",
                    "description": f"Terms related to {name} in laser cleaning applications.",
                    "mentions": term_items
                })
        
        # Add applications
        applications = self._get_frontmatter_value(frontmatter, "applications", [])
        if applications:
            app_items = []
            for app in applications:
                if isinstance(app, dict):
                    app_name = app.get("name", "")
                    app_desc = app.get("description", "")
                    
                    if app_name:
                        app_item = {
                            "@type": "Thing",
                            "name": self._normalize_text(app_name)
                        }
                        if app_desc:
                            app_item["description"] = self._normalize_text(app_desc)
                        app_items.append(app_item)
            
            if app_items:
                items.append({
                    "@type": "Thing",
                    "name": f"Applications Using {name}",
                    "description": f"Laser cleaning applications that utilize {name}.",
                    "mentions": app_items
                })
        
        return items