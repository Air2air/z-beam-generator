#!/usr/bin/env python3
"""
Metal Classification Module

Single source of truth for ferrous vs non-ferrous metal classification.
Used for contamination validation (rust only on ferrous metals, patina on copper alloys, etc.)

This centralizes logic that was duplicated in:
- ContaminationPatternSelector.FERROUS_METALS / NON_FERROUS_METALS
- MaterialImageGenerator.get_negative_prompt() corrosion_resistant_materials

Author: AI Assistant
Date: November 30, 2025
"""

from typing import Set, Optional
import logging

logger = logging.getLogger(__name__)


class MetalClassifier:
    """
    Central classification for metals based on iron content and corrosion behavior.
    
    Ferrous metals contain iron and can develop rust (iron oxide).
    Non-ferrous metals develop patina, tarnish, or other oxidation - NOT rust.
    
    Usage:
        classifier = MetalClassifier()
        
        # Check if material can rust
        if classifier.is_ferrous("Carbon Steel"):
            # Can show rust contamination
            
        if classifier.is_non_ferrous("Aluminum Bronze"):
            # Cannot show rust, may show patina
            
        # Get valid contamination types
        contams = classifier.get_valid_contamination_types("Copper")
        # Returns: ['patina', 'oxidation', 'tarnish'] but NOT ['rust']
    """
    
    # === FERROUS METALS (contain iron, can develop rust) ===
    FERROUS_METALS: Set[str] = {
        # Steel variants
        'steel', 'stainless steel', 'carbon steel', 'tool steel',
        'galvanized steel', 'weathering steel', 'alloy steel',
        'high-speed steel', 'spring steel', 'mild steel',
        # Iron variants  
        'iron', 'cast iron', 'wrought iron', 'ductile iron',
        'pig iron', 'gray iron', 'white iron',
    }
    
    # === NON-FERROUS METALS (no iron, develop patina/tarnish NOT rust) ===
    NON_FERROUS_METALS: Set[str] = {
        # Copper and copper alloys (develop green/blue patina)
        'copper', 'brass', 'bronze', 'aluminum bronze', 'phosphor bronze',
        'silicon bronze', 'naval brass', 'red brass', 'yellow brass',
        'beryllium copper', 'nickel silver', 'cupronickel',
        # Aluminum alloys (develop white oxidation)
        'aluminum', 'aluminium', 'aluminum alloy',
        '6061 aluminum', '7075 aluminum', 'anodized aluminum',
        # Other non-ferrous
        'zinc', 'titanium', 'nickel', 'lead', 'tin', 'cobalt', 
        'chromium', 'tungsten', 'magnesium', 'molybdenum',
        # Precious metals
        'gold', 'silver', 'platinum', 'palladium', 'rhodium',
    }
    
    # === CORROSION-RESISTANT METALS (should not show heavy corrosion) ===
    CORROSION_RESISTANT: Set[str] = {
        'stainless steel', 'titanium', 'aluminum', 'aluminium',
        'brass', 'bronze', 'copper', 'nickel', 'chromium',
        'gold', 'silver', 'platinum', 'zinc', 'galvanized steel',
    }
    
    # === CONTAMINATION MAPPINGS ===
    # What oxidation types are valid for each metal category
    FERROUS_OXIDATION = {'rust', 'rust-oxidation', 'iron-oxide', 'red-rust', 'orange-rust'}
    COPPER_OXIDATION = {'patina', 'copper-patina', 'verdigris', 'green-patina', 'tarnish'}
    ALUMINUM_OXIDATION = {'white-oxidation', 'aluminum-oxide', 'oxide-layer'}
    GENERIC_OXIDATION = {'oxidation', 'tarnish', 'surface-oxidation'}
    
    def __init__(self):
        """Initialize classifier with normalized lookup sets."""
        # Create lowercase lookup sets for case-insensitive matching
        self._ferrous_lower = {m.lower() for m in self.FERROUS_METALS}
        self._nonferrous_lower = {m.lower() for m in self.NON_FERROUS_METALS}
        self._corrosion_resistant_lower = {m.lower() for m in self.CORROSION_RESISTANT}
    
    def is_ferrous(self, material_name: str) -> bool:
        """
        Check if a material is a ferrous metal (contains iron, can rust).
        
        Args:
            material_name: Material name (e.g., "Carbon Steel", "Stainless Steel")
            
        Returns:
            True if ferrous (can rust), False otherwise
        """
        material_lower = material_name.lower()
        
        # Direct match
        if material_lower in self._ferrous_lower:
            return True
        
        # Keyword match for steel/iron
        if any(keyword in material_lower for keyword in ['steel', 'iron']):
            return True
        
        # Exclude if matches non-ferrous keywords
        nonferrous_keywords = [
            'bronze', 'brass', 'copper', 'aluminum', 'aluminium',
            'zinc', 'titanium', 'nickel', 'magnesium', 'gold',
            'silver', 'platinum', 'tin', 'lead', 'cobalt'
        ]
        if any(keyword in material_lower for keyword in nonferrous_keywords):
            return False
        
        return False
    
    def is_non_ferrous(self, material_name: str) -> bool:
        """
        Check if a material is a non-ferrous metal (no iron, develops patina not rust).
        
        Args:
            material_name: Material name
            
        Returns:
            True if non-ferrous, False otherwise
        """
        material_lower = material_name.lower()
        
        # Direct match
        if material_lower in self._nonferrous_lower:
            return True
        
        # Keyword match
        for metal in self.NON_FERROUS_METALS:
            if metal in material_lower or material_lower in metal:
                return True
        
        return False
    
    def is_corrosion_resistant(self, material_name: str) -> bool:
        """
        Check if material is corrosion-resistant.
        
        These materials should not show heavy rust/corrosion in images.
        
        Args:
            material_name: Material name
            
        Returns:
            True if corrosion-resistant
        """
        material_lower = material_name.lower()
        
        # Direct match
        if material_lower in self._corrosion_resistant_lower:
            return True
        
        # Keyword match
        for metal in self.CORROSION_RESISTANT:
            if metal in material_lower:
                return True
        
        return False
    
    def is_copper_alloy(self, material_name: str) -> bool:
        """
        Check if material is a copper alloy (develops green/blue patina).
        
        Args:
            material_name: Material name
            
        Returns:
            True if copper alloy
        """
        copper_keywords = ['copper', 'bronze', 'brass', 'cupronickel']
        material_lower = material_name.lower()
        return any(keyword in material_lower for keyword in copper_keywords)
    
    def get_valid_oxidation_types(self, material_name: str) -> Set[str]:
        """
        Get valid oxidation/corrosion types for a material.
        
        Args:
            material_name: Material name
            
        Returns:
            Set of valid oxidation pattern IDs
        """
        result = set(self.GENERIC_OXIDATION)
        
        if self.is_ferrous(material_name):
            result.update(self.FERROUS_OXIDATION)
        
        if self.is_copper_alloy(material_name):
            result.update(self.COPPER_OXIDATION)
        
        if 'aluminum' in material_name.lower() or 'aluminium' in material_name.lower():
            result.update(self.ALUMINUM_OXIDATION)
        
        return result
    
    def get_prohibited_contamination(self, material_name: str) -> Set[str]:
        """
        Get contamination types that should NOT appear on this material.
        
        Args:
            material_name: Material name
            
        Returns:
            Set of prohibited contamination pattern IDs
        """
        prohibited = set()
        
        # Non-ferrous metals cannot show rust
        if self.is_non_ferrous(material_name) or not self.is_ferrous(material_name):
            prohibited.update(self.FERROUS_OXIDATION)
        
        # Non-copper alloys cannot show copper patina
        if not self.is_copper_alloy(material_name):
            prohibited.update(self.COPPER_OXIDATION)
        
        return prohibited
    
    def get_metal_category(self, material_name: str) -> Optional[str]:
        """
        Get the category of a metal for image generation.
        
        Args:
            material_name: Material name
            
        Returns:
            Category string: 'ferrous', 'copper_alloy', 'aluminum', 'other_nonferrous', or None
        """
        if self.is_ferrous(material_name):
            return 'ferrous'
        if self.is_copper_alloy(material_name):
            return 'copper_alloy'
        if 'aluminum' in material_name.lower() or 'aluminium' in material_name.lower():
            return 'aluminum'
        if self.is_non_ferrous(material_name):
            return 'other_nonferrous'
        return None

    def can_rust(self, material_name: str) -> bool:
        """
        Check if a material can develop rust (iron oxide).
        
        Only ferrous metals (steel, iron) can rust.
        Non-ferrous metals develop patina or white oxidation instead.
        Non-metals cannot rust.
        
        Args:
            material_name: Material name
            
        Returns:
            True if material can rust, False otherwise
        """
        return self.is_ferrous(material_name)


# Module-level singleton for convenience
_classifier: Optional[MetalClassifier] = None


def get_classifier() -> MetalClassifier:
    """Get or create singleton metal classifier."""
    global _classifier
    if _classifier is None:
        _classifier = MetalClassifier()
    return _classifier


def is_ferrous(material_name: str) -> bool:
    """Check if material is ferrous (can rust)."""
    return get_classifier().is_ferrous(material_name)


def is_non_ferrous(material_name: str) -> bool:
    """Check if material is non-ferrous (develops patina not rust)."""
    return get_classifier().is_non_ferrous(material_name)


def is_corrosion_resistant(material_name: str) -> bool:
    """Check if material is corrosion-resistant."""
    return get_classifier().is_corrosion_resistant(material_name)


def get_prohibited_contamination(material_name: str) -> Set[str]:
    """Get prohibited contamination patterns for material."""
    return get_classifier().get_prohibited_contamination(material_name)
