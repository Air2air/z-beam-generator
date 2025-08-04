"""
Base type generator for JSON-LD type-specific implementations.

This module serves as the foundation for type-specific JSON-LD generators.
"""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

class BaseTypeGenerator(ABC):
    """Base abstract class for type-specific JSON-LD generators."""
    
    def __init__(self, data: Dict[str, Any]):
        """Initialize with the data needed for generation.
        
        Args:
            data: Dictionary containing template data
        """
        self.data = data
    
    @abstractmethod
    def generate(self) -> Dict[str, Any]:
        """Generate type-specific JSON-LD structure.
        
        Returns:
            Dict[str, Any]: JSON-LD data for the specific type
        """
        pass
    
    def get_image_data(self, slug: str) -> Optional[Dict[str, Any]]:
        """Generate image data for JSON-LD based on frontmatter.
        
        Args:
            slug: The URL slug for the article
            
        Returns:
            Optional[Dict[str, Any]]: Image object or None if no images available
        """
        frontmatter = self.data.get("frontmatter_data", {})
        if not frontmatter or "images" not in frontmatter:
            return None
            
        images = frontmatter["images"]
        if not images:
            return None
            
        image_objects = []
        base_url = "https://www.z-beam.com/images"
        
        # Add hero image if available
        if "hero" in images and "alt" in images["hero"]:
            hero_img = {
                "@type": "ImageObject",
                "url": f"{base_url}/{slug}-hero.jpg",
                "caption": images["hero"]["alt"]
            }
            image_objects.append(hero_img)
        
        # Add closeup image if available
        if "closeup" in images and "alt" in images["closeup"]:
            closeup_img = {
                "@type": "ImageObject",
                "url": f"{base_url}/{slug}-closeup.jpg",
                "caption": images["closeup"]["alt"]
            }
            image_objects.append(closeup_img)
            
        return image_objects if image_objects else None
