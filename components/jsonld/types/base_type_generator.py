"""
Base class for type-specific JSON-LD generators.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseTypeGenerator(ABC):
    """Base class for all type-specific JSON-LD generators."""
    
    def __init__(self, subject: str, frontmatter: Dict[str, Any] = None):
        """Initialize the type generator.
        
        Args:
            subject: Subject of the article
            frontmatter: Frontmatter data
        """
        self.subject = subject
        self.frontmatter = frontmatter or {}
    
    @abstractmethod
    def generate_jsonld(self, frontmatter: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate JSON-LD for this article type.
        
        Args:
            frontmatter: Article frontmatter data (override instance frontmatter if provided)
            
        Returns:
            JSON-LD structure
        """
        pass
    
    def _get_frontmatter_value(self, frontmatter: Dict[str, Any], key: str, default: Any = None) -> Any:
        """Get value from frontmatter safely.
        
        Args:
            frontmatter: Frontmatter data
            key: Key to retrieve
            default: Default value if key not found
            
        Returns:
            Value from frontmatter or default
        """
        return frontmatter.get(key, default)
        
    def _get_nested_value(self, data: Dict[str, Any], key_path: str, default: Any = "") -> Any:
        """Get nested value using dot notation.
        
        Args:
            data: Dictionary to extract from
            key_path: Path to key using dot notation (e.g., "author.name")
            default: Default value if key not found
            
        Returns:
            Nested value or default
        """
        if not isinstance(data, dict):
            return default
            
        keys = key_path.split('.')
        value = data
        
        for key in keys:
            if not isinstance(value, dict) or key not in value:
                return default
            value = value.get(key)
            
        return value if value is not None else default
        
    def _format_keywords(self, keywords: Any) -> str:
        """Format keywords as comma-separated string.
        
        Args:
            keywords: Keywords from frontmatter (list or string)
            
        Returns:
            Comma-separated keywords string
        """
        # If already a string, return as is
        if isinstance(keywords, str):
            return keywords
            
        # If a list, join with commas
        if isinstance(keywords, list):
            return ", ".join(keywords)
            
        # Default keywords
        return f"{self.subject} laser cleaning, precision surface preparation"
        
    def _get_current_date(self) -> str:
        """Get current date in YYYY-MM-DD format.
        
        Returns:
            Current date string
        """
        return datetime.now().strftime("%Y-%m-%d")
        
    def _get_slug(self, frontmatter: Dict[str, Any]) -> str:
        """Get slug from frontmatter or generate from name/subject.
        
        Args:
            frontmatter: Frontmatter data
            
        Returns:
            URL slug
        """
        if "slug" in frontmatter:
            return frontmatter["slug"]
            
        name = frontmatter.get("name", self.subject)
        return name.lower().replace(" ", "-")
        
    def _build_url(self, slug: str, article_type: str) -> str:
        """Build URL based on article type and slug.
        
        Args:
            slug: URL slug
            article_type: Type of article
            
        Returns:
            Complete URL
        """
        base_url = "https://www.z-beam.com"
        
        url_patterns = {
            "region": f"{base_url}/{slug}-laser-cleaning",
            "application": f"{base_url}/applications/{slug}",
            "thesaurus": f"{base_url}/glossary/{slug}",
            "material": f"{base_url}/materials/{slug}"
        }
        
        return url_patterns.get(article_type, f"{base_url}/{slug}")
        
    def _build_image_url(self, slug: str, article_type: str) -> str:
        """Build image URL based on article type and slug.
        
        Args:
            slug: URL slug
            article_type: Type of article
            
        Returns:
            Complete image URL
        """
        base_url = "https://www.z-beam.com/images"
        
        image_patterns = {
            "region": f"{base_url}/{slug}-laser-cleaning.jpg",
            "application": f"{base_url}/applications/{slug}.jpg",
            "thesaurus": f"{base_url}/glossary/{slug}.jpg",
            "material": f"{base_url}/materials/{slug}.jpg"
        }
        
        return image_patterns.get(article_type, f"{base_url}/{slug}.jpg")
        
    def _get_publisher(self) -> Dict[str, Any]:
        """Get standard publisher object.
        
        Returns:
            Publisher object
        """
        return {
            "@type": "Organization",
            "name": "Z-Beam",
            "logo": {
                "@type": "ImageObject",
                "url": "https://www.z-beam.com/logo.png"
            }
        }
        
    def _convert_list_to_schema_objects(self, items: List[Union[str, Dict[str, Any]]], 
                                      object_type: str = "Thing") -> List[Dict[str, Any]]:
        """Convert a list of strings or dicts to schema.org objects.
        
        Args:
            items: List of strings or dictionaries
            object_type: Schema.org type for the objects
            
        Returns:
            List of schema.org objects
        """
        result = []
        
        for item in items:
            if isinstance(item, str):
                result.append({
                    "@type": object_type,
                    "name": item
                })
            elif isinstance(item, dict) and "name" in item:
                obj = {
                    "@type": object_type,
                    "name": item["name"]
                }
                
                # Add additional properties if present
                for key, value in item.items():
                    if key != "name":
                        obj[key] = value
                        
                result.append(obj)
                
        return result