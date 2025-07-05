# generator/modules/metadata_generator.py

"""
Module for generating article metadata (YAML frontmatter).
"""

import datetime
import json
from typing import List, Dict, Any

from generator.modules.logger import get_logger

logger = get_logger("metadata_generator")


def generate_metadata(
    material: str,
    material_config: Dict[str, Any],
    article_config: Dict[str, Any],
    author_metadata: Dict[str, Any],
    ai_scores: Dict[str, float],
    article_category: str,
) -> str:
    """
    Generates the YAML frontmatter string for the article.

    Args:
        material (str): The primary material of the article.
        material_config (Dict[str, Any]): Researched data about the material.
        article_config (Dict[str, Any]): General article configuration (author, temperature, etc.).
        author_metadata (Dict[str, Any]): Full metadata for the author.
        ai_scores (Dict[str, float]): Dictionary of AI detection scores for each section.
        article_category (str): The category of the article.

    Returns:
        str: The YAML frontmatter string.
    """
    title = f"Laser Cleaning {material}"

    date_generated = datetime.datetime.now().strftime("%Y-%m-%d")

    # Combine categories and material for tags, ensure uniqueness and sort
    tags = [article_category.lower().replace(" ", "-")]
    if material:
        tags.append(material.lower().replace(" ", "-"))
    if (
        "material_details" in material_config
        and "applications" in material_config["material_details"]
    ):
        tags.extend(
            [
                app.lower().replace(" ", "-")
                for app in material_config["material_details"]["applications"]
            ]
        )
    tags = sorted(list(set(tags)))  # Unique and sorted

    # Assemble metadata dictionary with robust error handling
    def safe_get(d, key, default=None, warn_if_missing=False, context=""):
        value = d.get(key, default)
        if value == default and warn_if_missing:
            logger.warning(
                f"Missing key '{key}' in {context or 'dict'}, using default: {default}"
            )
        return value

    # Compose image path if not present
    image_value = safe_get(material_config, "image", "", False, "material_config")
    if not image_value:
        # Use articleCategory and material for image path
        image_value = f"/images/Material/material_{material.lower()}.jpg"

    metadata_dict = {
        "title": title,
        "nameShort": material,
        "publishedAt": date_generated,
        "authorName": safe_get(author_metadata, "name", "", True, "author_metadata"),
        "authorTitle": safe_get(author_metadata, "title", "", True, "author_metadata"),
        "authorBio": safe_get(author_metadata, "bio", "", True, "author_metadata"),
        "tags": tags,
        "keywords": safe_get(material_config, "keywords", [], True, "material_config"),
        "image": image_value,
        "atomicNumber": safe_get(
            material_config, "atomicNumber", None, True, "material_config"
        ),
        "chemicalSymbol": safe_get(
            material_config, "chemicalSymbol", None, True, "material_config"
        ),
        "materialType": safe_get(
            material_config, "materialType", "N/A", True, "material_config"
        ),
        "metalClass": safe_get(
            material_config, "metalClass", "N/A", True, "material_config"
        ),
        "crystalStructure": safe_get(
            material_config, "crystalStructure", "", True, "material_config"
        ),
        "primaryApplication": safe_get(
            material_config, "primaryApplication", "N/A", True, "material_config"
        ),
        "articleCategory": article_category or "Material",
        "temperature": safe_get(
            article_config, "temperature", None, True, "article_config"
        ),
        "industries": safe_get(
            material_config, "industries", [], True, "material_config"
        ),
    }

    # Format into YAML string
    yaml_lines = ["---"]
    for key, value in metadata_dict.items():
        if isinstance(value, list):
            yaml_lines.append(f"{key}:")
            for item in value:
                if isinstance(item, dict):
                    yaml_lines.append(f"  - {json.dumps(item)}")
                else:
                    yaml_lines.append(f"  - {json.dumps(item)}")
        elif isinstance(value, dict):
            yaml_lines.append(f"{key}:")
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, list):
                    yaml_lines.append(f"  {sub_key}:")
                    for item in sub_value:
                        yaml_lines.append(f"    - {json.dumps(item)}")
                elif isinstance(sub_value, dict):
                    yaml_lines.append(f"  {sub_key}: {json.dumps(sub_value)}")
                else:
                    yaml_lines.append(f"  {sub_key}: {json.dumps(sub_value)}")
        else:
            yaml_lines.append(f"{key}: {json.dumps(value)}")
    yaml_lines.append("---")
    yaml_frontmatter = "\n".join(yaml_lines)

    logger.debug(f"Generated YAML Frontmatter:\n{yaml_frontmatter}")
    return yaml_frontmatter


def assemble_page(yaml_frontmatter: str, mdx_content_sections: List[str]) -> str:
    """
    Assembles the complete MDX page with frontmatter and content.

    Args:
        yaml_frontmatter (str): The generated YAML frontmatter string.
        mdx_content_sections (List[str]): A list of MDX content strings for each section.

    Returns:
        str: The complete MDX page content.
    """
    return f"{yaml_frontmatter}\n\n" + "\n\n".join(mdx_content_sections)
