#!/usr/bin/env python3
"""Subtitle Component Generator - Simple 7-12 word subtitle generation."""

import datetime
import logging
import os
import random
import tempfile
import yaml
from pathlib import Path
from typing import Dict, Tuple
from generators.component_generators import APIComponentGenerator
from voice.post_processor import VoicePostProcessor

logger = logging.getLogger(__name__)

# ============================================================================
# SUBTITLE CONFIGURATION
# ============================================================================
# Configuration Constants
SUBTITLE_WORD_COUNT_RANGE = (6, 10)  # Increased 25% from 5-8
SUBTITLE_VOICE_INTENSITY = 2  # Reduced from 3 for lighter voice
SUBTITLE_TECHNICAL_INTENSITY = 3  # Increased to 3 for moderate technical content

# Generation settings
SUBTITLE_GENERATION_TEMPERATURE = 0.6
SUBTITLE_MAX_TOKENS = 100

# Data file paths
MATERIALS_DATA_PATH = "data/Materials.yaml"

# ============================================================================


class SubtitleComponentGenerator(APIComponentGenerator):
    """
    Generate material-specific subtitle/tagline.
    Voice enhancement handled by separate VoicePostProcessor.
    """
    
    def __init__(self):
        super().__init__("subtitle")

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

    def build_research_subtitle_prompt(self, material_name: str, word_count_range: Tuple[int, int], technical_intensity: int = 3) -> str:
        """
        Build research-based subtitle prompt (simplified version of FAQ prompt).
        
        This is a condensed 1-step version of the FAQ's 3-step research process,
        designed for quick tagline generation.
        
        Args:
            material_name: Name of the material
            word_count_range: (min, max) word count tuple
            technical_intensity: Technical complexity level 1-5
            
        Returns:
            str: The subtitle prompt
        """
        min_words, max_words = word_count_range
        technical_guidance = self._get_technical_guidance(technical_intensity)
        
        return f"""You are an expert in laser cleaning technologies specializing in creating compelling, SEO-optimized taglines for materials like {material_name}.

TASK: Create a {min_words}-{max_words} word subtitle/tagline for laser cleaning of {material_name}.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 LANGUAGE COMPLEXITY REQUIREMENT (HIGHEST PRIORITY):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{technical_guidance}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

QUICK RESEARCH CONTEXT (consider these to inform your tagline):
1. What makes {material_name} unique or valuable?
2. What is the #1 cleaning challenge for {material_name}?
3. What is the key benefit of laser cleaning for {material_name}?

REQUIREMENTS:
- Length: EXACTLY {min_words}-{max_words} words
- Include "{material_name}" in the tagline
- Highlight laser cleaning's primary advantage for this material
- Make it compelling and benefit-focused
- Use appropriate technical language per intensity guidance above
- Natural, professional tone (not salesy or hyperbolic)

EXAMPLES (for inspiration, not to copy):
- "Non-Thermal Laser Cleaning Preserves Steel's Metallurgical Integrity" (7 words)
- "Precision Oxide Removal Without Substrate Damage" (6 words)
- "Gentle Surface Restoration for Delicate Historical Materials" (7 words)

Generate ONLY the subtitle text - no quotes, no extra text, no explanations.
Your {min_words}-{max_words} word subtitle for {material_name}:"""

    def build_subtitle_prompt(self, material_name: str, word_count_range: Tuple[int, int], technical_intensity: int = 3) -> str:
        """
        Build fixed subtitle prompt template.
        
        Args:
            material_name: Name of the material
            word_count_range: (min, max) word count tuple
            technical_intensity: Technical complexity level 1-5 (default: 3)
            
        Returns:
            str: The prompt template
        """
        min_words, max_words = word_count_range
        technical_guidance = self._get_technical_guidance(technical_intensity)
        
        return f"""Generate an engaging, punchy subtitle for laser cleaning of {material_name}.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 LANGUAGE COMPLEXITY REQUIREMENT (HIGHEST PRIORITY - OVERRIDE ALL OTHER INSTRUCTIONS):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{technical_guidance}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Create a compelling {min_words}-{max_words} word subtitle that:
- Highlights unique laser cleaning benefits for {material_name}
- Uses active, powerful language
- Appeals to technical professionals
- Avoids clichés and generic phrases

REQUIREMENTS:
- Exactly {min_words}-{max_words} words
- Professional, technical tone
- Specific to {material_name} properties
- Memorable and engaging

Generate the subtitle now (output ONLY the subtitle text, no quotes or formatting):"""

    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author: dict = None,
        **kwargs
    ):
        """
        Generate subtitle content using fixed prompt template.
        
        Args:
            material_name: Name of the material
            material_data: Material properties dictionary (for future use)
            api_client: API client for generation (required)
            author: Author dictionary with 'country' key for voice enhancement (optional)
            **kwargs: Additional parameters (accepted for compatibility)
            
        Returns:
            ComponentResult with generated subtitle content
        """
        if not api_client:
            return self._create_result("", success=False, error_message="API client required")
        
        # Generate random target word count
        # Compensate for voice enhancement if author provided (reduce by ~2 words for subtitles)
        base_range = SUBTITLE_WORD_COUNT_RANGE
        if author and 'country' in author:
            # Reduce range to compensate for voice enhancement word additions
            # Smaller reduction for subtitles since they're shorter
            adjusted_range = (base_range[0], max(base_range[0], base_range[1] - 2))
            target_words = random.randint(adjusted_range[0], adjusted_range[1])
        else:
            target_words = random.randint(base_range[0], base_range[1])
        
        timestamp = datetime.datetime.now().isoformat() + "Z"
        
        logger.info(f"🎭 Generating subtitle for {material_name}")
        logger.info(f"   Target: {target_words} words")
        
        try:
            # Build prompt with technical intensity
            prompt = self.build_subtitle_prompt(material_name, target_words, SUBTITLE_TECHNICAL_INTENSITY)
            
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
                return self._create_result("", success=False, error_message=f"API generation failed: {response.error}")
            
            # Clean subtitle
            subtitle = response.content.strip()
            subtitle = subtitle.strip('"\'')  # Remove quotes
            
            # Apply voice enhancement if author provided (using BATCH for consistency)
            if author and 'country' in author:
                try:
                    voice_processor = VoicePostProcessor(api_client)
                    
                    # Create subtitle item for batch processing (using FAQ structure)
                    subtitle_items = [{'question': 'Subtitle:', 'answer': subtitle}]
                    
                    logger.info(f"🎭 Batch enhancing subtitle with {author.get('country', 'Unknown')} voice (intensity={SUBTITLE_VOICE_INTENSITY})...")
                    
                    # Use BATCH enhancement for consistency with FAQ/Caption architecture
                    enhanced_items = voice_processor.enhance_batch(
                        faq_items=subtitle_items,
                        author=author,
                        marker_distribution='varied',
                        preserve_length=True,
                        length_tolerance=3,
                        voice_intensity=SUBTITLE_VOICE_INTENSITY
                    )
                    
                    # Extract enhanced subtitle (answer field contains the enhanced text)
                    subtitle = enhanced_items[0]['answer']
                    
                except Exception as e:
                    logger.warning(f"Voice enhancement failed: {e}")
                    # Continue with original content
                    pass
            
            word_count = len(subtitle.split())
            logger.info(f"✅ Generated subtitle: '{subtitle}' ({word_count}w)")
            
            # Write to Materials.yaml
            self._write_to_materials(material_name, subtitle, timestamp, word_count)
            
            return self._create_result(
                f"Subtitle generated for {material_name}",
                success=True
            )
            
        except Exception as e:
            logger.error(f"Subtitle generation failed for {material_name}: {e}")
            return self._create_result("", success=False, error_message=str(e))

    def _write_to_materials(self, material_name: str, subtitle: str, timestamp: str, word_count: int):
        """Write subtitle to Materials.yaml with atomic write."""
        
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
        
        # Write subtitle
        materials_section[actual_key]['subtitle'] = {
            'text': subtitle,
            'generated': timestamp,
            'word_count': word_count
        }
        
        # Atomic write using temp file
        temp_fd, temp_path = tempfile.mkstemp(suffix='.yaml', dir=materials_path.parent)
        try:
            os.close(temp_fd)
            with open(temp_path, 'w', encoding='utf-8') as f:
                yaml.dump(materials_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            Path(temp_path).replace(materials_path)
            logger.info(f"✅ Subtitle written to Materials.yaml → materials.{actual_key}.subtitle")
            
        except Exception as e:
            if Path(temp_path).exists():
                Path(temp_path).unlink()
            raise e
