"""
Image handler for Z-Beam Generator components.

Provides standardized image URL generation and handling across all components.
"""
import re
import logging
from typing import Dict, Any, Optional

from components.base.utils.slug_utils import SlugUtils

logger = logging.getLogger(__name__)


class ImageHandler:
    """Handler for generating and standardizing image URLs across components."""
    
    @staticmethod
    def get_subject_slug(subject: str) -> str:
        """Convert a subject name to a URL-friendly slug.
        
        Args:
            subject: Raw subject name
            
        Returns:
            str: URL-friendly slug
        """
        return SlugUtils.create_subject_slug(subject)
    
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

import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ImageHandler:
    """Handler for generating and standardizing image URLs across components."""
    
    @staticmethod
    def get_subject_slug(subject: str) -> str:
        """Convert a subject name to a URL-friendly slug.
        
        Args:
            subject: Raw subject name
            
        Returns:
            str: URL-friendly slug
        """
        # First replace spaces and underscores with hyphens
        slug = subject.lower().replace(' ', '-').replace('_', '-')
        # Then replace any double hyphens with single hyphens
        slug = re.sub(r'-+', '-', slug)
        return slug
    
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
        slug = custom_slug or ImageHandler.get_subject_slug(subject)
        
        # For certain image types, add the laser-cleaning prefix
        if image_type in ["hero", "process", "equipment", "application"]:
            url = f"/images/{slug}-laser-cleaning-{image_type}.jpg"
        else:
            url = f"/images/{slug}-{image_type}.jpg"
        
        # Normalize the URL to ensure no double dashes
        return ImageHandler.normalize_url(url)
    
    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalize an image URL to follow Z-Beam standards.
        
        Args:
            url: Raw URL string
            
        Returns:
            str: Normalized URL
        """
        if not url:
            return ""
        
        # Convert to lowercase
        url = url.lower()
        
        # Remove domain if present (handle various formats)
        if "://" in url:
            url = "/" + "/".join(url.split("/")[3:])
        
        # Ensure URL starts with /images/
        if not url.startswith("/images/"):
            url = "/images/" + url.split("/")[-1]
        
        # Remove any arrow sequences that might have been introduced by the model
        url = re.sub(r'-+>+-*', '-', url)
        url = re.sub(r'([^a-z])>+-*', r'\1', url)
        
        # Replace any double hyphens with single hyphens
        url = re.sub(r'-+', '-', url)
        
        # Fix missing hyphens between subject and image type
        url = re.sub(r'(/images/[a-z0-9-]+)laser-cleaning', r'\1-laser-cleaning', url)
        
        # Replace any double dashes with single dashes
        url = re.sub(r'-+', '-', url)
        
        # Ensure .jpg extension
        if not url.endswith(".jpg"):
            url = re.sub(r'\.(png|jpeg|gif|webp)$', '.jpg', url)
            if not url.endswith(".jpg"):
                url += ".jpg"
        
        return url
    
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
        
        if isinstance(data["images"], dict):
            for image_type, image_data in data["images"].items():
                if isinstance(image_data, dict) and "url" in image_data:
                    # Get existing URL or generate a new one if empty
                    url = image_data["url"]
                    
                    if not url:
                        # Generate a new URL if none exists
                        image_data["url"] = cls.format_image_url(subject, image_type)
                    elif "://" in url or not url.startswith("/images/") or ">" in url:
                        # Normalize problematic URLs
                        image_data["url"] = cls.normalize_url(url)
                    
                    # Add alt text if missing
                    if "alt" not in image_data or not image_data["alt"]:
                        if image_type == "hero":
                            image_data["alt"] = f"Industrial laser cleaning system processing {subject} material"
                        elif image_type == "closeup":
                            image_data["alt"] = f"Close-up view of {subject} surface after laser cleaning"
                        else:
                            image_data["alt"] = f"{subject} being processed with laser cleaning technology"
        
        return data
    
    @classmethod
    def add_missing_images(cls, data: Dict[str, Any], subject: str) -> Dict[str, Any]:
        """Add standard images if they're missing from the data.
        
        Args:
            data: Dictionary to update
            subject: Subject name
            
        Returns:
            dict: Updated data with standard images added
        """
        if not isinstance(data, dict):
            return data
        
        # Create images section if it doesn't exist
        if "images" not in data:
            data["images"] = {}
        
        # Ensure standard image types exist
        standard_types = ["hero", "closeup"]
        
        for image_type in standard_types:
            if image_type not in data["images"]:
                data["images"][image_type] = {
                    "url": cls.format_image_url(subject, image_type),
                    "alt": f"{subject} laser cleaning {image_type} image"
                }
            elif not isinstance(data["images"][image_type], dict):
                data["images"][image_type] = {
                    "url": cls.format_image_url(subject, image_type),
                    "alt": f"{subject} laser cleaning {image_type} image"
                }
        
        return data
