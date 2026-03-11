"""
Author Validation

Consolidates author validation logic from:
- data/authors/registry.py
- generation/core/parameter_manager.py

Usage:
    from shared.validation.author_validator import validate_author_id
    
    is_valid = validate_author_id("todd_dunning")
"""

import logging
import re
from pathlib import Path
from typing import List, Dict, Optional

from shared.utils.file_ops.path_manager import PathManager
from shared.utils.yaml_utils import load_yaml

logger = logging.getLogger(__name__)


def _normalize_slug(value: str) -> str:
    """Normalize author or country names to underscore slugs."""
    return re.sub(r'[^a-z0-9]+', '_', value.strip().lower()).strip('_')


def _load_author_slug_map() -> Dict[str, str]:
    """Map author-name slugs to canonical voice profile filenames."""
    authors_data = load_yaml(PathManager.get_authors_file())
    if 'authors' not in authors_data or not isinstance(authors_data['authors'], dict):
        raise ValueError("Authors.yaml missing required 'authors' mapping")

    slug_map: Dict[str, str] = {}
    for author in authors_data['authors'].values():
        if not isinstance(author, dict):
            raise ValueError("Authors.yaml author entries must be mappings")
        if 'name' not in author or 'country' not in author:
            raise ValueError("Authors.yaml author entries must include 'name' and 'country'")

        author_slug = _normalize_slug(str(author['name']))
        country_slug = _normalize_slug(str(author['country']))
        slug_map[author_slug] = country_slug

    return slug_map


def validate_author_id(author_id: str, strict: bool = True) -> bool:
    """
    Validate author ID against registry of valid authors.
    
    Args:
        author_id: Author identifier to validate
        strict: If True, raise ValueError on invalid author (default: True)
    
    Returns:
        bool: True if valid, False otherwise
    
    Raises:
        ValueError: If author_id invalid and strict=True
    
    Example:
        >>> validate_author_id("todd_dunning")
        True
        >>> validate_author_id("invalid_author")
        ValueError: Invalid author_id: invalid_author...
    """
    valid_authors = _load_author_slug_map()
    is_valid = author_id in valid_authors
    
    if not is_valid and strict:
        raise ValueError(
            f"Invalid author_id: {author_id}. "
            f"Must be one of: {', '.join(sorted(valid_authors))}"
        )
    
    return is_valid


def get_valid_authors() -> List[str]:
    """
    Get list of all valid author IDs.
    
    Returns:
        List of valid author ID strings
    """
    return sorted(_load_author_slug_map())


def load_author_profile(author_id: str) -> Optional[Dict]:
    """
    Load author profile from persona file.
    
    Args:
        author_id: Author identifier
    
    Returns:
        Dict with author profile, or None if not found
    
    Raises:
        ValueError: If author_id is invalid
    """
    validate_author_id(author_id, strict=True)
    author_slug_map = _load_author_slug_map()
    
    # Path to persona files
    persona_path = PathManager.get_voice_profiles_dir() / f"{author_slug_map[author_id]}.yaml"
    
    if not persona_path.exists():
        logger.warning(f"Persona file not found: {persona_path}")
        return None
    
    try:
        profile = load_yaml(persona_path)
        return profile
    except Exception as e:
        logger.error(f"Error loading author profile: {e}")
        return None


def get_author_display_name(author_id: str) -> str:
    """
    Get human-readable display name for author.
    
    Args:
        author_id: Author identifier
    
    Returns:
        Display name (or author_id if not found)
    """
    profile = load_author_profile(author_id)
    
    if profile and 'name' in profile:
        return profile['name']
    
    # Fallback: Convert snake_case to Title Case
    return author_id.replace('_', ' ').title()
