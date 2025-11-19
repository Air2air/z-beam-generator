#!/usr/bin/env python3
"""
Caption Component Generator - Microscopy Caption Generation

⚠️ LEGACY COMPONENT - For Backward Compatibility Only

NEW CODE SHOULD USE: materials.unified_generator.UnifiedMaterialsGenerator
This generator is maintained for existing tests and ComponentGeneratorFactory compatibility.

Architecture:
- Generates before/after microscopy captions
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
import re
import tempfile
import yaml
from pathlib import Path
from typing import Dict

from generation.config.config_loader import get_config
from shared.generators.component_generators import APIComponentGenerator

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION - Load from config.yaml
# ============================================================================

# Load config once at module level
_config = get_config()
_caption_config = _config.config.get('component_lengths', {}).get('caption', {})

# Word count ranges for caption sections (from config)
MIN_WORDS_BEFORE = _caption_config.get('min_words_before', 30)
MAX_WORDS_BEFORE = _caption_config.get('max_words_before', 70)
MIN_WORDS_AFTER = _caption_config.get('min_words_after', 30)
MAX_WORDS_AFTER = _caption_config.get('max_words_after', 70)

# Total caption constraints (calculated from config)
MIN_TOTAL_WORDS = MIN_WORDS_BEFORE + MIN_WORDS_AFTER
MAX_TOTAL_WORDS = MAX_WORDS_BEFORE + MAX_WORDS_AFTER

# Generation settings (from config)
CAPTION_GENERATION_TEMPERATURE = _caption_config.get('generation_temperature', 0.6)
CAPTION_MAX_TOKENS = _caption_config.get('max_tokens', 300)

# Word count tolerance (from config)
WORD_COUNT_TOLERANCE = _caption_config.get('word_count_tolerance', 10)

# Data file paths
MATERIALS_DATA_PATH = "data/materials/Materials.yaml"

# ============================================================================


class CaptionComponentGenerator(APIComponentGenerator):
    """
    Generate material-specific microscopy captions (before/after).
    
    Responsibilities:
    - Generate "before" caption (contaminated surface)
    - Generate "after" caption (cleaned surface)
    - Write to Materials.yaml
    - Return caption data structure
    
    NOT Responsible For:
    - Author voice (use VoicePostProcessor separately)
    - Frontmatter management
    - Voice validation
    """
    
    def __init__(self):
        super().__init__("caption")
    
    def _load_materials_data(self) -> Dict:
        """Load Materials.yaml"""
        materials_path = Path(MATERIALS_DATA_PATH)
        if not materials_path.exists():
            raise FileNotFoundError(f"Materials.yaml not found at {materials_path}")
        
        with open(materials_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _build_caption_prompt(
        self,
        material_name: str,
        material_data: Dict,
        target_words_before: int,
        target_words_after: int
    ) -> str:
        """Build simple, focused prompt for caption generation"""
        
        # Extract key material properties
        properties = material_data.get('materialProperties', {})
        category = material_data.get('category', 'material')
        description = material_data.get('description', '')
        
        # Build context
        context_parts = [f"Material: {material_name}"]
        
        if category:
            context_parts.append(f"Category: {category}")
        
        if description:
            context_parts.append(f"Description: {description[:300]}")
        
        # Key properties for context
        key_props = []
        if properties:
            for prop in ['hardness', 'thermalConductivity', 'density', 'meltingPoint', 'surfaceFinish']:
                if prop in properties:
                    key_props.append(f"{prop}: {properties[prop]}")
        
        if key_props:
            context_parts.append("Properties: " + ", ".join(key_props[:5]))
        
        context = "\n".join(context_parts)
        
        # Build prompt
        prompt = f"""Generate microscopy image captions for laser cleaning of {material_name}.

CONTEXT:
{context}

Generate TWO captions:

**BEFORE_TEXT:**
Describe the contaminated surface BEFORE laser cleaning.
- Focus on: contaminant type, surface degradation, visible damage
- Length: Write EXACTLY {target_words_before} words (count carefully - this is important for database matching)
- Technical, descriptive tone
- Single paragraph

**AFTER_TEXT:**
Describe the cleaned surface AFTER laser cleaning.
- Focus on: restoration quality, surface condition, material integrity
- Length: Write EXACTLY {target_words_after} words (count carefully - this is important for database matching)
- Technical, descriptive tone
- Single paragraph

REQUIREMENTS:
- Write in technical, professional style
- Use precise microscopy terminology
- Describe visual characteristics clearly
- Target audience: engineers and technical professionals

Generate both captions now (use the **BEFORE_TEXT:** and **AFTER_TEXT:** markers):"""

        return prompt
    
    def _extract_caption_sections(self, ai_response: str, material_name: str) -> Dict[str, str]:
        """Extract before/after sections from AI response - FAIL FAST"""
        
        if not ai_response or not ai_response.strip():
            raise ValueError(f"Empty AI response for {material_name} caption")
        
        # Try to extract marked sections
        before_match = re.search(r'\*\*BEFORE_TEXT:\*\*\s*(.+?)(?=\*\*AFTER_TEXT:|\Z)', ai_response, re.DOTALL)
        after_match = re.search(r'\*\*AFTER_TEXT:\*\*\s*(.+)', ai_response, re.DOTALL)
        
        if before_match and after_match:
            before_text = before_match.group(1).strip()
            after_text = after_match.group(1).strip()
        else:
            # Fallback: try to split by paragraph
            paragraphs = [p.strip() for p in ai_response.split('\n\n') if p.strip()]
            
            if len(paragraphs) >= 2:
                before_text = paragraphs[0]
                after_text = paragraphs[1]
            else:
                raise ValueError(
                    f"Could not extract before/after sections for {material_name}. "
                    f"Response: {ai_response[:200]}..."
                )
        
        # Clean up any remaining markers
        before_text = re.sub(r'^\*\*(?:BEFORE_TEXT|AFTER_TEXT):\*\*\s*', '', before_text).strip()
        after_text = re.sub(r'^\*\*(?:BEFORE_TEXT|AFTER_TEXT):\*\*\s*', '', after_text).strip()
        
        # Validate word counts with configurable tolerance
        before_words = len(before_text.split())
        after_words = len(after_text.split())
        
        # Get tolerance from config
        # WORD_COUNT_TOLERANCE is stored as absolute words (30)
        # Convert to percentage for flexible min/max calculation
        # For 20-120 range: 30/(120-20)*100 = 30% tolerance
        range_span = MAX_WORDS_BEFORE - MIN_WORDS_BEFORE
        tolerance_pct = WORD_COUNT_TOLERANCE / range_span if range_span > 0 else 0.30
        
        # Calculate acceptable ranges using percentage
        before_min_acceptable = int(MIN_WORDS_BEFORE * (1 - tolerance_pct))
        before_max_acceptable = int(MAX_WORDS_BEFORE * (1 + tolerance_pct))
        after_min_acceptable = int(MIN_WORDS_AFTER * (1 - tolerance_pct))
        after_max_acceptable = int(MAX_WORDS_AFTER * (1 + tolerance_pct))
        
        # Strict validation: reject if outside tolerance range
        if before_words < before_min_acceptable:
            raise ValueError(
                f"Before caption too short for {material_name}: "
                f"{before_words} words < {before_min_acceptable} minimum (range: {MIN_WORDS_BEFORE}-{MAX_WORDS_BEFORE} ±{int(tolerance_pct*100)}%)"
            )
        
        if before_words > before_max_acceptable:
            raise ValueError(
                f"Before caption too long for {material_name}: "
                f"{before_words} words > {before_max_acceptable} maximum (range: {MIN_WORDS_BEFORE}-{MAX_WORDS_BEFORE} ±{int(tolerance_pct*100)}%)"
            )
        
        if after_words < after_min_acceptable:
            raise ValueError(
                f"After caption too short for {material_name}: "
                f"{after_words} words < {after_min_acceptable} minimum (range: {MIN_WORDS_AFTER}-{MAX_WORDS_AFTER} ±{int(tolerance_pct*100)}%)"
            )
        
        if after_words > after_max_acceptable:
            raise ValueError(
                f"After caption too long for {material_name}: "
                f"{after_words} words > {after_max_acceptable} maximum (range: {MIN_WORDS_AFTER}-{MAX_WORDS_AFTER} ±{int(tolerance_pct*100)}%)"
            )
        
        total_words = before_words + after_words
        logger.info(
            f"Extracted captions: before={before_words}w, after={after_words}w, total={total_words}w"
        )
        
        return {
            'before': before_text,
            'after': after_text
        }
    
    def _write_caption_to_materials(
        self,
        material_name: str,
        before_text: str,
        after_text: str,
        timestamp: str
    ) -> bool:
        """Write caption to Materials.yaml with atomic write"""
        
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
            
            # Write caption (template-compliant: only before and after)
            materials_section[actual_key]['caption'] = {
                'before': before_text,
                'after': after_text
            }
            
            # Atomic write using temp file
            temp_fd, temp_path = tempfile.mkstemp(suffix='.yaml', dir=materials_path.parent)
            try:
                os.close(temp_fd)  # Close file descriptor before writing
                with open(temp_path, 'w', encoding='utf-8') as f:
                    yaml.dump(materials_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                
                # Atomic rename
                Path(temp_path).replace(materials_path)
                logger.info(f"✅ Caption written to Materials.yaml → materials.{actual_key}.caption")
                return True
                
            except Exception as e:
                # Cleanup temp file on error
                if Path(temp_path).exists():
                    Path(temp_path).unlink()
                raise e
            
        except Exception as e:
            logger.error(f"Failed to write caption to Materials.yaml: {e}")
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
        Generate AI-powered caption content with optional voice enhancement.
        
        Args:
            material_name: Name of the material
            material_data: Material properties dictionary
            api_client: API client for generation (required)
            author: Author dictionary with 'country' key for voice enhancement (optional)
            **kwargs: Additional parameters
            
        Returns:
            ComponentResult with generated caption content
        """
        
        # Input validation
        if not api_client:
            raise ValueError("API client required for caption generation")
        
        if not material_data or not isinstance(material_data, dict):
            raise ValueError(f"Valid material_data dict required for {material_name}")
        
        # Generate random target word counts
        target_words_before = random.randint(MIN_WORDS_BEFORE, MAX_WORDS_BEFORE)
        target_words_after = random.randint(MIN_WORDS_AFTER, MAX_WORDS_AFTER)
        
        timestamp = datetime.datetime.now().isoformat() + "Z"
        
        logger.info(f"📸 Generating caption for {material_name}")
        logger.info(f"   Target: before={target_words_before}w, after={target_words_after}w")
        
        try:
            # Build prompt
            prompt = self._build_caption_prompt(
                material_name=material_name,
                material_data=material_data,
                target_words_before=target_words_before,
                target_words_after=target_words_after
            )
            
            # Cache-busting
            random_seed = random.randint(10000, 99999)
            prompt = prompt + f"\n\n[Generation ID: {random_seed}]"
            
            # Generate with API
            response = api_client.generate_simple(
                prompt=prompt,
                max_tokens=CAPTION_MAX_TOKENS,
                temperature=CAPTION_GENERATION_TEMPERATURE
            )
            
            if not response.success:
                raise ValueError(f"API generation failed: {response.error}")
            
            # Extract and validate caption sections
            sections = self._extract_caption_sections(response.content, material_name)
            
            logger.info("✅ Generated caption sections:")
            logger.info(f"   Before: '{sections['before'][:80]}...'")
            logger.info(f"   After: '{sections['after'][:80]}...'")
            
            # Write to Materials.yaml (atomic)
            self._write_caption_to_materials(
                material_name=material_name,
                before_text=sections['before'],
                after_text=sections['after'],
                timestamp=timestamp
            )
            
            return self._create_result(
                f"Caption generated for {material_name}",
                success=True
            )
            
        except Exception as e:
            logger.error(f"Caption generation failed for {material_name}: {e}")
            raise


class CaptionGenerator:
    """Simplified caption generator interface"""
    
    def __init__(self):
        self.generator = CaptionComponentGenerator()
    
    def generate(self, material: str, material_data: Dict = None, api_client=None) -> str:
        """Generate caption content"""
        
        if not api_client:
            raise ValueError("API client required")
        
        if not material_data:
            # Load from Materials.yaml
            gen = CaptionComponentGenerator()
            all_data = gen._load_materials_data()
            material_data = all_data.get('materials', {}).get(material, {})
        
        result = self.generator.generate(material, material_data, api_client=api_client)
        
        if not result.success:
            raise ValueError(f"Generation failed: {result.error_message}")
        
        return result.content


def generate_caption_content(material: str, material_data: Dict = None, api_client=None) -> str:
    """Generate caption content - FAIL FAST architecture"""
    
    if not api_client:
        raise ValueError("API client required")
    
    generator = CaptionGenerator()
    return generator.generate(material, material_data, api_client)
