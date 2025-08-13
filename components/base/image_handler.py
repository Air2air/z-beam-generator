"""
Image handler for Z-Beam Generator components.

Provides standardized image URL generation and handling across all components.
"""
import logging
from typing import Dict, Any, Optional

from components.base.utils.slug_utils import SlugUtils

logger = logging.getLogger(__name__)


class ImageHandler:
    """Handler for generating and standardizing image URLs across components."""
    
    @staticmethod
    def format_image_url(subject: str, image_type: str, custom_slug: Optional[str] = None) -> str:
        """Generate a standardized image URL for a subject.
        
        Args:
            subject: Subject name
            image_type: Type of image (hero, closeup, etc.)
            custom_slug: Optional custom slug override
            
        Returns:
            str: Formatted image URL
        """
        if custom_slug:
            slug = SlugUtils.normalize_existing_slug(custom_slug)
            if image_type in ["hero", "process", "equipment", "application"]:
                url = f"/images/{slug}-laser-cleaning-{image_type}.jpg"
            else:
                url = f"/images/{slug}-{image_type}.jpg"
        else:
            url = SlugUtils.create_image_url(subject, image_type)
        
        # Normalize the URL to ensure no double dashes
        return SlugUtils.normalize_image_url(url)
    
    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalize an image URL to follow Z-Beam standards.
        
        Args:
            url: Raw URL string
            
        Returns:
            str: Normalized URL
        """
        return SlugUtils.normalize_image_url(url)
    
    @classmethod
    def process_image_data(cls, data: Dict[str, Any], subject: str) -> Dict[str, Any]:
        """Process all image URLs in data to ensure they follow standards.
        
        Args:
            data: Dictionary containing image data
            subject: Subject name for generating URLs
            
        Returns:
            dict: Updated data with normalized image URLs
        """
        if not isinstance(data, dict) or "images" not in data:
            return data
        
        images = data.get("images", {})
        if not isinstance(images, dict):
            return data
        
        # Process each image type
        for image_type, image_data in images.items():
            if isinstance(image_data, dict):
                # Generate or normalize URL
                if "url" in image_data:
                    url = image_data["url"]
                    if isinstance(url, str):
                        image_data["url"] = cls.normalize_url(url)
                else:
                    # Generate URL if missing
                    image_data["url"] = cls.format_image_url(subject, image_type)
        
        return data
    
    @classmethod
    def add_missing_images(cls, data: Dict[str, Any], subject: str) -> Dict[str, Any]:
        """Add missing image entries with standard URLs.
        
        Args:
            data: Dictionary to add images to
            subject: Subject name for generating URLs
            
        Returns:
            dict: Updated data with image entries
        """
        if "images" not in data:
            data["images"] = {}
        
        images = data["images"]
        if not isinstance(images, dict):
            data["images"] = images = {}
        
        # Standard image types to ensure are present
        standard_types = ["hero", "closeup"]
        
        for image_type in standard_types:
            if image_type not in images:
                images[image_type] = {
                    "alt": f"{subject} laser cleaning {image_type} image",
                    "url": cls.format_image_url(subject, image_type),
                }
        
        return data
