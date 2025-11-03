#!/usr/bin/env python3
"""
Unified Materials Content Generator

Single generator for all material content types (caption, FAQ, subtitle, etc.)
Uses simple prompt templates instead of separate generator classes.

Architecture:
- Load prompt templates from materials/prompts/
- Substitute variables with material data
- Generate content via API
- Write to Materials.yaml
- No voice processing (handled separately)

Usage:
    generator = UnifiedMaterialsGenerator(api_client)
    
    # Generate caption
    generator.generate('Bronze', 'caption')
    
    # Generate FAQ
    generator.generate('Bronze', 'faq', faq_count=8)
    
    # Generate subtitle
    generator.generate('Bronze', 'subtitle')
"""

import datetime
import logging
import random
import re
import tempfile
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Paths
MATERIALS_DATA_PATH = Path("materials/data/Materials.yaml")
PROMPTS_DIR = Path("materials/prompts")

# Default generation settings
DEFAULT_SETTINGS = {
    'caption': {
        'temperature': 0.6,
        'max_tokens': 300,
        'min_words_before': 15,
        'max_words_before': 70,
        'min_words_after': 15,
        'max_words_after': 70,
    },
    'faq': {
        'temperature': 0.7,
        'max_tokens': 2000,
        'min_count': 2,
        'max_count': 8,
        'word_count_range': '10-50',  # High variability: some short (10-20), some medium (20-35), some long (35-50)
    },
    'subtitle': {
        'temperature': 0.6,
        'max_tokens': 100,
        'min_words': 8,
        'max_words': 15,
    }
}


class UnifiedMaterialsGenerator:
    """
    Unified generator for all materials content types.
    
    Responsibilities:
    - Load and format prompt templates
    - Generate content via API
    - Extract and validate responses
    - Write to Materials.yaml atomically
    
    NOT Responsible For:
    - Author voice (use VoicePostProcessor separately)
    - Frontmatter export (handled by export pipeline)
    """
    
    def __init__(self, api_client):
        """
        Initialize unified generator.
        
        Args:
            api_client: API client for content generation (required)
        """
        if not api_client:
            raise ValueError("API client required for content generation")
        
        self.api_client = api_client
        self.logger = logging.getLogger(__name__)
        
        # Load prompt templates
        self.prompts = {}
        for content_type in ['caption', 'faq', 'subtitle']:
            prompt_file = PROMPTS_DIR / f"{content_type}.txt"
            if prompt_file.exists():
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    self.prompts[content_type] = f.read()
                self.logger.debug(f"Loaded {content_type} prompt template")
            else:
                self.logger.warning(f"Prompt template not found: {prompt_file}")
        
        self.logger.info("UnifiedMaterialsGenerator initialized")
    
    def _load_materials_data(self) -> Dict:
        """Load Materials.yaml"""
        if not MATERIALS_DATA_PATH.exists():
            raise FileNotFoundError(f"Materials.yaml not found at {MATERIALS_DATA_PATH}")
        
        with open(MATERIALS_DATA_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _build_context(self, material_data: Dict) -> str:
        """Build context string from material data"""
        context_parts = []
        
        # Basic info
        if 'category' in material_data:
            context_parts.append(f"Category: {material_data['category']}")
        
        if 'description' in material_data:
            context_parts.append(f"Description: {material_data['description'][:300]}")
        
        # Key properties
        properties = material_data.get('materialProperties', {})
        key_props = []
        for prop in ['hardness', 'thermalConductivity', 'density', 'meltingPoint']:
            if prop in properties:
                key_props.append(f"{prop}: {properties[prop]}")
        
        if key_props:
            context_parts.append("Properties: " + ", ".join(key_props[:5]))
        
        return "\n".join(context_parts)
    
    def _format_prompt(self, content_type: str, material_name: str, material_data: Dict, **kwargs) -> str:
        """
        Format prompt template with material data and parameters.
        
        Args:
            content_type: Type of content ('caption', 'faq', 'subtitle')
            material_name: Name of material
            material_data: Material data dictionary
            **kwargs: Additional parameters for prompt formatting
            
        Returns:
            Formatted prompt string
        """
        if content_type not in self.prompts:
            raise ValueError(f"No prompt template for content type: {content_type}")
        
        prompt_template = self.prompts[content_type]
        
        # Build context
        context = self._build_context(material_data)
        
        # Get settings for this content type
        settings = DEFAULT_SETTINGS.get(content_type, {})
        
        # Build format parameters
        format_params = {
            'material_name': material_name,
            'context': context,
            'category': material_data.get('category', 'material'),
            'subcategory': material_data.get('subcategory', ''),
            'description': material_data.get('description', ''),
        }
        
        # Add content-type specific parameters
        if content_type == 'caption':
            format_params['target_words_before'] = random.randint(
                settings['min_words_before'], settings['max_words_before']
            )
            format_params['target_words_after'] = random.randint(
                settings['min_words_after'], settings['max_words_after']
            )
        
        elif content_type == 'faq':
            # Random count between min_count and max_count if not specified
            default_faq_count = random.randint(settings['min_count'], settings['max_count'])
            format_params['faq_count'] = kwargs.get('faq_count', default_faq_count)
            format_params['word_count_range'] = settings['word_count_range']
        
        # Override with any kwargs
        format_params.update(kwargs)
        
        # Format prompt
        try:
            formatted_prompt = prompt_template.format(**format_params)
        except KeyError as e:
            self.logger.error(f"Missing parameter in prompt template: {e}")
            raise
        
        # Add cache-busting
        random_seed = random.randint(10000, 99999)
        formatted_prompt += f"\n\n[Generation ID: {random_seed}]"
        
        return formatted_prompt
    
    def _generate_with_api(self, prompt: str, content_type: str) -> str:
        """Generate content using API"""
        settings = DEFAULT_SETTINGS.get(content_type, {})
        
        response = self.api_client.generate_simple(
            prompt=prompt,
            max_tokens=settings.get('max_tokens', 500),
            temperature=settings.get('temperature', 0.7)
        )
        
        if not response.success:
            raise ValueError(f"API generation failed: {response.error}")
        
        return response.content
    
    def _write_to_materials_yaml(self, material_name: str, content_type: str, content_data: Dict):
        """
        Write generated content to Materials.yaml atomically.
        
        Args:
            material_name: Name of material
            content_type: Type of content ('caption', 'faq', 'subtitle')
            content_data: Content data to write
        """
        # Load current data
        materials_data = self._load_materials_data()
        
        if material_name not in materials_data['materials']:
            raise ValueError(f"Material '{material_name}' not found in Materials.yaml")
        
        # Update content
        materials_data['materials'][material_name][content_type] = content_data
        
        # Atomic write via temp file
        with tempfile.NamedTemporaryFile(
            mode='w',
            encoding='utf-8',
            dir=MATERIALS_DATA_PATH.parent,
            delete=False,
            suffix='.yaml'
        ) as temp_f:
            yaml.dump(materials_data, temp_f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            temp_path = temp_f.name
        
        # Atomic rename
        Path(temp_path).replace(MATERIALS_DATA_PATH)
        self.logger.info(f"✅ {content_type} written to Materials.yaml → materials.{material_name}.{content_type}")
    
    def generate_caption(self, material_name: str, material_data: Dict) -> Dict[str, str]:
        """Generate before/after microscopy captions"""
        self.logger.info(f"📸 Generating caption for {material_name}")
        
        # Format prompt
        prompt = self._format_prompt('caption', material_name, material_data)
        
        # Generate
        response = self._generate_with_api(prompt, 'caption')
        
        # Extract sections
        before_match = re.search(r'\*\*BEFORE_TEXT:\*\*\s*(.+?)(?=\*\*AFTER_TEXT:|\Z)', response, re.DOTALL)
        after_match = re.search(r'\*\*AFTER_TEXT:\*\*\s*(.+)', response, re.DOTALL)
        
        if not before_match or not after_match:
            # Fallback: split by paragraph
            paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]
            if len(paragraphs) < 2:
                raise ValueError(f"Could not extract before/after sections: {response[:200]}")
            before_text = paragraphs[0]
            after_text = paragraphs[1]
        else:
            before_text = before_match.group(1).strip()
            after_text = after_match.group(1).strip()
        
        # Clean up markers
        before_text = re.sub(r'^\*\*(?:BEFORE_TEXT|AFTER_TEXT):\*\*\s*', '', before_text).strip()
        after_text = re.sub(r'^\*\*(?:BEFORE_TEXT|AFTER_TEXT):\*\*\s*', '', after_text).strip()
        
        caption_data = {
            'before': before_text,
            'after': after_text
        }
        
        self.logger.info(f"   Before: {len(before_text.split())} words")
        self.logger.info(f"   After: {len(after_text.split())} words")
        
        return caption_data
    
    def generate_faq(self, material_name: str, material_data: Dict, faq_count: int = None) -> list:
        """Generate FAQ questions and answers"""
        # Randomize FAQ count between 2-8 if not specified
        settings = DEFAULT_SETTINGS['faq']
        if faq_count is None:
            faq_count = random.randint(settings['min_count'], settings['max_count'])
        
        self.logger.info(f"❓ Generating {faq_count} FAQ items for {material_name}")
        
        # Format prompt
        prompt = self._format_prompt('faq', material_name, material_data, faq_count=faq_count)
        
        # Generate
        response = self._generate_with_api(prompt, 'faq')
        
        # Extract JSON - Look for the final FAQ JSON block specifically
        import json
        try:
            # Find the last JSON block with "faq" key
            faq_pattern = r'\{\s*"faq"\s*:\s*\[(.*?)\]\s*\}'
            matches = list(re.finditer(faq_pattern, response, re.DOTALL))
            
            if matches:
                # Use the last match (final FAQ output)
                json_str = matches[-1].group(0)
                data = json.loads(json_str)
                faq_list = data.get('faq', [])
            else:
                raise ValueError("Could not find FAQ JSON in response")
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse FAQ JSON: {e}")
            raise ValueError(f"Invalid FAQ JSON: {response[:200]}")
        
        if not faq_list:
            raise ValueError("FAQ list is empty")
        
        self.logger.info(f"   Generated {len(faq_list)} FAQ items")
        
        return faq_list
    
    def generate_subtitle(self, material_name: str, material_data: Dict) -> str:
        """Generate SEO-optimized subtitle"""
        self.logger.info(f"📝 Generating subtitle for {material_name}")
        
        # Format prompt
        prompt = self._format_prompt('subtitle', material_name, material_data)
        
        # Generate
        response = self._generate_with_api(prompt, 'subtitle')
        
        # Extract subtitle (first meaningful line)
        subtitle = response.strip().split('\n')[0].strip()
        
        # Clean up quotes if present
        subtitle = subtitle.strip('"\'')
        
        # Validate word count
        word_count = len(subtitle.split())
        settings = DEFAULT_SETTINGS['subtitle']
        if word_count < settings['min_words'] or word_count > settings['max_words']:
            self.logger.warning(f"Subtitle word count {word_count} outside range {settings['min_words']}-{settings['max_words']}")
        
        self.logger.info(f"   Generated: {subtitle[:80]}...")
        
        return subtitle
    
    def generate(self, material_name: str, content_type: str, **kwargs):
        """
        Generate content for material.
        
        Args:
            material_name: Name of material
            content_type: Type of content ('caption', 'faq', 'subtitle')
            **kwargs: Additional parameters (e.g., faq_count=8)
            
        Returns:
            Generated content (dict for caption/faq, str for subtitle)
        """
        # Load material data
        materials_data = self._load_materials_data()
        
        if material_name not in materials_data['materials']:
            raise ValueError(f"Material '{material_name}' not found in Materials.yaml")
        
        material_data = materials_data['materials'][material_name]
        
        # Generate based on type
        if content_type == 'caption':
            content_data = self.generate_caption(material_name, material_data)
        elif content_type == 'faq':
            content_data = self.generate_faq(material_name, material_data, **kwargs)
        elif content_type == 'subtitle':
            content_data = self.generate_subtitle(material_name, material_data)
        else:
            raise ValueError(f"Unknown content type: {content_type}")
        
        # Write to Materials.yaml
        self._write_to_materials_yaml(material_name, content_type, content_data)
        
        return content_data
