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

        return f"""You are a senior materials scientist and laser processing expert with expertise in advanced surface characterization and contamination analysis.

TASK: Generate comprehensive technical descriptions for detailed microscopic before/after analysis of {material_name} laser cleaning with enhanced scientific depth.

MATERIAL CONTEXT:
- Material: {material_name}
- Category: {category}
- Material Properties: {json.dumps(context_data['properties'], indent=2) if context_data['properties'] else 'Limited data available'}
- Applications: {', '.join(context_data['applications']) if context_data['applications'] else 'General cleaning'}

REQUIREMENTS:
- Write detailed technical descriptions with specific measurements, wavelengths, and quantitative data
- Include material-specific properties, crystal structures, thermal characteristics
- Reference specific contamination mechanisms and surface phenomena
- Use advanced microscopy and spectroscopy terminology
- Include laser parameters, processing conditions, and surface analysis metrics
- Mention specific analytical techniques (SEM, EDX, XPS, AFM, profilometry)

Generate exactly two comprehensive text blocks:

**BEFORE_TEXT:**
[Write 500-700 characters of highly detailed technical description of the contaminated {material_name.lower()} surface, including:
- Specific contamination types with chemical compositions
- Quantitative surface roughness, thickness, and composition data  
- Material-specific properties affecting laser interaction
- Crystallographic structure and thermal properties
- Surface morphology and contamination mechanisms
- Optical properties and laser absorption characteristics]

**AFTER_TEXT:**
[Write 500-700 characters of comprehensive technical description of the cleaned surface, including:
- Quantitative improvement metrics with specific measurements
- Surface quality parameters and analytical results
- Material structure preservation and integrity assessment
- Comparison of key properties before/after treatment
- Process optimization parameters and achieved specifications
- Advanced characterization results from multiple analytical techniques]

Ensure all content is scientifically accurate, quantitative, and demonstrates deep materials science expertise specific to {material_name} within the {category} category."""

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
        
        # Validate content - FAIL FAST (Enhanced thresholds for detailed scientific content)
        if not before_text or len(before_text) < 200:
            raise ValueError(f"BEFORE_TEXT too short or missing for {material_name} - fail-fast requires detailed scientific content (minimum 200 characters)")
        
        if not after_text or len(after_text) < 200:
            raise ValueError(f"AFTER_TEXT too short or missing for {material_name} - fail-fast requires detailed scientific content (minimum 200 characters)")
        
        return {
            'before_text': before_text,
            'after_text': after_text,
            'technical_focus': 'surface_analysis',
            'unique_characteristics': [f'{material_name.lower()}_specific'],
            'contamination_profile': f'{material_name.lower()} surface contamination',
            'microscopy_parameters': f'SEM analysis of {material_name.lower()}',
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
