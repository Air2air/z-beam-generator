#!/usr/bin/env python3
"""
JSON-LD Component Generator

Generates JSON-LD structured data using frontmatter extraction.
Integrated with the modular component architecture.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Optional

from generators.component_generators import (

    ComponentResult,
    FrontmatterComponentGenerator,
)


class JsonldComponentGenerator(FrontmatterComponentGenerator):
    """Generator for JSON-LD components using frontmatter data"""

    def __init__(self):
        super().__init__("jsonld")
        self._material_data = None
        self._author_info = None

    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> ComponentResult:
        """Generate component from frontmatter data - store material_data and author_info for use in extraction"""
        self._material_data = material_data
        self._author_info = author_info
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
        """Generate JSON-LD structured data from frontmatter using schema and example"""

        # Load example file to understand the expected format
        try:
            example_path = Path(__file__).parent / "example_jsonld.md"
            example_fields = {}
            if example_path.exists():
                with open(example_path, "r", encoding="utf-8") as f:
                    example_content = f.read()
                    example_fields = self._parse_example_json_ld(example_content)
        except Exception:
            example_fields = {}

        # Load schema to understand expected structure
        try:
            schema_path = (
                Path(__file__).parent.parent.parent / "schemas" / "material.json"
            )
            schema_structure = {}
            if schema_path.exists():
                with open(schema_path, "r", encoding="utf-8") as f:
                    schema = json.load(f)
                    # Extract relevant properties for JSON-LD
                    if (
                        "materialProfile" in schema
                        and "profile" in schema["materialProfile"]
                    ):
                        material_profile = schema["materialProfile"]["profile"]
                        schema_structure = {
                            "basic": material_profile.get("basicInfo", {}),
                            "chemical": material_profile.get("chemicalProperties", {}),
                            "physical": material_profile.get("physicalProperties", {}),
                            "technical": material_profile.get(
                                "technicalSpecifications", {}
                            ),
                        }
                    else:
                        raise Exception(
                            "Schema missing required 'materialProfile.profile' structure - fail-fast architecture requires complete schema"
                        )
            else:
                raise Exception(
                    f"Required schema file missing: {schema_path} - fail-fast architecture requires complete schema configuration"
                )
        except Exception as e:
            raise Exception(
                f"Failed to load schema: {e} - fail-fast architecture requires valid schema configuration"
            )

        # Extract values dynamically
        if example_fields:
            # Use example structure as template
            jsonld_data = self._build_from_example(
                frontmatter_data, example_fields, material_name, self._material_data
            )
        elif schema_structure:
            # Use schema structure
            jsonld_data = self._build_from_schema(
                frontmatter_data, schema_structure, material_name
            )
        else:
            # FAIL-FAST: No fallback allowed - system must have required schema or example
            raise Exception(
                f"No schema or example provided for JSON-LD generation of {material_name} - fail-fast architecture requires explicit configuration"
            )

        # Format as proper JSON-LD script tag
        json_content = json.dumps(jsonld_data, indent=2)
        return f'<script type="application/ld+json">\n{json_content}\n</script>'

    def _parse_example_json_ld(self, example_content: str) -> Dict:
        """Parse example file to extract JSON-LD structure"""
        try:
            # Look for JSON-LD script tags
            if '<script type="application/ld+json">' in example_content:
                start_tag = '<script type="application/ld+json">'
                end_tag = "</script>"
                start_idx = example_content.find(start_tag) + len(start_tag)
                end_idx = example_content.find(end_tag, start_idx)
                if start_idx > 0 and end_idx > start_idx:
                    json_str = example_content[start_idx:end_idx].strip()
                    return json.loads(json_str)
        except Exception:
            pass
        return {}

    def _build_from_example(
        self, frontmatter_data: Dict, example_structure: Dict, material_name: str, material_data: Dict
    ) -> Dict:
        """Build JSON-LD using example structure as template"""
        result = {}

        for key, example_value in example_structure.items():
            if key in ["@context", "@type"]:
                result[key] = example_value
            elif key == "name":
                result[key] = self._get_field(
                    frontmatter_data, ["title", "name"], material_name
                )  # material_name as fallback for name
            elif key == "description":
                result[key] = self._get_field(
                    frontmatter_data,
                    ["description"],
                    f"Technical specifications and properties for {material_name}",
                )  # Generated description as fallback
            elif key == "category":
                if (
                    "category" not in frontmatter_data
                    and "type" not in frontmatter_data
                ):
                    raise Exception(
                        "Frontmatter data missing required 'category' or 'type' field - fail-fast architecture requires complete material information"
                    )
                result[key] = self._get_field(
                    frontmatter_data, ["category", "type"], None
                )  # No default - must exist
            elif isinstance(example_value, dict):
                result[key] = self._build_nested_structure(
                    frontmatter_data, example_value, key, self._author_info
                )
            elif isinstance(example_value, list):
                # Only process arrays that are expected to contain property objects
                if key in ["additionalProperty", "properties"]:
                    result[key] = self._build_properties_array(
                        frontmatter_data, example_value, material_data
                    )
                else:
                    # For other arrays (keywords, mentions, etc.), use as-is
                    result[key] = example_value
            else:
                # Try to extract similar field from frontmatter - allow defaults for optional fields
                result[key] = self._get_field(
                    frontmatter_data, [key], str(example_value)
                )

        return result

    def _build_from_schema(
        self, frontmatter_data: Dict, schema_structure: Dict, material_name: str
    ) -> Dict:
        """Build JSON-LD using schema structure"""
        jsonld = {
            "@context": "https://schema.org",
            "@type": "Material",
            "name": self._get_field(
                frontmatter_data, ["title", "name"], material_name
            ),  # material_name as fallback
            "description": self._get_field(
                frontmatter_data,
                ["description"],
                f"Technical specifications and properties for {material_name}",
            ),  # Generated fallback
            "category": self._get_field(
                frontmatter_data, ["category", "type"], None
            ),  # No default - must exist
        }

        # Add chemical composition if available
        if "chemical" in schema_structure:
            chem_props = schema_structure["chemical"].get("properties", {})
            if chem_props:
                # FAIL-FAST: Chemical properties must be available if schema defines them
                formula = self._get_field(
                    frontmatter_data, ["chemicalProperties.formula", "formula"], None
                )
                symbol = self._get_field(
                    frontmatter_data, ["chemicalProperties.symbol", "symbol"], None
                )
                if not formula:
                    raise Exception(
                        "Chemical formula required but not found in frontmatter data - fail-fast architecture requires complete chemical information"
                    )
                if not symbol:
                    raise Exception(
                        "Chemical symbol required but not found in frontmatter data - fail-fast architecture requires complete chemical information"
                    )

                jsonld["chemicalComposition"] = {
                    "@type": "ChemicalSubstance",
                    "molecularFormula": formula,  # Already validated above
                    "identifier": symbol,  # Already validated above
                }

        # Add properties array
        properties = []
        for section_name, section_data in schema_structure.items():
            if section_name != "basic" and isinstance(section_data, dict):
                if "properties" not in section_data:
                    raise Exception(
                        f"Schema section '{section_name}' missing required 'properties' field - fail-fast architecture requires complete schema"
                    )
                section_props = section_data["properties"]
                for prop_name, prop_config in section_props.items():
                    prop_value = self._get_field(
                        frontmatter_data,
                        [f"{section_name}Properties.{prop_name}", prop_name],
                        None,
                    )
                    if not prop_value:
                        raise Exception(
                            f"Property '{prop_name}' required by schema but not found in frontmatter data - fail-fast architecture requires complete property information"
                        )

                    # FAIL-FAST: Property config must have title
                    if "title" not in prop_config:
                        raise Exception(
                            f"Property config for '{prop_name}' missing required 'title' field - fail-fast architecture requires complete schema configuration"
                        )

                    properties.append(
                        {
                            "@type": "PropertyValue",
                            "name": prop_config["title"],  # Already validated above
                            "value": prop_value,  # Already validated above
                        }
                    )

        if properties:
            jsonld["properties"] = properties

        return jsonld

    def _build_nested_structure(
        self, frontmatter_data: Dict, example_structure: Dict, parent_key: str, author_info: Optional[Dict]
    ) -> Dict:
        """Build nested dictionary structure"""
        result = {}
        for key, example_value in example_structure.items():
            if key in ["@type"]:
                result[key] = example_value
            elif parent_key in ["author", "reviewedBy"] and key == "name":
                # Special handling for author and reviewer names - extract from author_info first, then frontmatter
                if author_info and "name" in author_info:
                    result[key] = author_info["name"]
                else:
                    author_name = self._get_field(frontmatter_data, ["author"], None)
                    if author_name:
                        result[key] = author_name
                    else:
                        # Fallback to example value if author not found
                        result[key] = str(example_value)
            else:
                field_path = (
                    f"{parent_key}.{key}"
                    if parent_key != "chemicalComposition"
                    else f"chemicalProperties.{key}"
                )
                result[key] = self._get_field(
                    frontmatter_data, [field_path, key], str(example_value)
                )  # Allow example_value as fallback for optional nested fields
        return result

    def _build_properties_array(
        self, frontmatter_data: Dict, example_array: list, material_data: Dict
    ) -> list:
        """Build properties array from example structure"""
        if not example_array:
            return []

        # Use first item as template
        template = example_array[0] if isinstance(example_array[0], dict) else {}

        # FAIL-FAST: Template must have @type
        if not isinstance(template, dict) or "@type" not in template:
            raise Exception(
                "Example array template missing required '@type' field - fail-fast architecture requires complete example structure"
            )

        properties = []
        # Look for common property sections
        for section_name in [
            "physicalProperties",
            "technicalSpecifications",
            "properties",
            "chemicalProperties"
        ]:
            if section_name not in frontmatter_data:
                continue  # Skip sections that don't exist
            section_data = frontmatter_data[section_name]
            if isinstance(section_data, dict):
                for prop_name, prop_value in section_data.items():
                    properties.append(
                        {
                            "@type": template["@type"],
                            "name": prop_name.replace("_", " ").title(),
                            "value": str(prop_value),
                        }
                    )

        # If no properties found in sections, try to extract from material_data
        if not properties:
            if isinstance(material_data, dict):
                # Try properties from material_data
                material_props = material_data.get("properties", {})
                if isinstance(material_props, dict):
                    for prop_name, prop_value in material_props.items():
                        properties.append(
                            {
                                "@type": template["@type"],
                                "name": prop_name.replace("_", " ").title(),
                                "value": str(prop_value),
                            }
                        )

        # If still no properties, try data section
        if not properties:
            data_section = material_data.get("data", {})
            if isinstance(data_section, dict):
                for prop_name, prop_value in data_section.items():
                    properties.append(
                        {
                            "@type": template["@type"],
                            "name": prop_name.replace("_", " ").title(),
                            "value": str(prop_value),
                        }
                    )

        if not properties:
            raise Exception(
                "No properties found in frontmatter data - fail-fast architecture requires at least one property for JSON-LD generation"
            )

        return properties

    def _get_field(self, data: Dict, paths: list, default: str = None) -> str:
        """Extract field using dot notation paths - FAIL-FAST: default must be explicitly handled"""
        for path in paths:
            if "." in path:
                # Handle nested path
                keys = path.split(".")
                current = data
                try:
                    for key in keys:
                        if key not in current:
                            continue
                        current = current[key]
                    if current is not None:
                        return str(current)
                except (KeyError, TypeError):
                    continue
            else:
                # Handle direct key
                if path in data and data[path] is not None:
                    return str(data[path])

        # FAIL-FAST: If no default provided, field must exist
        if default is None:
            raise Exception(
                f"Required field not found in data. Searched paths: {paths} - fail-fast architecture requires complete data"
            )
        return default
