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
                content = api_response.content
                logger.info(f"Generated tags for {material_name}")

                # Apply centralized version stamping (will prepend to any existing legacy stamps)
                from versioning import stamp_component_output

                final_content = stamp_component_output("tags", content)

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
    def _create_template_vars(
        self,
        material_name: str,
        material_data: Dict,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> Dict:
        """Create template variables for tags generation"""
        return {
            "material_name": material_name,
            "material_category": material_data.get("category", "material"),
            "material_formula": material_data.get("formula", ""),
            "material_symbol": material_data.get("symbol", ""),
            "author_name": author_info.get("name", "Expert") if author_info else "Expert",
            "author_country": author_info.get("country", "Unknown") if author_info else "Unknown",
        }

    def _build_api_prompt(self, template_vars: Dict, frontmatter_data: Optional[Dict] = None) -> str:
        """Build API prompt for tags generation"""
        material_name = template_vars["material_name"]
        
        prompt = f"""Generate navigation tags for {material_name} laser cleaning.

Output EXACTLY 8 tags as a comma-separated list like this example:
ablation, fused-silica, sio2, cleaning, laser, aerospace, non-contact, yi-chun-lin

REQUIREMENTS:
- Output exactly 8 tags
- Use single words or hyphenated terms only
- Include material name (use {material_name})
- Include "ablation", "cleaning", "laser"
- Include 1-2 industry applications (aerospace, automotive, manufacturing, electronics, etc.)
- Include "non-contact"
- Include 1 author slug using {template_vars.get('author_name', 'expert')} (already in lowercase hyphenated format)
- Make tags relevant to {material_name} laser cleaning
- Use lowercase throughout
- Output ONLY the comma-separated list, no other text"""

        return prompt
