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
                "Usage: python3 run.py --material 'Steel'  # Author automatically resolved from Materials.yaml",
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
    material_data_or_name: Any, fallback_author_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get author information for a material, prioritizing material data author_id.

    This function first tries to extract author ID from the material data,
    then falls back to existing frontmatter, and finally to the fallback ID.

    Args:
        material_data_or_name: Material data dictionary or material name
        fallback_author_id: Optional author ID to use as fallback

    Returns:
        Dictionary with author information ready for content generation
    """
    # Extract material name for frontmatter lookup
    material_name = material_data_or_name
    material_author_id = None

    # Debug print
    print(f"⚠️ Material data extracted directly: {material_data_or_name}")

    # If material_data_or_name is a dictionary with material data
    if isinstance(material_data_or_name, dict):
        # Extract author_id from material data
        if "author_id" in material_data_or_name:
            material_author_id = material_data_or_name["author_id"]
            import logging
            logging.info(f"Resolved author_id {material_author_id} to {get_author_by_id(material_author_id)['name'] if get_author_by_id(material_author_id) else 'Unknown'}")
        elif "data" in material_data_or_name and "author_id" in material_data_or_name["data"]:
            material_author_id = material_data_or_name["data"]["author_id"]
            import logging
            logging.info(f"Resolved author_id {material_author_id} from data to {get_author_by_id(material_author_id)['name'] if get_author_by_id(material_author_id) else 'Unknown'}")
        
        # Extract material name for frontmatter lookup
        if "name" in material_data_or_name:
            material_name = material_data_or_name["name"].strip()
        elif "material_name" in material_data_or_name:
            material_name = material_data_or_name["material_name"].strip()
    
    # If we found an author_id in the material data, use it
    if material_author_id is not None:
        author = get_author_by_id(material_author_id)
        if author:
            print(f"👤 Using author {author['name']} (ID: {material_author_id}) from material data")
            return {
                "name": author.get("name", "Unknown Author"),
                "country": author.get("country", "Unknown"),
                "bio": author.get("bio", ""),
                "expertise": author.get("expertise", "laser cleaning technology"),
                "experience": author.get("experience", ""),
                "specialization": author.get("specialization", ""),
                "id": material_author_id,
                "sex": author.get("sex", "unknown"),
                "title": author.get("title", "Expert"),
                "image": author.get("image", None)
            }

    # Try to extract from frontmatter file as a fallback
    frontmatter_author = extract_author_info_from_frontmatter_file(material_name)
    if frontmatter_author:
        print(f"👤 Using author from existing frontmatter: {frontmatter_author.get('name', 'Unknown')}")
        return {
            "name": frontmatter_author.get("name", "Unknown Author"),
            "country": frontmatter_author.get("country", "Unknown"),
            "bio": "",
            "expertise": "laser cleaning technology",
            "experience": "",
            "specialization": "",
            "id": frontmatter_author.get("id", 1),
        }

    # Final fallback to provided author_id or default
    print(f"👤 Using fallback author ID: {fallback_author_id or 'Default'}")
    return get_author_info_for_generation(fallback_author_id)
