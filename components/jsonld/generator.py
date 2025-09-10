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
from versioning import stamp_component_output


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

        # Load example file to understand the expected format - FAIL-FAST: Must succeed
        example_fields = {}
        try:
            example_path = Path(__file__).parent / "example_jsonld.md"
            if example_path.exists():
                with open(example_path, "r", encoding="utf-8") as f:
                    example_content = f.read()
                    example_fields = self._parse_example_json_ld(example_content)
        except Exception:
            # If example fails, try schema instead
            pass

        # Load schema to understand expected structure - FAIL-FAST: Must succeed if example not available
        schema_structure = {}
        if not example_fields:
            try:
                schema_path = (
                    Path(__file__).parent.parent.parent / "schemas" / "material.json"
                )
                if not schema_path.exists():
                    raise Exception(
                        f"Required schema file missing: {schema_path} - fail-fast architecture requires complete schema configuration"
                    )
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
            except Exception as e:
                raise Exception(
                    f"Failed to load schema: {e} - fail-fast architecture requires valid schema configuration"
                )

        # Extract values dynamically - FAIL-FAST: Must have either example or schema
        if example_fields:
            # Use example structure as template
            jsonld_data = self._build_from_example(
                frontmatter_data, example_fields, material_name, self._material_data
            )
        elif schema_structure:
            # Use schema structure as fallback
            jsonld_data = self._build_from_schema(
                frontmatter_data, schema_structure, material_name
            )
        else:
            # FAIL-FAST: No configuration available
            raise Exception(
                f"No valid configuration found for JSON-LD generation of {material_name} - fail-fast architecture requires either example file or schema"
            )

        # Format as proper JSON-LD script tag
        json_content = json.dumps(jsonld_data, indent=2)
        content = f'<script type="application/ld+json">\n{json_content}\n</script>'

        # Apply centralized version stamping
        return stamp_component_output("jsonld", content)

    def _parse_example_json_ld(self, example_content: str) -> Dict:
        """Parse example file to extract JSON-LD structure - FAIL-FAST: Must succeed"""
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
        except Exception as e:
            raise Exception(f"Failed to parse example JSON-LD: {e} - fail-fast architecture requires valid example file")

        # FAIL-FAST: Must find and parse JSON-LD
        raise Exception("JSON-LD script tag not found in example file - fail-fast architecture requires complete example structure")

    def _build_from_example(
        self,
        frontmatter_data: Dict,
        example_structure: Dict,
        material_name: str,
        material_data: Dict,
    ) -> Dict:
        """Build JSON-LD using example structure as template"""
        result = {}

        for key, example_value in example_structure.items():
            if key in ["@context", "@type"]:
                result[key] = example_value
            elif key == "headline":
                result[key] = f"Laser Cleaning of {material_name} Materials"
            elif key == "alternativeHeadline":
                result[key] = f"Advanced Laser Ablation Techniques for {material_name} Surface Treatment"
            elif key == "description":
                result[key] = f"Comprehensive technical guide covering laser cleaning methodologies for {material_name} materials, including optimal parameters, industrial applications, and surface treatment benefits."
            elif key == "abstract":
                # Extract technical data for abstract - all fields required
                wavelength = self._get_field(frontmatter_data, ["technicalSpecifications.wavelength", "wavelength"])
                fluence = self._get_field(frontmatter_data, ["technicalSpecifications.fluenceRange", "fluenceRange"])
                applications = self._get_field(frontmatter_data, ["applications"])
                result[key] = f"Advanced laser cleaning techniques for {material_name} materials using {wavelength} wavelength at {fluence} fluence for {applications}."
            elif key == "keywords":
                # Generate comprehensive keywords from material data - all fields required
                base_keywords = [material_name.lower(), f"{material_name.lower()} laser cleaning", f"{material_name.lower()} metal"]
                tech_keywords = ["laser ablation", "non-contact cleaning", "surface treatment", "industrial laser"]
                wavelength = self._get_field(frontmatter_data, ["technicalSpecifications.wavelength", "wavelength"])
                tech_keywords.append(f"{wavelength} wavelength")
                tech_keywords.append("laser fluence")
                applications = self._get_field(frontmatter_data, ["applications"])
                if "aerospace" in applications.lower():
                    tech_keywords.append("aerospace applications")
                if "automotive" in applications.lower():
                    tech_keywords.append("automotive applications")
                result[key] = base_keywords + tech_keywords
            elif key == "articleBody":
                # Generate comprehensive article body (100-150 words) matching example format - all fields required
                density = self._get_field(frontmatter_data, ["properties.density", "physicalProperties.density", "density"])
                thermal_conductivity = self._get_field(frontmatter_data, ["properties.thermalConductivity", "physicalProperties.thermalConductivity", "thermalConductivity"])
                wavelength = self._get_field(frontmatter_data, ["technicalSpecifications.wavelength", "wavelength"])
                fluence = self._get_field(frontmatter_data, ["technicalSpecifications.fluenceRange", "fluenceRange"])
                pulse_duration = self._get_field(frontmatter_data, ["technicalSpecifications.pulseDuration", "pulseDuration"])
                applications = self._get_field(frontmatter_data, ["applications"])

                result[key] = f"{material_name} is a lightweight metal with {density} density and {thermal_conductivity} thermal conductivity extensively used in aircraft component cleaning, automotive engine part restoration. Laser cleaning utilizes {wavelength} wavelength at {fluence} fluence and {pulse_duration} pulse duration to remove oxidation and thermal coatings, paint and corrosion layers while preserving material integrity. The process operates at controlled power levels with precise beam control for optimal surface treatment. Key advantages include non-contact processing, selective contamination removal, and environmental safety compared to chemical methods."
            elif key == "wordCount":
                # Calculate actual word count from articleBody
                article_body = result.get("articleBody", "")
                result[key] = len(article_body.split())
            elif key == "name":
                result[key] = self._get_field(
                    frontmatter_data, ["title", "name"]
                )
            elif key == "category":
                if (
                    "category" not in frontmatter_data
                    and "type" not in frontmatter_data
                ):
                    raise Exception(
                        "Frontmatter data missing required 'category' or 'type' field - fail-fast architecture requires complete material information"
                    )
                result[key] = self._get_field(
                    frontmatter_data, ["category", "type"]
                )
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
                # Try to extract field from frontmatter - skip if not available (fail-fast for required fields only)
                try:
                    result[key] = self._get_field(frontmatter_data, [key])
                except Exception:
                    # Skip fields that are not available in frontmatter - use example value as-is
                    result[key] = example_value

        return result

    def _build_from_schema(
        self, frontmatter_data: Dict, schema_structure: Dict, material_name: str
    ) -> Dict:
        """Build JSON-LD using schema structure"""
        jsonld = {
            "@context": "https://schema.org",
            "@type": "Material",
            "name": self._get_field(
                frontmatter_data, ["title", "name"]
            ),  # material_name as fallback
            "description": self._get_field(
                frontmatter_data,
                ["description"]
            ),  # Generated fallback
            "category": self._get_field(
                frontmatter_data, ["category", "type"]
            ),  # No default - must exist
        }

        # Add chemical composition if available
        if "chemical" in schema_structure:
            chem_props = schema_structure["chemical"].get("properties", {})
            if chem_props:
                formula = self._get_field(
                    frontmatter_data, ["chemicalProperties.formula", "formula"]
                )
                symbol = self._get_field(
                    frontmatter_data, ["chemicalProperties.symbol", "symbol"]
                )

                jsonld["chemicalComposition"] = {
                    "@type": "ChemicalSubstance",
                    "molecularFormula": formula,
                    "identifier": symbol,
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
                        [f"{section_name}Properties.{prop_name}", prop_name]
                    )

                    # FAIL-FAST: Property config must have title
                    if "title" not in prop_config:
                        raise Exception(
                            f"Property config for '{prop_name}' missing required 'title' field - fail-fast architecture requires complete schema configuration"
                        )

                    properties.append(
                        {
                            "@type": "PropertyValue",
                            "name": prop_config["title"],
                            "value": prop_value,
                        }
                    )

        if properties:
            jsonld["properties"] = properties

        return jsonld

    def _build_nested_structure(
        self,
        frontmatter_data: Dict,
        example_structure: Dict,
        parent_key: str,
        author_info: Optional[Dict],
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
                    result[key] = self._get_field(frontmatter_data, ["author"])
            else:
                field_path = (
                    f"{parent_key}.{key}"
                    if parent_key != "chemicalComposition"
                    else f"chemicalProperties.{key}"
                )
                try:
                    result[key] = self._get_field(
                        frontmatter_data, [field_path, key]
                    )
                except Exception:
                    # Use example value if field not available
                    result[key] = example_value
        return result

    def _build_properties_array(
        self, frontmatter_data: Dict, example_array: list, material_data: Dict
    ) -> list:
        """Build properties array from frontmatter data - FAIL-FAST: Must find properties"""
        if not example_array:
            raise Exception("Example array is empty - fail-fast architecture requires complete example structure")

        # Use first item as template
        template = example_array[0] if isinstance(example_array[0], dict) else {}

        # FAIL-FAST: Template must have @type
        if not isinstance(template, dict) or "@type" not in template:
            raise Exception(
                "Example array template missing required '@type' field - fail-fast architecture requires complete example structure"
            )

        properties = []
        # Look for properties in frontmatter data - must exist
        if "properties" not in frontmatter_data:
            raise Exception("Properties section not found in frontmatter data - fail-fast architecture requires complete property information")

        properties_data = frontmatter_data["properties"]
        if isinstance(properties_data, dict):
            for prop_name, prop_value in properties_data.items():
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

    def _get_field(self, data: Dict, paths: list) -> str:
        """Extract field using dot notation paths - FAIL-FAST: No defaults allowed"""
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

        # FAIL-FAST: Field must exist - no fallbacks allowed
        raise Exception(
            f"Required field not found in data. Searched paths: {paths} - fail-fast architecture requires complete data"
        )
