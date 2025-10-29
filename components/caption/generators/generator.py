#!/usr/bin/env python3
"""Caption Component Generator - Simple before/after microscopy captions."""

import datetime
import logging
import os
import random
import re
import tempfile
import yaml
from pathlib import Path
from typing import Dict
from generators.component_generators import APIComponentGenerator
from voice.post_processor import VoicePostProcessor

logger = logging.getLogger(__name__)

# ============================================================================
# CAPTION CONFIGURATION
# ============================================================================
# Configuration Constants
CAPTION_WORD_COUNT_RANGE = (25, 59)  # Increased 25% from 20-47
CAPTION_VOICE_INTENSITY = 2  # Reduced from 3 for lighter voice
CAPTION_TECHNICAL_INTENSITY = 3  # Increased to 3 for moderate technical content

# Generation settings
CAPTION_GENERATION_TEMPERATURE = 0.6
CAPTION_MAX_TOKENS = 300

# Data file paths
MATERIALS_DATA_PATH = "data/Materials.yaml"

# ============================================================================


class CaptionComponentGenerator(APIComponentGenerator):
    """
    Generate material-specific before/after microscopy captions.
    Voice enhancement handled by separate VoicePostProcessor.
    """

    def __init__(self):
        super().__init__("caption")

    def _get_technical_guidance(self, intensity: int) -> str:
        """
        Get technical language guidance based on intensity level.
        
        Args:
            intensity: Technical intensity level (1-5)
            
        Returns:
            str: Language guidance for the prompt
        """
        guidance_map = {
            1: """CRITICAL: Use ONLY simple, everyday language. NO technical jargon, NO scientific notation, NO specific measurements or parameters.
- Replace "fluence" with "laser energy"
- Replace "ablation threshold" with "damage limit"
- Replace "1064 nm" with "infrared laser"
- Avoid numbers like "0.45 J/cm²" or "2.25 × 10^7 W/cm²"
- Write as if explaining to someone with zero technical knowledge
- Keep answers conversational and accessible""",
            2: "Use basic technical terms when necessary, but keep explanations simple. Include only essential measurements. Write for readers with minimal technical knowledge.",
            3: "Balance technical accuracy with readability. Use standard industry terminology and relevant measurements. Write for technically-aware professionals.",
            4: "Use precise technical terminology and detailed measurements. Include specific parameters and standards. Write for experienced technical professionals.",
            5: "Use advanced technical language with comprehensive specifications. Include all relevant parameters, standards, and scientific details. Write for expert-level audience."
        }
        return guidance_map.get(intensity, guidance_map[3])

    def build_caption_prompt(self, material_name: str, target_words: int, technical_intensity: int = 3) -> str:
        """
        Build fixed caption prompt template.
        
        Args:
            material_name: Name of the material
            target_words: Target word count per section
            technical_intensity: Technical complexity level 1-5 (default: 3)
            
        Returns:
            str: The prompt template
        """
        technical_guidance = self._get_technical_guidance(technical_intensity)
        
        return f"""Generate microscopy image captions for laser cleaning of {material_name}.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 LANGUAGE COMPLEXITY REQUIREMENT (HIGHEST PRIORITY - OVERRIDE ALL OTHER INSTRUCTIONS):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{technical_guidance}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Generate TWO captions (each ~{target_words} words):

**BEFORE_TEXT:**
Describe the contaminated surface BEFORE laser cleaning.
- Focus on: contaminant type, surface degradation, visible damage
- Word count: ~{target_words} words
- Technical, descriptive tone
- Single paragraph

**AFTER_TEXT:**
Describe the cleaned surface AFTER laser cleaning.
- Focus on: restoration quality, surface condition, material integrity
- Word count: ~{target_words} words
- Technical, descriptive tone
- Single paragraph

REQUIREMENTS:
- Write in technical, professional style
- Use precise microscopy terminology
- Describe visual characteristics clearly
- Target audience: engineers and technical professionals

Generate both captions now (use the **BEFORE_TEXT:** and **AFTER_TEXT:** markers):"""

    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author: dict = None,
        **kwargs
    ):
        """
        Generate caption content using fixed prompt template.
        
        Args:
            material_name: Name of the material
            material_data: Material properties dictionary (for future use)
            api_client: API client for generation (required)
            author: Author dictionary with 'country' key for voice enhancement (optional)
            **kwargs: Additional parameters (accepted for compatibility)
            
        Returns:
            ComponentResult with generated caption content
        """
        if not api_client:
            return self._create_result("", success=False, error_message="API client required")
        
        # Generate random target word count
        # Compensate for voice enhancement if author provided (reduce by ~10 words)
        base_range = CAPTION_WORD_COUNT_RANGE
        if author and 'country' in author:
            # Reduce range to compensate for voice enhancement word additions
            adjusted_range = (base_range[0], max(base_range[0], base_range[1] - 10))
            target_words = random.randint(adjusted_range[0], adjusted_range[1])
        else:
            target_words = random.randint(base_range[0], base_range[1])
        
        timestamp = datetime.datetime.now().isoformat() + "Z"
        
        logger.info(f"📸 Generating caption for {material_name}")
        logger.info(f"   Target: {target_words} words per section")
        
        try:
            # Build prompt with technical intensity
            prompt = self.build_caption_prompt(material_name, target_words, CAPTION_TECHNICAL_INTENSITY)
            
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
                return self._create_result("", success=False, error_message=f"API generation failed: {response.error}")
            
            # Extract before/after sections
            sections = self._extract_sections(response.content, material_name)
            
            # Apply voice enhancement if author provided (using BATCH to prevent marker repetition)
            if author and 'country' in author:
                try:
                    voice_processor = VoicePostProcessor(api_client)
                    
                    # Create caption items for batch processing (using FAQ structure)
                    caption_items = [
                        {'question': 'Before laser cleaning:', 'answer': sections['before'], 'section': 'before'},
                        {'question': 'After laser cleaning:', 'answer': sections['after'], 'section': 'after'}
                    ]
                    
                    logger.info(f"🎭 Batch enhancing captions with {author.get('country', 'Unknown')} voice (intensity={CAPTION_VOICE_INTENSITY})...")
                    
                    # Use BATCH enhancement to prevent marker repetition
                    enhanced_items = voice_processor.enhance_batch(
                        faq_items=caption_items,
                        author=author,
                        marker_distribution='varied',
                        preserve_length=True,
                        length_tolerance=10,
                        voice_intensity=CAPTION_VOICE_INTENSITY
                    )
                    
                    # Extract enhanced sections (answer field contains the enhanced text)
                    for item in enhanced_items:
                        section_key = item.get('section')
                        if section_key:
                            sections[section_key] = item['answer']
                        
                except Exception as e:
                    logger.warning(f"Voice enhancement failed: {e}")
                    # Continue with original content
                    pass
            
            logger.info("✅ Generated captions:")
            logger.info(f"   Before: {len(sections['before'].split())}w")
            logger.info(f"   After: {len(sections['after'].split())}w")
            
            # Write to Materials.yaml
            self._write_to_materials(material_name, sections, timestamp)
            
            return self._create_result(
                f"Caption generated for {material_name}",
                success=True
            )
            
        except Exception as e:
            logger.error(f"Caption generation failed for {material_name}: {e}")
            return self._create_result("", success=False, error_message=str(e))

    def _extract_sections(self, ai_response: str, material_name: str) -> Dict[str, str]:
        """Extract before/after sections from AI response."""
        
        if not ai_response or not ai_response.strip():
            raise ValueError(f"Empty AI response for {material_name}")
        
        # Try to extract marked sections
        before_match = re.search(r'\*\*BEFORE_TEXT:\*\*\s*(.+?)(?=\*\*AFTER_TEXT:|\Z)', ai_response, re.DOTALL)
        after_match = re.search(r'\*\*AFTER_TEXT:\*\*\s*(.+)', ai_response, re.DOTALL)
        
        if before_match and after_match:
            before_text = before_match.group(1).strip()
            after_text = after_match.group(1).strip()
        else:
            # Fallback: split by paragraph
            paragraphs = [p.strip() for p in ai_response.split('\n\n') if p.strip()]
            
            if len(paragraphs) >= 2:
                before_text = paragraphs[0]
                after_text = paragraphs[1]
            else:
                raise ValueError(
                    f"Could not extract before/after sections for {material_name}. "
                    f"Response: {ai_response[:200]}..."
                )
        
        # Clean up markers
        before_text = re.sub(r'^\*\*(?:BEFORE_TEXT|AFTER_TEXT):\*\*\s*', '', before_text).strip()
        after_text = re.sub(r'^\*\*(?:BEFORE_TEXT|AFTER_TEXT):\*\*\s*', '', after_text).strip()
        
        return {
            'before': before_text,
            'after': after_text
        }

    def _write_to_materials(self, material_name: str, sections: Dict[str, str], timestamp: str):
        """Write caption to Materials.yaml with atomic write."""
        
        materials_path = Path(MATERIALS_DATA_PATH)
        
        # Load Materials.yaml
        with open(materials_path, 'r', encoding='utf-8') as f:
            materials_data = yaml.safe_load(f) or {}
        
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
        
        # Write caption
        materials_section[actual_key]['caption'] = {
            'before': sections['before'],
            'after': sections['after'],
            'generated': timestamp,
            'word_count_before': len(sections['before'].split()),
            'word_count_after': len(sections['after'].split()),
            'total_words': len(sections['before'].split()) + len(sections['after'].split())
        }
        
        # Atomic write using temp file
        temp_fd, temp_path = tempfile.mkstemp(suffix='.yaml', dir=materials_path.parent)
        try:
            os.close(temp_fd)
            with open(temp_path, 'w', encoding='utf-8') as f:
                yaml.dump(materials_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            Path(temp_path).replace(materials_path)
            logger.info(f"✅ Caption written to Materials.yaml → materials.{actual_key}.caption")
            
        except Exception as e:
            if Path(temp_path).exists():
                Path(temp_path).unlink()
            raise e
