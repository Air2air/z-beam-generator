"""
Frontmatter generator for Z-Beam Generator implementation with robust error handling and auto-recovery.
"""

import logging
import yaml
import re
from components.base.component import BaseComponent
from components.base.utils.validation import (
    validate_length, validate_required_fields, validate_category_consistency
)
from components.base.utils.formatting import format_frontmatter_with_comment

logger = logging.getLogger(__name__)

class FrontmatterGenerator(BaseComponent):
    """Generator for article frontmatter with robust validation and auto-recovery."""
    
    def _get_prompt_path(self) -> str:
        """Override to use the correct directory name.
        
        Returns:
            str: Path to prompt template
        """
        return "components/frontmatter/prompt.yaml"
    
    def _get_base_data(self) -> dict:
        """Get base data for the prompt template."""
        data = super()._get_base_data()
        return data
    
    def _get_subject_slug(self) -> str:
        """Get standardized subject slug for URLs.
        
        Returns:
            str: Hyphenated lowercase subject name
        """
        return self.subject.lower().replace(' ', '-').replace('_', '-')
    
    def _format_image_url(self, image_type, extension="jpg") -> str:
        """Format image URL based on image type.
        
        Args:
            image_type: Type of image (e.g., 'hero', 'thumbnail')
            extension: File extension (default: 'jpg')
            
        Returns:
            str: Formatted image URL
        """
        base_url = "/images"
        slug = self.data.get("slug", "").strip()
        
        if not slug:
            # Generate a fallback slug if not available
            title = self.data.get("title", "untitled").lower()
            slug = "-".join(title.split())
        
        # Format URL with appropriate components
        return f"{base_url}/{slug}-{image_type}.{extension}"
    
    def _process_images(self, data) -> dict:
        """Process all image URLs in the data dictionary.
        
        Args:
            data: Dictionary containing image data
            
        Returns:
            dict: Updated data with standardized image URLs
        """
        if not isinstance(data, dict) or "images" not in data:
            return data
            
        for image_type, image_data in data["images"].items():
            if isinstance(image_data, dict):
                # If URL is missing or empty, generate standardized URL
                if "url" not in image_data or not image_data["url"]:
                    image_data["url"] = self._format_image_url(image_type)
                else:
                    # Normalize existing URL
                    url = image_data["url"].lower()
                    
                    # Remove domain if present (handle various formats)
                    if "://" in url:
                        url = "/" + "/".join(url.split("/")[3:])
                    
                    # Ensure URL starts with /images/
                    if not url.startswith("/images/"):
                        url = "/images/" + url.split("/")[-1]
                    
                    # Get extension (default to jpg)
                    extension = "jpg"
                    if "." in url:
                        extension = url.split(".")[-1]
                    
                    # Create standardized URL
                    image_data["url"] = self._format_image_url(image_type, extension)
        
        return data
