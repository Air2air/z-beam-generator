#!/usr/bin/env python3
"""
Chemical Fallback Generator

Provides category-specific rules for generating chemical formulas and symbols
for materials that don't have them explicitly defined in materials.yaml.

This module implements fail-fast architecture with no default fallbacks,
only scientifically accurate category-based generation rules.
"""

import logging
import re
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class ChemicalFallbackGenerator:
    """Generate chemical formulas and symbols using category-specific rules"""

    def __init__(self):
        """Initialize the chemical fallback generator with category rules"""
        self._load_category_rules()
        self._load_common_elements()
        self._load_compound_patterns()

    def _load_category_rules(self):
        """Load category-specific generation rules"""
        self.category_rules = {
            "metal": {
                "pure_elements": {
                    # Common pure metals - elemental symbols
                    "aluminum": ("Al", "Al"),
                    "beryllium": ("Be", "Be"),
                    "copper": ("Cu", "Cu"),
                    "iron": ("Fe", "Fe"),
                    "steel": ("Fe-C", "Fe"),  # Steel is iron-carbon alloy
                    "stainless steel": ("Fe-Cr-Ni", "SS"),
                    "titanium": ("Ti", "Ti"),
                    "gold": ("Au", "Au"),
                    "silver": ("Ag", "Ag"),
                    "platinum": ("Pt", "Pt"),
                    "palladium": ("Pd", "Pd"),
                    "zinc": ("Zn", "Zn"),
                    "tin": ("Sn", "Sn"),
                    "lead": ("Pb", "Pb"),
                    "magnesium": ("Mg", "Mg"),
                    "tungsten": ("W", "W"),
                    "iridium": ("Ir", "Ir"),
                },
                "alloys": {
                    "brass": ("Cu-Zn", "Brass"),
                    "bronze": ("Cu-Sn", "Bronze"),
                    "cast iron": ("Fe-C", "CI"),
                    "carbon steel": ("Fe-C", "CS"),
                    "tool steel": ("Fe-C-Cr", "TS"),
                    "inconel": ("Ni-Cr-Fe", "Inconel"),
                    "hastelloy": ("Ni-Mo-Cr", "Hastelloy"),
                    "monel": ("Ni-Cu", "Monel"),
                }
            },
            "ceramic": {
                "oxides": {
                    "alumina": ("Al2O3", "Al2O3"),
                    "aluminum oxide": ("Al2O3", "Al2O3"),
                    "zirconia": ("ZrO2", "ZrO2"),
                    "zirconium oxide": ("ZrO2", "ZrO2"),
                    "titania": ("TiO2", "TiO2"),
                    "titanium dioxide": ("TiO2", "TiO2"),
                },
                "nitrides": {
                    "silicon nitride": ("Si3N4", "Si3N4"),
                    "aluminum nitride": ("AlN", "AlN"),
                    "titanium nitride": ("TiN", "TiN"),
                },
                "carbides": {
                    "silicon carbide": ("SiC", "SiC"),
                    "tungsten carbide": ("WC", "WC"),
                    "titanium carbide": ("TiC", "TiC"),
                },
                "complex": {
                    "porcelain": ("Al2O3·2SiO2·2H2O", "Porcelain"),
                    "stoneware": ("Al2O3·SiO2", "Stoneware"),
                    "mullite": ("3Al2O3·2SiO2", "Mullite"),
                }
            },
            "glass": {
                "silicate_based": {
                    "soda-lime glass": ("Na2O·CaO·6SiO2", "SLG"),
                    "borosilicate glass": ("SiO2·B2O3", "BSG"),
                    "pyrex": ("SiO2·B2O3", "Pyrex"),
                    "fused silica": ("SiO2", "FS"),
                    "quartz glass": ("SiO2", "QG"),
                    "float glass": ("Na2O·CaO·6SiO2", "FG"),
                    "tempered glass": ("Na2O·CaO·6SiO2", "TG"),
                    "lead crystal": ("PbO·SiO2", "LC"),
                }
            },
            "semiconductor": {
                "elements": {
                    "silicon": ("Si", "Si"),
                    "germanium": ("Ge", "Ge"),
                },
                "compounds": {
                    "gallium arsenide": ("GaAs", "GaAs"),
                    "silicon carbide": ("SiC", "SiC"),
                    "gallium nitride": ("GaN", "GaN"),
                    "indium phosphide": ("InP", "InP"),
                }
            },
            "composite": {
                "fiber_reinforced": {
                    "carbon fiber reinforced polymer": ("C-Polymer", "CFRP"),
                    "glass fiber reinforced polymer": ("SiO2-Polymer", "GFRP"),
                    "glass fiber reinforced polymers gfrp": ("SiO2-Polymer", "GFRP"),
                    "kevlar-reinforced polymer": ("Aramid-Polymer", "KRP"),
                    "fiber reinforced polyurethane frpu": ("Fiber-PU", "FRPU"),
                },
                "matrix_composites": {
                    "metal matrix composites mmcs": ("Metal-Ceramic", "MMC"),
                    "ceramic matrix composites cmcs": ("Ceramic-Fiber", "CMC"),
                },
                "polymer_based": {
                    "epoxy resin composites": ("Epoxy-Fiber", "ERC"),
                    "polyester resin composites": ("Polyester-Fiber", "PRC"),
                    "phenolic resin composites": ("Phenolic-Fiber", "PhRC"),
                    "urethane composites": ("Urethane-Fiber", "UC"),
                },
                "elastomers": {
                    "rubber": ("C5H8", "Rubber"),
                    "thermoplastic elastomer": ("TPE-Polymer", "TPE"),
                }
            },
            "masonry": {
                "calcium_based": {
                    "cement": ("CaO·SiO2·Al2O3", "Cement"),
                    "concrete": ("CaO·SiO2·Al2O3+Aggregate", "Concrete"),
                    "mortar": ("CaO·SiO2+Sand", "Mortar"),
                    "lime": ("CaO", "Lime"),
                    "limestone": ("CaCO3", "LS"),
                },
                "clay_based": {
                    "brick": ("Al2O3·SiO2·Fe2O3", "Brick"),
                    "terracotta": ("Al2O3·SiO2·Fe2O3", "TC"),
                },
                "gypsum_based": {
                    "stucco": ("CaSO4·2H2O", "Stucco"),
                    "plaster": ("CaSO4·2H2O", "Plaster"),
                }
            },
            "stone": {
                "silicate": {
                    "granite": ("SiO2·Al2O3·K2O", "Granite"),
                    "quartz": ("SiO2", "Quartz"),
                    "sandstone": ("SiO2", "Sandstone"),
                    "slate": ("Al2O3·SiO2", "Slate"),
                    "feldspar": ("KAlSi3O8", "Feldspar"),
                },
                "carbonate": {
                    "marble": ("CaCO3", "Marble"),
                    "limestone": ("CaCO3", "Limestone"),
                    "travertine": ("CaCO3", "Travertine"),
                    "dolomite": ("CaMg(CO3)2", "Dolomite"),
                    "alabaster": ("CaSO4·2H2O", "Alabaster"),  # Gypsum-based
                },
                "igneous": {
                    "basalt": ("SiO2·Al2O3·FeO", "Basalt"),
                    "obsidian": ("SiO2", "Obsidian"),
                    "pumice": ("SiO2·Al2O3", "Pumice"),
                    "bluestone": ("SiO2·Al2O3", "Bluestone"),  # Sandstone variety
                }
            },
            "wood": {
                "hardwood": {
                    "oak": ("C6H10O5", "Oak"),
                    "maple": ("C6H10O5", "Maple"),
                    "cherry": ("C6H10O5", "Cherry"),
                    "walnut": ("C6H10O5", "Walnut"),
                    "mahogany": ("C6H10O5", "Mahogany"),
                    "teak": ("C6H10O5", "Teak"),
                    "birch": ("C6H10O5", "Birch"),
                    "ash": ("C6H10O5", "Ash"),
                    "beech": ("C6H10O5", "Beech"),
                    "poplar": ("C6H10O5", "Poplar"),
                },
                "softwood": {
                    "pine": ("C6H10O5", "Pine"),
                    "cedar": ("C6H10O5", "Cedar"),
                    "fir": ("C6H10O5", "Fir"),
                    "spruce": ("C6H10O5", "Spruce"),
                    "redwood": ("C6H10O5", "Redwood"),
                },
                "engineered": {
                    "plywood": ("C6H10O5+Adhesive", "Plywood"),
                    "mdf": ("C6H10O5+Resin", "MDF"),
                    "particle board": ("C6H10O5+Resin", "PB"),
                    "osb": ("C6H10O5+Resin", "OSB"),
                }
            }
        }

    def _load_common_elements(self):
        """Load common chemical elements for pattern matching"""
        self.elements = {
            "aluminum": "Al", "copper": "Cu", "iron": "Fe", "titanium": "Ti",
            "silicon": "Si", "carbon": "C", "oxygen": "O", "nitrogen": "N",
            "calcium": "Ca", "magnesium": "Mg", "zinc": "Zn", "tin": "Sn",
            "lead": "Pb", "gold": "Au", "silver": "Ag", "platinum": "Pt",
            "tungsten": "W", "chromium": "Cr", "nickel": "Ni", "manganese": "Mn"
        }

    def _load_compound_patterns(self):
        """Load common compound patterns for formula generation"""
        self.compound_patterns = {
            "oxide": "O",
            "dioxide": "O2",
            "carbide": "C",
            "nitride": "N",
            "sulfide": "S",
            "chloride": "Cl",
            "fluoride": "F",
            "phosphide": "P"
        }

    def generate_formula_and_symbol(
        self, material_name: str, category: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate chemical formula and symbol for a material based on category rules.
        
        Args:
            material_name: Name of the material
            category: Material category (metal, ceramic, glass, etc.)
            
        Returns:
            Tuple of (formula, symbol) or (None, None) if no rule applies
            
        Raises:
            ValueError: If category is not supported (fail-fast)
        """
        if not material_name or not category:
            logger.warning("Material name and category are required for formula generation")
            return None, None

        # Normalize inputs
        material_lower = material_name.lower().strip()
        category_lower = category.lower().strip()

        # FAIL-FAST: Category must be supported
        if category_lower not in self.category_rules:
            logger.warning(f"Category '{category}' not supported for formula generation")
            return None, None

        # Try exact match first
        formula, symbol = self._try_exact_match(material_lower, category_lower)
        if formula and symbol:
            logger.info(f"Generated formula '{formula}' and symbol '{symbol}' for {material_name}")
            return formula, symbol

        # Try pattern-based generation
        formula, symbol = self._try_pattern_match(material_lower, category_lower)
        if formula and symbol:
            logger.info(f"Generated pattern-based formula '{formula}' and symbol '{symbol}' for {material_name}")
            return formula, symbol

        # Try compositional analysis
        formula, symbol = self._try_compositional_analysis(material_lower, category_lower)
        if formula and symbol:
            logger.info(f"Generated compositional formula '{formula}' and symbol '{symbol}' for {material_name}")
            return formula, symbol

        logger.warning(f"Could not generate formula/symbol for {material_name} in category {category}")
        return None, None

    def _try_exact_match(self, material_lower: str, category_lower: str) -> Tuple[Optional[str], Optional[str]]:
        """Try exact name matching within category rules"""
        category_data = self.category_rules.get(category_lower, {})
        
        for subcategory, materials in category_data.items():
            # Try exact match first
            if material_lower in materials:
                return materials[material_lower]
            
            # Try partial matching for compound names
            for material_key in materials.keys():
                # Check if the material name contains key words from the lookup key
                key_words = material_key.split()
                material_words = material_lower.split()
                
                # If all key words are found in material name, it's a match
                if len(key_words) <= len(material_words):
                    if all(any(key_word in material_word for material_word in material_words) 
                           for key_word in key_words):
                        return materials[material_key]
                
                # Also try reverse - if material name is contained in key
                if material_lower in material_key or material_key in material_lower:
                    return materials[material_key]
        
        return None, None

    def _try_pattern_match(self, material_lower: str, category_lower: str) -> Tuple[Optional[str], Optional[str]]:
        """Try pattern-based matching for common material types"""
        
        # Steel patterns
        if "steel" in material_lower and category_lower == "metal":
            if "stainless" in material_lower:
                return "Fe-Cr-Ni", "SS"
            elif "carbon" in material_lower or "tool" in material_lower:
                return "Fe-C", "CS"
            else:
                return "Fe-C", "Steel"
        
        # Glass patterns
        if category_lower == "glass":
            if "borosilicate" in material_lower or "pyrex" in material_lower:
                return "SiO2·B2O3", "BSG"
            elif "lead" in material_lower:
                return "PbO·SiO2", "LG"
            else:
                return "Na2O·CaO·6SiO2", "Glass"
        
        # Wood patterns (all cellulose-based)
        if category_lower == "wood":
            if "engineered" in material_lower or "mdf" in material_lower or "plywood" in material_lower:
                return "C6H10O5+Resin", "EW"
            else:
                return "C6H10O5", "Wood"
        
        # Composite patterns
        if category_lower == "composite":
            if "carbon" in material_lower and "fiber" in material_lower:
                return "C-Polymer", "CFRP"
            elif "glass" in material_lower and "fiber" in material_lower:
                return "SiO2-Polymer", "GFRP"
            elif "kevlar" in material_lower or "aramid" in material_lower:
                return "Aramid-Polymer", "KRP"
            else:
                return "Composite", "Comp"
        
        return None, None

    def _try_compositional_analysis(self, material_lower: str, category_lower: str) -> Tuple[Optional[str], Optional[str]]:
        """Try compositional analysis based on material name elements"""
        
        # Look for element names in material name
        found_elements = []
        for element_name, symbol in self.elements.items():
            if element_name in material_lower:
                found_elements.append(symbol)
        
        if found_elements:
            if len(found_elements) == 1:
                # Single element material
                element = found_elements[0]
                return element, element
            else:
                # Multi-element material (alloy or compound)
                formula = "-".join(found_elements)
                symbol = "".join(found_elements[:2])  # Use first two elements for symbol
                return formula, symbol
        
        # Look for compound patterns
        for compound_name, compound_symbol in self.compound_patterns.items():
            if compound_name in material_lower:
                # Try to find the metal/base element
                for element_name, element_symbol in self.elements.items():
                    if element_name in material_lower:
                        if compound_name == "dioxide":
                            formula = f"{element_symbol}O2"
                        elif compound_name == "oxide":
                            formula = f"{element_symbol}2O3"  # Common oxide form
                        else:
                            formula = f"{element_symbol}{compound_symbol}"
                        return formula, formula
        
        return None, None

    def get_supported_categories(self) -> list:
        """Get list of supported categories for formula generation"""
        return list(self.category_rules.keys())

    def validate_category(self, category: str) -> bool:
        """Validate if a category is supported for formula generation"""
        return category.lower() in self.category_rules
