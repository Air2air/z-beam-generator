#!/usr/bin/env python3
"""
Author Component Generator

Generates author information content using local JSON data.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional

from generators.component_generators import APIComponentGenerator, ComponentResult

logger = logging.getLogger(__name__)


class AuthorComponentGenerator(APIComponentGenerator):
    """Generator for author components using local author data"""

    def __init__(self):
        super().__init__("author")

    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> ComponentResult:
        """Generate author component content using local author data"""
        try:
            from utils.author_manager import get_author_by_id

            # FAIL-FAST: Author information is required - no defaults
            if not author_info or "id" not in author_info:
                raise Exception(
                    "Author information with 'id' field is required for author component generation"
                )

            author_id = author_info["id"]

            # Get author data using existing system - fail fast if not found
            author = get_author_by_id(author_id)
            if not author:
                raise Exception(
                    f"Author {author_id} not found - no fallback authors permitted in fail-fast architecture"
                )

            # Generate author content using local data
            content = self._create_author_content(material_name, author)
            logger.info(
                f"Generated author component for {material_name} using author {author.get('name', 'Unknown')}"
            )

            return ComponentResult(
                component_type="author", content=content, success=True
            )

        except Exception as e:
            logger.error(f"Error generating author component for {material_name}: {e}")
            return ComponentResult(
                component_type="author", content="", success=False, error_message=str(e)
            )

    def _create_author_content(self, material_name: str, author: Dict) -> str:
        """Create author content from author data - FAIL-FAST: all required fields must be present"""
        # FAIL-FAST: All required author fields must be present
        required_fields = ["name", "title", "country", "expertise", "image"]
        for field in required_fields:
            if field not in author:
                raise Exception(
                    f"Author data missing required field '{field}' - fail-fast architecture requires complete author information"
                )

        name = author["name"]
        title = author["title"]
        country = author["country"]
        expertise = author["expertise"]
        image_path = author["image"]

        content = f"""**{name}, {title}**
*{expertise}*
*{country}*

![{name}]({image_path})

Expert analysis of {material_name} laser cleaning applications, providing technical insights based on extensive research in materials processing and laser technology."""

        return content


def create_author_generator():
    """Factory function to create an author generator"""
    return AuthorComponentGenerator()
