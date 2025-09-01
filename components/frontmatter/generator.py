#!/usr/bin/env python3
"""
Frontmatter Component Generator

Generates frontmatter YAML content with property enhancement.
"""

import logging
from typing import Dict, Optional
from generators.component_generators import APIComponentGenerator, ComponentResult

logger = logging.getLogger(__name__)

class FrontmatterComponentGenerator(APIComponentGenerator):
    """API-based generator for frontmatter components"""
    
    def __init__(self):
        super().__init__("frontmatter")
    
    def generate(self, material_name: str, material_data: Dict,
                api_client=None, author_info: Optional[Dict] = None,
                frontmatter_data: Optional[Dict] = None,
                schema_fields: Optional[Dict] = None) -> ComponentResult:
        """Generate frontmatter using API"""
        try:
            if not api_client:
                logger.error("API client is required for frontmatter generation")
                return ComponentResult(
                    component_type="frontmatter",
                    content="",
                    success=False,
                    error_message="API client not provided"
                )
            
            # Create template variables
            template_vars = self._create_template_vars(
                material_name, material_data, author_info, 
                frontmatter_data, schema_fields
            )
            
            # Build API prompt
            prompt = self._build_api_prompt(template_vars, frontmatter_data)
            
            # Call API
            api_response = api_client.generate_content(prompt)
            
            if api_response.get('success'):
                content = api_response.get('content', '')
                
                # Post-process the content with property enhancement
                enhanced_content = self._post_process_content(content, material_name, material_data)
                
                logger.info(f"Generated frontmatter for {material_name}")
                
                return ComponentResult(
                    component_type="frontmatter",
                    content=enhanced_content,
                    success=True
                )
            else:
                error_msg = api_response.get('error', 'API call failed')
                logger.error(f"API error for frontmatter generation: {error_msg}")
                return ComponentResult(
                    component_type="frontmatter",
                    content="",
                    success=False,
                    error_message=error_msg
                )
                
        except Exception as e:
            logger.error(f"Error generating frontmatter for {material_name}: {e}")
            return ComponentResult(
                component_type="frontmatter",
                content="",
                success=False,
                error_message=str(e)
            )
    
    def _post_process_content(self, content: str, material_name: str, material_data: Dict) -> str:
        """Post-process frontmatter content with property enhancement"""
        try:
            # Try to use the property enhancer if available
            from utils.property_enhancer import enhance_generated_frontmatter
            category = material_data.get('category', '')
            enhanced_content = enhance_generated_frontmatter(content, category)
            logger.info(f"Enhanced frontmatter for {material_name} with property context")
            return enhanced_content
        except Exception as e:
            logger.warning(f"Failed to enhance frontmatter for {material_name}: {e}")
            return content
