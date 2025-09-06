#!/usr/bin/env python3
"""
Text Component Generator

Lightweight wrapper for ComponentGeneratorFactory integration.
Provides a clean interface to the fail_fast_generator.py text generation system.
"""

import logging
from typing import Dict, Optional

from generators.component_generators import APIComponentGenerator, ComponentResult

logger = logging.getLogger(__name__)


class TextComponentGenerator(APIComponentGenerator):
    """
    Text component generator that wraps the fail_fast_generator.

    This is a lightweight wrapper that integrates with ComponentGeneratorFactory
    while delegating the actual text generation to fail_fast_generator.py.
    """

    def __init__(self):
        """Initialize the text component generator."""
        super().__init__("text")

    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> ComponentResult:
        """
        Generate text content using simplified prompting.

        Args:
            material_name: Name of the material
            material_data: Material data dictionary
            api_client: API client for text generation
            author_info: Author information
            frontmatter_data: Frontmatter data from previous generation
            schema_fields: Schema fields (not used for text)

        Returns:
            ComponentResult with generated content
        """
        try:
            # Import the fail_fast_generator
            from .fail_fast_generator import create_fail_fast_generator

            logger.info(
                f"📝 Generating text for {material_name} using simplified approach"
            )

            # Create generator with basic settings
            generator = create_fail_fast_generator(
                max_retries=3,
                retry_delay=1.0,
                enable_scoring=False,  # Disable scoring for basic text generation
                skip_ai_detection=True,  # No AI detection in basic text component
            )

            # Generate content with provided author info
            current_author_info = author_info.copy() if author_info else {}
            if not current_author_info:
                current_author_info = {
                    "name": "Technical Expert",
                    "country": "usa",
                    "language": "english",
                }

            # Simple text generation
            result = generator.generate(
                material_name=material_name,
                material_data=material_data,
                api_client=api_client,
                author_info=current_author_info,
                frontmatter_data=frontmatter_data,
            )

            if not result.success:
                logger.warning(
                    f"❌ Text generation failed for {material_name}: {result.error_message}"
                )
                return ComponentResult(
                    component_type="text",
                    content="",
                    success=False,
                    error_message=result.error_message,
                )

            logger.info(f"✅ Text generated successfully for {material_name}")
            
            # Format content with frontmatter at the bottom
            formatted_content = self._format_content_with_frontmatter(
                result.content, material_name, author_info, frontmatter_data
            )
            
            return ComponentResult(
                component_type="text",
                content=formatted_content,
                success=True,
                error_message=None,
            )

        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return ComponentResult(
                component_type="text", content="", success=False, error_message=str(e)
            )

    def _format_content_with_frontmatter(
        self,
        content: str,
        material_name: str,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
    ) -> str:
        """
        Format content with frontmatter at the bottom.
        
        Args:
            content: Generated text content
            material_name: Name of the material
            author_info: Author information from generation
            frontmatter_data: Frontmatter data from counterpart component
            
        Returns:
            Formatted content with frontmatter
        """
        import time
        
        # Extract author information from frontmatter data if available
        author_name = "Technical Expert"
        if frontmatter_data and "author" in frontmatter_data:
            author_name = frontmatter_data["author"]
        elif author_info and "name" in author_info:
            author_name = author_info["name"]
            
        # Create frontmatter
        frontmatter = f"""---
author: {author_name}
material: {material_name}
component: text
generated: {time.strftime('%Y-%m-%d')}
source: frontmatter
---"""
        
        # Combine content with frontmatter at the bottom
        return content + "\n\n" + frontmatter
