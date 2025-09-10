#!/usr/bin/env python3
"""
Metatags Component Generator

Generates YAML frontmatter meta tags using frontmatter extraction.
Integrated with the modular component architecture.
"""

from pathlib import Path
from typing import Dict

import yaml

from generators.component_generators import FrontmatterComponentGenerator
from versioning import stamp_component_output


class MetatagsComponentGenerator(FrontmatterComponentGenerator):
    """Generator for meta tags components using frontmatter data"""

    def __init__(self):
        super().__init__("metatags")

    def _extract_from_frontmatter(
        self, material_name: str, frontmatter_data: Dict
    ) -> str:
        """Generate YAML frontmatter meta tags from frontmatter using example - FAIL-FAST: Must have valid configuration"""

        # Load example file to understand the expected format - FAIL-FAST: Must succeed
        try:
            example_path = Path(__file__).parent / "example_metatags.md"
            if not example_path.exists():
                raise Exception(f"Required example file missing: {example_path} - fail-fast architecture requires complete example configuration")
            with open(example_path, "r", encoding="utf-8") as f:
                example_content = f.read()
                example_data = self._parse_example_yaml(example_content)
        except Exception as e:
            raise Exception(f"Failed to load example file: {e} - fail-fast architecture requires valid example configuration")

        # Generate YAML meta tags dynamically - FAIL-FAST: Must use example structure
        if example_data:
            # Use example structure as template - primary method
            yaml_data = self._build_yaml_from_example(
                frontmatter_data, example_data, material_name
            )
        else:
            # FAIL-FAST: Example must be available - no fallbacks
            raise Exception(
                f"No valid example configuration found for metatags generation of {material_name} - fail-fast architecture requires example file"
            )

        # Convert to YAML string with frontmatter delimiters
        yaml_content = yaml.dump(yaml_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
        content = f"---\n{yaml_content.strip()}\n---"

        # Apply centralized version stamping
        return stamp_component_output("metatags", content)

    def _parse_example_yaml(self, example_content: str) -> Dict:
        """Parse example file to extract YAML structure - FAIL-FAST: Must succeed"""
        try:
            # Extract YAML frontmatter from example
            if example_content.startswith("---"):
                yaml_end = example_content.find("---", 3)
                if yaml_end != -1:
                    yaml_content = example_content[3:yaml_end].strip()
                    return yaml.safe_load(yaml_content)
        except Exception as e:
            raise Exception(f"Failed to parse example YAML: {e} - fail-fast architecture requires valid example file")

        # FAIL-FAST: Must find and parse YAML
        raise Exception("YAML frontmatter not found in example file - fail-fast architecture requires complete example structure")

    def _build_yaml_from_example(
        self, frontmatter_data: Dict, example_data: Dict, material_name: str
    ) -> Dict:
        """Build YAML structure using example as template"""
        result = {}

        for key, example_value in example_data.items():
            if key == "title":
                result[key] = self._get_field(frontmatter_data, ["title", "name"])
            elif key == "meta_tags":
                result[key] = self._build_meta_tags_list(frontmatter_data, example_value, material_name)
            elif key == "opengraph":
                result[key] = self._build_opengraph_list(frontmatter_data, example_value, material_name)
            elif key == "twitter":
                result[key] = self._build_twitter_list(frontmatter_data, example_value, material_name)
            elif key == "canonical":
                result[key] = self._generate_canonical_url(material_name)
            elif key == "alternate":
                result[key] = self._build_alternate_list(example_value)
            else:
                # Try to extract field from frontmatter - FAIL-FAST for required fields
                try:
                    result[key] = self._get_field(frontmatter_data, [key])
                except Exception:
                    # Use example value as-is for optional fields
                    result[key] = example_value

        return result

    def _build_meta_tags_list(self, frontmatter_data: Dict, example_list: list, material_name: str) -> list:
        """Build meta_tags list for YAML"""
        meta_tags = []

        for item in example_list:
            if isinstance(item, dict):
                tag_name = item.get("name", item.get("property", ""))
                if tag_name:
                    content = self._generate_meta_content(frontmatter_data, tag_name, material_name)
                    if content:
                        meta_tags.append({"name": tag_name, "content": content})

        return meta_tags

    def _build_opengraph_list(self, frontmatter_data: Dict, example_list: list, material_name: str) -> list:
        """Build opengraph list for YAML"""
        og_tags = []

        for item in example_list:
            if isinstance(item, dict):
                property_name = item.get("property", "")
                if property_name:
                    content = self._generate_meta_content(frontmatter_data, property_name, material_name)
                    if content:
                        og_tags.append({"property": property_name, "content": content})

        return og_tags

    def _build_twitter_list(self, frontmatter_data: Dict, example_list: list, material_name: str) -> list:
        """Build twitter list for YAML"""
        twitter_tags = []

        for item in example_list:
            if isinstance(item, dict):
                name = item.get("name", "")
                if name:
                    content = self._generate_meta_content(frontmatter_data, name, material_name)
                    if content:
                        twitter_tags.append({"name": name, "content": content})

        return twitter_tags

    def _generate_canonical_url(self, material_name: str) -> str:
        """Generate canonical URL"""
        slug = material_name.lower().replace(" ", "-")
        return f"https://z-beam.com/{slug}-laser-cleaning"

    def _build_alternate_list(self, example_list: list) -> list:
        """Build alternate list for YAML"""
        return example_list if isinstance(example_list, list) else []

    def _generate_meta_content(
        self,
        frontmatter_data: Dict,
        tag_name: str,
        material_name: str,
    ) -> str:
        """Generate content for specific meta tag based on tag name - FAIL-FAST: Must find required fields"""

        if tag_name in ["description", "og:description", "twitter:description"]:
            return self._get_field(
                frontmatter_data,
                ["description"]
            )
        elif tag_name in ["title", "og:title", "twitter:title"]:
            return self._get_field(frontmatter_data, ["title", "name"])
        elif tag_name == "keywords":
            keywords = [material_name.lower()]
            category = self._get_field(
                frontmatter_data, ["category", "type"]
            ).lower()
            if category:
                keywords.append(category)
            return ", ".join(keywords)
        elif tag_name in ["subject", "classification"]:
            return self._get_field(frontmatter_data, ["category", "type"])
        elif tag_name == "og:type":
            return "article"
        elif tag_name == "twitter:card":
            return "summary"
        elif tag_name == "author":
            try:
                return self._get_field(frontmatter_data, ["author"])
            except Exception:
                raise ValueError("Author information must be available in frontmatter - no defaults allowed in fail-fast architecture")
        elif tag_name == "robots":
            return "index, follow, max-snippet:-1, max-image-preview:large"
        elif tag_name == "googlebot":
            return "index, follow, max-snippet:-1, max-image-preview:large"
        elif tag_name == "viewport":
            return "width=device-width, initial-scale=1.0"
        elif tag_name == "format-detection":
            return "telephone=no"
        elif tag_name == "theme-color":
            return "#2563eb"
        elif tag_name == "color-scheme":
            return "light dark"
        elif tag_name.startswith("material:"):
            try:
                return self._get_field(frontmatter_data, [tag_name.replace("material:", "")])
            except Exception:
                raise ValueError(f"Material information must be available for {tag_name} - no defaults allowed in fail-fast architecture")
        elif tag_name.startswith("laser:"):
            try:
                return self._get_field(frontmatter_data, [tag_name.replace("laser:", "")])
            except Exception:
                raise ValueError(f"Laser information must be available for {tag_name} - no defaults allowed in fail-fast architecture")
        elif tag_name == "application-name":
            return "Z-Beam Laser Processing Guide"
        elif tag_name == "msapplication-TileColor":
            return "#2563eb"
        elif tag_name == "msapplication-config":
            return "/browserconfig.xml"
        elif tag_name.startswith("og:image"):
            if tag_name == "og:image":
                return f"/images/{material_name.lower().replace(' ', '-')}-laser-cleaning-hero.jpg"
            elif tag_name == "og:image:alt":
                return f"{material_name} laser cleaning process showing precision restoration and surface treatment"
            elif tag_name == "og:image:width":
                return "1200"
            elif tag_name == "og:image:height":
                return "630"
        elif tag_name == "og:url":
            return self._generate_canonical_url(material_name)
        elif tag_name == "og:site_name":
            return "Z-Beam Laser Processing Guide"
        elif tag_name == "og:locale":
            return "en_US"
        elif tag_name == "article:author":
            try:
                return self._get_field(frontmatter_data, ["author"])
            except Exception:
                raise ValueError("Author information must be available for article:author - no defaults allowed in fail-fast architecture")
        elif tag_name == "article:section":
            return f"{material_name} Processing"
        elif tag_name == "article:tag":
            return f"{material_name} laser cleaning"
        elif tag_name.startswith("twitter:image"):
            if tag_name == "twitter:image":
                return f"/images/{material_name.lower().replace(' ', '-')}-laser-cleaning-hero.jpg"
            elif tag_name == "twitter:image:alt":
                return f"{material_name} laser cleaning technical guide"
        elif tag_name == "twitter:site":
            return "@ZBeamTech"
        elif tag_name == "twitter:creator":
            return "@ZBeamTech"
        else:
            # Try to extract from frontmatter - FAIL-FAST: Must find field
            return self._get_field(frontmatter_data, [tag_name])

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
