#!/usr/bin/env python3
"""
Frontmatter-Integrated Caption Generator
Modified version of the caption generator that returns structured data
for direct integration into frontmatter files instead of YAML strings.
"""

import sys
import datetime
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Add the project root to the Python path
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root))

from components.caption.generators.generator import CaptionComponentGenerator
from generators.component_generators import ComponentResult

logger = logging.getLogger(__name__)

class FrontmatterCaptionGenerator(CaptionComponentGenerator):
    """
    Caption generator that returns structured data for frontmatter integration.
    Inherits all the AI generation logic but returns data instead of YAML.
    """
    
    def generate_for_frontmatter(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> ComponentResult:
        """
        Generate caption data for frontmatter integration.
        Returns structured data instead of YAML string.
        """
        
        # FAIL FAST: API client is required - no fallbacks allowed
        if not api_client:
            raise ValueError("API client required for caption generation - fail-fast architecture does not allow fallbacks")
        
        # Load frontmatter if not provided
        if not frontmatter_data:
            frontmatter_data = self._load_frontmatter_data(material_name)
        
        # FAIL FAST: Frontmatter is required
        if not frontmatter_data:
            raise ValueError(f"Frontmatter data required for {material_name} - fail-fast architecture requires complete material data")
        
        timestamp = datetime.datetime.now().isoformat() + "Z"
        
        # Extract required data - FAIL FAST if missing
        author_obj = frontmatter_data.get('author', {})
        if not author_obj or not author_obj.get('name'):
            raise ValueError(f"Author information required in frontmatter for {material_name} - fail-fast requires complete metadata")
        
        author = author_obj.get('name')
        category = frontmatter_data.get('category')
        if not category:
            raise ValueError(f"Material category required in frontmatter for {material_name} - fail-fast requires complete classification")
        
        # Build AI prompt and generate content
        try:
            prompt = self._build_prompt(
                material_name, material_data, author_info, frontmatter_data, schema_fields
            )
            
            response = api_client.generate_simple(
                prompt=prompt,
                max_tokens=3000,  # Increased for detailed scientific content
                temperature=0.2   # Reduced for more precise technical content
            )
            
            # FAIL FAST: API response must be successful
            if not response.success:
                raise ValueError(f"AI generation failed for {material_name}: {response.error} - fail-fast requires successful API responses")
            
            if not response.content or not response.content.strip():
                raise ValueError(f"Empty AI response for {material_name} - fail-fast requires meaningful content")
            
            # Extract and validate AI content - FAIL FAST
            ai_content = self._extract_ai_content(response.content, material_name)
                
        except Exception as e:
            logger.error(f"AI processing failed for {material_name}: {e}")
            raise ValueError(f"Caption generation failed for {material_name}: {e} - fail-fast architecture requires successful processing") from e
        
        # Get existing micro image from frontmatter if available
        micro_image = None
        if 'images' in frontmatter_data and 'micro' in frontmatter_data['images']:
            micro_image = frontmatter_data['images']['micro']
        elif 'caption' in frontmatter_data and 'imageUrl' in frontmatter_data['caption']:
            micro_image = frontmatter_data['caption']['imageUrl']
        
        # Create structured caption data for frontmatter integration
        caption_data = {
            "beforeText": ai_content['before_text'],
            "afterText": ai_content['after_text'],
            "description": f"Microscopic analysis of {material_name.lower()} surface before and after laser cleaning treatment",
            "alt": f"Microscopic view of {material_name.lower()} surface showing laser cleaning effects",
            "technicalAnalysis": {
                "focus": ai_content.get('technical_focus', ''),
                "uniqueCharacteristics": ai_content.get('unique_characteristics', []),
                "contaminationProfile": ai_content.get('contamination_profile', '')
            },
            "microscopy": {
                "parameters": ai_content.get('microscopy_parameters', ''),
                "qualityMetrics": ai_content.get('quality_metrics', '')
            },
            "generation": {
                "method": "frontmatter_integrated_generation",
                "timestamp": timestamp,
                "generator": "FrontmatterCaptionGenerator",
                "componentType": "ai_caption_frontmatter"
            },
            "author": author,
            "materialProperties": {
                "materialType": category,
                "analysisMethod": "ai_microscopy"
            }
        }
        
        # Add micro image if available
        if micro_image:
            caption_data["imageUrl"] = micro_image
        
        # Return structured data instead of YAML string
        return ComponentResult(
            component_type="caption",
            content=caption_data,
            success=True,
            error_message=None
        )
    
    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
        return_structured_data: bool = False
    ):
        """
        Generate caption content with option for structured data or YAML.
        
        Args:
            return_structured_data: If True, returns structured data for frontmatter integration
                                   If False, returns YAML string (legacy behavior)
        """
        
        if return_structured_data:
            return self.generate_for_frontmatter(
                material_name, material_data, api_client, 
                author_info, frontmatter_data, schema_fields
            )
        else:
            # Use parent class method for YAML output (backward compatibility)
            return super().generate(
                material_name, material_data, api_client,
                author_info, frontmatter_data, schema_fields
            )


def generate_caption_for_frontmatter(
    material_name: str, 
    material_data: Dict = None, 
    api_client=None,
    frontmatter_data: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Generate caption data for frontmatter integration.
    Convenience function that returns structured data.
    """
    
    if not api_client:
        raise ValueError("API client required for caption content generation - fail-fast architecture does not allow fallbacks")
    
    generator = FrontmatterCaptionGenerator()
    result = generator.generate_for_frontmatter(
        material_name, 
        material_data or {}, 
        api_client=api_client,
        frontmatter_data=frontmatter_data
    )
    
    if not result.success:
        raise ValueError(f"Caption generation failed for {material_name}: {result.error_message}")
    
    return result.content