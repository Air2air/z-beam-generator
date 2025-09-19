#!/usr/bin/env python3
"""
JSON-LD Component Generator

Generates JSON-LD structured data using frontmatter extraction.
Integrated with the modular component architecture.
"""

import json
import yaml
import logging
from pathlib import Path
from typing import Dict, Optional

from generators.hybrid_generator import HybridComponentGenerator
from generators.component_generators import ComponentResult
from versioning import stamp_component_output

logger = logging.getLogger(__name__)


class JsonldComponentGenerator(HybridComponentGenerator):
    """
    Generator for JSON-LD structured data components for laser cleaning materials.
    
    Extracts rich technical specifications, applications, and laser cleaning data
    from frontmatter to create Schema.org Article structured data with embedded
    Material and HowTo entities for comprehensive SEO optimization.
    """

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
        """Generate component using template-based approach with frontmatter data"""
        self._material_data = material_data
        self._author_info = author_info
        
        # Load frontmatter data if not provided
        if frontmatter_data is None:
            from utils.file_ops.frontmatter_loader import load_frontmatter_data
            frontmatter_data = load_frontmatter_data(material_name) or {}
        
        # Generate JSON-LD using template-based approach
        try:
            jsonld_content = self._generate_from_template(
                material_name=material_name,
                frontmatter_data=frontmatter_data,
                author_info=author_info
            )
            
            return ComponentResult(
                component_type=self.component_type,
                content=jsonld_content,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Template-based generation failed: {e}")
            return ComponentResult(
                component_type=self.component_type,
                content="",
                success=False,
                error_message=str(e)
            )

    def _generate_from_template(
        self,
        material_name: str,
        frontmatter_data: Dict,
        author_info: Optional[Dict] = None
    ) -> str:
        """Generate JSON-LD using template-based approach"""
        
        # Load example structure
        example_structure = self._load_example_structure()
        
        # Build JSON-LD structure using template
        jsonld_data = self._build_from_example(
            frontmatter_data=frontmatter_data,
            example_structure=example_structure,
            material_name=material_name,
            material_data=self._material_data
        )
        
        # Convert to YAML format
        import yaml
        yaml_content = yaml.dump({"jsonld": jsonld_data}, default_flow_style=False, allow_unicode=True)
        
        return yaml_content

    def _load_example_structure(self) -> Dict:
        """Load example JSON-LD structure from template file"""
        try:
            example_path = Path(__file__).parent / "example_jsonld.md"
            if example_path.exists():
                with open(example_path, "r", encoding="utf-8") as f:
                    example_content = f.read()
                    return self._parse_example_json_ld(example_content)
            else:
                raise Exception(f"Example file not found at {example_path}")
        except Exception as e:
            raise Exception(f"Failed to load example JSON-LD structure: {e}")

    def _build_prompt(
        self,
        material_name: str,
        material_data: Dict,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> str:
        """Build enhanced prompt incorporating frontmatter data for hybrid generation"""
        
        # Extract key frontmatter data for context
        context_parts = []
        
        if frontmatter_data:
            # Extract technical specifications
            tech_specs = frontmatter_data.get("technicalSpecifications", {})
            if tech_specs:
                specs_summary = []
                for key, value in tech_specs.items():
                    if isinstance(value, (str, int, float)):
                        specs_summary.append(f"{key}: {value}")
                if specs_summary:
                    context_parts.append(f"Technical Specifications: {', '.join(specs_summary[:5])}")
            
            # Extract applications
            applications = frontmatter_data.get("applications", [])
            if applications and isinstance(applications, list):
                app_list = []
                for app in applications[:3]:  # Limit to first 3
                    if isinstance(app, dict) and app.get("industry"):
                        detail = app.get("detail", "")
                        app_list.append(f"{app['industry']}: {detail}"[:100])  # Truncate long details
                if app_list:
                    context_parts.append(f"Applications: {'; '.join(app_list)}")
            
            # Extract environmental impact
            env_impact = frontmatter_data.get("environmentalImpact", [])
            if env_impact and isinstance(env_impact, list):
                benefits = []
                for impact in env_impact[:2]:  # Limit to first 2
                    if isinstance(impact, dict) and impact.get("benefit"):
                        benefits.append(impact["benefit"])
                if benefits:
                    context_parts.append(f"Environmental Benefits: {', '.join(benefits)}")
            
            # Extract key properties
            properties = frontmatter_data.get("properties", {})
            if properties:
                key_props = []
                for prop in ["density", "meltingPoint", "thermalConductivity", "wavelength"]:
                    if prop in properties:
                        key_props.append(f"{prop}: {properties[prop]}")
                if key_props:
                    context_parts.append(f"Key Properties: {', '.join(key_props[:4])}")

        # Build enhanced prompt
        prompt = f"""Generate comprehensive JSON-LD structured data for {material_name} laser cleaning using Schema.org Article format.

Material: {material_name}
Category: {material_data.get('category', 'material')}

"""
        
        if context_parts:
            prompt += "Available Context Data:\n"
            for i, part in enumerate(context_parts, 1):
                prompt += f"{i}. {part}\n"
            prompt += "\n"

        prompt += """Requirements:
- Use Schema.org Article @type (NOT ChemicalSubstance)
- Include specific laser cleaning technical parameters and applications
- Integrate environmental benefits and industrial use cases
- Focus on laser cleaning methodology and material-specific optimization
- Include author information and material properties
- Ensure content is highly specific to this material and its laser cleaning applications
- Generate rich, detailed content that maximizes differences between materials
- Output ONLY valid JSON content, no markdown formatting or code blocks
- Do not include ```json or ``` or any markdown syntax"""

        return prompt

    def _post_process_content(
        self, content: str, material_name: str, material_data: Dict
    ) -> str:
        """Post-process API-generated content by integrating comprehensive frontmatter data"""
        
        # Strip any markdown formatting that might have been generated
        if content.startswith('````yaml') or content.startswith('```yaml'):
            # Remove markdown yaml block formatting
            lines = content.split('\n')
            # Find the start and end of the actual content
            start_idx = 0
            end_idx = len(lines)
            
            for i, line in enumerate(lines):
                if line.strip().startswith('{') and '"@context"' in line:
                    start_idx = i
                    break
            
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].strip() == '}':
                    end_idx = i + 1
                    break
            
            # Extract just the JSON content
            content = '\n'.join(lines[start_idx:end_idx])
        
        # Remove any remaining markdown code block markers
        content = content.replace('```json', '').replace('```yaml', '').replace('```', '').replace('````', '')
        content = content.strip()
        
        # In hybrid mode, enhance API content with comprehensive frontmatter data
        try:
            import json
            from utils.file_ops.frontmatter_loader import load_frontmatter_data
            
            # Load frontmatter data for enhancement
            frontmatter_data = load_frontmatter_data(material_name)
            if not frontmatter_data:
                logger.warning(f"No frontmatter data available for {material_name}, using API content as-is")
                return content
            
            # Parse the API-generated JSON-LD
            try:
                api_jsonld = json.loads(content)
            except json.JSONDecodeError:
                logger.warning(f"API generated invalid JSON for {material_name}, falling back to frontmatter extraction")
                return self._extract_from_frontmatter(material_name, frontmatter_data)
            
            # Enhance API content with comprehensive frontmatter data
            enhanced_jsonld = self._enhance_api_content_with_frontmatter(
                api_jsonld, frontmatter_data, material_name
            )
            
            # Convert enhanced content to YAML format for consistency with other components
            import yaml
            jsonld_yaml_data = {"jsonld": enhanced_jsonld}
            yaml_content = yaml.dump(jsonld_yaml_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
            enhanced_content = f"---\n{yaml_content.strip()}\n---"
            
            # Apply centralized version stamping
            from versioning import stamp_component_output
            return stamp_component_output("jsonld", enhanced_content)
            
        except Exception as e:
            logger.warning(f"Failed to enhance API content with frontmatter for {material_name}, using API content: {e}")
            return content

    def _enhance_api_content_with_frontmatter(
        self, api_jsonld: Dict, frontmatter_data: Dict, material_name: str
    ) -> Dict:
        """Enhance API-generated JSON-LD with comprehensive frontmatter data"""
        
        # Start with API content as base
        enhanced = api_jsonld.copy()
        
        # Ensure material name is in title case
        material_name_title = material_name.title()
        material_slug = self._apply_standardized_naming(material_name.lower())
        
        # Extract comprehensive frontmatter data
        tech_specs = frontmatter_data.get("technicalSpecifications", {})
        applications_list = frontmatter_data.get("applications", [])
        env_impact = frontmatter_data.get("environmentalImpact", [])
        outcomes = frontmatter_data.get("outcomes", [])
        author_obj = frontmatter_data.get("author_object", {})
        images = frontmatter_data.get("images", {})
        composition = frontmatter_data.get("composition", [])
        
        # Build meaningful keywords from frontmatter (ignore API keywords to avoid character splitting)
        enhanced_keywords = set()
        
        # Add base material keywords
        enhanced_keywords.update([
            f"{material_name.lower()}-laser-cleaning",
            f"{material_name.lower()}-surface-treatment", 
            "industrial-laser-cleaning"
        ])
        
        # Add category-specific keywords
        category = frontmatter_data.get("category", "")
        if category:
            enhanced_keywords.update([f"{material_name.lower()}-{category}", f"{category}-laser-processing"])
        
        # Add application industry keywords
        if applications_list:
            for app in applications_list[:3]:
                if app.get("industry"):
                    industry = app["industry"].lower().replace(" & ", "-").replace(" ", "-")
                    enhanced_keywords.add(f"{industry}-laser-cleaning")
        
        # Add technical specification keywords
        if tech_specs.get("wavelength"):
            wavelength = tech_specs["wavelength"].replace("nm", "").replace(" ", "").replace("(primary),", "").replace("(optional)", "")
            enhanced_keywords.add(f"{wavelength.split(',')[0].strip()}-nm-laser")
        
        # Add environmental keywords if applicable
        if env_impact:
            enhanced_keywords.update(["eco-friendly-cleaning", "sustainable-laser-processing"])
        
        # Add base material keywords
        enhanced_keywords.update([
            f"{material_name.lower()}-laser-cleaning",
            f"{material_name.lower()}-surface-treatment", 
            "industrial-laser-cleaning"
        ])
        
        enhanced["keywords"] = list(enhanced_keywords)[:20]  # Limit for SEO
        
        # Enhance author information with comprehensive frontmatter data
        if author_obj:
            enhanced["author"] = {
                "@type": "Person",
                "name": author_obj.get("name", enhanced.get("author", {}).get("name", "")),
                "jobTitle": f"{author_obj.get('title', '')} in {author_obj.get('expertise', 'Laser Processing')}",
                "affiliation": {
                    "@type": "Organization",
                    "name": f"Advanced Materials Research Institute - {author_obj.get('country', 'International')}"
                },
                "knowsAbout": [
                    "Laser Materials Processing",
                    f"{material_name_title} Surface Engineering",
                    author_obj.get("expertise", "Industrial Laser Applications")
                ],
                "image": author_obj.get("image", ""),
                "nationality": author_obj.get("country", "")
            }
        
        # Enhance images with frontmatter data
        enhanced_images = []
        if images.get("hero"):
            enhanced_images.append({
                "@type": "ImageObject",
                "url": images["hero"].get("url", f"/images/{material_slug}-laser-cleaning-hero.jpg"),
                "name": f"{material_name_title} Laser Cleaning Before/After Comparison",
                "caption": images["hero"].get("alt", f"{material_name_title} surface undergoing laser cleaning"),
                "description": f"High-resolution demonstration of {material_name_title} component processed with {tech_specs.get('wavelength', '1064nm')} wavelength at {tech_specs.get('fluenceRange', 'optimized fluence')}, showing complete contamination removal while preserving material integrity",
                "width": 1200,
                "height": 800,
                "encodingFormat": "image/jpeg",
                "representativeOfPage": True
            })
        
        if images.get("micro"):
            enhanced_images.append({
                "@type": "ImageObject",
                "url": images["micro"].get("url", f"/images/{material_slug}-laser-cleaning-micro.jpg"),
                "name": f"{material_name_title} Surface Microstructure Analysis",
                "caption": images["micro"].get("alt", f"Microscopic view of {material_name_title} surface after laser cleaning"),
                "description": f"Scanning electron micrographs of {material_name_title} surface processed with {tech_specs.get('wavelength', '1064nm')} wavelength, verified at high magnification showing detailed surface structure",
                "width": 800,
                "height": 600,
                "encodingFormat": "image/jpeg"
            })
        
        if enhanced_images:
            enhanced["image"] = enhanced_images
        
        # Add comprehensive about section with material properties
        material_about = {
            "@type": "Material",
            "name": material_name_title,
            "identifier": frontmatter_data.get("chemicalProperties", {}).get("symbol", material_name_title),
            "category": frontmatter_data.get("category", "material"),
            "description": frontmatter_data.get("description", f"{material_name_title} for precision laser cleaning applications"),
            "additionalProperty": self._build_comprehensive_properties(frontmatter_data)
        }
        
        enhanced["about"] = [
            material_about,
            {
                "@type": "Process",
                "name": "Laser Cleaning",
                "description": f"Non-contact surface treatment process optimized for {material_name_title} materials"
            }
        ]
        
        # Add comprehensive HowTo with material-specific steps
        enhanced["mainEntity"] = {
            "@type": "HowTo",
            "name": f"How to Laser Clean {material_name_title}",
            "description": f"Step-by-step process for laser cleaning {material_name_title} materials using optimized parameters",
            "step": [
                {
                    "@type": "HowToStep",
                    "name": "Material Preparation",
                    "text": f"Secure {material_name_title} component in laser processing fixture ensuring stable positioning and adequate ventilation for {tech_specs.get('safetyClass', 'industrial safety')} operation."
                },
                {
                    "@type": "HowToStep", 
                    "name": "Parameter Configuration",
                    "text": f"Configure laser parameters: {tech_specs.get('wavelength', '1064nm')} wavelength, {tech_specs.get('fluenceRange', 'optimized fluence')}, {tech_specs.get('pulseDuration', 'nanosecond pulse duration')}, {tech_specs.get('repetitionRate', 'optimized repetition rate')}."
                },
                {
                    "@type": "HowToStep",
                    "name": "Surface Treatment", 
                    "text": f"Execute systematic scanning pattern with {tech_specs.get('spotSize', 'precision spot size')} maintaining consistent standoff distance for {material_name_title} processing."
                },
                {
                    "@type": "HowToStep",
                    "name": "Quality Verification",
                    "text": f"Inspect cleaned {material_name_title} surface using optical microscopy to verify contaminant removal and material integrity preservation."
                }
            ]
        }
        
        # Add mentions from applications
        mentions = []
        if applications_list:
            for app in applications_list:
                if app.get("industry"):
                    industry_words = app["industry"].lower().split()
                    mentions.extend(industry_words[:2])  # Take first 2 words per industry
        enhanced["mentions"] = list(set(mentions))[:10]  # Unique mentions, max 10
        
        # Add comprehensive technical specifications section if not present
        if tech_specs:
            enhanced["technicalSpecifications"] = {
                "@type": "PropertyValue",
                "name": "Laser Processing Parameters",
                "value": {
                    "wavelength": tech_specs.get("wavelength", ""),
                    "fluenceRange": tech_specs.get("fluenceRange", ""),
                    "powerRange": tech_specs.get("powerRange", ""),
                    "pulseDuration": tech_specs.get("pulseDuration", ""),
                    "repetitionRate": tech_specs.get("repetitionRate", ""),
                    "spotSize": tech_specs.get("spotSize", ""),
                    "safetyClass": tech_specs.get("safetyClass", "")
                }
            }
        
        # Add environmental impact data
        if env_impact:
            environmental_benefits = []
            for impact in env_impact:
                if impact.get("benefit") and impact.get("description"):
                    environmental_benefits.append({
                        "@type": "PropertyValue",
                        "name": impact["benefit"],
                        "description": impact["description"]
                    })
            if environmental_benefits:
                enhanced["environmentalBenefits"] = environmental_benefits
        
        # Add outcomes and performance metrics
        if outcomes:
            performance_metrics = []
            for outcome in outcomes:
                if outcome.get("result") and outcome.get("metric"):
                    performance_metrics.append({
                        "@type": "PropertyValue",
                        "name": outcome["result"],
                        "value": outcome["metric"]
                    })
            if performance_metrics:
                enhanced["performanceMetrics"] = performance_metrics
        
        # Add applications with detailed descriptions
        if applications_list:
            detailed_applications = []
            for app in applications_list:
                if app.get("industry") and app.get("detail"):
                    detailed_applications.append({
                        "@type": "PropertyValue",
                        "name": app["industry"],
                        "description": app["detail"]
                    })
            if detailed_applications:
                enhanced["applications"] = detailed_applications
        
        # Add composition if available
        if composition:
            enhanced["chemicalComposition"] = {
                "@type": "ChemicalSubstance",
                "name": f"{material_name_title} Composition",
                "description": ", ".join(composition)
            }
        
        # Remove unwanted fields
        enhanced.pop("publisher", None)
        
        return enhanced

    def _apply_standardized_naming(self, material_name_lower: str) -> str:
        """Apply naming standardization aligned with materials.yaml single source of truth"""
        # Basic kebab-case conversion
        slug = material_name_lower.replace(" ", "-")
        
        # Apply standardizations aligned with materials.yaml database
        naming_mappings = {
            # Hyphenation standardizations
            "terra-cotta": "terracotta",
            # Composite material naming (align with materials.yaml authority)
            "fiber-reinforced-polymer": "fiber-reinforced-polyurethane-frpu",
            "carbon-fiber-reinforced-polymer": "carbon-fiber-reinforced-polymer",
            "glass-fiber-reinforced-polymers": "glass-fiber-reinforced-polymers-gfrp",
            "metal-matrix-composites": "metal-matrix-composites-mmcs",
            "ceramic-matrix-composites": "ceramic-matrix-composites-cmcs",
            # Wood materials (remove any wood- prefix as materials.yaml defines them without prefix)
            "wood-oak": "oak",
            "wood-pine": "pine",
            "wood-maple": "maple",
            # Steel standardization (materials.yaml has Steel and Stainless Steel)
            "stainless-steel": "stainless-steel",
            "carbon-steel": "steel",  # Consolidate to main steel type per materials.yaml
            "galvanized-steel": "steel",
            "tool-steel": "steel",
            # Standardize common variants
            "aluminium": "aluminum",
        }
        
        # Apply standardization if material matches known mappings
        if slug in naming_mappings:
            slug = naming_mappings[slug]
            
        # Remove wood- prefix (wood materials are defined without prefix in materials.yaml)
        if slug.startswith("wood-"):
            slug = slug[5:]  # Remove "wood-" prefix
            
        return slug

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
                    
            # FAIL-FAST: Must have example structure for proper JSON-LD generation
            if not example_fields:
                raise Exception("Example JSON-LD structure not found - fail-fast architecture requires complete example template")
                
        except Exception as e:
            raise Exception(f"Failed to load example JSON-LD: {e} - fail-fast architecture requires valid example template")

        # Use example structure as template - prioritize frontmatter extraction
        jsonld_data = self._build_from_example(
            frontmatter_data, example_fields, material_name, self._material_data
        )

        # Format as YAML frontmatter structure
        jsonld_yaml_data = {
            "jsonld": jsonld_data
        }
        
        # Convert to YAML string with frontmatter delimiters
        yaml_content = yaml.dump(jsonld_yaml_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
        content = f"---\n{yaml_content.strip()}\n---"

        # Apply centralized version stamping
        return stamp_component_output("jsonld", content)

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
        """Build comprehensive JSON-LD using example structure and complete frontmatter data"""
        result = {}
        
        # Ensure material name is in title case
        material_name_title = material_name.title()
        
        # Apply standardized naming for URLs and image paths
        material_slug = self._apply_standardized_naming(material_name.lower())
        
        # Extract comprehensive technical data for maximum specificity
        tech_specs = frontmatter_data.get("technicalSpecifications", {})
        properties = frontmatter_data.get("properties", {})
        applications_list = frontmatter_data.get("applications", [])
        env_impact = frontmatter_data.get("environmentalImpact", [])
        author_obj = frontmatter_data.get("author_object", {})
        images = frontmatter_data.get("images", {})
        
        # Process each field in example structure with comprehensive frontmatter integration
        for key, example_value in example_structure.items():
            if key in ["@context", "@type"]:
                result[key] = example_value
            elif key == "headline":
                result[key] = f"{material_name_title} Laser Cleaning"
            elif key == "alternativeHeadline":
                # Create specific alternative headline using applications
                primary_industry = ""
                if applications_list and isinstance(applications_list, list) and applications_list[0].get("industry"):
                    primary_industry = f" for {applications_list[0]['industry']}"
                result[key] = f"Advanced Laser Ablation Techniques{primary_industry} using {material_name_title}"
            elif key == "description":
                # Enhanced description with specific frontmatter data
                category = frontmatter_data.get("category", "materials")
                wavelength = tech_specs.get("wavelength", "laser")
                result[key] = f"Comprehensive technical guide covering laser cleaning methodologies for {material_name_title} {category}, including {wavelength} wavelength optimization, industrial applications, and surface treatment benefits with detailed material properties."
            elif key == "abstract":
                # Highly specific abstract using comprehensive frontmatter data
                wavelength = tech_specs.get("wavelength", "1064nm")
                fluence = tech_specs.get("fluenceRange", "optimized fluence")
                power_range = tech_specs.get("powerRange", "controlled power")
                pulse_duration = tech_specs.get("pulseDuration", "nanosecond pulses")
                
                # Extract specific applications with industry context
                app_context = ""
                if applications_list and isinstance(applications_list, list):
                    industries = [app.get("industry", "") for app in applications_list[:2] if app.get("industry")]
                    if industries:
                        app_context = f" for {' and '.join(industries)}"
                
                # Include material properties for technical specificity
                density = properties.get("density", "")
                thermal = properties.get("thermalConductivity", "")
                prop_context = ""
                if density and thermal:
                    prop_context = f" Material properties: {density} density, {thermal} thermal conductivity."
                
                result[key] = f"Advanced laser cleaning techniques for {material_name_title} using {wavelength} wavelength at {fluence} with {pulse_duration} and {power_range}{app_context}.{prop_context}"
            elif key == "keywords":
                # Generate comprehensive keywords from all frontmatter data
                keywords = [
                    material_name.lower(),
                    f"{material_name.lower()} laser cleaning",
                    "laser ablation",
                    "non-contact cleaning",
                    "surface treatment"
                ]
                
                # Add category-specific keywords
                category = frontmatter_data.get("category", "")
                if category:
                    keywords.extend([f"{material_name.lower()} {category}", f"{category} laser processing"])
                
                # Add application industry keywords
                if applications_list:
                    for app in applications_list[:3]:
                        if app.get("industry"):
                            industry = app["industry"].lower().replace(" & ", "-").replace(" ", "-")
                            keywords.append(f"{industry}-laser-cleaning")
                
                # Add technical specification keywords
                if tech_specs.get("wavelength"):
                    wavelength = tech_specs["wavelength"].replace("nm", "").replace(" ", "")
                    keywords.append(f"{wavelength}-laser")
                
                # Add chemical/material keywords
                formula = frontmatter_data.get("chemicalProperties", {}).get("formula")
                if formula:
                    keywords.append(f"{formula}-laser-processing")
                
                # Add environmental keywords if applicable
                if env_impact:
                    keywords.extend(["eco-friendly-cleaning", "sustainable-processing"])
                
                result[key] = keywords[:20]  # Limit for SEO optimization
            elif key == "articleBody":
                # Use frontmatter description for articleBody
                result[key] = frontmatter_data.get("description", f"Technical overview of {material_name_title}, for laser cleaning applications, including optimal wavelength interaction, and industrial applications in surface preparation.")
            elif key == "wordCount":
                # Calculate actual word count from comprehensive articleBody
                article_body = result.get("articleBody", "")
                result[key] = len(article_body.split()) if article_body else 0
            elif key == "author":
                # Enhanced author information from frontmatter author_object
                if author_obj:
                    result[key] = {
                        "@type": "Person",
                        "name": author_obj.get("name", ""),
                        "jobTitle": f"{author_obj.get('title', '')} in {author_obj.get('expertise', 'Laser Processing')}",
                        "affiliation": {
                            "@type": "Organization",
                            "name": f"Advanced Materials Research Institute - {author_obj.get('country', 'International')}"
                        },
                        "knowsAbout": [
                            "Laser Materials Processing",
                            f"{material_name_title} Surface Engineering",
                            author_obj.get("expertise", "Industrial Laser Applications")
                        ],
                        "image": author_obj.get("image", ""),
                        "nationality": author_obj.get("country", "")
                    }
                else:
                    # FAIL-FAST: Author information must be provided
                    raise ValueError(f"Author information not found in frontmatter for {material_slug} - fail-fast architecture requires complete data")
            elif key == "image":
                # Enhanced image array using frontmatter images data with absolute URLs
                result[key] = []
                
                # Hero image from frontmatter with absolute URL
                if images.get("hero"):
                    hero_img = {
                        "@type": "ImageObject",
                        "url": f"https://z-beam.com{images['hero']['url']}",
                        "name": f"{material_name_title} Laser Cleaning Before/After Comparison",
                        "caption": images["hero"]["alt"],
                        "description": f"High-resolution demonstration of {material_name_title} component processed with {tech_specs['wavelength']} wavelength at {tech_specs['fluenceRange']}, showing complete contamination removal while preserving material integrity",
                        "width": 1200,
                        "height": 800,
                        "encodingFormat": "image/jpeg",
                        "representativeOfPage": True
                    }
                    result[key].append(hero_img)
                
                # Microscopic image from frontmatter with absolute URL
                if images.get("micro"):
                    micro_img = {
                        "@type": "ImageObject",
                        "url": f"https://z-beam.com{images['micro'].get('url', f'/images/{material_slug}-laser-cleaning-micro.jpg')}",
                        "name": f"{material_name_title} Surface Microstructure Analysis",
                        "caption": images["micro"].get("alt", f"Microscopic view of {material_name_title} surface after laser cleaning"),
                        "description": f"Scanning electron micrographs of {material_name_title} surface processed with {tech_specs.get('wavelength', '1064nm')} wavelength, verified at high magnification showing detailed surface structure",
                        "width": 800,
                        "height": 600,
                        "encodingFormat": "image/jpeg"
                    }
                    result[key].append(micro_img)
                
                # If no frontmatter images, use standardized naming with absolute URLs
                if not result[key]:
                    result[key] = [{
                        "@type": "ImageObject",
                        "url": f"https://z-beam.com/images/{material_slug}-laser-cleaning-hero.jpg",
                        "name": f"{material_name_title} Laser Cleaning Process",
                        "caption": f"{material_name_title} surface laser cleaning demonstration",
                        "width": 1200,
                        "height": 800
                    }]
            elif key == "about":
                # Enhanced about section with comprehensive material data
                material_about = {
                    "@type": "Material",
                    "name": material_name_title,
                    "alternateName": [],
                    "identifier": frontmatter_data.get("chemicalProperties", {}).get("symbol", material_name_title),
                    "category": frontmatter_data.get("category", "material"),
                    "description": frontmatter_data.get("description", f"{material_name_title} for precision laser cleaning applications"),
                    "additionalProperty": self._build_comprehensive_properties(frontmatter_data)
                }
                
                # Add chemical formula if available
                formula = frontmatter_data.get("chemicalProperties", {}).get("formula")
                if formula and formula != material_name_title:
                    material_about["alternateName"].append(formula)
                
                # Add chemical symbol as alternate name (avoid duplicates)
                symbol = frontmatter_data.get("chemicalProperties", {}).get("symbol")
                if symbol and symbol != material_name_title and symbol not in material_about["alternateName"]:
                    material_about["alternateName"].append(symbol)
                
                result[key] = [
                    material_about,
                    {
                        "@type": "Process",
                        "name": "Laser Cleaning",
                        "description": f"Non-contact surface treatment process optimized for {material_name_title} materials"
                    }
                ]
            elif key == "mainEntity":
                # Enhanced HowTo with material-specific steps
                result[key] = {
                    "@type": "HowTo",
                    "name": f"How to Laser Clean {material_name_title}",
                    "description": f"Step-by-step process for laser cleaning {material_name_title} materials using optimized parameters",
                    "step": [
                        {
                            "@type": "HowToStep",
                            "name": "Material Preparation",
                            "text": f"Secure {material_name_title} component in laser processing fixture ensuring stable positioning and adequate ventilation for {tech_specs.get('safetyClass', 'industrial safety')} operation."
                        },
                        {
                            "@type": "HowToStep", 
                            "name": "Parameter Configuration",
                            "text": f"Configure laser parameters: {tech_specs.get('wavelength', '1064nm')} wavelength, {tech_specs.get('fluenceRange', 'optimized fluence')}, {tech_specs.get('pulseDuration', 'nanosecond pulse duration')}, {tech_specs.get('repetitionRate', 'optimized repetition rate')}."
                        },
                        {
                            "@type": "HowToStep",
                            "name": "Surface Treatment", 
                            "text": f"Execute systematic scanning pattern with {tech_specs.get('spotSize', 'precision spot size')} maintaining consistent standoff distance for {material_name_title} processing."
                        },
                        {
                            "@type": "HowToStep",
                            "name": "Quality Verification",
                            "text": f"Inspect cleaned {material_name_title} surface using optical microscopy to verify contaminant removal and material integrity preservation."
                        }
                    ]
                }
            elif key == "mentions":
                # Extract mentions from applications industries
                mentions = []
                if applications_list:
                    for app in applications_list:
                        if app.get("industry"):
                            industry_words = app["industry"].lower().split()
                            mentions.extend(industry_words[:2])  # Take first 2 words per industry
                result[key] = list(set(mentions))[:10]  # Unique mentions, max 10
            elif key == "copyrightHolder":
                # Always use Z-Beam as copyright holder with complete org info
                result[key] = {
                    "@type": "Organization",
                    "name": "Z-Beam",
                    "url": "https://z-beam.com",
                    "logo": {
                        "@type": "ImageObject",
                        "url": "https://www.z-beam.com/images/site/logo/logo_.png"
                    },
                    "sameAs": [
                        "https://www.linkedin.com/company/z-beam"
                    ]
                }
            elif key == "publisher":
                # Add required publisher field for Schema.org Article compliance
                result[key] = {
                    "@type": "Organization", 
                    "name": "Z-Beam",
                    "url": "https://z-beam.com",
                    "logo": {
                        "@type": "ImageObject",
                        "url": "https://www.z-beam.com/images/site/logo/logo_.png"
                    },
                    "sameAs": [
                        "https://www.linkedin.com/company/z-beam"
                    ]
                }
            elif key in ["datePublished", "dateModified"]:
                # Use current date for compliance
                from datetime import datetime
                current_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                result[key] = current_date
            elif key == "isPartOf":
                # Use Z-Beam website with material-specific URL
                result[key] = {
                    "@type": "WebSite",
                    "name": "Z-Beam Laser Processing Guide",
                    "url": f"https://z-beam.com/{material_slug}-laser-cleaning"
                }
            elif key == "breadcrumb":
                # Create proper breadcrumb structure
                category = frontmatter_data.get("category", "materials")
                result[key] = {
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {
                            "@type": "ListItem",
                            "position": 1,
                            "name": "Materials",
                            "item": "https://z-beam.com/materials"
                        },
                        {
                            "@type": "ListItem", 
                            "position": 2,
                            "name": category.title(),
                            "item": f"https://z-beam.com/materials/{category}"
                        },
                        {
                            "@type": "ListItem",
                            "position": 3,
                            "name": material_name_title,
                            "item": f"https://z-beam.com/{material_slug}-laser-cleaning"
                        }
                    ]
                }
            elif key == "potentialAction":
                # Create proper ReadAction
                result[key] = {
                    "@type": "ReadAction",
                    "target": f"https://z-beam.com/{material_slug}-laser-cleaning"
                }
            elif isinstance(example_value, dict):
                result[key] = self._build_nested_structure(
                    frontmatter_data, example_value, key, self._author_info, material_name_title, material_slug
                )
            elif isinstance(example_value, list):
                result[key] = example_value  # Keep example arrays as-is for other fields
            else:
                # For simple fields, try to extract from frontmatter or use example
                try:
                    result[key] = self._get_field(frontmatter_data, [key])
                except Exception:
                    result[key] = example_value

        # Add required publisher field for Schema.org Article compliance (not in example)
        if "publisher" not in result:
            result["publisher"] = {
                "@type": "Organization", 
                "name": "Z-Beam",
                "url": "https://z-beam.com",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://www.z-beam.com/images/site/logo/logo_.png"
                },
                "sameAs": [
                    "https://www.linkedin.com/company/z-beam"
                ]
            }

        return result

    def _build_from_schema(
        self, frontmatter_data: Dict, schema_structure: Dict, material_name: str
    ) -> Dict:
        """Build JSON-LD using schema structure"""
        # Ensure material name is in title case
        material_name_title = material_name.title()
        
        jsonld = {
            "@context": "https://schema.org",
            "@type": "Material",
            "name": f"{material_name_title} Laser Cleaning Guide",
            "description": self._get_field(
                frontmatter_data,
                ["description"]
            ),  # Must exist - no fallbacks
            "category": self._get_field(
                frontmatter_data, ["category", "type"]
            ),  # Must exist - no fallbacks
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
        material_name_title: str = None,
        material_slug: str = None,
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
            elif key == "url":
                if parent_key == "author":
                    if author_info and "url" in author_info:
                        result[key] = author_info["url"]
                    else:
                        result[key] = "https://z-beam.com"
                elif parent_key == "logo":
                    # Set specific logo URL
                    result[key] = "https://www.z-beam.com/images/site/logo/logo_.png"
                elif material_slug:
                    # Use standardized material slug for URLs
                    result[key] = f"https://z-beam.com/{material_slug}-laser-cleaning"
                else:
                    result[key] = example_value
            elif key == "@id" and material_slug:
                # Use standardized material slug for @id fields
                result[key] = f"https://z-beam.com/{material_slug}-laser-cleaning"
            elif key == "sameAs" and isinstance(example_value, list):
                # Handle sameAs arrays with correct LinkedIn URLs
                result[key] = []
                for item in example_value:
                    if "linkedin.com" in str(item):
                        result[key].append("https://www.linkedin.com/company/z-beam")
                    else:
                        result[key].append(item)
            elif key == "name" and parent_key in ["copyrightHolder", "isPartOf"]:
                # Always use Z-Beam for organization names
                result[key] = "Z-Beam" if parent_key == "copyrightHolder" else "Z-Beam Laser Processing Guide"
            elif isinstance(example_value, str) and material_name_title and "Aluminum" in example_value:
                # Replace placeholder material name with actual material name
                result[key] = example_value.replace("Aluminum", material_name_title)
            elif isinstance(example_value, str) and "Z-Beam" not in example_value and parent_key in ["copyrightHolder", "isPartOf"] and "name" in key.lower():
                # Ensure organization names use Z-Beam
                result[key] = "Z-Beam"
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

    def _build_comprehensive_properties(self, frontmatter_data: Dict) -> list:
        """Build comprehensive properties array from all available frontmatter data"""
        properties = []
        
        # Extract all property sections
        props = frontmatter_data.get("properties", {})
        tech_specs = frontmatter_data.get("technicalSpecifications", {})
        chem_props = frontmatter_data.get("chemicalProperties", {})
        
        # Physical and mechanical properties with Schema.org compliant naming
        property_mappings = {
            # Basic physical properties
            "Density": ["density"],
            "Melting Point": ["meltingPoint", "meltingMax"], 
            "Thermal Conductivity": ["thermalConductivity"],
            "Thermal Diffusivity Range": ["thermalDiffusivityMin", "thermalDiffusivityMax"],
            "Thermal Expansion Range": ["thermalExpansionMin", "thermalExpansionMax"],
            "Specific Heat Range": ["specificHeatMin", "specificHeatMax"],
            
            # Mechanical properties
            "Tensile Strength": ["tensileStrength", "tensileMax"],
            "Young's Modulus": ["youngsModulus", "modulusMax"],
            "Hardness": ["hardness", "hardnessMax"],
            
            # Laser-specific properties with proper naming
            "Laser Absorption Range": ["laserAbsorptionMin", "laserAbsorptionMax"],
            "Laser Reflectivity Range": ["laserReflectivityMin", "laserReflectivityMax"],
            
            # Chemical properties
            "Chemical Formula": ["formula"],
            "Material Type": ["materialType"],
            "Chemical Symbol": ["symbol"],
            "Decomposition Point": ["decompositionPoint"],
        }
        
        # Technical laser specifications with proper Schema.org naming
        tech_mappings = {
            "Laser Wavelength": ["wavelength"],
            "Laser Fluence Range": ["fluenceRange"], 
            "Laser Power Range": ["powerRange"],
            "Laser Pulse Duration": ["pulseDuration"],
            "Laser Repetition Rate": ["repetitionRate"],
            "Laser Spot Size": ["spotSize"],
            "Laser Safety Class": ["safetyClass"],
        }
        
        # Add physical/mechanical properties with proper Schema.org naming
        for prop_name, field_names in property_mappings.items():
            for field in field_names:
                value = props.get(field) or chem_props.get(field)
                if value and str(value).strip():
                    # Format ranges for min/max properties
                    if len(field_names) == 2 and ("Min" in field_names[0] or "Max" in field_names[0]):
                        min_field, max_field = field_names
                        min_val = props.get(min_field) or chem_props.get(min_field)
                        max_val = props.get(max_field) or chem_props.get(max_field)
                        if min_val and max_val:
                            value = f"{min_val} - {max_val}"
                            # Remove "Range" suffix if present for cleaner display
                            display_name = prop_name.replace(" Range", "")
                            properties.append({
                                "@type": "PropertyValue",
                                "name": display_name,
                                "value": str(value)
                            })
                        elif min_val:
                            properties.append({
                                "@type": "PropertyValue", 
                                "name": prop_name.replace(" Range", ""),
                                "value": str(min_val)
                            })
                        elif max_val:
                            properties.append({
                                "@type": "PropertyValue",
                                "name": prop_name.replace(" Range", ""),
                                "value": str(max_val)
                            })
                        break  # Skip processing other fields for this property
                    else:
                        # Single value property
                        properties.append({
                            "@type": "PropertyValue",
                            "name": prop_name,
                            "value": str(value)
                        })
                        break  # Use first available value
        
        # Add technical laser specifications
        for tech_name, field_names in tech_mappings.items():
            for field in field_names:
                value = tech_specs.get(field)
                if value and str(value).strip():
                    properties.append({
                        "@type": "PropertyValue",
                        "name": tech_name,
                        "value": str(value)
                    })
                    break
        
        # Add composition as property
        composition = frontmatter_data.get("composition", [])
        if composition and isinstance(composition, list):
            properties.append({
                "@type": "PropertyValue",
                "name": "Chemical Composition",
                "value": ", ".join(composition)
            })
        
        # Add compatibility
        compatibility = frontmatter_data.get("compatibility", [])
        if compatibility and isinstance(compatibility, list):
            properties.append({
                "@type": "PropertyValue",
                "name": "Material Compatibility",
                "value": ", ".join(compatibility)
            })
        
        # Add regulatory standards
        regulatory = frontmatter_data.get("regulatoryStandards")
        if regulatory:
            properties.append({
                "@type": "PropertyValue",
                "name": "Regulatory Standards",
                "value": str(regulatory)
            })
        
        return properties

    def _build_properties_array(
        self, frontmatter_data: Dict, example_array: list, material_data: Dict
    ) -> list:
        """Build highly specific properties array from comprehensive frontmatter data"""
        if not example_array:
            raise Exception("Example array is empty - fail-fast architecture requires complete example structure")

        properties = []
        
        # Extract comprehensive material properties for maximum specificity
        material_properties = {
            # Physical properties with specific values
            "Density": self._get_field_safe(frontmatter_data, ["properties.density"], ""),
            "Melting Point": self._get_field_safe(frontmatter_data, ["properties.meltingPoint"], ""),
            "Thermal Conductivity": self._get_field_safe(frontmatter_data, ["properties.thermalConductivity"], ""),
            "Tensile Strength": self._get_field_safe(frontmatter_data, ["properties.tensileStrength"], ""),
            "Hardness": self._get_field_safe(frontmatter_data, ["properties.hardness"], ""),
            "Young's Modulus": self._get_field_safe(frontmatter_data, ["properties.youngsModulus"], ""),
            
            # Laser-specific properties for maximum differentiation
            "Laser Wavelength": self._get_field_safe(frontmatter_data, ["technicalSpecifications.wavelength", "properties.wavelength"], ""),
            "Fluence Range": self._get_field_safe(frontmatter_data, ["technicalSpecifications.fluenceRange", "properties.fluenceRange"], ""),
            "Power Range": self._get_field_safe(frontmatter_data, ["technicalSpecifications.powerRange"], ""),
            "Pulse Duration": self._get_field_safe(frontmatter_data, ["technicalSpecifications.pulseDuration"], ""),
            "Spot Size": self._get_field_safe(frontmatter_data, ["technicalSpecifications.spotSize"], ""),
            "Repetition Rate": self._get_field_safe(frontmatter_data, ["technicalSpecifications.repetitionRate"], ""),
            "Safety Class": self._get_field_safe(frontmatter_data, ["technicalSpecifications.safetyClass"], ""),
            
            # Chemical properties for specificity
            "Chemical Formula": self._get_field_safe(frontmatter_data, ["chemicalProperties.formula", "properties.chemicalFormula"], ""),
            "Chemical Symbol": self._get_field_safe(frontmatter_data, ["chemicalProperties.symbol"], ""),
            "Material Type": self._get_field_safe(frontmatter_data, ["chemicalProperties.materialType", "category"], ""),
        }
        
        # Add thermal properties for laser interaction specificity with proper naming
        thermal_properties = {
            "Thermal Diffusivity Range": ["thermalDiffusivityMin", "thermalDiffusivityMax"],
            "Thermal Expansion Range": ["thermalExpansionMin", "thermalExpansionMax"], 
            "Specific Heat Range": ["specificHeatMin", "specificHeatMax"],
        }
        
        for prop_name, field_names in thermal_properties.items():
            for field in field_names:
                if field in props:
                    value = props.get(field)
                    if value and str(value).strip():
                        # Format ranges for min/max properties  
                        if len(field_names) == 2:
                            min_field, max_field = field_names
                            min_val = props.get(min_field)
                            max_val = props.get(max_field)
                            if min_val and max_val:
                                value = f"{min_val} - {max_val}"
                            elif min_val:
                                value = str(min_val)
                            elif max_val:
                                value = str(max_val)
                            else:
                                continue
                        
                        properties.append({
                            "@type": "PropertyValue",
                            "name": prop_name,
                            "value": str(value)
                        })
                        break  # Use first available value
        
        # Add laser absorption properties for maximum technical specificity with proper naming
        laser_properties = {
            "Laser Absorption Range": ["laserAbsorptionMin", "laserAbsorptionMax"],
            "Laser Reflectivity Range": ["laserReflectivityMin", "laserReflectivityMax"],
        }
        
        for prop_name, field_names in laser_properties.items():
            for field in field_names:
                if field in props:
                    value = props.get(field)
                    if value and str(value).strip():
                        # Format ranges for min/max properties
                        if len(field_names) == 2:
                            min_field, max_field = field_names
                            min_val = props.get(min_field)
                            max_val = props.get(max_field)
                            if min_val and max_val:
                                value = f"{min_val} - {max_val}"
                            elif min_val:
                                value = str(min_val)
                            elif max_val:
                                value = str(max_val)
                            else:
                                continue
                        
                        properties.append({
                            "@type": "PropertyValue",
                            "name": prop_name,
                            "value": str(value)
                        })
                        break  # Use first available value
        
        # Add composition as a special property if available
        composition = frontmatter_data.get("composition", [])
        if composition and isinstance(composition, list):
            composition_text = ", ".join(composition)
            properties.append({
                "@type": "PropertyValue", 
                "name": "Chemical Composition",
                "value": composition_text
            })
        
        # Add compatibility information for industrial context
        compatibility = frontmatter_data.get("compatibility", [])
        if compatibility and isinstance(compatibility, list):
            compatibility_text = ", ".join(compatibility)
            properties.append({
                "@type": "PropertyValue",
                "name": "Material Compatibility", 
                "value": compatibility_text
            })
        
        # Add regulatory standards for compliance specificity
        regulatory = self._get_field_safe(frontmatter_data, ["regulatoryStandards"], "")
        if regulatory:
            properties.append({
                "@type": "PropertyValue",
                "name": "Regulatory Standards",
                "value": regulatory
            })
        
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
