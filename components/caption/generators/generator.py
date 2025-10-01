#!/usr/bin/env python3
"""Caption Component Generator - AI-Enhanced"""

import datetime
import json
import logging
from pathlib import Path
from typing import Dict, Optional
from generators.component_generators import APIComponentGenerator
from utils.config_loader import load_yaml_config

logger = logging.getLogger(__name__)

class CaptionComponentGenerator(APIComponentGenerator):
    def __init__(self):
        super().__init__("caption")

    def _load_frontmatter_data(self, material_name: str) -> Dict:
        """Load frontmatter data for the material - case-insensitive search"""
        content_dir = Path("content/components/frontmatter")
        
        # Normalize material name for more flexible matching
        normalized_name = material_name.lower().replace('_', ' ').replace(' ', '-')
        
        potential_paths = [
            content_dir / f"{material_name.lower()}.yaml",
            content_dir / f"{material_name.lower().replace(' ', '-')}.yaml",
            content_dir / f"{material_name.lower().replace('_', '-')}.yaml",
            content_dir / f"{normalized_name}.yaml",
            content_dir / f"{material_name.lower().replace(' ', '-')}-laser-cleaning.yaml",
            content_dir / f"{normalized_name}-laser-cleaning.yaml"
        ]
        
        for path in potential_paths:
            if path.exists():
                try:
                    return load_yaml_config(str(path))
                except Exception as e:
                    print(f"Warning: Could not load frontmatter from {path}: {e}")
                    continue
        
        return {}

    def _build_prompt(
        self,
        material_name: str,
        material_data: Dict,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> str:
        """Build AI prompt for caption generation"""
        
        # Generate separate random target lengths for before/after variation
        import random
        before_target = random.randint(200, 800)  # Independent random range for before text
        after_target = random.randint(200, 800)   # Independent random range for after text
        
        # Determine paragraph count based on target length
        before_paragraphs = "1-2 paragraphs" if before_target < 400 else "2-3 paragraphs"
        after_paragraphs = "1-2 paragraphs" if after_target < 400 else "2-3 paragraphs"
        
        # Load frontmatter if not provided
        if not frontmatter_data:
            frontmatter_data = self._load_frontmatter_data(material_name)
        
        # Extract material properties for context
        material_props = frontmatter_data.get('materialProperties', {})
        machine_settings = frontmatter_data.get('machineSettings', {})
        category = frontmatter_data.get('category', 'material')
        applications = frontmatter_data.get('applications', [])
        
        # Build comprehensive context for AI
        context_data = {
            'material': material_name,
            'category': category,
            'properties': {},
            'settings': {},
            'applications': applications[:3] if applications else []
        }
        
        # Extract key material properties
        for prop, data in material_props.items():
            if isinstance(data, dict) and 'value' in data:
                context_data['properties'][prop] = {
                    'value': data['value'],
                    'unit': data.get('unit', ''),
                    'description': data.get('description', '')
                }
        
        # Extract machine settings
        for setting, data in machine_settings.items():
            if isinstance(data, dict) and 'value' in data:
                context_data['settings'][setting] = {
                    'value': data['value'], 
                    'unit': data.get('unit', ''),
                    'description': data.get('description', '')
                }

        return f"""You are a technical writer specializing in making complex engineering concepts accessible to educated professionals.

TASK: Generate clear, readable descriptions of {material_name} laser cleaning that explain the process and results in accessible language.

MATERIAL CONTEXT:
- Material: {material_name}
- Category: {category}
- Material Properties: {json.dumps(context_data['properties'], indent=2) if context_data['properties'] else 'Limited data available'}
- Applications: {', '.join(context_data['applications']) if context_data['applications'] else 'General cleaning'}

REQUIREMENTS:
- Write clear, accessible descriptions that educated professionals can understand
- Use appropriate scientific terminology when it adds precision, but explain complex concepts
- Balance technical accuracy with readability - include key scientific terms but avoid excessive jargon
- Include specific measurements and analytical techniques when relevant to understanding
- Focus on visual and performance impacts while maintaining scientific credibility
- Prioritize clarity over showing technical knowledge, but don't oversimplify
- Use scientific terms when standard (e.g., "scanning electron microscopy (SEM)") but explain significance
- Connect technical data to real-world implications and practical benefits
- Use objective, factual language - avoid emotional or dramatic descriptors (no "stunning", "dramatic", "striking", etc.)

Generate exactly two comprehensive text blocks:

**BEFORE_TEXT:**
[Write a detailed microscopic analysis of the contaminated {material_name.lower()} surface in {before_paragraphs} (target ~{before_target} characters):

CRITICAL: Focus on specific contamination visible at 500x magnification. Describe what you would actually see through the microscope - layer thickness, surface texture, contamination patterns, and visual characteristics. Use accessible language while maintaining technical precision. Use objective, factual language - avoid emotional descriptors.

For shorter descriptions: Detail the most prominent contamination features and their microscopic appearance in 1-2 focused paragraphs.

For longer descriptions: Provide comprehensive microscopic analysis including contamination layer structure, surface appearance, and detailed visual characteristics across 2-3 paragraphs.

Write as a clear microscopic observation. Include specific measurements and visual details, but explain technical terms. Use paragraph breaks for clarity.]

**AFTER_TEXT:**
[Write a detailed microscopic analysis of the cleaned {material_name.lower()} surface in {after_paragraphs} (target ~{after_target} characters):

CRITICAL: Focus on the visual transformation visible at 500x magnification. Contrast the cleaned surface directly with the contaminated state, highlighting specific improvements in surface appearance. Use accessible language while maintaining technical precision. Use objective, factual language - avoid emotional descriptors.

For shorter descriptions: Emphasize the most significant visual differences and surface quality improvements in 1-2 focused paragraphs.

For longer descriptions: Provide comprehensive before/after comparison including surface changes, contamination removal evidence, and detailed visual transformation across 2-3 paragraphs.

Write as a clear comparative analysis. Include specific observations about what changed and how the surface now appears, but explain technical terms. Use paragraph breaks for clarity.]

Ensure all content is scientifically accurate but prioritize clarity and readability over technical complexity. Focus on practical benefits and visual results rather than showcasing scientific expertise."""

    def _extract_ai_content(self, ai_response: str, material_name: str) -> Dict:
        """Extract before/after text from AI response - FAIL FAST"""
        
        if not ai_response or not ai_response.strip():
            raise ValueError(f"Empty AI response for {material_name} - fail-fast architecture requires valid content")
        
        # Extract BEFORE_TEXT
        before_start = ai_response.find('**BEFORE_TEXT:**')
        before_end = ai_response.find('**AFTER_TEXT:**')
        
        if before_start == -1 or before_end == -1:
            raise ValueError(f"Missing BEFORE_TEXT or AFTER_TEXT markers in AI response for {material_name}")
        
        before_text = ai_response[before_start + len('**BEFORE_TEXT:**'):before_end].strip()
        before_text = before_text.strip('[]').strip()
        
        # Extract AFTER_TEXT  
        after_start = before_end + len('**AFTER_TEXT:**')
        after_text = ai_response[after_start:].strip()
        after_text = after_text.strip('[]').strip()
        
        # Validate content - FAIL FAST (100 character minimum to allow short random targets)
        min_length = 100  # Flexible minimum to accommodate random variation
        
        if not before_text or len(before_text) < min_length:
            raise ValueError(f"BEFORE_TEXT too short for {material_name} - minimum {min_length} characters for basic content")
        
        if not after_text or len(after_text) < min_length:
            raise ValueError(f"AFTER_TEXT too short for {material_name} - minimum {min_length} characters for basic content")
        
        return {
            'before_text': before_text,
            'after_text': after_text,
            'technical_focus': 'surface_analysis',
            'unique_characteristics': [f'{material_name.lower()}_specific'],
            'contamination_profile': f'{material_name.lower()} surface contamination',
            'microscopy_parameters': f'Microscopic analysis of {material_name.lower()}',
            'quality_metrics': 'Surface improvement analysis'
        }

    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ):
        """Generate AI-powered caption content - FAIL FAST ARCHITECTURE"""
        
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
        
        # Generate YAML content with validated AI data
        yaml_content = f"""---
# Caption Content for {material_name}
before_text: |
  {ai_content['before_text']}

after_text: |
  {ai_content['after_text']}

# Technical Analysis
technical_analysis:
  focus: "{ai_content.get('technical_focus', '')}"
  unique_characteristics: {ai_content.get('unique_characteristics', [])}
  contamination_profile: "{ai_content.get('contamination_profile', '')}"

# Processing Information  
processing:
  frontmatter_available: true
  ai_generated: true
  generation_method: "ai_research"

# Microscopy Parameters
microscopy:
  parameters: "{ai_content.get('microscopy_parameters', '')}"
  quality_metrics: "{ai_content.get('quality_metrics', '')}"

# Generation Metadata
generation:
  generated: "{timestamp}"
  component_type: "ai_caption_fail_fast"

# Author Information
author: "{author}"

# SEO Optimization
seo:
  title: "{material_name.title()} Laser Cleaning Surface Analysis"
  description: "Microscopic analysis of {material_name.lower()} surface treatment with technical insights"

# Material Classification
material_properties:
  materialType: "{category}"
  analysisMethod: "ai_microscopy"

---
# Component Metadata
Material: "{material_name.lower()}"
Component: caption
Generated: {timestamp}
Generator: Z-Beam v2.0.0 (Fail-Fast AI)
---"""

        return self._create_result(yaml_content, success=True)


class CaptionGenerator:
    """FAIL-FAST Caption Generator - requires API client"""
    
    def __init__(self):
        self.generator = CaptionComponentGenerator()

    def generate(self, material: str, material_data: Dict = None, api_client=None) -> str:
        """Generate caption content - FAIL FAST if API client missing"""
        
        if not api_client:
            raise ValueError("API client required for caption generation - fail-fast architecture does not allow fallbacks")
        
        result = self.generator.generate(material, material_data or {}, api_client=api_client)
        
        if not result.success:
            raise ValueError(f"Caption generation failed for {material}: {result.error_message} - fail-fast requires successful processing")
        
        return result.content


def generate_caption_content(material: str, material_data: Dict = None, api_client=None) -> str:
    """Generate caption content - FAIL FAST architecture"""
    
    if not api_client:
        raise ValueError("API client required for caption content generation - fail-fast architecture does not allow fallbacks")
    
    generator = CaptionGenerator()
    return generator.generate(material, material_data, api_client)
