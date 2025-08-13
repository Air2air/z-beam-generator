"""
JSON-LD generator for Z-Beam Generator.

Strict fail-fast implementation with no fallbacks or defaults.
Version: 3.0.5
"""

import logging
from components.base.component import BaseComponent
from components.base.utils.jsonld_formatter import JsonldFormatter

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
        """Create an image object for the JSON-LD using utility.
        
        Args:
            subject: The material subject to create an image for
            
        Returns:
            str: Image URL for the material
        """
        return JsonldFormatter.create_image_object(subject, self.category)
