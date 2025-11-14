#!/usr/bin/env python3
"""
Subtitle Component Generator - Subtitle Generation

⚠️ LEGACY COMPONENT - For Backward Compatibility Only

NEW CODE SHOULD USE: materials.unified_generator.UnifiedMaterialsGenerator
This generator is maintained for existing tests and ComponentGeneratorFactory compatibility.

Architecture:
- Generates engaging 8-12 word subtitles
- Writes to Materials.yaml only (single source of truth)
- Single API call per generation (no post-processing)
- Minimal, clean interface

Migration Path:
- Use UnifiedMaterialsGenerator for new implementations
- This will be deprecated in future major version
"""

import datetime
import logging
import os
import random
import tempfile
import yaml
from pathlib import Path
from typing import Dict
from shared.generators.component_generators import APIComponentGenerator

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Word count range for subtitles (random selection within bounds)
MIN_WORDS_PER_SUBTITLE = 7  # Allow 7 for flexibility
MAX_WORDS_PER_SUBTITLE = 12

# Generation settings
SUBTITLE_GENERATION_TEMPERATURE = 0.6
SUBTITLE_MAX_TOKENS = 100

# Data file paths
MATERIALS_DATA_PATH = "data/materials/Materials.yaml"

# ============================================================================


class SubtitleComponentGenerator(APIComponentGenerator):
    """
    Generate material-specific subtitle/tagline.
    
    Responsibilities:
    - Generate engaging 8-12 word subtitle
    - Write to Materials.yaml
    - Return subtitle text
    
    NOT Responsible For:
    - Author voice (use VoicePostProcessor separately)
    - Frontmatter management
    - Voice validation
    """
    
    def __init__(self):
        super().__init__("subtitle")
        self.min_words = MIN_WORDS_PER_SUBTITLE
        self.max_words = MAX_WORDS_PER_SUBTITLE
    
    def _load_materials_data(self) -> Dict:
        """Load Materials.yaml"""
        materials_path = Path(MATERIALS_DATA_PATH)
        if not materials_path.exists():
            raise FileNotFoundError(f"Materials.yaml not found at {materials_path}")
        
        with open(materials_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _build_subtitle_prompt(
        self,
        material_name: str,
        material_data: Dict,
        target_words: int
    ) -> str:
        """Build simple, focused prompt for subtitle generation"""
        
        # Extract key material properties
        properties = material_data.get('materialProperties', {})
        category = material_data.get('category', 'material')
        description = material_data.get('description', '')
        
        # Build context from material data
        context_parts = [f"Material: {material_name}"]
        
        if category:
            context_parts.append(f"Category: {category}")
        
        if description:
            context_parts.append(f"Description: {description[:200]}")
        
        # Key properties for subtitle focus
        key_props = []
        if properties:
            for prop in ['hardness', 'thermalConductivity', 'density', 'meltingPoint']:
                if prop in properties:
                    key_props.append(f"{prop}: {properties[prop]}")
        
        if key_props:
            context_parts.append("Key Properties: " + ", ".join(key_props[:3]))
        
        context = "\n".join(context_parts)
        
        # Build prompt
        prompt = f"""Generate a professional, engaging subtitle for laser cleaning of {material_name}.

CONTEXT:
{context}

REQUIREMENTS:
- Write EXACTLY {target_words} words (±2 words tolerance)
- Create a concise, professional tagline
- Appeal to technical decision-makers
- Highlight key material benefits for laser cleaning
- No punctuation at the end
- Single phrase format

TARGET AUDIENCE: Technical professionals and decision-makers in industrial laser cleaning

Write the subtitle now:"""

        return prompt
    
    def _extract_subtitle_content(self, ai_response: str, material_name: str) -> str:
        """Extract subtitle text from AI response - FAIL FAST"""
        
        if not ai_response or not ai_response.strip():
            raise ValueError(f"Empty AI response for {material_name} subtitle")
        
        # Clean the response
        content = ai_response.strip()
        
        # Remove common wrapper patterns
        content = content.strip('[]').strip('"').strip("'").strip()
        
        # Remove trailing punctuation
        if content and content[-1] in '.!?':
            content = content[:-1].strip()
        
        # Validate word count
        word_count = len(content.split())
        
        if word_count < self.min_words:
            raise ValueError(
                f"Subtitle too short for {material_name}: {word_count} words < {self.min_words} minimum"
            )
        
        if word_count > self.max_words + 3:  # Allow small tolerance
            logger.warning(f"Subtitle too long for {material_name}: {word_count} words, trimming...")
            words = content.split()
            content = ' '.join(words[:self.max_words])
        
        logger.info(f"Extracted subtitle: {len(content)} chars, {len(content.split())} words")
        return content
    
    def _write_subtitle_to_materials(
        self,
        material_name: str,
        subtitle: str,
        timestamp: str
    ) -> bool:
        """Write subtitle to Materials.yaml with atomic write"""
        
        materials_path = Path(MATERIALS_DATA_PATH)
        
        try:
            # Load Materials.yaml - FAIL-FAST on empty/invalid file
            with open(materials_path, 'r', encoding='utf-8') as f:
                materials_data = yaml.safe_load(f)
            
            # FAIL-FAST: Materials.yaml must have valid content
            if not materials_data:
                raise ValueError(f"CRITICAL: Materials.yaml at {materials_path} is empty or invalid")
            
            # Navigate to materials section
            if 'materials' not in materials_data:
                raise ValueError("No 'materials' section found in Materials.yaml")
            
            materials_section = materials_data['materials']
            
            # Find material (case-insensitive)
            actual_key = None
            for key in materials_section.keys():
                if key.lower().replace('_', ' ') == material_name.lower().replace('_', ' '):
                    actual_key = key
                    break
            
            if not actual_key:
                raise ValueError(f"Material {material_name} not found in Materials.yaml")
            
            # Write subtitle
            materials_section[actual_key]['subtitle'] = subtitle
            
            # Add metadata
            if 'subtitle_metadata' not in materials_section[actual_key]:
                materials_section[actual_key]['subtitle_metadata'] = {}
            
            materials_section[actual_key]['subtitle_metadata'] = {
                'generated': timestamp,
                'word_count': len(subtitle.split()),
                'character_count': len(subtitle),
                'generation_method': 'ai_discrete'
            }
            
            # Atomic write using temp file
            temp_fd, temp_path = tempfile.mkstemp(suffix='.yaml', dir=materials_path.parent)
            try:
                os.close(temp_fd)  # Close file descriptor before writing
                with open(temp_path, 'w', encoding='utf-8') as f:
                    yaml.dump(materials_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                
                # Atomic rename
                Path(temp_path).replace(materials_path)
                logger.info(f"✅ Subtitle written to Materials.yaml → materials.{actual_key}.subtitle")
                return True
                
            except Exception as e:
                # Cleanup temp file on error
                if Path(temp_path).exists():
                    Path(temp_path).unlink()
                raise e
            
        except Exception as e:
            logger.error(f"Failed to write subtitle to Materials.yaml: {e}")
            raise
    
    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author: Dict = None,
        **kwargs
    ):
        """
        Generate AI-powered subtitle content with optional voice enhancement.
        
        Args:
            material_name: Name of the material
            material_data: Material properties dictionary
            api_client: API client for generation (required)
            author: Author dictionary with 'country' key for voice enhancement (optional)
            **kwargs: Additional parameters
            
        Returns:
            ComponentResult with generated subtitle content
        """
        
        # Input validation
        if not api_client:
            raise ValueError("API client required for subtitle generation")
        
        if not material_data or not isinstance(material_data, dict):
            raise ValueError(f"Valid material_data dict required for {material_name}")
        
        # Generate random target word count
        target_words = random.randint(self.min_words, self.max_words)
        
        timestamp = datetime.datetime.now().isoformat() + "Z"
        
        logger.info(f"🎭 Generating subtitle for {material_name}")
        logger.info(f"   Target: {target_words} words")
        
        try:
            # Build prompt
            prompt = self._build_subtitle_prompt(
                material_name=material_name,
                material_data=material_data,
                target_words=target_words
            )
            
            # Cache-busting
            random_seed = random.randint(10000, 99999)
            prompt = prompt + f"\n\n[Generation ID: {random_seed}]"
            
            # Generate with API
            response = api_client.generate_simple(
                prompt=prompt,
                max_tokens=SUBTITLE_MAX_TOKENS,
                temperature=SUBTITLE_GENERATION_TEMPERATURE
            )
            
            if not response.success:
                raise ValueError(f"API generation failed: {response.error}")
            
            # Extract and validate subtitle
            subtitle = self._extract_subtitle_content(response.content, material_name)
            logger.info(f"✅ Generated subtitle: '{subtitle}'")
            
            # Write to Materials.yaml (atomic)
            self._write_subtitle_to_materials(
                material_name=material_name,
                subtitle=subtitle,
                timestamp=timestamp
            )
            
            return self._create_result(
                f"Subtitle generated for {material_name}: '{subtitle}'",
                success=True
            )
            
        except Exception as e:
            logger.error(f"Subtitle generation failed for {material_name}: {e}")
            raise


class SubtitleGenerator:
    """Simplified subtitle generator interface"""
    
    def __init__(self):
        self.generator = SubtitleComponentGenerator()
    
    def generate(self, material: str, material_data: Dict = None, api_client=None) -> str:
        """Generate subtitle content"""
        
        if not api_client:
            raise ValueError("API client required")
        
        if not material_data:
            # Load from Materials.yaml
            gen = SubtitleComponentGenerator()
            all_data = gen._load_materials_data()
            material_data = all_data.get('materials', {}).get(material, {})
        
        result = self.generator.generate(material, material_data, api_client=api_client)
        
        if not result.success:
            raise ValueError(f"Generation failed: {result.error_message}")
        
        return result.content
