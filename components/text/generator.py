#!/usr/bin/env python3
"""
Text Component Generator

Lightweight wrapper for ComponentGeneratorFactory integration.
Provides a clean interface to the fail_fast_generator.py text generation system.
"""

import logging
from typing import Dict, Optional, Any

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

    def get_component_info(self) -> Dict[str, Any]:
        """Get component information"""
        return {
            "name": "text",
            "description": "Technical content generation for laser cleaning articles",
            "version": "3.0.0",
            "requires_api": True,
            "type": "dynamic",
        }

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
        Generate text content using frontmatter data as primary source.

        FAIL-FAST: Requires counterpart frontmatter file to exist. Will not generate
        frontmatter itself - must be pre-generated.

        Args:
            material_name: Name of the material
            material_data: Raw material data from materials.yaml (fallback)
            api_client: API client for text generation
            author_info: Author information
            frontmatter_data: Processed frontmatter data (primary source)
            schema_fields: Schema fields (not used for text)

        Returns:
            ComponentResult with generated content
        """
        try:
            # FAIL-FAST: Text component requires counterpart frontmatter file
            if not frontmatter_data:
                from pathlib import Path
                safe_material = material_name.lower().replace(" ", "-").replace("/", "-")
                frontmatter_path = Path("content") / "components" / "frontmatter" / f"{safe_material}-laser-cleaning.md"

                if not frontmatter_path.exists():
                    error_msg = f"Counterpart frontmatter file not found: {frontmatter_path}. Text component requires pre-generated frontmatter data."
                    logger.error(f"❌ {error_msg}")
                    return ComponentResult(
                        component_type="text",
                        content="",
                        success=False,
                        error_message=error_msg,
                    )
                else:
                    # Try to load existing frontmatter data
                    try:
                        from utils.file_ops.frontmatter_loader import load_frontmatter_data
                        frontmatter_data = load_frontmatter_data(material_name)
                        if not frontmatter_data:
                            error_msg = f"Failed to load frontmatter data from existing file: {frontmatter_path}"
                            logger.error(f"❌ {error_msg}")
                            return ComponentResult(
                                component_type="text",
                                content="",
                                success=False,
                                error_message=error_msg,
                            )
                        # Convert datetime objects to strings for JSON serialization
                        import datetime
                        def convert_datetimes(obj):
                            if isinstance(obj, dict):
                                return {k: convert_datetimes(v) for k, v in obj.items()}
                            elif isinstance(obj, list):
                                return [convert_datetimes(item) for item in obj]
                            elif isinstance(obj, datetime.datetime):
                                return obj.isoformat()
                            elif isinstance(obj, datetime.date):
                                return obj.isoformat()
                            else:
                                return obj
                        frontmatter_data = convert_datetimes(frontmatter_data)
                    except Exception as e:
                        error_msg = f"Error loading frontmatter data: {e}"
                        logger.error(f"❌ {error_msg}")
                        return ComponentResult(
                            component_type="text",
                            content="",
                            success=False,
                            error_message=error_msg,
                        )

            # Import the fail_fast_generator
            from .generators.fail_fast_generator import create_fail_fast_generator

            logger.info(
                f"📝 Generating text for {material_name} using simplified approach"
            )

            # Create generator with settings optimized for test vs production
            # Use faster retry delays in test mode to speed up test execution
            # Test mode detection using environment variables directly
            import os
            is_test_mode = any([
                os.getenv("TEST_MODE", "").lower() in ("true", "1", "yes"),
                os.getenv("PYTEST_CURRENT_TEST", "") != "",
                "pytest" in os.getenv("_", "").lower(),
            ])
            
            retry_delay = 0.1 if is_test_mode else 1.0
            
            generator = create_fail_fast_generator(
                max_retries=3,
                retry_delay=retry_delay,
                enable_scoring=False,  # Disable scoring for basic text generation
                skip_ai_detection=True,  # No AI detection in basic text component
            )

            # Generate content with provided author info
            if not author_info:
                raise ValueError("Author information is required for text generation")

            # Use frontmatter_data as primary source, fall back to material_data
            primary_data = frontmatter_data if frontmatter_data else material_data

            # Simple text generation
            result = generator.generate(
                material_name=material_name,
                material_data=primary_data,  # Use frontmatter data as primary source
                api_client=api_client,
                author_info=author_info,
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

            # Format content with frontmatter at the bottom
            try:
                formatted_content = self._format_content_with_frontmatter(
                    result.content, material_name, author_info, frontmatter_data
                )
            except ValueError as e:
                # Re-raise ValueError for missing required dependencies (fail-fast)
                logger.error(f"Validation error in content formatting: {e}")
                raise

            # Apply centralized version stamping (will prepend to any existing legacy stamps)
            from versioning import stamp_component_output

            final_content = stamp_component_output("text", formatted_content)

            return ComponentResult(
                component_type="text",
                content=final_content,
                success=True,
                error_message=None,
            )

        except ValueError as e:
            # Re-raise ValueError for missing required dependencies (fail-fast)
            logger.error(f"Validation error in text generation: {e}")
            raise
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
        if frontmatter_data and "author" in frontmatter_data:
            author_name = frontmatter_data["author"]
        elif author_info and "name" in author_info:
            author_name = author_info["name"]
        else:
            raise ValueError("Author information is required for content formatting")

        # Create frontmatter
        frontmatter = f"""---
author: {author_name}
material: {material_name}
component: text
generated: {time.strftime('%Y-%m-%d')}
source: text
---"""

        # Combine content with frontmatter at the bottom
        return content + "\n\n" + frontmatter
