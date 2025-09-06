#!/usr/bin/env python3
"""
Tags Generator - API-based tags generation for laser cleaning materials.
"""

import logging
from typing import Dict, Optional

from generators.component_generators import APIComponentGenerator, ComponentResult

logger = logging.getLogger(__name__)


class TagsComponentGenerator(APIComponentGenerator):
    """API-based generator for tags components"""

    def __init__(self):
        super().__init__("tags")

    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> ComponentResult:
        """Generate tags using API"""
        try:
            if not api_client:
                logger.error("API client is required for tags generation")
                return ComponentResult(
                    component_type="tags",
                    content="",
                    success=False,
                    error_message="API client not provided",
                )

            # Create template variables
            template_vars = self._create_template_vars(
                material_name,
                material_data,
                author_info,
                frontmatter_data,
                schema_fields,
            )

            # Build API prompt
            prompt = self._build_api_prompt(template_vars, frontmatter_data)

            # Call API
            api_response = api_client.generate_content(prompt)

            if api_response.get("success"):
                content = api_response.get("content", "")
                logger.info(f"Generated tags for {material_name}")

                return ComponentResult(
                    component_type="tags", content=content, success=True
                )
            else:
                error_msg = api_response.get("error", "API call failed")
                logger.error(f"API error for tags generation: {error_msg}")
                return ComponentResult(
                    component_type="tags",
                    content="",
                    success=False,
                    error_message=error_msg,
                )

        except Exception as e:
            logger.error(f"Error generating tags for {material_name}: {e}")
            return ComponentResult(
                component_type="tags", content="", success=False, error_message=str(e)
            )
