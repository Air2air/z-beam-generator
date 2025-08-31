#!/usr/bin/env python3
"""
Frontmatter Component Generator

Generates frontmatter YAML content with property enhancement and percentile calculations.
"""

import logging
from typing import Dict, Optional
from generators.component_generators import APIComponentGenerator, ComponentResult

logger = logging.getLogger(__name__)

class FrontmatterComponentGenerator(APIComponentGenerator):
    """Generator for frontmatter components with enhanced property processing"""
    
    def __init__(self):
        super().__init__("frontmatter")
    
    def _post_process_content(self, content: str, material_name: str, material_data: Dict) -> str:
        """Post-process frontmatter content with property enhancement and percentiles"""
        try:
            from utils.property_enhancer import enhance_generated_frontmatter
            category = material_data.get('category', '')
            enhanced_content = enhance_generated_frontmatter(content, category)
            logger.info(f"Enhanced frontmatter for {material_name} with property context and percentiles")
            return enhanced_content
        except Exception as e:
            logger.warning(f"Failed to enhance frontmatter for {material_name}: {e}")
            return content
    
    def generate(self, material_name: str, material_data: Dict, 
                api_client=None, author_info: Optional[Dict] = None,
                frontmatter_data: Optional[Dict] = None,
                schema_fields: Optional[Dict] = None) -> ComponentResult:
        """Generate frontmatter component with special processing"""
        
        # Use the parent class generation
        result = super().generate(material_name, material_data, api_client, author_info, frontmatter_data, schema_fields)
        
        # Log the enhancement process
        if result.success:
            logger.info(f"Successfully generated enhanced frontmatter for {material_name}")
        
        return result

def create_frontmatter_generator():
    """Factory function to create a frontmatter generator"""
    return FrontmatterComponentGenerator()
