"""
Base type generator for JSON-LD data.
"""

import logging
import re
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseTypeGenerator:
    """Base generator for JSON-LD data."""
    
    def __init__(self, subject: str, frontmatter: Dict[str, Any] = None):
        """Initialize the generator.
        
        Args:
            subject: The subject of the article
            frontmatter: Optional frontmatter data
        """
        self.subject = subject
        self.frontmatter = frontmatter or {}
    
    def generate_jsonld(self, frontmatter: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate JSON-LD for this article.
        
        Args:
            frontmatter: Optional frontmatter data
            
        Returns:
            Dict[str, Any]: Generated JSON-LD
        """
        # This should be implemented by subclasses
        raise NotImplementedError("Subclasses must implement generate_jsonld()")
    
    def set_frontmatter(self, frontmatter_data: Dict[str, Any]) -> 'BaseTypeGenerator':
        """Set frontmatter data.
        
        Args:
            frontmatter_data: Frontmatter data
            
        Returns:
            Self for method chaining
        """
        self.frontmatter = frontmatter_data or {}
        return self
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text by removing extra whitespace.
        
        Args:
            text: Text to normalize
            
        Returns:
            str: Normalized text
        """
        if not text:
            return ""
        
        # Replace multiple spaces/newlines with a single space
        normalized = re.sub(r'\s+', ' ', text)
        return normalized.strip()
    
    def _get_frontmatter_value(self, frontmatter: Dict[str, Any], key: str, default: Any = None) -> Any:
        """Get value from frontmatter safely.
        
        Args:
            frontmatter: Frontmatter data
            key: Key to get
            default: Default value if key not found
            
        Returns:
            Any: Value from frontmatter or default
        """
        return frontmatter.get(key, default)
    
    def _get_nested_value(self, data: Dict[str, Any], key: str, default: Any = None) -> Any:
        """Get nested value from dictionary.
        
        Args:
            data: Dictionary to get value from
            key: Key to get
            default: Default value if key not found
            
        Returns:
            Any: Value from dictionary or default
        """
        if not isinstance(data, dict):
            return default
        return data.get(key, default)
    
    def _get_current_date(self) -> str:
        """Get current date in YYYY-MM-DD format.
        
        Returns:
            str: Current date
        """
        return datetime.now().strftime("%Y-%m-%d")
    
    def _get_common_jsonld_structure(self, frontmatter: Dict[str, Any], article_type: str = "Article") -> Dict[str, Any]:
        """Get common JSON-LD structure.
        
        Args:
            frontmatter: Frontmatter data
            article_type: Type of article (Article, TechnicalArticle, etc.)
            
        Returns:
            Dict[str, Any]: Common JSON-LD structure
        """
        # Get basic information
        name = self._get_frontmatter_value(frontmatter, "name", self.subject)
        description = self._get_frontmatter_value(frontmatter, "description", f"Information about {self.subject}")
        website = self._get_frontmatter_value(frontmatter, "website", f"https://www.z-beam.com/{self.subject}-laser-cleaning")
        
        # Get author information
        author_data = self._get_frontmatter_value(frontmatter, "author", {})
        if isinstance(author_data, dict):
            author_name = author_data.get("author_name", "Z-Beam Technical Writer")
            author_org = author_data.get("name", "Laser Technology Institute")
        else:
            author_name = "Z-Beam Technical Writer"
            author_org = "Laser Technology Institute"
        
        # Get keywords
        keywords = self._get_frontmatter_value(frontmatter, "keywords", [])
        if isinstance(keywords, str):
            keywords = [k.strip() for k in keywords.split(",")]
        
        # Build base structure
        jsonld = {
            "@context": "https://schema.org",
            "@type": article_type,
            "headline": name,
            "name": name,
            "description": self._normalize_text(description),
            "url": website,
            "datePublished": self._get_current_date(),
            "dateModified": self._get_current_date(),
            "author": {
                "@type": "Person",
                "name": author_name,
                "affiliation": {
                    "@type": "Organization",
                    "name": author_org
                }
            },
            "publisher": {
                "@type": "Organization",
                "name": "Z-Beam",
                "url": "https://www.z-beam.com"
            }
        }
        
        # Add keywords if available
        if keywords:
            jsonld["keywords"] = keywords
        
        return jsonld
    
    def _get_slug(self, frontmatter: Dict[str, Any]) -> str:
        """Get URL slug from frontmatter or generate one.
        
        Args:
            frontmatter: Frontmatter data
            
        Returns:
            str: URL slug
        """
        if "slug" in frontmatter:
            return frontmatter["slug"]
        name = frontmatter.get("name", self.subject)
        return name.lower().replace(" ", "-")
    
    def _format_keywords(self, keywords: Any, article_type: str = None, subject: str = None) -> str:
        """Format keywords as comma-separated string with type-specific defaults.
        
        Args:
            keywords: Keywords to format
            article_type: Article type
            subject: Subject
            
        Returns:
            str: Formatted keywords
        """
        subject = subject or self.subject
        
        if isinstance(keywords, str):
            return keywords
        
        if isinstance(keywords, list) and keywords:
            return ", ".join(keywords)
        
        # Type-specific default keywords
        if article_type == "material":
            return f"{subject} laser cleaning, {subject} surface preparation, laser ablation, contaminant removal"
        elif article_type == "application":
            return f"{subject} applications, laser cleaning technology, surface treatment, industrial cleaning"
        elif article_type == "thesaurus":
            return f"{subject}, laser cleaning glossary, technical terminology, industrial laser definition"
        
        return f"{subject} laser cleaning"
    
    def _format_property_name(self, key: str) -> str:
        """Convert camelCase property name to Title Case.
        
        Args:
            key: Property name in camelCase
            
        Returns:
            str: Property name in Title Case
        """
        # Convert camelCase to Title Case
        title = re.sub(r'([a-z])([A-Z])', r'\1 \2', key)
        return title.title()
    
    def _build_url(self, slug: str, article_type: str) -> str:
        """Build URL for article with consistent patterns.
        
        Args:
            slug: URL slug
            article_type: Article type
            
        Returns:
            str: URL for article
        """
        if article_type == "thesaurus":
            return f"https://www.z-beam.com/glossary/{slug}"
        elif article_type == "material":
            return f"https://www.z-beam.com/materials/{slug}"
        elif article_type == "application":
            return f"https://www.z-beam.com/applications/{slug}"
        elif article_type == "region":
            return f"https://www.z-beam.com/regions/{slug}"
        else:
            return f"https://www.z-beam.com/{slug}"
    
    def _generate_structured_value(self, props: Dict[str, Any]) -> str:
        """Generate a structured value string from properties.
        
        Args:
            props: Properties to format
            
        Returns:
            str: Structured value string
        """
        parts = []
        for key, value in props.items():
            if value:
                parts.append(f"{self._format_property_name(key)}: {value}")
        
        return "; ".join(parts)