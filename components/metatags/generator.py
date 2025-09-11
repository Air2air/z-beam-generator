#!/usr/bin/env python3
"""
Metatags Component Generator

Generates YAML frontmatter meta tags using frontmatter extraction.
Integrated with the modular component architecture.
"""

from pathlib import Path
from typing import Dict, Optional

import yaml

from generators.hybrid_generator import HybridComponentGenerator
from generators.component_generators import ComponentResult
from utils.file_ops.frontmatter_loader import load_frontmatter_data
from versioning import stamp_component_output


class MetatagsComponentGenerator(HybridComponentGenerator):
    """Generator for meta tags components using frontmatter data and API when needed"""

    def __init__(self):
        super().__init__("metatags")
        
    def _build_prompt(
        self,
        material_name: str,
        material_data: Dict,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> str:
        """
        Build prompt using both material data and frontmatter data.
        """
        # Get important details for the prompt
        category = frontmatter_data.get("category", material_data.get("category", "material")) if frontmatter_data else material_data.get("category", "material")
        formula = material_data.get("formula", "")
        formula_str = f" ({formula})" if formula else ""
        author_name = author_info.get("name", "Z-Beam Engineering Team") if author_info else "Z-Beam Engineering Team"
        
        # Ensure material name is in title case
        material_name_title = material_name.title()
        
        # Extract technical details if available
        laser_params = material_data.get("laser_parameters", {})
        wavelength = laser_params.get("wavelength_optimal", "1064nm") if laser_params else "1064nm"
        
        # Extract applications if available
        applications = material_data.get("applications", [])
        applications_str = "\n".join([f"- {app}" for app in applications]) if applications else "No specific applications provided"
        
        return f"""Generate comprehensive YAML frontmatter metatags for a {material_name_title}{formula_str} laser cleaning technical guide webpage.

MATERIAL DETAILS:
- Name: {material_name_title}
- Category: {category}
- Formula: {formula}
- Wavelength: {wavelength}
- Author: {author_name}

APPLICATIONS:
{applications_str}

The title should be simple: "{material_name_title} Laser Cleaning"

Your output must follow this exact structure:
1. A title section with the page title (as specified above)
2. A meta_tags list containing:
   - description (150-160 chars)
   - keywords (comma-separated, include technical terms)
   - author, category, robots, etc.
3. An opengraph list with og:title, og:description, og:image, etc.
4. A twitter list with twitter:card, twitter:title, twitter:description, etc.
5. A canonical URL: https://z-beam.com/{material_name.lower()}-laser-cleaning
6. An alternate section with hreflang tags

Your output should be STRICTLY in YAML format with proper frontmatter delimiters (---).
Do NOT generate explanatory text - ONLY the YAML frontmatter with metadata.
Include appropriate technical details about laser cleaning parameters, applications, and material properties.
"""
        
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
        Generate component content using both frontmatter data and API when in hybrid mode.
        Will automatically load frontmatter data from file if not provided.
        """
        # If no frontmatter data was provided, try to load it from file
        if frontmatter_data is None:
            frontmatter_data = load_frontmatter_data(material_name)
            if not frontmatter_data:
                return ComponentResult(
                    component_type=self.component_type,
                    content="",
                    success=False,
                    error_message="No frontmatter data available",
                )
        
        # Determine if we should use API based on configuration
        from utils.component_mode import should_use_api
        use_api = should_use_api(self.component_type, api_client)
        
        # Use the structured frontmatter data as a base
        try:
            # First, extract basic metatags from frontmatter
            base_content = self._extract_from_frontmatter(material_name, frontmatter_data)
            
            # Then, if in hybrid mode, use API to enhance the descriptions and keywords
            if use_api:
                print(f"Generating {self.component_type} for {material_name} in hybrid mode with API enhancement")
                enhanced_content = self._enhance_with_api(
                    material_name=material_name,
                    material_data=material_data,
                    api_client=api_client,
                    author_info=author_info,
                    frontmatter_data=frontmatter_data,
                    base_content=base_content
                )
                
                return ComponentResult(
                    component_type=self.component_type,
                    content=enhanced_content,
                    success=True,
                )
            else:
                print(f"Generating {self.component_type} for {material_name} in static mode")
                return ComponentResult(
                    component_type=self.component_type,
                    content=base_content,
                    success=True,
                )
        except Exception as e:
            # Fall back to parent implementation if direct extraction fails
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
        """Generate YAML frontmatter meta tags from frontmatter using example - FAIL-FAST: Must have valid configuration"""
        
        # Load the example metatags as a template
        example_path = Path(__file__).parent / "example_metatags.md"
        try:
            with open(example_path, "r", encoding="utf-8") as f:
                example_content = f.read()
            example_data = self._parse_example_yaml(example_content)
        except Exception as e:
            raise Exception(f"Failed to load example metatags: {e} - FAIL-FAST requires valid template")
        
        # Get key metadata from frontmatter
        description = frontmatter_data.get("description", "")
        category = frontmatter_data.get("category", "material")
        author = frontmatter_data.get("author", "")
        keywords = frontmatter_data.get("keywords", "")
        
        # Get properties for technical details
        properties = frontmatter_data.get("properties", {})
        wavelength = properties.get("wavelength", "1064nm")
        
        # Ensure material name is in title case
        material_name_title = material_name.title()
        
        # Build title and descriptions
        title = f"{material_name_title} Laser Cleaning"
        og_title = f"{material_name_title} Laser Cleaning"
        twitter_title = f"{material_name_title} Laser Cleaning"
        
        # Create meta_tags list
        meta_tags = []
        meta_tags.append({"name": "description", "content": description})
        meta_tags.append({"name": "keywords", "content": keywords})
        meta_tags.append({"name": "author", "content": author})
        meta_tags.append({"name": "category", "content": category})
        meta_tags.append({"name": "robots", "content": "index, follow, max-snippet:-1, max-image-preview:large"})
        meta_tags.append({"name": "googlebot", "content": "index, follow, max-snippet:-1, max-image-preview:large"})
        meta_tags.append({"name": "viewport", "content": "width=device-width, initial-scale=1.0"})
        meta_tags.append({"name": "format-detection", "content": "telephone=no"})
        meta_tags.append({"name": "theme-color", "content": "#2563eb"})
        meta_tags.append({"name": "color-scheme", "content": "light dark"})
        meta_tags.append({"name": "material:category", "content": category})
        meta_tags.append({"name": "laser:wavelength", "content": wavelength})
        meta_tags.append({"name": "application-name", "content": "Z-Beam Laser Processing Guide"})
        meta_tags.append({"name": "msapplication-TileColor", "content": "#2563eb"})
        meta_tags.append({"name": "msapplication-config", "content": "/browserconfig.xml"})
        
        # Create opengraph list
        opengraph = []
        opengraph.append({"property": "og:title", "content": og_title})
        opengraph.append({"property": "og:description", "content": description})
        opengraph.append({"property": "og:type", "content": "article"})
        opengraph.append({"property": "og:image", "content": f"/images/{material_name.lower()}-laser-cleaning-hero.jpg"})
        opengraph.append({"property": "og:image:alt", "content": f"{material_name} laser cleaning process showing precision {category} restoration and surface treatment"})
        opengraph.append({"property": "og:image:width", "content": "1200"})
        opengraph.append({"property": "og:image:height", "content": "630"})
        opengraph.append({"property": "og:url", "content": f"https://z-beam.com/{material_name.lower()}-laser-cleaning"})
        opengraph.append({"property": "og:site_name", "content": "Z-Beam Laser Processing Guide"})
        opengraph.append({"property": "og:locale", "content": "en_US"})
        opengraph.append({"property": "article:author", "content": author})
        opengraph.append({"property": "article:section", "content": f"{material_name} Processing"})
        opengraph.append({"property": "article:tag", "content": f"{material_name} laser cleaning"})
        
        # Create twitter list
        twitter = []
        twitter.append({"name": "twitter:card", "content": "summary_large_image"})
        twitter.append({"name": "twitter:title", "content": twitter_title})
        twitter.append({"name": "twitter:description", "content": description})
        twitter.append({"name": "twitter:image", "content": f"/images/{material_name.lower()}-laser-cleaning-hero.jpg"})
        twitter.append({"name": "twitter:image:alt", "content": f"{material_name} {category} laser cleaning technical guide"})
        twitter.append({"name": "twitter:site", "content": "@z-beamTech"})
        twitter.append({"name": "twitter:creator", "content": "@z-beamTech"})
        
        # Create canonical and alternate URLs
        canonical = f"https://z-beam.com/{material_name.lower()}-laser-cleaning"
        alternate = [{"hreflang": "en", "href": canonical}]
        
        # Build the complete meta tags structure
        metatags_data = {
            "title": title,
            "meta_tags": meta_tags,
            "opengraph": opengraph,
            "twitter": twitter,
            "canonical": canonical,
            "alternate": alternate
        }
        
        # Convert to YAML string with frontmatter delimiters
        yaml_content = yaml.dump(metatags_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
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
        
    def _enhance_with_api(
        self,
        material_name: str,
        material_data: Dict,
        api_client,
        author_info: Optional[Dict],
        frontmatter_data: Dict,
        base_content: str,
    ) -> str:
        """Enhance metatags with API-generated content"""
        print(f"\n🔍 DEBUG: Enhancing metatags for {material_name} with API")
        
        # Parse the base content to get the YAML structure
        yaml_start = base_content.find("---") + 3
        yaml_end = base_content.find("---", yaml_start)
        yaml_content = base_content[yaml_start:yaml_end].strip()
        
        try:
            data = yaml.safe_load(yaml_content)
        except Exception as e:
            print(f"⚠️ DEBUG: Failed to parse base metatags content: {e}")
            raise Exception(f"Failed to parse base metatags content: {e}")
        
        # Prepare category and material info for the API prompt
        category = frontmatter_data.get("category", "material")
        formula = material_data.get("formula", "")
        formula_str = f" ({formula})" if formula else ""
        
        # Ensure material name is in title case for the API prompt
        material_name_title = material_name.title()
        
        # Create a detailed prompt for the API to generate enhanced descriptions
        prompt = f"""Generate enhanced meta descriptions for a {material_name_title}{formula_str} laser cleaning webpage.
The material category is {category}.
The title of the page is "{material_name_title} Laser Cleaning".

I need three improved descriptions of different lengths:
1. A detailed meta description (150-160 characters)
2. An engaging og:description (200-250 characters)
3. A concise twitter:description (120-130 characters)

Each description should include technical details about {material_name_title} laser cleaning, including wavelength information, applications, and key benefits.
Format your response as YAML with the keys 'meta_description', 'og_description', and 'twitter_description'.
"""
        print(f"\n🔍 DEBUG: Sending API prompt for descriptions:\n{prompt}")

        try:
            # Generate enhanced descriptions with the API
            print(f"🔍 DEBUG: Calling API to generate enhanced descriptions")
            response = api_client.generate_simple(prompt)
            print(f"🔍 DEBUG: Received API response: {response.content[:100]}..." if hasattr(response, 'content') else "No response content")
            
            if not response or not hasattr(response, 'content') or not response.content.strip():
                print("⚠️ DEBUG: API returned empty response for meta descriptions")
                raise Exception("API returned empty response for meta descriptions")
                
            # Parse the API response
            enhanced_text = response.content.strip()
            
            # Try to extract YAML from the response
            try:
                enhanced_data = yaml.safe_load(enhanced_text)
                print(f"🔍 DEBUG: Parsed API response as YAML: {enhanced_data}")
                
                if isinstance(enhanced_data, dict):
                    # Update the descriptions in our data
                    for meta_tag in data.get("meta_tags", []):
                        if meta_tag.get("name") == "description" and "meta_description" in enhanced_data:
                            meta_tag["content"] = enhanced_data["meta_description"]
                            
                    for og_tag in data.get("opengraph", []):
                        if og_tag.get("property") == "og:description" and "og_description" in enhanced_data:
                            og_tag["content"] = enhanced_data["og_description"]
                            
                    for twitter_tag in data.get("twitter", []):
                        if twitter_tag.get("name") == "twitter:description" and "twitter_description" in enhanced_data:
                            twitter_tag["content"] = enhanced_data["twitter_description"]
            except Exception as e:
                print(f"⚠️ DEBUG: Failed to parse API response as YAML: {e}")
                # If parsing fails, try to extract descriptions using text analysis
                if "meta_description:" in enhanced_text:
                    meta_desc = enhanced_text.split("meta_description:")[1].split("\n")[0].strip()
                    for meta_tag in data.get("meta_tags", []):
                        if meta_tag.get("name") == "description":
                            meta_tag["content"] = meta_desc
                
                if "og_description:" in enhanced_text:
                    og_desc = enhanced_text.split("og_description:")[1].split("\n")[0].strip()
                    for og_tag in data.get("opengraph", []):
                        if og_tag.get("property") == "og:description":
                            og_tag["content"] = og_desc
                
                if "twitter_description:" in enhanced_text:
                    twitter_desc = enhanced_text.split("twitter_description:")[1].split("\n")[0].strip()
                    for twitter_tag in data.get("twitter", []):
                        if twitter_tag.get("name") == "twitter:description":
                            twitter_tag["content"] = twitter_desc
        
            # Now generate enhanced keywords with the API
            keywords_prompt = f"""Generate an enhanced, comma-separated list of SEO keywords for {material_name_title} laser cleaning.
Include technical terms related to {category} processing, laser parameters, surface treatments, and applications.
The output should be a simple comma-separated list with no introductory text."""

            print(f"🔍 DEBUG: Sending API prompt for keywords:\n{keywords_prompt}")
            keywords_response = api_client.generate_simple(keywords_prompt)
            print(f"🔍 DEBUG: Received API keywords response: {keywords_response.content[:50]}..." if hasattr(keywords_response, 'content') else "No keywords response content")
            
            if keywords_response and hasattr(keywords_response, 'content') and keywords_response.content.strip():
                # Update keywords in meta_tags
                for meta_tag in data.get("meta_tags", []):
                    if meta_tag.get("name") == "keywords":
                        meta_tag["content"] = keywords_response.content.strip()
        
            # Convert back to YAML string with frontmatter delimiters
            enhanced_yaml = yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)
            enhanced_content = f"---\n{enhanced_yaml.strip()}\n---"
            
            print("✅ DEBUG: Successfully enhanced metatags with API content")
            
            # Apply version stamping to the enhanced content
            return stamp_component_output("metatags", enhanced_content)
            
        except Exception as e:
            print(f"⚠️ DEBUG: Error enhancing with API: {e}")
            # If API enhancement fails, return the base content
            return base_content
