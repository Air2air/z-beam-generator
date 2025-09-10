#!/usr/bin/env python3
"""
Frontmatter Component Post-Processor

Component-specific post-processing logic for frontmatter components.
"""

import logging
from typing import Any, Dict

import yaml

from .utils import validate_frontmatter_properties_completeness

logger = logging.getLogger(__name__)


def analyze_frontmatter_completeness(content: str) -> Dict[str, Any]:
    """
    Analyze frontmatter content for completeness and structure.

    Args:
        content: The frontmatter content to analyze

    Returns:
        Dictionary with analysis results
    """
    try:
        # Extract YAML content from frontmatter
        if not content.startswith("---"):
            return {"error": "Content does not start with frontmatter markers"}

        yaml_end = content.find("---", 3)
        if yaml_end == -1:
            return {"error": "Frontmatter not properly closed"}

        yaml_content = content[3:yaml_end].strip()
        frontmatter_data = yaml.safe_load(yaml_content)

        if not frontmatter_data:
            return {"error": "Empty frontmatter data"}

        # Get completeness analysis
        completeness = validate_frontmatter_properties_completeness(frontmatter_data)

        # Add additional metrics
        summary = {
            "total_fields": len(frontmatter_data),
            "has_properties": "properties" in frontmatter_data,
            "has_chemical_props": "chemicalProperties" in frontmatter_data,
            "has_category": "category" in frontmatter_data,
            "completeness_score": completeness["completeness"],
            "missing_sections": completeness["missing_sections"],
            "missing_properties": completeness["missing_properties"],
            "recommendations": completeness["recommendations"],
        }

        return summary

    except Exception as e:
        return {"error": f"Analysis failed: {e}"}


def post_process_frontmatter(content: str, material_name: str) -> str:
    """
    Post-process frontmatter content with enhancements.

    Args:
        content: Raw frontmatter content
        material_name: Name of the material

    Returns:
        Enhanced frontmatter content
    """
    try:
        logger.info(f"Post-processing frontmatter for {material_name}")

        # Basic validation
        if not content or not content.strip():
            logger.warning(f"Empty frontmatter content for {material_name}")
            return content

        # Ensure proper frontmatter markers
        if not content.startswith("---"):
            content = f"---\n{content}"
        if not content.strip().endswith("---"):
            content = f"{content}\n---"

        logger.info(f"Successfully post-processed frontmatter for {material_name}")
        return content

    except Exception as e:
        logger.error(f"Error post-processing frontmatter for {material_name}: {e}")
        return content
