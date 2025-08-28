#!/usr/bin/env python3
"""
Slug Utilities for Z-Beam Generator

Provides consistent slug generation across all components and generators,
ensuring clean paths without parentheses, special characters, or inconsistencies.
"""

import re
from typing import Optional


def create_material_slug(material_name: str) -> str:
    """
    Create a clean, consistent slug from a material name.
    
    Args:
        material_name: Raw material name (e.g., "Metal Matrix Composites (MMCs)")
        
    Returns:
        Clean slug (e.g., "metal-matrix-composites-mmcs")
        
    Examples:
        >>> create_material_slug("Metal Matrix Composites (MMCs)")
        'metal-matrix-composites-mmcs'
        >>> create_material_slug("Fiber-Reinforced Polyurethane (FRPU)")
        'fiber-reinforced-polyurethane-frpu'
        >>> create_material_slug("Stainless Steel")
        'stainless-steel'
    """
    if not material_name:
        return ""
    
    # Convert to lowercase
    slug = material_name.lower()
    
    # Handle parentheses - extract content and append
    # "Metal Matrix Composites (MMCs)" -> "metal matrix composites mmcs"
    slug = re.sub(r'\s*\(([^)]+)\)\s*', r' \1 ', slug)
    
    # Replace all non-alphanumeric characters with spaces
    slug = re.sub(r'[^a-z0-9]+', ' ', slug)
    
    # Remove extra spaces and replace with hyphens
    slug = re.sub(r'\s+', '-', slug.strip())
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    return slug


def create_filename_slug(material_name: str, suffix: str = "laser-cleaning") -> str:
    """
    Create a complete filename slug for material content files.
    
    Args:
        material_name: Material name to convert
        suffix: Filename suffix (default: "laser-cleaning")
        
    Returns:
        Complete filename slug (e.g., "metal-matrix-composites-mmcs-laser-cleaning")
    """
    material_slug = create_material_slug(material_name)
    if suffix:
        return f"{material_slug}-{suffix}"
    return material_slug


def extract_material_from_filename(filename: str) -> Optional[str]:
    """
    Extract material name from a filename slug.
    
    Args:
        filename: Filename like "metal-matrix-composites-mmcs-laser-cleaning.md"
        
    Returns:
        Material slug part or None if not a valid format
    """
    # Remove file extension
    basename = filename.replace('.md', '').replace('.yaml', '').replace('.json', '')
    
    # Remove common suffixes
    suffixes = ['-laser-cleaning', '-material', '-component']
    
    for suffix in suffixes:
        if basename.endswith(suffix):
            return basename[:-len(suffix)]
    
    return basename


def normalize_material_name(material_name: str) -> str:
    """
    Normalize a material name for display purposes.
    
    Args:
        material_name: Raw material name
        
    Returns:
        Normalized material name for display
        
    Examples:
        >>> normalize_material_name("Metal Matrix Composites (MMCs)")
        'Metal Matrix Composites (MMCs)'
        >>> normalize_material_name("metal-matrix-composites-mmcs")
        'Metal Matrix Composites MMCs'
    """
    if not material_name:
        return ""
    
    # If it's already a display name with parentheses, return as-is
    if '(' in material_name and ')' in material_name:
        return material_name
    
    # If it's a slug, convert back to display format
    if '-' in material_name and material_name.islower():
        # Split into words
        words = material_name.split('-')
        
        # Capitalize each word
        normalized_words = []
        for word in words:
            # Handle acronyms (all caps)
            if len(word) <= 4 and word.upper() in ['MMC', 'MMCS', 'CMC', 'CMCS', 'FRPU', 'GFRP']:
                normalized_words.append(word.upper())
            else:
                normalized_words.append(word.capitalize())
        
        return ' '.join(normalized_words)
    
    # Return as-is for other formats
    return material_name


def get_clean_material_mapping() -> dict:
    """
    Get a mapping of materials with parentheses to their clean slug versions.
    
    Returns:
        Dictionary mapping original names to clean slugs
    """
    materials_with_parentheses = [
        "Glass Fiber Reinforced Polymers (GFRP)",
        "Fiber-Reinforced Polyurethane (FRPU)", 
        "Metal Matrix Composites (MMCs)",
        "Ceramic Matrix Composites (CMCs)"
    ]
    
    mapping = {}
    for material in materials_with_parentheses:
        clean_slug = create_material_slug(material)
        mapping[material] = clean_slug
    
    return mapping


def validate_slug(slug: str) -> bool:
    """
    Validate that a slug follows the clean naming convention.
    
    Args:
        slug: Slug to validate
        
    Returns:
        True if slug is clean and valid
    """
    if not slug:
        return False
    
    # Check for invalid characters
    if re.search(r'[^a-z0-9\-]', slug):
        return False
    
    # Check for parentheses (should be removed)
    if '(' in slug or ')' in slug:
        return False
    
    # Check for double hyphens or leading/trailing hyphens
    if '--' in slug or slug.startswith('-') or slug.endswith('-'):
        return False
    
    return True


def main():
    """Test the slug utilities"""
    test_materials = [
        "Metal Matrix Composites (MMCs)",
        "Fiber-Reinforced Polyurethane (FRPU)",
        "Glass Fiber Reinforced Polymers (GFRP)",
        "Ceramic Matrix Composites (CMCs)",
        "Stainless Steel",
        "Aluminum",
        "Carbon Fiber Reinforced Polymer"
    ]
    
    print("🔧 Material Slug Generation Test")
    print("=" * 50)
    
    for material in test_materials:
        slug = create_material_slug(material)
        filename = create_filename_slug(material)
        is_valid = validate_slug(slug)
        
        print(f"Material: {material}")
        print(f"Slug:     {slug}")
        print(f"Filename: {filename}.md")
        print(f"Valid:    {'✅' if is_valid else '❌'}")
        print("-" * 30)
    
    print("\n🗂️  Clean Material Mapping")
    print("=" * 50)
    mapping = get_clean_material_mapping()
    for original, clean in mapping.items():
        print(f"{original}")
        print(f"  → {clean}")


if __name__ == "__main__":
    main()
