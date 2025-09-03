#!/usr/bin/env python3
"""
Content Component Generator

Lightweight wrapper for ComponentGeneratorFactory integration.
Provides a clean interface to the fail_fast_generator.py content generation system.
"""

import logging
from typing import Dict, Optional
from generators.component_generators import APIComponentGenerator, ComponentResult

logger = logging.getLogger(__name__)

class TextComponentGenerator(APIComponentGenerator):
    """
    Text component generator that wraps the fail_fast_generator.

    This is a lightweight wrapper that integrates with ComponentGeneratorFactory
    while delegating the actual content generation to fail_fast_generator.py.
    """

    def __init__(self, ai_detection_service=None):
        """Initialize the text component generator."""
        super().__init__("text")
        self.ai_detection_service = ai_detection_service

    def generate(self, material_name: str, material_data: Dict,
                api_client=None, author_info: Optional[Dict] = None,
                frontmatter_data: Optional[Dict] = None,
                schema_fields: Optional[Dict] = None) -> ComponentResult:
        """
        Generate content using the fail_fast_generator.

        Args:
            material_name: Name of the material
            material_data: Material data dictionary
            api_client: API client for content generation
            author_info: Author information
            frontmatter_data: Frontmatter data from previous generation
            schema_fields: Schema fields (not used for content)

        Returns:
            ComponentResult with generated content
        """
        try:
            # Import the fail_fast_generator
            from .generators.fail_fast_generator import create_fail_fast_generator

            # Create the generator with scoring enabled
            generator = create_fail_fast_generator(
                max_retries=3,
                retry_delay=1.0,
                enable_scoring=True,
                human_threshold=75.0
            )

            # Generate content
            result = generator.generate(
                material_name=material_name,
                material_data=material_data,
                api_client=api_client,
                author_info=author_info,
                frontmatter_data=frontmatter_data
            )

            # Convert to ComponentResult
            return ComponentResult(
                component_type="text",
                content=result.content,
                success=result.success,
                error_message=result.error_message if not result.success else None
            )

        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return ComponentResult(
                component_type="text",
                content="",
                success=False,
                error_message=str(e)
            )