"""
Centralized URL formatting for Z-Beam frontmatter generation.

Ensures consistent URL/filename generation across all domains.
"""

import re
from typing import Optional


def slugify(text: str) -> str:
    """
    Convert text to URL-safe slug format.
    
    Examples:
        "Aluminum" -> "aluminum"
        "Stainless Steel 316" -> "stainless-steel-316"
        "Acrylic (PMMA)" -> "acrylic-pmma"
        "Carbon Fiber Reinforced Polymer" -> "carbon-fiber-reinforced-polymer"
    
    Args:
        text: Input text to slugify
        
    Returns:
        URL-safe slug (lowercase, hyphens, no special chars)
    """
    if not text:
        return ""
    
    # Convert to lowercase
    slug = text.lower()
    
    # Remove content in parentheses but keep the text inside
    # "Acrylic (PMMA)" -> "acrylic pmma"
    slug = re.sub(r'\(([^)]+)\)', r' \1', slug)
    
    # Replace non-alphanumeric characters (except hyphens) with spaces
    slug = re.sub(r'[^a-z0-9\s-]', ' ', slug)
    
    # Replace multiple spaces/hyphens with single hyphen
    slug = re.sub(r'[\s-]+', '-', slug)
    
    # Strip leading/trailing hyphens
    slug = slug.strip('-')
    
    return slug


def format_domain_url(
    domain: str,
    item_id: str,
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    slugify_item_id: bool = False
) -> str:
    """
    Generate consistent domain URL.
    
    Examples:
        format_domain_url("materials", "aluminum-laser-cleaning")
        -> "/materials/aluminum-laser-cleaning"
        
        format_domain_url("materials", "aluminum-laser-cleaning", "metal")
        -> "/materials/metal/aluminum-laser-cleaning"
        
        format_domain_url("materials", "aluminum-laser-cleaning", "metal", "non-ferrous")
        -> "/materials/metal/non-ferrous/aluminum-laser-cleaning"
        
        format_domain_url("settings", "Aluminum", slugify_item_id=True)
        -> "/settings/aluminum"
    
    Args:
        domain: Domain name (materials, contaminants, compounds, settings)
        item_id: Item identifier (may need slugification)
        category: Optional category (will be lowercased)
        subcategory: Optional subcategory (will be lowercased)
        slugify_item_id: If True, slugify the item_id
        
    Returns:
        Formatted URL path
    """
    # Slugify item_id if requested
    if slugify_item_id:
        item_id = slugify(item_id)
    
    # Build URL parts
    parts = [domain]
    
    if category:
        # Slugify category for URL-safe path (converts underscores to hyphens)
        parts.append(slugify(category))
    
    if subcategory:
        # Slugify subcategory for URL-safe path (converts underscores to hyphens)
        parts.append(slugify(subcategory))
    
    parts.append(item_id)
    
    return '/' + '/'.join(parts)


def format_filename(
    item_id: str,
    suffix: str = "",
    slugify_id: bool = False
) -> str:
    """
    Generate consistent filename.
    
    Examples:
        format_filename("aluminum-laser-cleaning")
        -> "aluminum-laser-cleaning.yaml"
        
        format_filename("Aluminum", "-settings", slugify_id=True)
        -> "aluminum-settings.yaml"
        
        format_filename("Acrylic (PMMA)", "-settings", slugify_id=True)
        -> "acrylic-pmma-settings.yaml"
    
    Args:
        item_id: Item identifier
        suffix: Optional suffix (e.g., "-settings", "-compound")
        slugify_id: If True, slugify the item_id
        
    Returns:
        Formatted filename with .yaml extension
    """
    if slugify_id:
        item_id = slugify(item_id)
    
    return f"{item_id}{suffix}.yaml"
