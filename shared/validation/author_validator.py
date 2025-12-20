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
from pathlib import Path
from typing import List, Dict, Optional
from shared.utils.yaml_utils import load_yaml

logger = logging.getLogger(__name__)


# Valid author IDs (centralized list)
VALID_AUTHORS = [
    'todd_dunning',
    'yi_chun_lin',
    'alessandro_moretti',
    'ikmanda_roswati'
]


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
    is_valid = author_id in VALID_AUTHORS
    
    if not is_valid and strict:
        raise ValueError(
            f"Invalid author_id: {author_id}. "
            f"Must be one of: {', '.join(VALID_AUTHORS)}"
        )
    
    return is_valid


def get_valid_authors() -> List[str]:
    """
    Get list of all valid author IDs.
    
    Returns:
        List of valid author ID strings
    """
    return VALID_AUTHORS.copy()


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
    
    # Path to persona files
    persona_path = Path("shared/voice/profiles") / f"{author_id}.yaml"
    
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
