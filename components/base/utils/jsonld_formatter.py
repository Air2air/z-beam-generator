"""JSON-LD formatting utilities for structured data generation."""

import re
import logging
from components.base.utils.slug_utils import SlugUtils
from components.base.image_handler import ImageHandler

logger = logging.getLogger(__name__)

class JsonldFormatter:
    """Utilities for processing and formatting JSON-LD structured data."""
    
    @staticmethod
    def clean_subject_name(subject: str) -> str:
        """Clean and format the subject name for JSON-LD.
        
        Args:
            subject: Raw subject name
            
        Returns:
            str: Cleaned subject name
        """
        # Remove common suffixes and clean the name
        cleaned = re.sub(r'\s+(alloy|composite|material|substance)$', '', subject, flags=re.IGNORECASE)
        return cleaned.strip() or subject
    
    @staticmethod
    def create_image_object(subject: str, category: str = None) -> str:
        """Create an image object for the JSON-LD.
        
        Args:
            subject: The material subject to create an image for
            category: Optional category for the image handler
            
        Returns:
            str: Image URL for the material
        """
        # Use the image handler to get a properly formatted image
        image_handler = ImageHandler(category or 'material')
        return image_handler.get_image_url(subject)
    
    @staticmethod
    def create_slug(subject: str) -> str:
        """Create a URL-friendly slug for the subject.
        
        Args:
            subject: The subject to create a slug for
            
        Returns:
            str: URL-friendly slug
        """
        return SlugUtils.create_slug(subject)
    
    @staticmethod
    def validate_jsonld_structure(content: str) -> bool:
        """Validate that content contains proper JSON-LD structure.
        
        Args:
            content: Content to validate
            
        Returns:
            bool: True if content appears to be valid JSON-LD structure
        """
        # Check for common JSON-LD markers
        jsonld_markers = [
            '@context',
            '@type',
            'schema.org',
            'Material',
            'name',
            'description'
        ]
        
        # Content should contain most JSON-LD structural elements
        found_markers = sum(1 for marker in jsonld_markers if marker in content)
        
        return found_markers >= 3  # At least 3 core JSON-LD elements
    
    @staticmethod
    def sanitize_jsonld_content(content: str) -> str:
        """Sanitize JSON-LD content to ensure proper formatting.
        
        Args:
            content: Raw JSON-LD content
            
        Returns:
            str: Sanitized JSON-LD content
        """
        # Remove any markdown code block markers
        content = re.sub(r'```(?:json|yaml|jsonld)?\s*', '', content)
        content = re.sub(r'```\s*$', '', content, flags=re.MULTILINE)
        
        # Clean up extra whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        # Ensure proper YAML structure
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip empty lines at the start
            if not line.strip() and not cleaned_lines:
                continue
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    @staticmethod
    def format_material_jsonld(subject: str, category: str = None, **kwargs) -> dict:
        """Create a basic JSON-LD structure for a material.
        
        Args:
            subject: Material name
            category: Material category
            **kwargs: Additional properties
            
        Returns:
            dict: Basic JSON-LD structure
        """
        clean_name = JsonldFormatter.clean_subject_name(subject)
        slug = JsonldFormatter.create_slug(subject)
        image_url = JsonldFormatter.create_image_object(subject, category)
        
        jsonld_structure = {
            '@context': 'https://schema.org',
            '@type': 'Material',
            'name': clean_name,
            'identifier': slug,
            'image': image_url,
            'url': f'https://z-beam.com/{slug}',
            'category': category or 'material'
        }
        
        # Add any additional properties
        for key, value in kwargs.items():
            if value and key not in jsonld_structure:
                jsonld_structure[key] = value
        
        return jsonld_structure
