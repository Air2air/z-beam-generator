#!/usr/bin/env python3
"""
Tags Generator - API-based tags generation for laser cleaning materials.
"""

import logging
from typing import Dict, Optional, Any

from generators.component_generators import APIComponentGenerator, ComponentResult

logger = logging.getLogger(__name__)


class TagsComponentGenerator(APIComponentGenerator):
    """API-based generator for tags components"""

    def __init__(self):
        super().__init__("tags")

    def get_component_info(self) -> Dict[str, Any]:
        """Get component information"""
        return {
            "name": "tags",
            "description": "Navigation tags generation for laser cleaning articles",
            "version": "2.0.0",
            "requires_api": True,
            "type": "dynamic",
        }

    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> ComponentResult:
        """Generate tags using API"""
        try:
            if not api_client:
                logger.error("API client is required for tags generation")
                return ComponentResult(
                    component_type="tags",
                    content="",
                    success=False,
                    error_message="API client not provided",
                )

            # Create template variables
            template_vars = self._create_template_vars(
                material_name,
                material_data,
                author_info,
                frontmatter_data,
                schema_fields,
            )

            # Build API prompt
            prompt = self._build_api_prompt(template_vars, frontmatter_data)

            # Call API
            api_response = api_client.generate_simple(prompt)

            # Handle APIResponse object
            if api_response.success:
                content = api_response.content.strip()
                logger.info(f"Generated tags for {material_name}")

                # Convert comma-separated tags to list and filter out excluded terms
                tags_list = [tag.strip() for tag in content.split(',') if tag.strip()]
                
                # Filter out excluded terms
                material_name_lower = material_name.lower()
                material_formula = template_vars["material_formula"].lower()
                
                excluded_terms = {
                    "laser", "cleaning", "non-contact", "ablation", "beam", "photon", "wavelength",
                    "nm", "micron", "µm", "mm", "energy", "joule", "watt", "power", "frequency",
                    "hz", "khz", "mhz", "pulse", "cw", "continuous", "wave", "radiation", "light",
                    "optics", "optical", "surface-treatment", "expert", material_name_lower
                }
                
                if material_formula:
                    excluded_terms.add(material_formula)
                
                # Filter tags
                filtered_tags = [tag for tag in tags_list if tag.lower() not in excluded_terms]
                
                # Ensure we have 8 tags - if filtered too many, pad with category terms
                if len(filtered_tags) < 8:
                    padding_tags = ["manufacturing", "industrial", "decontamination", "restoration", "texturing", "polishing"]
                    for pad_tag in padding_tags:
                        if len(filtered_tags) >= 8:
                            break
                        if pad_tag not in [t.lower() for t in filtered_tags]:
                            filtered_tags.append(pad_tag)
                
                # Take only first 8 tags
                final_tags = filtered_tags[:8]
                
                # Create structured YAML output without HTML comments for clean format
                yaml_content = self._format_as_yaml(material_name, final_tags, template_vars)
                
                # For YAML format, use simpler versioning without HTML comments
                from datetime import datetime
                version_info = f"""---
Material: "{material_name.lower()}"
Component: tags
Generated: {datetime.now().isoformat()}
Generator: Z-Beam v1.0.0
Format: YAML v2.0
---"""
                
                final_content = f"{yaml_content}\n\n{version_info}"

                return ComponentResult(
                    component_type="tags", content=final_content, success=True
                )
            else:
                error_msg = api_response.error or "API call failed"
                logger.error(f"API error for tags generation: {error_msg}")
                return ComponentResult(
                    component_type="tags",
                    content="",
                    success=False,
                    error_message=error_msg,
                )

        except Exception as e:
            logger.error(f"Error generating tags for {material_name}: {e}")
            return ComponentResult(
                component_type="tags",
                content="",
                success=False,
                error_message=str(e),
            )

    def _format_as_yaml(self, material_name: str, tags_list: list, template_vars: Dict) -> str:
        """Format tags as structured YAML for Next.js consumption"""
        from datetime import datetime
        
        # Categorize tags
        material_tags = []
        industry_tags = []
        process_tags = []
        author_tags = []
        other_tags = []
        
        # Known categories for classification
        industries = {'aerospace', 'automotive', 'manufacturing', 'electronics', 'marine', 'medical', 'industrial'}
        processes = {'decoating', 'decontamination', 'restoration', 'polishing', 'texturing', 'etching', 'passivation', 'anodizing'}
        
        material_name_lower = material_name.lower()
        material_formula = template_vars["material_formula"].lower()
        
        for tag in tags_list:
            tag_clean = tag.strip().lower()
            # Since we exclude material names now, this section won't match
            if tag_clean in industries:
                industry_tags.append(tag_clean)
            elif tag_clean in processes:
                process_tags.append(tag_clean)
            elif '-' in tag_clean and len(tag_clean.split('-')) == 2:  # Likely author name
                author_tags.append(tag_clean)
            else:
                other_tags.append(tag_clean)
        
        # Format as proper YAML
        yaml_content = "tags:\n"
        for tag in tags_list:
            yaml_content += f"  - {tag.strip()}\n"
        
        yaml_content += f"material: \"{material_name.lower()}\"\n"
        yaml_content += f"count: {len(tags_list)}\n"
        yaml_content += "categories:\n"
        
        yaml_content += "  industry:\n"
        for tag in industry_tags:
            yaml_content += f"    - {tag}\n"
        
        yaml_content += "  process:\n"
        for tag in process_tags:
            yaml_content += f"    - {tag}\n"
        
        yaml_content += "  author:\n"
        for tag in author_tags:
            yaml_content += f"    - {tag}\n"
        
        yaml_content += "  other:\n"
        for tag in other_tags:
            yaml_content += f"    - {tag}\n"
        
        yaml_content += "metadata:\n"
        yaml_content += f"  generated: \"{datetime.now().isoformat()}\"\n"
        yaml_content += "  format: \"yaml\"\n"
        yaml_content += "  version: \"2.0\""
        
        return yaml_content

    def _create_template_vars(
        self,
        material_name: str,
        material_data: Dict,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> Dict:
        """Create template variables for tags generation"""
        # FAIL-FAST: Validate required material data
        if not material_data.get("category"):
            raise ValueError(f"Material category not found for {material_name} - fail-fast architecture requires complete data")
        if not material_data.get("formula"):
            raise ValueError(f"Material formula not found for {material_name} - fail-fast architecture requires complete data")
        if not material_data.get("symbol"):
            raise ValueError(f"Material symbol not found for {material_name} - fail-fast architecture requires complete data")
        if not author_info or not author_info.get("name"):
            raise ValueError(f"Author name not found for {material_name} - fail-fast architecture requires complete data")
        if not author_info.get("country"):
            raise ValueError(f"Author country not found for {material_name} - fail-fast architecture requires complete data")

        return {
            "material_name": material_name,
            "material_category": material_data["category"],
            "material_formula": material_data["formula"],
            "material_symbol": material_data["symbol"],
            "author_name": author_info["name"],
            "author_country": author_info["country"],
        }

    def _build_api_prompt(self, template_vars: Dict, frontmatter_data: Optional[Dict] = None) -> str:
        """Build API prompt for tags generation"""
        material_name = template_vars["material_name"]
        material_formula = template_vars["material_formula"]
        material_category = template_vars["material_category"]
        
        prompt = f"""Generate navigation tags for {material_name} surface treatment.

Output EXACTLY 12 tags as a comma-separated list like this example:
aerospace, automotive, manufacturing, electronics, anodizing, passivation, decoating, restoration, polishing, texturing, metal, industrial

REQUIREMENTS:
- Output exactly 12 tags (we will filter to final 8)
- Use single words or hyphenated terms only"""
        
        # Add formula if available
        if material_formula:
            prompt += f"\n- Include chemical formula or symbol ({material_formula.lower()})"
        
        # Build exclusion list
        exclusions = [
            "laser", "cleaning", "non-contact", "ablation", "beam", "photon", "wavelength", 
            "nm", "micron", "µm", "mm", "energy", "joule", "watt", "power", "frequency", 
            "hz", "khz", "mhz", "pulse", "cw", "continuous", "wave", "radiation", "light", 
            "optics", "optical", "surface-treatment", "expert", material_name.lower()
        ]
        
        # Add chemical formula to exclusions if present
        if material_formula:
            exclusions.append(material_formula.lower())
        
        exclusion_text = ", ".join(exclusions)
        
        prompt += f"""
- Include 2-3 industry applications (aerospace, automotive, manufacturing, electronics, marine, medical, etc.)
- Include relevant process terms (decoating, decontamination, restoration, etching, passivation, polishing, texturing, etc.)
- Include material category terms (metal, polymer, ceramic, composite, etc.) if relevant
- Include 1 author slug: {template_vars['author_name'].lower().replace(' ', '-')}
- Make tags specific and valuable for {material_name} applications
- Use lowercase throughout
- DO NOT INCLUDE any of these terms: {exclusion_text}
- DO NOT use the material name '{material_name.lower()}' as a tag
- Focus on applications, processes, and industries, NOT the material itself
- Output ONLY the comma-separated list, no other text"""

        return prompt
