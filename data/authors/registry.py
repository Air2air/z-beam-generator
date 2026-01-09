#!/usr/bin/env python3
"""
Author Registry - Single Source of Truth

CRITICAL: This is the ONLY authoritative source for author information.
NO fallbacks, NO normalization ambiguity, NO silent failures.

All author lookups MUST use this registry. Any missing author ID is a configuration
error and should fail immediately with a clear error message.

Usage:
    from data.authors.registry import get_author, get_country_normalized
    
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
        "countryDisplay": "Taiwan",
        "title": "Ph.D.",
        "sex": "f",
        "jobTitle": "Laser Processing Engineer",
        "expertise": [
            "Laser Materials Processing"
        ],
        "affiliation": {
            "name": "National Taiwan University",
            "type": "EducationalOrganization"
        },
        "credentials": [
            "Ph.D. Materials Engineering, National Taiwan University, 2018",
            "Post-Ph.D. fellowship at TSMC's laser fab lab, 2018-2020",
            "3+ years in laser processing R&D",
            "Assisted in projects on ultrafast laser applications"
        ],
        "email": "info@z-beam.com",
        "image": "/images/author/yi-chun-lin.jpg",
        "imageAlt": "Yi-Chun Lin, Ph.D., Laser Processing Engineer at National Taiwan University, in lab setting",
        "url": "https://z-beam.com/authors/yi-chun-lin",
        "sameAs": [
            "https://scholar.google.com/citations?user=ghi789",
            "https://linkedin.com/in/yi-chun-lin-engineer",
            "https://www.researchgate.net/profile/Yi-Chun-Lin-2"
        ],
        "personaFile": "taiwan_persona.yaml",
        "formattingFile": "taiwan_formatting.yaml",
    },
    2: {
        "id": 2,
        "name": "Alessandro Moretti",
        "country": "Italy",
        "countryDisplay": "Italy",
        "title": "Ph.D.",
        "sex": "m",
        "jobTitle": "Materials Engineer",
        "expertise": [
            "Laser-Based Additive Manufacturing"
        ],
        "affiliation": {
            "name": "Politecnico di Milano's Materials Dept.",
            "type": "EducationalOrganization"
        },
        "alumniOf": {
            "name": "University of Bologna",
            "type": "EducationalOrganization"
        },
        "credentials": [
            "Ph.D. Materials Science, TU Milano, 2015",
            "5+ years industrial ceramics experience",
            "Assisted in EU Horizon 2020 laser additive projects, 2016-2019"
        ],
        "email": "info@z-beam.com",
        "image": "/images/author/alessandro-moretti.jpg",
        "imageAlt": "Alessandro Moretti, Ph.D., Materials Engineer at Politecnico di Milano's Materials Dept., in research lab",
        "url": "https://z-beam.com/authors/alessandro-moretti-phd",
        "sameAs": [
            "https://scholar.google.com/citations?user=def456",
            "https://linkedin.com/in/alessandro-moretti-engineer"
        ],
        "personaFile": "italy_persona.yaml",
        "formattingFile": "italy_formatting.yaml",
    },
    3: {
        "id": 3,
        "name": "Ikmanda Roswati",
        "country": "Indonesia",
        "countryDisplay": "Indonesia",
        "title": "Ph.D.",
        "sex": "m",
        "jobTitle": "Junior Research Scientist in Laser Physics",
        "expertise": [
            "Ultrafast Laser Physics and Material Interactions"
        ],
        "affiliation": {
            "name": "Bandung Institute of Technology",
            "type": "EducationalOrganization"
        },
        "credentials": [
            "Ph.D. Physics, ITB, 2020",
            "2+ years in ultrafast laser research including ASEAN optics workshops",
            "Assisted in international optics projects"
        ],
        "languages": [
            "English",
            "Bahasa Indonesia"
        ],
        "email": "info@z-beam.com",
        "image": "/images/author/ikmanda-roswati.jpg",
        "imageAlt": "Ikmanda Roswati, Ph.D., Junior Research Scientist in Laser Physics at Bandung Institute of Technology, fieldwork optics setup",
        "url": "https://z-beam.com/authors/ikmanda-roswati",
        "sameAs": [
            "https://linkedin.com/in/ikmanda-roswati-physicist",
            "https://www.academia.edu/profile/IkmandaRoswati"
        ],
        "personaFile": "indonesia_persona.yaml",
        "formattingFile": "indonesia_formatting.yaml",
    },
    4: {
        "id": 4,
        "name": "Todd Dunning",
        "country": "United States",
        "countryDisplay": "United States",
        "title": "MA",
        "sex": "m",
        "jobTitle": "Junior Optical Materials Specialist",
        "expertise": [
            "Optical Materials for Laser Systems"
        ],
        "affiliation": {
            "name": "Coherent Inc.",
            "type": "Organization"
        },
        "credentials": [
            "BA Physics, UC Irvine, 2017",
            "Hands-on at JPL optics internship, 2018",
            "MA Optics and Photonics, UC Irvine, 2019",
            "3+ years in laser systems development",
            "Hands-on experience with optical fabrication"
        ],
        "email": "info@z-beam.com",
        "image": "/images/author/todd-dunning.jpg",
        "imageAlt": "Todd Dunning, MA, Junior Optical Materials Specialist at Coherent Inc., with precision optics tools",
        "url": "https://z-beam.com/authors/todd-dunning",
        "sameAs": [
            "https://linkedin.com/in/todd-dunning-optics",
            "https://spie.org/profile/Todd.Dunning"
        ],
        "personaFile": "usa_persona.yaml",
        "formattingFile": "usa_formatting.yaml",
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
    return (author["personaFile"], author["formattingFile"])


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


def assign_random_author() -> Dict[str, str]:
    """
    Randomly assign an author for new materials.
    
    This is the ONLY way to assign an author to a new material.
    Ensures even distribution across all 4 authors over time.
    
    Returns:
        Complete author information dictionary (copy)
        
    Example:
        >>> from data.authors.registry import assign_random_author
        >>> new_material['author'] = assign_random_author()
    """
    import random
    author_id = random.choice(list(AUTHOR_REGISTRY.keys()))
    return AUTHOR_REGISTRY[author_id].copy()


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
    "assign_random_author",
    "resolve_author_for_generation",
]
