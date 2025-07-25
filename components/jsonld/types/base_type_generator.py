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
        
    def _get_common_jsonld_structure(self, frontmatter: Dict[str, Any], schema_type: str) -> Dict[str, Any]:
        """Generate common JSON-LD structure used by most types.
        
        Args:
            frontmatter: Frontmatter data
            schema_type: Schema.org type to use
            
        Returns:
            Base JSON-LD structure
        """
        # Get basic data
        name = self._get_frontmatter_value(frontmatter, "name", self.subject)
        slug = self._get_slug(frontmatter)
        description = self._get_frontmatter_value(
            frontmatter, 
            "description", 
            f"Information about {name}."
        )
        keywords = self._format_keywords(self._get_frontmatter_value(frontmatter, "keywords", []))
        today = self._get_current_date()
        
        # Get website URL from frontmatter or build default
        website_url = self._get_frontmatter_value(
            frontmatter, 
            "website", 
            self._build_url(slug, self._get_article_type_from_class())
        )
        
        # Build base structure
        return {
            "@context": "https://schema.org",
            "@type": schema_type,
            "headline": name,
            "description": description,
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": website_url
            },
            "author": self._generate_author_object(frontmatter),
            "publisher": self._get_publisher(),
            "datePublished": today,
            "dateModified": today,
            "image": self._build_image_url(slug, self._get_article_type_from_class()),
            "keywords": keywords
        }
    
    def _generate_author_object(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """Generate author object from frontmatter data.
        
        Args:
            frontmatter: Frontmatter data
            
        Returns:
            Author object
        """
        # Get author information with proper fallbacks
        author_data = self._get_frontmatter_value(frontmatter, "author", {})
        
        # Check if we should use an organization or person
        use_organization = self._get_nested_value(author_data, "use_organization", False)
        
        if use_organization:
            return {
                "@type": "Organization",
                "name": self._get_nested_value(author_data, "name", "Z-Beam")
            }
        else:
            # Use person with affiliation
            author_id = self._get_nested_value(author_data, "author_id", 1)
            author_name = self._get_nested_value(author_data, "author_name", "")
            author_country = self._get_nested_value(author_data, "author_country", "")
            author_credentials = self._get_nested_value(
                author_data, 
                "credentials", 
                "Industry Leader in Laser Cleaning Technology"
            )
            organization_name = self._get_nested_value(author_data, "name", "Laser Technology Institute")
            
            return {
                "@type": "Person",
                "identifier": author_id,
                "name": author_name,
                "nationality": author_country,
                "description": author_credentials,
                "affiliation": {
                    "@type": "Organization",
                    "name": organization_name
                }
            }
    
    def _generate_structured_value(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a Schema.org StructuredValue from a dictionary.
        
        Args:
            data: Dictionary to convert
            
        Returns:
            StructuredValue object
        """
        structured_value = {"@type": "StructuredValue"}
        
        for key, value in data.items():
            if key and value:
                # Convert camelCase to standard format
                formatted_key = key[0].lower() + key[1:]  # Ensure first letter is lowercase
                structured_value[formatted_key] = value
                
        return structured_value
    
    def _process_list_items(self, 
                           items: List[Union[Dict[str, Any], str]], 
                           name_key: str = "name",
                           description_key: str = "description",
                           thing_type: str = "Thing") -> List[Dict[str, Any]]:
        """Process a list of items into schema.org objects.
        
        Args:
            items: List of dictionaries or strings
            name_key: Key to use for name in dictionaries
            description_key: Key to use for description in dictionaries
            thing_type: Schema.org type to use
            
        Returns:
            List of schema.org objects
        """
        result = []
        
        for item in items:
            if isinstance(item, dict):
                name = item.get(name_key, "")
                description = item.get(description_key, "")
                
                if name:
                    obj = {
                        "@type": thing_type,
                        "name": name
                    }
                    
                    if description:
                        obj["description"] = description
                        
                    # Add other properties
                    for key, value in item.items():
                        if key not in [name_key, description_key]:
                            obj[key] = value
                            
                    result.append(obj)
            elif isinstance(item, str):
                result.append({
                    "@type": thing_type,
                    "name": item
                })
                
        return result
    
    def _get_article_type_from_class(self) -> str:
        """Extract article type from class name.
        
        Returns:
            Article type
        """
        # E.g., "ApplicationJsonldGenerator" -> "application"
        class_name = self.__class__.__name__
        if class_name.endswith("JsonldGenerator"):
            return class_name[:-len("JsonldGenerator")].lower()
        return "article"
        
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
        
    def _get_nested_value(self, data: Dict[str, Any], key: str, default: Any = "") -> Any:
        """Get nested value using dot notation.
        
        Args:
            data: Dictionary to extract from
            key: Key to extract
            default: Default value if key not found
            
        Returns:
            Value as string or empty string if not found
        """
        if not isinstance(data, dict):
            return default
        return str(data.get(key, default)) if data.get(key) is not None else default
        
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