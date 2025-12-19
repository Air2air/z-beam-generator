"""
Formatting Utilities
====================

Centralized formatting utilities for consistent data transformation across the system.

Created: December 19, 2025
Purpose: Consolidate repeated formatting patterns (category normalization, slug extraction, etc.)
"""

from typing import Optional, Tuple


def normalize_category(category: Optional[str], default: str = 'general') -> str:
    """
    Normalize category from underscore to dash format.
    
    Args:
        category: Category string (may contain underscores)
        default: Default value if category is None or empty
    
    Returns:
        Normalized category with dashes instead of underscores
    
    Example:
        >>> normalize_category('organic_residue')
        'organic-residue'
        >>> normalize_category(None)
        'general'
    """
    return (category or default).replace('_', '-')


def normalize_taxonomy(data: dict) -> Tuple[str, str]:
    """
    Extract and normalize category/subcategory from data dictionary.
    
    Args:
        data: Dictionary containing 'category' and 'subcategory' keys
    
    Returns:
        Tuple of (normalized_category, normalized_subcategory)
    
    Example:
        >>> normalize_taxonomy({'category': 'organic_residue', 'subcategory': 'adhesive'})
        ('organic-residue', 'adhesive')
    """
    category = normalize_category(data.get('category', 'general'))
    subcategory = normalize_category(data.get('subcategory', 'misc'), default='misc')
    return category, subcategory


def extract_slug(item_id: str, suffix: Optional[str] = None) -> str:
    """
    Extract slug by removing domain suffix.
    
    Args:
        item_id: Full item ID with suffix (e.g., 'steel-laser-cleaning')
        suffix: Optional specific suffix to remove (e.g., 'laser-cleaning')
    
    Returns:
        Slug without suffix (e.g., 'steel')
    
    Example:
        >>> extract_slug('steel-laser-cleaning', 'laser-cleaning')
        'steel'
        >>> extract_slug('rust-oxidation-contamination')  # auto-detects suffix
        'rust-oxidation'
    """
    if suffix:
        return item_id.replace(f'-{suffix}', '')
    
    # Auto-detect common suffixes
    common_suffixes = ['laser-cleaning', 'contamination', 'compound', 'setting']
    for s in common_suffixes:
        if item_id.endswith(f'-{s}'):
            return item_id.replace(f'-{s}', '')
    
    return item_id


def format_image_url(domain: str, item_id: str) -> str:
    """
    Generate image URL based on domain conventions.
    
    Each domain has different image path conventions:
    - materials: /images/material/{id}-hero.jpg
    - contaminants: /images/contaminants/{slug}.jpg  
    - compounds: /images/compounds/{slug}.jpg
    - settings: /images/settings/{id}.jpg
    
    Args:
        domain: Domain name (materials, contaminants, compounds, settings)
        item_id: Full item ID with suffix
    
    Returns:
        Image URL following domain conventions
    
    Example:
        >>> format_image_url('materials', 'steel-laser-cleaning')
        '/images/material/steel-laser-cleaning-hero.jpg'
        >>> format_image_url('contaminants', 'rust-oxidation-contamination')
        '/images/contaminants/rust-oxidation.jpg'
    """
    if domain == 'materials':
        return f"/images/material/{item_id}-hero.jpg"
    elif domain == 'contaminants':
        slug = extract_slug(item_id, 'contamination')
        return f"/images/contaminants/{slug}.jpg"
    elif domain == 'compounds':
        slug = extract_slug(item_id, 'compound')
        return f"/images/compounds/{slug}.jpg"
    elif domain == 'settings':
        return f"/images/settings/{item_id}.jpg"
    
    # Fallback for unknown domains
    return f"/images/{domain}/{item_id}.jpg"


def format_display_name(item_id: str, suffix: Optional[str] = None) -> str:
    """
    Generate human-readable display name from item ID.
    
    Args:
        item_id: Item ID with dashes and optional suffix
        suffix: Optional suffix to remove before formatting
    
    Returns:
        Title-cased display name
    
    Example:
        >>> format_display_name('steel-laser-cleaning', 'laser-cleaning')
        'Steel'
        >>> format_display_name('rust-oxidation-contamination')
        'Rust Oxidation'
    """
    slug = extract_slug(item_id, suffix) if suffix else extract_slug(item_id)
    return slug.replace('-', ' ').title()
