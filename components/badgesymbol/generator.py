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
                        .get("properties", {})
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
        """Extract field value using multiple potential paths with intelligent chemical fallbacks"""

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
                if field_name == "symbol" and len(value) > 4:
                    # Truncate long symbols
                    return value[:4].upper()
                elif field_name == "materialType":
                    return value.lower()
                return value

        # Generate intelligent category-specific fallback values
        if field_name == "symbol":
            return self._generate_symbol_fallback(frontmatter_data, material_name)
        elif field_name == "materialType":
            return self._generate_material_type_fallback(frontmatter_data)

        return field_name

    def _generate_symbol_fallback(self, frontmatter_data: Dict, material_name: str) -> str:
        """Generate intelligent symbol fallback using category-specific rules"""
        try:
            from utils.core.chemical_fallback_generator import ChemicalFallbackGenerator
            
            # Try to extract category from frontmatter first
            category = self._get_field(frontmatter_data, ["category"], None)
            
            # If not in frontmatter, try to get from stored material_data
            if not category and hasattr(self, '_material_data') and self._material_data:
                category = self._material_data.get('category')
            
            if category and material_name:
                fallback_generator = ChemicalFallbackGenerator()
                _, generated_symbol = fallback_generator.generate_formula_and_symbol(
                    material_name, category
                )
                
                if generated_symbol:
                    # Apply 4-character limit for badge display
                    if len(generated_symbol) > 4:
                        return generated_symbol[:4].upper()
                    return generated_symbol.upper()
            
        except Exception as e:
            # Log warning but continue with basic fallback
            logger = __import__('logging').getLogger(__name__)
            logger.warning(f"Chemical fallback generation failed for {material_name}: {e}")
        
        # Basic fallback: first 2 characters of material name
        return material_name[:2].upper() if material_name else "???"

    def _generate_material_type_fallback(self, frontmatter_data: Dict) -> str:
        """Generate material type fallback from available data"""
        # Try to get category from frontmatter first
        category = self._get_field(frontmatter_data, ["category"], None)
        
        # If not in frontmatter, try to get from stored material_data
        if not category and hasattr(self, '_material_data') and self._material_data:
            category = self._material_data.get('category')
        
        if category:
            return category.lower()
        
        # Final fallback
        return "material"

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
