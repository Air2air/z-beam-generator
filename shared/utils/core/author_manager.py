#!/usr/bin/env python3
"""
Author Management

Centralized author loading and management functionality.
Extracted from run.py to reduce bloat and improve testability.

IMPORTANT: This module now delegates to config.authors_registry as the
single source of truth. The JSON file is kept for backward compatibility
but the registry is authoritative.
"""

import logging
from typing import Any, Dict, List, Optional

# Import authoritative registry
from data.authors.registry import (
    get_author as registry_get_author,
    get_all_authors as registry_get_all_authors,
    list_valid_author_ids as registry_list_valid_author_ids,
)


def load_authors() -> List[Dict[str, Any]]:
    """
    Load author information - delegates to registry.
    
    This function is kept for backward compatibility but now returns
    data from the authoritative registry instead of parsing JSON.

    Returns:
        List of author dictionaries from registry
    """
    return registry_get_all_authors()


def get_author_by_id(author_id: int) -> Optional[Dict[str, Any]]:
    """
    Get author information by ID - delegates to registry.
    
    Args:
        author_id: Author ID

    Returns:
        Author dictionary from registry, or None if not found
    """
    try:
        return registry_get_author(author_id)
    except KeyError:
        logging.warning(
            f"Author ID {author_id} not in registry. "
            f"Valid IDs: {registry_list_valid_author_ids()}"
        )
        return None


def list_authors() -> str:
    """
    Generate formatted list of all authors.

    Returns:
        Formatted string with all authors and their countries
    """
    authors = load_authors()

    if not authors:
        return "No authors found."

    output = ["📝 Available Authors:", "=" * 50]

    for author in authors:
        author_id = author.get("id", "?")
        name = author.get("name", "Unknown")
        country = author.get("country", "Unknown")
        output.append(f"  {author_id:2d}. {name} ({country})")

    output.extend(
        [
            "=" * 50,
            f"Total: {len(authors)} authors available",
            "",
            "Usage: python3 run.py --material 'Steel'  # Author automatically resolved from Materials.yaml",
        ]
    )

    return "\n".join(output)


# validate_author_id is imported directly from registry


# validate_author_id is imported directly from registry


def get_author_info_for_generation(author_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Get author information formatted for content generation.
    
    DEPRECATED: Use config.authors_registry.get_author() directly instead.

    Args:
        author_id: Author ID (required - no fallbacks)

    Returns:
        Dictionary with author information ready for content generation
        
    Raises:
        ValueError: If author_id is None (no fallbacks allowed)
        KeyError: If author_id not in registry
    """
    if author_id is None:
        raise ValueError(
            "author_id is required - no fallback authors allowed. "
            "Ensure Materials.yaml has author.id for all materials."
        )

    author = get_author_by_id(author_id)
    if author is None:
        raise KeyError(
            f"Author ID {author_id} not in registry. "
            f"Valid IDs: {registry_list_valid_author_ids()}"
        )

    return {
        "name": author["name"],
        "country": author["country"],
        "expertise": author["expertise"],
        "title": author.get("title", ""),
        "sex": author.get("sex", ""),
        "image": author.get("image", ""),
    }


def extract_author_info_from_frontmatter_file(
    material_name: str,
) -> Optional[Dict[str, Any]]:
    """
    Extract author information from the corresponding frontmatter file.

    This function reads the frontmatter file for a material and extracts
    author information including name, country, and ID.

    Args:
        material_name: Name of the material (e.g., "Alumina", "Steel")

    Returns:
        Dictionary with author information or None if not found
    """
    try:
        from pathlib import Path

        # Look for the frontmatter file
        frontmatter_path = (
            Path("frontmatter/materials")
            / f"{material_name}-laser-cleaning.md"
        )

        if not frontmatter_path.exists():
            return None

        with open(frontmatter_path, "r", encoding="utf-8") as f:
            content = f.read()

        return extract_author_info_from_content(content)

    except Exception as e:
        print(f"⚠️ Error extracting author info from frontmatter file: {e}")
        return None


def extract_author_info_from_content(content: str) -> Optional[Dict[str, Any]]:
    """
    Extract author information from content frontmatter.

    Args:
        content: Markdown content with frontmatter

    Returns:
        Dictionary with author information or None if not found
    """
    try:
        lines = content.split("\n")
        in_frontmatter = False
        author_info = {}

        for line in lines:
            if line.strip() == "---":
                if not in_frontmatter:
                    in_frontmatter = True
                else:
                    break
                continue

            if in_frontmatter and ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip().strip('"')

                if key == "author":
                    author_info["name"] = value
                elif key == "persona_country":
                    author_info["country"] = value.lower()

        if author_info:
            # NO fallbacks - require explicit values
            return author_info

    except Exception as e:
        print(f"⚠️ Error extracting author info: {e}")

    return None


def get_author_info_for_material(
    material_data_or_name: Any, fallback_author_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get author information for a material using author.id from Materials.yaml.
    
    FAIL-FAST: No fallbacks allowed. Material must have author.id defined.

    Args:
        material_data_or_name: Material data dictionary with author.id
        fallback_author_id: DEPRECATED - no fallbacks allowed

    Returns:
        Dictionary with author information ready for content generation
        
    Raises:
        ValueError: If material_data_or_name is not a dict or missing author.id
        KeyError: If author.id not in registry
    """
    # Must be a dictionary with author.id
    if not isinstance(material_data_or_name, dict):
        raise ValueError(
            f"material_data_or_name must be dict with author.id, "
            f"got {type(material_data_or_name).__name__}"
        )

    # Extract author.id from material data (REQUIRED)
    if "author" not in material_data_or_name:
        raise ValueError(
            "Material missing 'author' field. "
            "Add author.id to Materials.yaml for this material."
        )
    
    author_field = material_data_or_name["author"]
    if not isinstance(author_field, dict) or "id" not in author_field:
        raise ValueError(
            "Material author missing 'id' field. "
            "Add author.id to Materials.yaml for this material."
        )
    
    material_author_id = author_field["id"]
    logging.info(
        f"Resolved author.id {material_author_id} for material {material_data_or_name.get('name', 'Unknown')}"
    )
    
    # Get author from registry - FAIL-FAST if not found
    author = get_author_by_id(material_author_id)
    if not author:
        raise KeyError(
            f"Author ID {material_author_id} not in registry. "
            f"Valid IDs: {registry_list_valid_author_ids()}"
        )
    
    logging.info(f"👤 Using author {author['name']} (ID: {material_author_id}) from Materials.yaml")
    return {
        "name": author["name"],
        "country": author["country"],
        "expertise": author["expertise"],
        "id": material_author_id,
        "sex": author.get("sex", ""),
        "title": author.get("title", ""),
        "image": author.get("image", ""),
    }
