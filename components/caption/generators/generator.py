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

        return f"""You are an expert materials scientist specializing in laser surface treatment and microscopic analysis.

TASK: Generate comprehensive, research-grade image caption content for microscopic before/after analysis of {material_name} laser cleaning.

MATERIAL CONTEXT:
- Material: {material_name}
- Category: {category}
- Material Properties: {json.dumps(context_data['properties'], indent=2) if context_data['properties'] else 'Limited data available'}
- Machine Settings: {json.dumps(context_data['settings'], indent=2) if context_data['settings'] else 'Standard parameters'}
- Applications: {', '.join(context_data['applications']) if context_data['applications'] else 'General cleaning'}

REQUIREMENTS:
1. Generate two distinct text descriptions (150-200 characters each):
   - before_text: Describe contaminated surface state with technical detail
   - after_text: Describe cleaned surface with quality metrics

2. Incorporate specific material properties that make {material_name} unique within {category} materials

3. Reference actual technical values from the material data when available

4. Use professional microscopy terminology (SEM analysis, surface topography, etc.)

5. Emphasize what makes {material_name} different from other {category} materials

6. Include material-specific contamination types and cleaning challenges

RESPONSE FORMAT (JSON):
{{
  "before_text": "Technical description of contaminated {material_name.lower()} surface with specific material properties...",
  "after_text": "Technical description of cleaned surface with quality metrics and material-specific results...",
  "technical_focus": "Primary technical aspect emphasized (thermal/mechanical/optical/chemical)",
  "unique_characteristics": ["distinctive trait 1", "distinctive trait 2"],
  "contamination_profile": "Material-specific contamination description",
  "quality_metrics": "Quantified improvement measurements",
  "microscopy_parameters": "Optimized analysis parameters for {material_name}"
}}

Generate content that is completely unique for {material_name} and cannot be confused with other materials."""

    def _extract_ai_content(self, ai_response: str, material_name: str) -> Dict:
        """Extract and validate AI-generated content - FAIL FAST"""
        
        if not ai_response or not ai_response.strip():
            raise ValueError(f"Empty AI response for {material_name} - fail-fast architecture requires valid content")
        
        # Try to parse JSON response
        if '{' not in ai_response or '}' not in ai_response:
            raise ValueError(f"No JSON structure found in AI response for {material_name} - fail-fast requires proper JSON format")
        
        try:
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            json_content = ai_response[start_idx:end_idx]
            ai_data = json.loads(json_content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in AI response for {material_name}: {e} - fail-fast requires valid JSON")
        
        # Validate required fields - FAIL FAST
        required_fields = ['before_text', 'after_text']
        for field in required_fields:
            if field not in ai_data:
                raise ValueError(f"Missing required field '{field}' in AI response for {material_name} - fail-fast requires complete data")
            
            if not ai_data[field] or not ai_data[field].strip():
                raise ValueError(f"Empty required field '{field}' in AI response for {material_name} - fail-fast requires meaningful content")
        
        return ai_data

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
        author_obj = frontmatter_data.get('author_object', {})
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
                max_tokens=1500,
                temperature=0.3
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
# AI-Generated Caption Content for {material_name}
before_text: |
  {ai_content['before_text']}

after_text: |
  {ai_content['after_text']}

# AI-Generated Technical Analysis
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
  title: "{material_name.title()} AI-Generated Surface Analysis"
  description: "AI-generated microscopic analysis of {material_name.lower()} surface treatment with technical insights"

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
