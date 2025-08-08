"""
JSON-LD generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
Version: 3.0.5
"""

import logging
import re
from components.base.component import BaseComponent
from components.base.image_handler import ImageHandler
from components.base.utils.slug_utils import SlugUtils

logger = logging.getLogger(__name__)


class JsonldGenerator(BaseComponent):
    """JSON-LD structure generator optimized for materials science."""

    def _component_specific_processing(self, content: str) -> str:
        """Process JSON-LD with centralized structured content processing."""
        return self._process_structured_content(content, output_format="yaml")

    def _get_system_prompt(self) -> str:
        """Get JSON-LD-specific system prompt."""
        return (
            "You are a JSON-LD expert for materials science. "
            "Generate valid JSON-LD structured data in YAML format only. "
            "Focus on schema.org/Material or related schemas. "
            "Return only YAML format - no JSON, no code blocks, no explanations."
        )

    def _create_image_object(self, subject: str) -> str:
        """Create an image object for the JSON-LD.
        
        Args:
            subject: The material subject to create an image for
            
        Returns:
            str: Image URL for the material
        """
        # Use the image handler to get a properly formatted image
        image_handler = ImageHandler(self.category)
        return image_handler.get_image_url(subject)

    def _clean_subject_name(self, subject: str) -> str:
        """Clean and format the subject name for JSON-LD.
        
        Args:
            subject: Raw subject name
            
        Returns:
            str: Cleaned subject name
        """
        # Remove common suffixes and clean the name
        cleaned = re.sub(r'\s+(alloy|composite|material|substance)$', '', subject, flags=re.IGNORECASE)
        return cleaned.strip() or subject

    def _create_slug(self, subject: str) -> str:
        """Create a URL-friendly slug for the subject.
        
        Args:
            subject: The subject to create a slug for
            
        Returns:
            str: URL-friendly slug
        """
        return SlugUtils.create_slug(subject)
