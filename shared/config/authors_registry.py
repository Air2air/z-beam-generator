#!/usr/bin/env python3
"""
Author Registry - Single Source of Truth

CRITICAL: This is the ONLY authoritative source for author information.
NO fallbacks, NO normalization ambiguity, NO silent failures.

All author lookups MUST use this registry. Any missing author ID is a configuration
error and should fail immediately with a clear error message.

Usage:
    from shared.config.authors_registry import get_author, get_country_normalized
    
    author = get_author(author_id)  # Raises KeyError if invalid
    country = get_country_normalized(author_id)  # Returns normalized key
"""

from typing import Dict, Literal, Tuple

# Type-safe country identifiers - ONLY these 4 values allowed
AuthorCountry = Literal["taiwan", "italy", "indonesia", "usa"]

# Strict author registry - NO variations, NO fallbacks
# This maps author.id (from Materials.yaml) to complete author information
AUTHOR_REGISTRY: Dict[int, Dict[str, str]] = {
    1: {
        "id": 1,
        "name": "Yi-Chun Lin",
        "country": "Taiwan",  # Title case for voice profile lookup and display
        "title": "Ph.D.",
        "sex": "f",
        "expertise": "Laser Materials Processing",
        "image": "/images/author/yi-chun-lin.jpg",
        "persona_file": "taiwan_persona.yaml",
        "formatting_file": "taiwan_formatting.yaml",
    },
    2: {
        "id": 2,
        "name": "Alessandro Moretti",
        "country": "Italy",
        "title": "Ph.D.",
        "sex": "m",
        "expertise": "Laser-Based Additive Manufacturing",
        "image": "/images/author/alessandro-moretti.jpg",
        "persona_file": "italy_persona.yaml",
        "formatting_file": "italy_formatting.yaml",
    },
    3: {
        "id": 3,
        "name": "Ikmanda Roswati",
        "country": "Indonesia",
        "title": "Ph.D.",
        "sex": "m",
        "expertise": "Ultrafast Laser Physics and Material Interactions",
        "image": "/images/author/ikmanda-roswati.jpg",
        "persona_file": "indonesia_persona.yaml",
        "formatting_file": "indonesia_formatting.yaml",
    },
    4: {
        "id": 4,
        "name": "Todd Dunning",
        "country": "United States",
        "title": "MA",
        "sex": "m",
        "expertise": "Optical Materials for Laser Systems",
        "image": "/images/author/todd-dunning.jpg",
        "persona_file": "usa_persona.yaml",
        "formatting_file": "usa_formatting.yaml",
    },
}


def get_author(author_id: int) -> Dict[str, str]:
    """
    Get author by ID - FAIL-FAST if not found.
    
    Args:
        author_id: Author ID from Materials.yaml author.id field
        
    Returns:
        Complete author information dictionary
        
    Raises:
        KeyError: If author_id not in registry (configuration error)
    """
    if author_id not in AUTHOR_REGISTRY:
        valid_ids = sorted(AUTHOR_REGISTRY.keys())
        raise KeyError(
            f"Author ID {author_id} not in registry. "
            f"Valid IDs: {valid_ids}. "
            f"Check Materials.yaml author.id field."
        )
    return AUTHOR_REGISTRY[author_id].copy()  # Return copy to prevent mutation


def get_country_normalized(author_id: int) -> AuthorCountry:
    """
    Get normalized country code - always lowercase, no variations.
    
    Args:
        author_id: Author ID from Materials.yaml
        
    Returns:
        Normalized country code: "taiwan", "italy", "indonesia", or "usa"
        
    Raises:
        KeyError: If author_id not in registry
    """
    return get_author(author_id)["country"]


def get_persona_files(author_id: int) -> Tuple[str, str]:
    """
    Get persona and formatting files for author.
    
    Args:
        author_id: Author ID from Materials.yaml
        
    Returns:
        Tuple of (persona_file, formatting_file) for prompt construction
        
    Raises:
        KeyError: If author_id not in registry
    """
    author = get_author(author_id)
    return (author["persona_file"], author["formatting_file"])


def validate_author_id(author_id: int) -> bool:
    """
    Check if author ID exists in registry.
    
    Args:
        author_id: Author ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    return author_id in AUTHOR_REGISTRY


def list_valid_author_ids() -> list[int]:
    """
    Get list of all valid author IDs.
    
    Returns:
        Sorted list of valid author IDs
    """
    return sorted(AUTHOR_REGISTRY.keys())


def get_all_authors() -> list[Dict[str, str]]:
    """
    Get all authors in registry.
    
    Returns:
        List of all author dictionaries (copies)
    """
    return [author.copy() for author in AUTHOR_REGISTRY.values()]


def resolve_author_for_generation(material_data: Dict) -> Dict[str, str]:
    """
    Single author resolution path for content generation - NO fallbacks.
    
    This is the ONLY way to get author info for generation.
    Extracts author.id from Materials.yaml and looks up in registry.
    
    Args:
        material_data: Material dictionary from Materials.yaml
        
    Returns:
        Complete author information dictionary
        
    Raises:
        ValueError: If material_data malformed or missing author field
        KeyError: If author.id not in registry
    """
    if not isinstance(material_data, dict):
        raise ValueError(
            f"material_data must be dictionary, got {type(material_data).__name__}"
        )
    
    if "author" not in material_data:
        raise ValueError(
            f"Material missing 'author' field. "
            f"Add author.id to Materials.yaml for this material."
        )
    
    author_field = material_data["author"]
    if not isinstance(author_field, dict):
        raise ValueError(
            f"Material 'author' must be dictionary with 'id' field, "
            f"got {type(author_field).__name__}"
        )
    
    author_id = author_field.get("id")
    if author_id is None:
        raise ValueError(
            f"Material author missing 'id' field. "
            f"Add author.id to Materials.yaml for this material."
        )
    
    if not isinstance(author_id, int):
        raise ValueError(
            f"Material author.id must be integer, got {type(author_id).__name__}"
        )
    
    return get_author(author_id)  # Raises KeyError if invalid


# Export all public functions
__all__ = [
    "AuthorCountry",
    "AUTHOR_REGISTRY",
    "get_author",
    "get_country_normalized",
    "get_persona_files",
    "validate_author_id",
    "list_valid_author_ids",
    "get_all_authors",
    "resolve_author_for_generation",
]
