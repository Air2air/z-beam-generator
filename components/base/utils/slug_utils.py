"""
Centralized slug utilities for Z-Beam Generator.

This module provides consistent slug generation across all components.
"""

import re
import logging

logger = logging.getLogger(__name__)


class SlugUtils:
    """Centralized utilities for creating URL-friendly slugs."""
    
    @staticmethod
    def create_slug(text: str) -> str:
        """Create a URL-friendly slug from any text.
        
        Args:
            text: Raw text to convert to slug
            
        Returns:
            str: URL-friendly slug with no double dashes
        """
        if not text:
            return ""
        
        # Convert to lowercase
        slug = text.lower()
        
        # Replace spaces and underscores with hyphens
        slug = slug.replace(' ', '-').replace('_', '-')
        
        # Remove any characters that aren't alphanumeric or hyphens
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        
        # Replace multiple consecutive hyphens with single hyphens
        slug = re.sub(r'-+', '-', slug)
        
        # Remove leading and trailing hyphens
        slug = slug.strip('-')
        
        return slug
    
    @staticmethod
    def create_subject_slug(subject: str) -> str:
        """Create a subject-specific slug.
        
        Args:
            subject: Subject name
            
        Returns:
            str: Subject slug
        """
        return SlugUtils.create_slug(subject)
    
    @staticmethod
    def create_category_slug(category: str) -> str:
        """Create a category-specific slug.
        
        Args:
            category: Category name
            
        Returns:
            str: Category slug
        """
        return SlugUtils.create_slug(category)
    
    @staticmethod
    def create_article_type_slug(article_type: str) -> str:
        """Create an article type-specific slug.
        
        Args:
            article_type: Article type name
            
        Returns:
            str: Article type slug
        """
        return SlugUtils.create_slug(article_type)
    
    @staticmethod
    def create_image_slug(subject: str, image_type: str = "hero") -> str:
        """Create an image filename slug.
        
        Args:
            subject: Subject name
            image_type: Type of image (hero, closeup, etc.)
            
        Returns:
            str: Image filename slug
        """
        subject_slug = SlugUtils.create_subject_slug(subject)
        
        # Handle empty subject case
        if not subject_slug:
            if image_type in ["hero", "closeup", "process", "equipment", "application"]:
                return f"unknown-laser-cleaning-{image_type}"
            else:
                return f"unknown-{image_type}"
        
        # For certain image types, add the laser-cleaning prefix
        if image_type in ["hero", "closeup", "process", "equipment", "application"]:
            return f"{subject_slug}-laser-cleaning-{image_type}"
        else:
            return f"{subject_slug}-{image_type}"
    
    @staticmethod
    def create_image_url(subject: str, image_type: str = "hero", extension: str = "jpg") -> str:
        """Create a complete image URL.
        
        Args:
            subject: Subject name
            image_type: Type of image (hero, closeup, etc.)
            extension: File extension (default: jpg)
            
        Returns:
            str: Complete image URL
        """
        slug = SlugUtils.create_image_slug(subject, image_type)
        return f"/images/{slug}.{extension}"
    
    @staticmethod
    def normalize_existing_slug(slug: str) -> str:
        """Normalize an existing slug to ensure consistency.
        
        Args:
            slug: Existing slug that may have inconsistencies
            
        Returns:
            str: Normalized slug
        """
        return SlugUtils.create_slug(slug)
    
    @staticmethod
    def normalize_image_url(url: str) -> str:
        """Normalize an existing image URL.
        
        Args:
            url: Existing image URL
            
        Returns:
            str: Normalized image URL
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
        
        # Replace any double dashes with single dashes (redundant but safe)
        url = re.sub(r'-+', '-', url)
        
        # Extract the filename part and ensure no trailing dashes before extension
        if ".jpg" in url:
            path_part, extension = url.rsplit('.', 1)
            # Remove trailing dashes from the path
            path_part = path_part.rstrip('-')
            url = f"{path_part}.{extension}"
        
        # Ensure .jpg extension
        if not url.endswith(".jpg"):
            url = re.sub(r'\.(png|jpeg|gif|webp)$', '.jpg', url)
            if not url.endswith(".jpg"):
                url += ".jpg"
        
        return url
