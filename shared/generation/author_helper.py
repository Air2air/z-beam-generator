#!/usr/bin/env python3
"""
Reusable Author Helper

Domain-agnostic helper for getting author information for voice variation.

Usage:
    from shared.generation.author_helper import get_random_author, get_author
    
    # Get random author for voice variation
    author = get_random_author()
    print(f"Using {author['name']} from {author['country']}")
    
    # Get specific author by ID
    author = get_author(1)  # Yi-Chun Lin from Taiwan
"""

import random
from typing import Dict, Any, Tuple, List


def get_random_author() -> Dict[str, Any]:
    """
    Get a random author for voice variation.
    
    Returns:
        Complete author dictionary with all fields
    """
    from data.authors.registry import AUTHOR_REGISTRY
    
    author_id = random.choice(list(AUTHOR_REGISTRY.keys()))
    return AUTHOR_REGISTRY[author_id].copy()


def get_author(author_id: int) -> Dict[str, Any]:
    """
    Get a specific author by ID.
    
    Args:
        author_id: Integer author ID from AUTHOR_REGISTRY (1-4)
    
    Returns:
        Complete author dictionary with all fields
    
    Raises:
        KeyError: If author_id not found
    """
    from data.authors.registry import get_author as registry_get_author
    return registry_get_author(author_id)


def get_author_name_country(author_id: int) -> Tuple[str, str]:
    """
    Get author name and country as tuple (convenience function).
    
    Args:
        author_id: Integer author ID
    
    Returns:
        Tuple of (author_name, country)
    """
    author = get_author(author_id)
    return author['name'], author['country']


def list_author_ids() -> List[int]:
    """
    List all available author IDs.
    
    Returns:
        List of integer author IDs
    """
    from data.authors.registry import AUTHOR_REGISTRY
    return list(AUTHOR_REGISTRY.keys())
