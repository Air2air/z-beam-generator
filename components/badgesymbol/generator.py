#!/usr/bin/env python3
"""
Badge Symbol Generator

Generates standardized badge symbol tables by extracting data from frontmatter.
Integrated with the modular component architecture.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from generators.hybrid_generator import HybridComponentGenerator
from generators.component_generators import ComponentResult
from versioning import stamp_component_output


class BadgesymbolComponentGenerator(HybridComponentGenerator):
    """Generator for badge symbol components using frontmatter data and API when needed"""

    def __init__(self):
        super().__init__("badgesymbol")

    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> ComponentResult:
        """
        Generate badge symbol content with enhanced material data access for chemical fallbacks.
        Overrides parent to ensure material_data is available for category-specific generation.
        """
        # Store material_data for use in extraction methods
        self._material_data = material_data
        
        # Call parent generate method
        return super().generate(
            material_name=material_name,
            material_data=material_data,
            api_client=api_client,
            author_info=author_info,
            frontmatter_data=frontmatter_data,
            schema_fields=schema_fields,
        )

    def _extract_from_frontmatter(
        self, material_name: str, frontmatter_data: Dict
    ) -> str:
        """Generate badge symbol component content from frontmatter data using schema and example"""

        # Load example file to understand the expected format
        try:
            example_path = Path(__file__).parent / "example_badgesymbol.md"
            example_fields = {}
            if example_path.exists():
                with open(example_path, "r", encoding="utf-8") as f:
                    example_content = f.read()
                    example_fields = self._parse_example_frontmatter(example_content)
        except Exception:
            example_fields = {}

        # Load schema to understand expected structure
        try:
            schema_path = (
                Path(__file__).parent.parent.parent / "schemas" / "material.json"
            )
            schema_fields = {}
            if schema_path.exists():
                with open(schema_path, "r", encoding="utf-8") as f:
                    schema = json.load(f)
                    chem_props = (
                        schema.get("materialProfile", {})
                        .get("profile", {})
                        .get("chemicalProperties", {})
                        .get("materialProperties", {})
                    )
                    if chem_props:
                        schema_fields = {
                            "symbol": chem_props.get("symbol", {}),
                            "materialType": chem_props.get("materialType", {}),
                        }
        except Exception:
            schema_fields = {}

        # Extract values dynamically
        frontmatter_output = {}

        # Priority 1: Use example fields if available
        if example_fields:
            for field_name, example_value in example_fields.items():
                extracted_value = self._extract_field_value(
                    frontmatter_data, field_name, material_name
                )
                frontmatter_output[field_name] = extracted_value
        # Priority 2: Use schema fields
        elif schema_fields:
            for field_name in schema_fields.keys():
                extracted_value = self._extract_field_value(
                    frontmatter_data, field_name, material_name
                )
                frontmatter_output[field_name] = extracted_value
        # FAIL-FAST: No fallback allowed - system must have required schema or example
        else:
            raise Exception(
                f"No schema or example provided for badge symbol generation of {material_name} - fail-fast architecture requires explicit configuration"
            )

        # Build frontmatter YAML
        yaml_lines = ["---"]
        for key, value in frontmatter_output.items():
            yaml_lines.append(f'{key}: "{value}"')
        yaml_lines.append("---")

        content = "\n".join(yaml_lines)

        # Apply centralized version stamping
        return stamp_component_output("badgesymbol", content)

    def _parse_example_frontmatter(self, example_content: str) -> Dict[str, str]:
        """Parse example file to extract frontmatter fields"""
        try:
            if example_content.startswith("---"):
                parts = example_content.split("---", 2)
                if len(parts) >= 2:
                    frontmatter_yaml = parts[1].strip()
                    return yaml.safe_load(frontmatter_yaml) or {}
        except Exception:
            pass
        return {}

    def _extract_field_value(
        self, frontmatter_data: Dict, field_name: str, material_name: str
    ) -> str:
        """Extract field value using multiple potential paths with intelligent fallbacks"""

        # Define field extraction paths
        field_paths = {
            "symbol": ["chemicalProperties.symbol", "symbol", "chemicalFormula"],
            "materialType": [
                "chemicalProperties.materialType",
                "materialType",
                "category",
                "type",
            ],
        }

        paths = field_paths.get(field_name, [field_name])

        for path in paths:
            value = self._get_field(frontmatter_data, [path], None)
            if value and value != "None":
                # Apply field-specific processing
                if field_name == "symbol" and len(value) > 2:
                    # Truncate long symbols to 2 characters maximum
                    return value[:2].upper()
                elif field_name == "materialType":
                    return value.lower()
                return value

        # Intelligent fallbacks for missing data
        if field_name == "symbol":
            # Generate 2-character symbol from material name
            return self._generate_symbol_from_name(material_name)
        elif field_name == "materialType":
            # Infer material type from name or use category data
            return self._infer_material_type(material_name, frontmatter_data)

        # Last resort: use first 2 chars of material name
        return material_name[:2].upper()

    def _get_field(self, data: Dict[str, Any], paths: list, default: str) -> str:
        """Get field value from nested dict using dot notation paths"""
        for path in paths:
            value = data
            for key in path.split("."):
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    value = None
                    break
            if value is not None:
                return str(value)
        return default

    def _generate_symbol_from_name(self, material_name: str) -> str:
        """Generate a 2-character symbol from material name"""
        # Handle special cases and common materials
        name_lower = material_name.lower()
        
        # Chemical elements - use periodic table symbols
        element_symbols = {
            "aluminum": "Al", "beryllium": "Be", "brass": "Br", "bronze": "Bn",
            "cobalt": "Co", "copper": "Cu", "gallium": "Ga", "gold": "Au",
            "hafnium": "Hf", "indium": "In", "iridium": "Ir", "iron": "Fe",
            "lead": "Pb", "magnesium": "Mg", "molybdenum": "Mo", "nickel": "Ni",
            "niobium": "Nb", "palladium": "Pd", "platinum": "Pt", "rhenium": "Re",
            "rhodium": "Rh", "ruthenium": "Ru", "silver": "Ag", "tantalum": "Ta",
            "tin": "Sn", "titanium": "Ti", "tungsten": "W", "vanadium": "V",
            "zinc": "Zn", "zirconium": "Zr", "chromium": "Cr", "manganese": "Mn",
            "silicon": "Si"
        }
        
        # Check for exact matches
        if name_lower in element_symbols:
            return element_symbols[name_lower]
            
        # Material type abbreviations
        if "steel" in name_lower:
            return "St"
        elif "glass" in name_lower:
            return "Gl"
        elif "carbide" in name_lower:
            return "Cd"
        elif "oxide" in name_lower:
            return "Ox"
        elif "nitride" in name_lower:
            return "Ni"
        elif "composite" in name_lower or "fiber" in name_lower:
            return "Cf"
        elif "polymer" in name_lower or "plastic" in name_lower:
            return "Pl"
        elif "wood" in name_lower or any(wood in name_lower for wood in ["oak", "pine", "birch", "cedar", "maple", "ash", "beech", "cherry", "fir", "hickory", "mahogany", "poplar", "redwood", "rosewood", "teak", "walnut", "willow", "bamboo"]):
            return "Wd"
        elif "stone" in name_lower or "granite" in name_lower or "marble" in name_lower:
            return "St"
        elif "ceramic" in name_lower or any(cer in name_lower for cer in ["alumina", "zirconia", "porcelain"]):
            return "Ce"
            
        # Default: use first letter + first consonant or vowel
        name_clean = ''.join(c for c in material_name if c.isalpha()).upper()
        if len(name_clean) >= 2:
            return name_clean[0] + name_clean[1]
        elif len(name_clean) == 1:
            return name_clean[0] + "X"
        else:
            return "XX"

    def _infer_material_type(self, material_name: str, frontmatter_data: Dict) -> str:
        """Infer material type from name and available data"""
        name_lower = material_name.lower()
        
        # Check category from frontmatter first
        category = frontmatter_data.get("category", "").lower()
        if category:
            return category
            
        # Infer from material name
        if any(metal in name_lower for metal in ["aluminum", "steel", "iron", "copper", "brass", "bronze", "titanium", "gold", "silver", "lead", "zinc", "nickel", "cobalt", "tungsten", "chromium", "manganese", "beryllium", "magnesium", "palladium", "platinum", "gallium", "hafnium", "indium", "iridium", "molybdenum", "niobium", "rhenium", "rhodium", "ruthenium", "tantalum", "tin", "vanadium", "zirconium"]):
            return "metal"
        elif "glass" in name_lower:
            return "glass"
        elif any(ceramic in name_lower for ceramic in ["ceramic", "alumina", "zirconia", "porcelain", "stoneware"]):
            return "ceramic"
        elif any(wood in name_lower for wood in ["wood", "oak", "pine", "birch", "cedar", "maple", "ash", "beech", "cherry", "fir", "hickory", "mahogany", "poplar", "redwood", "rosewood", "teak", "walnut", "willow", "bamboo", "mdf", "plywood"]):
            return "wood"
        elif any(stone in name_lower for stone in ["stone", "granite", "marble", "limestone", "sandstone", "slate", "basalt", "quartzite", "onyx", "travertine", "alabaster", "calcite", "schist", "serpentine", "soapstone", "bluestone", "breccia", "porphyry", "shale"]):
            return "stone"
        elif "concrete" in name_lower or "cement" in name_lower or "mortar" in name_lower or "brick" in name_lower or "plaster" in name_lower or "stucco" in name_lower or "terracotta" in name_lower:
            return "construction"
        elif "polymer" in name_lower or "plastic" in name_lower or any(poly in name_lower for poly in ["polyethylene", "polypropylene", "polystyrene", "polyvinyl", "polycarbonate", "polytetrafluoroethylene"]):
            return "polymer"
        elif "composite" in name_lower or "fiber" in name_lower or "resin" in name_lower:
            return "composite"
        elif "carbide" in name_lower:
            return "carbide"
        elif "semiconductor" in name_lower or "silicon" in name_lower:
            return "semiconductor"
        elif "rubber" in name_lower or "elastomer" in name_lower:
            return "elastomer"
        else:
            return "material"


# Legacy compatibility class
class BadgeSymbolGenerator:
    """Legacy badge symbol generator for backward compatibility"""

    def __init__(self):
        self.generator = BadgesymbolComponentGenerator()
        self.component_info = {
            "name": "Badge Symbol",
            "description": "Generates standardized badge symbol tables from frontmatter data",
            "version": "2.0.0",  # Updated version
            "type": "static",
        }

    def generate_content(
        self, material_name: str, frontmatter_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Legacy generate_content method"""
        result = self.generator.generate(
            material_name, {}, frontmatter_data=frontmatter_data or {}
        )
        return result.content if hasattr(result, "content") else str(result)


# Static functions for compatibility
def create_badge_symbol_template(material_name: str) -> str:
    """Create badge symbol template for a material"""
    generator = BadgeSymbolGenerator()
    return generator.generate_content(material_name)


def generate_badge_symbol_content(
    material_name: str, frontmatter_data: Optional[Dict[str, Any]] = None
) -> str:
    """Generate badge symbol content from material name and optional frontmatter"""
    generator = BadgeSymbolGenerator()
    return generator.generate_content(material_name, frontmatter_data)
