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
                "Usage: python3 run.py --material 'Steel' --author 2",
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
