#!/usr/bin/env python3
"""
Material Name Resolver for Z-Beam Generator

Provides centralized, consistent material name handling across all components.
Ensures synchronization between Materials.yaml data, component generators, 
slug utilities, and frontmatter processing.
"""

import re
import sys
import os
from typing import Dict, List, Optional, Set
from functools import lru_cache

# Add parent directory to path for imports when run directly
if __name__ == "__main__":
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from materials.data.materials import load_materials
from shared.utils.core.slug_utils import create_material_slug, normalize_material_name


class MaterialNameResolver:
    """
    Centralized service for consistent material name handling across the system.
    
    Provides canonical name lookup, slug generation, display formatting,
    and validation to ensure all components use consistent naming.
    """
    
    def __init__(self):
        self._materials_data = None
        self._material_index = None
        self._canonical_names = None
        self._name_mappings = None
        self._abbrev_mappings = None
    
    @property
    def materials_data(self) -> Dict:
        """Lazy load materials data"""
        if self._materials_data is None:
            self._materials_data = load_materials()
        return self._materials_data
    
    @property
    def material_index(self) -> Dict:
        """Get material index from materials data - use materials as authoritative source"""
        if self._material_index is None:
            # Use materials section as authoritative source, fallback to material_index
            materials = self.materials_data.get('materials', {})
            if materials:
                self._material_index = materials
            else:
                self._material_index = self.materials_data.get('material_index', {})
        return self._material_index
    
    @property
    def canonical_names(self) -> Set[str]:
        """Get set of all canonical material names from Materials.yaml"""
        if self._canonical_names is None:
            self._canonical_names = set(self.material_index.keys())
        return self._canonical_names
    
    @property
    def name_mappings(self) -> Dict[str, str]:
        """
        Create mappings from various name formats to canonical names.
        Handles case-insensitive lookup and common variations.
        """
        if self._name_mappings is None:
            mappings = {}
            for canonical_name in self.canonical_names:
                # Direct canonical name
                mappings[canonical_name] = canonical_name
                
                # Case-insensitive variations
                mappings[canonical_name.lower()] = canonical_name
                mappings[canonical_name.upper()] = canonical_name
                mappings[canonical_name.title()] = canonical_name
                
                # Slug variations
                slug = create_material_slug(canonical_name)
                mappings[slug] = canonical_name
                
                # Handle common spacing/punctuation variations
                no_spaces = canonical_name.replace(" ", "")
                mappings[no_spaces.lower()] = canonical_name
                
                # Handle parentheses removal
                no_parens = re.sub(r'\s*\([^)]*\)\s*', ' ', canonical_name).strip()
                if no_parens != canonical_name:
                    mappings[no_parens] = canonical_name
                    mappings[no_parens.lower()] = canonical_name
            
            self._name_mappings = mappings
        return self._name_mappings
    
    @property
    def abbrev_mappings(self) -> Dict[str, str]:
        """
        Create mappings from abbreviations to full canonical names.
        Handles bidirectional name resolution for materials with industry-standard abbreviations.
        
        Examples:
            "CMCs" -> "Ceramic Matrix Composites CMCs"
            "FRPU" -> "Fiber Reinforced Polyurethane FRPU"
            "PTFE" -> "Polytetrafluoroethylene"
        """
        if self._abbrev_mappings is None:
            mappings = {}
            
            # Extract from MATERIAL_ABBREVIATIONS constant
            try:
                from components.frontmatter.core.streamlined_generator import MATERIAL_ABBREVIATIONS
                
                for full_name_key, abbrev_data in MATERIAL_ABBREVIATIONS.items():
                    abbrev = abbrev_data['abbreviation']
                    
                    # Find the canonical name in Materials.yaml that matches
                    # Try exact match first
                    if full_name_key in self.canonical_names:
                        canonical = full_name_key
                    else:
                        # Try to find matching canonical name
                        canonical = None
                        full_name_normalized = full_name_key.lower().replace(' ', '').replace('-', '')
                        
                        for candidate in self.canonical_names:
                            candidate_normalized = candidate.lower().replace(' ', '').replace('-', '')
                            if full_name_normalized in candidate_normalized or candidate_normalized in full_name_normalized:
                                canonical = candidate
                                break
                    
                    if canonical:
                        # Map abbreviation to canonical name (all case variations)
                        mappings[abbrev] = canonical
                        mappings[abbrev.lower()] = canonical
                        mappings[abbrev.upper()] = canonical
                        mappings[abbrev.title()] = canonical
                        mappings[abbrev.capitalize()] = canonical
            except ImportError:
                # If import fails, fall back to parsing from canonical names
                pass
            
            # Also parse abbreviations from Materials.yaml names
            # e.g., "Ceramic Matrix Composites CMCs" -> extract "CMCs"
            for canonical_name in self.canonical_names:
                words = canonical_name.split()
                if len(words) > 1:
                    last_word = words[-1]
                    # Check if last word looks like an abbreviation (all caps, 2-5 chars)
                    if last_word.isupper() and 2 <= len(last_word) <= 5:
                        mappings[last_word] = canonical_name
                        mappings[last_word.lower()] = canonical_name
                        mappings[last_word.upper()] = canonical_name
                        mappings[last_word.title()] = canonical_name
                        mappings[last_word.capitalize()] = canonical_name
            
            self._abbrev_mappings = mappings
        return self._abbrev_mappings
    
    def resolve_canonical_name(self, input_name: str) -> Optional[str]:
        """
        Resolve any name variation to the canonical name from Materials.yaml.
        
        Args:
            input_name: Name in any format (e.g., "aluminum", "Aluminum", "aluminum-laser-cleaning")
            
        Returns:
            Canonical name from Materials.yaml or None if not found
            
        Examples:
            >>> resolver.resolve_canonical_name("aluminum")
            'Aluminum'
            >>> resolver.resolve_canonical_name("stainless-steel")
            'Stainless Steel'
            >>> resolver.resolve_canonical_name("Metal Matrix Composites (MMCs)")
            'Metal Matrix Composites (MMCs)'
        """
        if not input_name:
            return None
        
        # Clean the input - remove common suffixes
        cleaned_name = input_name
        suffixes_to_remove = ['-laser-cleaning', '-material', '-component', '.md', '.yaml', '.json']
        for suffix in suffixes_to_remove:
            if cleaned_name.endswith(suffix):
                cleaned_name = cleaned_name[:-len(suffix)]
                break
        
        # Try abbreviation mappings first (highest priority for exact matches)
        if cleaned_name in self.abbrev_mappings:
            return self.abbrev_mappings[cleaned_name]
        
        # Try direct lookup in name mappings
        if cleaned_name in self.name_mappings:
            return self.name_mappings[cleaned_name]
        
        # Try fuzzy matching for close variations
        cleaned_lower = cleaned_name.lower()
        for mapped_name, canonical in self.name_mappings.items():
            if mapped_name.lower() == cleaned_lower:
                return canonical
        
        return None
    
    def get_display_name(self, input_name: str) -> str:
        """
        Get the proper display name for a material.
        
        Args:
            input_name: Name in any format
            
        Returns:
            Canonical display name or normalized version of input
        """
        canonical = self.resolve_canonical_name(input_name)
        if canonical:
            return canonical
        
        # If not found in materials, return normalized version
        return normalize_material_name(input_name)
    
    def get_slug(self, input_name: str) -> str:
        """
        Get the URL-safe slug for a material name.
        
        Args:
            input_name: Name in any format
            
        Returns:
            URL-safe slug (lowercase, hyphenated)
        """
        canonical = self.resolve_canonical_name(input_name)
        if canonical:
            return create_material_slug(canonical)
        
        # If not found in materials, create slug from input
        return create_material_slug(input_name)
    
    def get_title_case(self, input_name: str) -> str:
        """
        Get title case version of material name.
        
        Args:
            input_name: Name in any format
            
        Returns:
            Title case name
        """
        canonical = self.resolve_canonical_name(input_name)
        if canonical:
            return canonical  # Canonical names are already in proper case
        
        return input_name.title()
    
    def get_lowercase(self, input_name: str) -> str:
        """
        Get lowercase version of material name.
        
        Args:
            input_name: Name in any format
            
        Returns:
            Lowercase name
        """
        canonical = self.resolve_canonical_name(input_name)
        if canonical:
            return canonical.lower()
        
        return input_name.lower()
    
    def validate_material_name(self, input_name: str) -> bool:
        """
        Check if a material name is valid (exists in Materials.yaml).
        
        Args:
            input_name: Name to validate
            
        Returns:
            True if material exists in Materials.yaml
        """
        return self.resolve_canonical_name(input_name) is not None
    
    def get_material_data(self, input_name: str) -> Optional[Dict]:
        """
        Get material data from Materials.yaml using any name format.
        
        Args:
            input_name: Name in any format
            
        Returns:
            Material data dictionary or None if not found
        """
        canonical = self.resolve_canonical_name(input_name)
        if not canonical:
            return None
            
        # material_index can be either a dict of material data or a string category
        # Need to check the materials dict directly
        materials = self.materials_data.get('materials', {})
        if canonical in materials:
            return materials[canonical]
        
        return None
    
    def list_all_materials(self) -> List[str]:
        """
        Get list of all canonical material names.
        
        Returns:
            Sorted list of all material names from Materials.yaml
        """
        return sorted(list(self.canonical_names))
    
    def find_materials_by_category(self, category: str) -> List[str]:
        """
        Find all materials in a specific category.
        
        Args:
            category: Category name (e.g., 'metal', 'ceramic')
            
        Returns:
            List of material names in the category
        """
        materials_in_category = []
        for name, data in self.material_index.items():
            if data.get('category', '').lower() == category.lower():
                materials_in_category.append(name)
        
        return sorted(materials_in_category)
    
    def get_canonical_url(self, input_name: str) -> str:
        """
        Get canonical URL path for a material.
        
        Args:
            input_name: Name in any format
            
        Returns:
            URL path like "aluminum-laser-cleaning"
        """
        slug = self.get_slug(input_name)
        return f"{slug}-laser-cleaning"
    
    @lru_cache(maxsize=128)
    def get_material_filename(self, input_name: str, extension: str = "md") -> str:
        """
        Get standardized filename for a material.
        
        Args:
            input_name: Name in any format
            extension: File extension (default: "md")
            
        Returns:
            Standardized filename
        """
        slug = self.get_slug(input_name)
        return f"{slug}-laser-cleaning.{extension}"


# Global singleton instance
_resolver_instance = None

def get_material_name_resolver() -> MaterialNameResolver:
    """
    Get global MaterialNameResolver instance.
    
    Returns:
        Singleton MaterialNameResolver instance
    """
    global _resolver_instance
    if _resolver_instance is None:
        _resolver_instance = MaterialNameResolver()
    return _resolver_instance


# Convenience functions for common operations
def resolve_material_name(input_name: str) -> Optional[str]:
    """Resolve any name variation to canonical name"""
    return get_material_name_resolver().resolve_canonical_name(input_name)

def get_material_slug(input_name: str) -> str:
    """Get URL-safe slug for material name"""
    return get_material_name_resolver().get_slug(input_name)

def get_material_display_name(input_name: str) -> str:
    """Get proper display name for material"""
    return get_material_name_resolver().get_display_name(input_name)

def validate_material(input_name: str) -> bool:
    """Check if material exists in Materials.yaml"""
    return get_material_name_resolver().validate_material_name(input_name)


def main():
    """Test the material name resolver"""
    resolver = get_material_name_resolver()
    
    print("🔍 Material Name Resolution Test")
    print("=" * 50)
    
    test_names = [
        "Aluminum",
        "aluminum", 
        "aluminum-laser-cleaning",
        "ALUMINUM",
        "Stainless Steel",
        "stainless-steel",
        "Metal Matrix Composites (MMCs)",
        "metal-matrix-composites-mmcs",
        "NonExistentMaterial"
    ]
    
    for name in test_names:
        canonical = resolver.resolve_canonical_name(name)
        slug = resolver.get_slug(name)
        display = resolver.get_display_name(name)
        valid = resolver.validate_material_name(name)
        
        print(f"Input:     '{name}'")
        print(f"Canonical: {canonical}")
        print(f"Slug:      {slug}")
        print(f"Display:   {display}")
        print(f"Valid:     {'✅' if valid else '❌'}")
        print("-" * 30)
    
    print(f"\nTotal materials: {len(resolver.list_all_materials())}")
    print(f"Metal materials: {len(resolver.find_materials_by_category('metal'))}")


if __name__ == "__main__":
    main()