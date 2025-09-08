#!/usr/bin/env python3
"""
Author Management

Centralized author loading and management functionality.
Extracted from run.py to reduce bloat and improve testability.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional


def load_authors() -> List[Dict[str, Any]]:
    """
    Load author information from JSON file.

    Returns:
        List of author dictionaries

    Raises:
        FileNotFoundError: If authors file doesn't exist
        json.JSONDecodeError: If authors file is invalid JSON
    """
    authors_file = Path("components/author/authors.json")

    if not authors_file.exists():
        raise FileNotFoundError(f"Authors file not found: {authors_file}")

    try:
        with open(authors_file, "r", encoding="utf-8") as f:
            authors_data = json.load(f)

        # Handle both formats: direct list or object with "authors" key
        if isinstance(authors_data, list):
            return authors_data
        elif isinstance(authors_data, dict) and "authors" in authors_data:
            authors_list = authors_data["authors"]
            if not isinstance(authors_list, list):
                raise ValueError("Authors data must contain a list of authors")
            return authors_list
        else:
            raise ValueError(
                "Authors file must contain a list of authors or an object with 'authors' key"
            )

    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in authors file: {e}")


def get_author_by_id(author_id: int) -> Optional[Dict[str, Any]]:
    """
    Get author information by ID.

    Args:
        author_id: Author ID

    Returns:
        Author dictionary or None if not found
    """
    try:
        authors = load_authors()

        # Find author by ID field rather than array index
        for author in authors:
            if author.get("id") == author_id:
                return author

        return None

    except (FileNotFoundError, json.JSONDecodeError):
        return None


def list_authors() -> str:
    """
    Generate formatted list of all authors.

    Returns:
        Formatted string with all authors and their countries
    """
    try:
        authors = load_authors()

        if not authors:
            return "No authors found."

        output = ["📝 Available Authors:", "=" * 50]

        for i, author in enumerate(authors, 1):
            name = author.get("name", "Unknown")
            country = author.get("country", "Unknown")
            output.append(f"  {i:2d}. {name} ({country})")

        output.extend(
            [
                "=" * 50,
                f"Total: {len(authors)} authors available",
                "",
                "Usage: python3 run.py --material 'Steel'  # Author automatically resolved from materials.yaml",
            ]
        )

        return "\n".join(output)

    except (FileNotFoundError, json.JSONDecodeError) as e:
        return f"Error loading authors: {e}"


def validate_author_id(author_id: int) -> bool:
    """
    Validate if author ID is valid.

    Args:
        author_id: Author ID to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        authors = load_authors()
        return 1 <= author_id <= len(authors)
    except (FileNotFoundError, json.JSONDecodeError):
        return False


def get_author_info_for_generation(author_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Get author information formatted for content generation.

    Args:
        author_id: Optional author ID, if None returns default/empty author info

    Returns:
        Dictionary with author information ready for content generation
    """
    if author_id is None:
        return {
            "name": "AI Assistant",
            "country": "International",
            "bio": "AI-powered content generation system",
            "expertise": "laser cleaning technology",
        }

    author = get_author_by_id(author_id)
    if author is None:
        # Fallback to default
        return get_author_info_for_generation(None)

    return {
        "name": author.get("name", "Unknown Author"),
        "country": author.get("country", "Unknown"),
        "bio": author.get("bio", ""),
        "expertise": author.get("expertise", "laser cleaning technology"),
        "experience": author.get("experience", ""),
        "specialization": author.get("specialization", ""),
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
            Path("content/components/frontmatter")
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
                elif key == "author_id":
                    author_info["id"] = int(value) if value.isdigit() else 1

        if author_info:
            author_info.setdefault("id", 1)
            author_info.setdefault("country", "usa")
            return author_info

    except Exception as e:
        print(f"⚠️ Error extracting author info: {e}")

    return None


def get_author_info_for_material(
    material_name: str, fallback_author_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get author information for a material, prioritizing frontmatter data.

    This function first tries to extract author information from the material's
    frontmatter file. If that fails, it falls back to the provided author_id
    or default author information.

    Args:
        material_name: Name of the material
        fallback_author_id: Optional author ID to use as fallback

    Returns:
        Dictionary with author information ready for content generation
    """
    # First, try to extract from frontmatter file
    frontmatter_author = extract_author_info_from_frontmatter_file(material_name)
    if frontmatter_author:
        return {
            "name": frontmatter_author.get("name", "Unknown Author"),
            "country": frontmatter_author.get("country", "Unknown"),
            "bio": "",
            "expertise": "laser cleaning technology",
            "experience": "",
            "specialization": "",
            "id": frontmatter_author.get("id", 1),
        }

    # Fallback to provided author_id or default
    return get_author_info_for_generation(fallback_author_id)
