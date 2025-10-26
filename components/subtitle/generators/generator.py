#!/usr/bin/env python3
"""Subtitle Component Generator - Author Voice Integration (Phase 1)"""

import datetime
import json
import logging
from pathlib import Path
from typing import Dict, Optional
from generators.component_generators import APIComponentGenerator
from utils.config_loader import load_yaml_config
from voice.orchestrator import VoiceOrchestrator

logger = logging.getLogger(__name__)


class SubtitleComponentGenerator(APIComponentGenerator):
    """Generate engaging 8-12 word subtitles with Author Voice"""
    
    def __init__(self):
        super().__init__("subtitle")
    
    def _load_frontmatter_data(self, material_name: str) -> Dict:
        """Load frontmatter data for the material - case-insensitive search"""
        content_dir = Path("content/frontmatter")
        
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
    
    def _build_subtitle_prompt(
        self,
        material_name: str,
        frontmatter_data: Dict,
        target_words: int = 10
    ) -> str:
        """Build AI prompt for subtitle generation using Voice service
        
        Args:
            material_name: Name of the material
            frontmatter_data: Frontmatter data dictionary
            target_words: Target word count (8-12 words)
            
        Returns:
            Complete prompt string for subtitle generation
        """
        # Extract author data
        author_obj = frontmatter_data.get('author', {})
        if not author_obj or not author_obj.get('country'):
            raise ValueError(f"No author data found in frontmatter for {material_name} - required for voice system")
        
        # Get author details
        author_name = author_obj.get('name', 'Unknown')
        author_country = author_obj.get('country', 'Unknown')
        author_expertise = author_obj.get('expertise', 'Laser cleaning technology')
        
        # Initialize VoiceOrchestrator for country-specific voice
        voice = VoiceOrchestrator(country=author_country)
        
        # Extract material properties for context
        material_props = frontmatter_data.get('materialProperties', {})
        category = frontmatter_data.get('category', 'material')
        applications = frontmatter_data.get('applications', [])
        
        # Build comprehensive context
        properties_json = json.dumps(
            {prop: data.get('value') for prop, data in material_props.items() 
             if isinstance(data, dict) and 'value' in data},
            indent=2
        ) if material_props else 'Standard material characteristics'
        
        applications_str = ', '.join(applications[:3]) if applications else 'General cleaning applications'
        
        # Build material context dict
        material_context = {
            'material_name': material_name,
            'category': category,
            'properties': properties_json,
            'applications': applications_str
        }
        
        # Build author dict
        author_dict = {
            'name': author_name,
            'country': author_country,
            'expertise': author_expertise
        }
        
        # Call Voice service to generate subtitle prompt
        try:
            # Generate base prompt from voice system
            prompt = voice.get_unified_prompt(
                component_type='subtitle',
                material_context=material_context,
                author=author_dict,
                section_focus='marketing_tagline',
                section_instruction=f"Write a concise, engaging {target_words}-word subtitle/tagline for {material_name} laser cleaning. Capture the essence of this material in a professional phrase that appeals to technical decision-makers.",
                target_words=target_words,
                style_guidance='concise and professional',
                paragraph_count='single phrase'
            )
            
            # Add explicit word limit enforcement to prompt
            prompt += f"\n\nSTRICT WORD LIMIT: Write EXACTLY {target_words} words (±2 words tolerance).\n"
            prompt += f"FORMAT: Write as a single, concise phrase without punctuation at the end.\n"
            prompt += f"TONE: Professional, engaging, technically accurate.\n"
            prompt += f"TARGET AUDIENCE: Technical professionals and decision-makers in industrial laser cleaning.\n"
            
            logger.info(f"✅ Generated subtitle prompt for {material_name} ({author_country}): {target_words}w")
            return prompt
            
        except Exception as e:
            logger.error(f"Failed to generate subtitle prompt for {material_name}: {e}")
            raise ValueError(f"Failed to generate subtitle prompt: {e}")
    
    def _extract_subtitle_content(self, ai_response: str, material_name: str) -> str:
        """Extract subtitle text from AI response - FAIL FAST
        
        Args:
            ai_response: Raw AI response text
            material_name: Material being processed
            
        Returns:
            Cleaned subtitle text
        """
        if not ai_response or not ai_response.strip():
            raise ValueError(f"Empty AI response for {material_name} subtitle - fail-fast architecture requires valid content")
        
        # Clean the response - remove any formatting artifacts
        content = ai_response.strip()
        
        # Remove common wrapper patterns
        content = content.strip('[]').strip('"').strip("'").strip()
        
        # Remove trailing punctuation if present (subtitles shouldn't have periods)
        if content and content[-1] in '.!?':
            content = content[:-1].strip()
        
        # Validate content - FAIL FAST with word count check
        min_words = 6   # Minimum 6 words for subtitle
        max_words = 15  # Maximum 15 words for subtitle
        word_count = len(content.split())
        
        if not content or word_count < min_words:
            raise ValueError(f"Subtitle too short for {material_name} - {word_count} words < {min_words} minimum")
        
        if word_count > max_words:
            logger.warning(f"Subtitle too long for {material_name} - {word_count} words > {max_words} maximum, trimming...")
            # Trim to max words
            words = content.split()
            content = ' '.join(words[:max_words])
        
        logger.info(f"Extracted subtitle: {len(content)} chars, {len(content.split())} words")
        return content
    
    def _write_subtitle_to_materials(self, material_name: str, subtitle: str, timestamp: str, author: str, author_country: str = None) -> bool:
        """Write subtitle to Materials.yaml with full author metadata"""
        import yaml
        from pathlib import Path
        
        materials_path = Path("data/Materials.yaml")
        
        try:
            # Load Materials.yaml
            with open(materials_path, 'r', encoding='utf-8') as f:
                materials_data = yaml.safe_load(f) or {}
            
            # Find the material in the materials section (case-insensitive lookup)
            if 'materials' not in materials_data:
                logger.error("No 'materials' section found in Materials.yaml")
                return False
            
            actual_material_key = None
            materials_section = materials_data['materials']
            for key in materials_section.keys():
                # Handle space vs underscore variations and case insensitive matching
                key_normalized = key.lower().replace('_', ' ').replace('-', ' ')
                material_normalized = material_name.lower().replace('_', ' ').replace('-', ' ')
                if key_normalized == material_normalized:
                    actual_material_key = key
                    break
            
            if not actual_material_key:
                logger.error(f"Material {material_name} not found in Materials.yaml materials section (checked case-insensitive)")
                return False
            
            # Write subtitle to the 'subtitle' key
            materials_section[actual_material_key]['subtitle'] = subtitle
            
            # Also add metadata about generation
            if 'subtitle_metadata' not in materials_section[actual_material_key]:
                materials_section[actual_material_key]['subtitle_metadata'] = {}
            
            materials_section[actual_material_key]['subtitle_metadata'] = {
                'generated': timestamp,
                'author_name': author,
                'author_country': author_country or 'unknown',
                'generation_method': 'ai_research_voice',
                'word_count': len(subtitle.split()),
                'character_count': len(subtitle)
            }
            
            # Write updated data
            with open(materials_path, 'w', encoding='utf-8') as f:
                yaml.dump(materials_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            logger.info(f"✅ Subtitle written to Materials.yaml → materials.{actual_material_key}.subtitle")
            return True
            
        except Exception as e:
            logger.error(f"Failed to write subtitle to Materials.yaml: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
        **kwargs
    ):
        """Generate AI-powered subtitle content - FAIL FAST ARCHITECTURE with retry logic"""
        
        # FAIL FAST: API client is required - no fallbacks allowed
        if not api_client:
            raise ValueError("API client required for subtitle generation - fail-fast architecture does not allow fallbacks")
        
        # Load frontmatter if not provided - with retry logic
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            if not frontmatter_data:
                frontmatter_data = self._load_frontmatter_data(material_name)
            
            # Extract required data - retry if missing
            author_obj = frontmatter_data.get('author', {}) if frontmatter_data else {}
            
            if author_obj and author_obj.get('name'):
                # Success - author data found
                break
            else:
                retry_count += 1
                if retry_count < max_retries:
                    logger.warning(f"Author data missing for {material_name}, retry {retry_count}/{max_retries}")
                    frontmatter_data = None  # Force reload on next iteration
                    import time
                    time.sleep(0.5)  # Brief delay before retry
                else:
                    # Final retry failed - FAIL FAST
                    raise ValueError(
                        f"Author information required in frontmatter for {material_name} - "
                        f"failed after {max_retries} retries. Fail-fast requires complete metadata."
                    )
        
        # FAIL FAST: Frontmatter is required
        if not frontmatter_data:
            raise ValueError(f"Frontmatter data required for {material_name} - fail-fast architecture requires complete material data")
        
        timestamp = datetime.datetime.now().isoformat() + "Z"
        
        author_name = author_obj.get('name')
        author_country = author_obj.get('country', 'usa')
        
        # Build subtitle prompt and generate content
        try:
            import random
            
            # Target: 8-12 words for subtitle
            target_words = random.randint(8, 12)
            
            logger.info(f"🎭 Generating subtitle for {material_name} ({author_country})")
            logger.info(f"   Target: {target_words} words")
            
            # Build prompt using voice system
            prompt = self._build_subtitle_prompt(
                material_name=material_name,
                frontmatter_data=frontmatter_data,
                target_words=target_words
            )
            
            # Add cache-busting
            import time
            random_seed = random.randint(10000, 99999)
            timestamp_seed = int(time.time() * 1000) % 100000
            prompt = prompt + f"\n\n[Generation ID: {random_seed}-{timestamp_seed}]"
            
            # Generate with API
            response = api_client.generate_simple(
                prompt=prompt,
                max_tokens=100,  # Subtitles are short, 100 tokens is plenty
                temperature=0.6  # Slight creativity for variety
            )
            
            if not response.success:
                raise ValueError(f"Subtitle generation failed for {material_name}: {response.error}")
            
            # Extract subtitle content
            subtitle = self._extract_subtitle_content(response.content, material_name)
            logger.info(f"✅ Generated subtitle: '{subtitle}' ({len(subtitle.split())} words)")
            
        except Exception as e:
            logger.error(f"AI processing failed for {material_name}: {e}")
            raise ValueError(f"Subtitle generation failed for {material_name}: {e}") from e
        
        # Write subtitle to Materials.yaml with full author metadata
        success = self._write_subtitle_to_materials(
            material_name=material_name,
            subtitle=subtitle,
            timestamp=timestamp,
            author=author_name,
            author_country=author_country
        )
        
        if not success:
            raise ValueError(f"Failed to write subtitle to Materials.yaml for {material_name}")
        
        return self._create_result(
            f"Subtitle generated and written to Materials.yaml for {material_name}: '{subtitle}'",
            success=True
        )


class SubtitleGenerator:
    """FAIL-FAST Subtitle Generator - requires API client"""
    
    def __init__(self):
        self.generator = SubtitleComponentGenerator()
    
    def generate(self, material: str, material_data: Dict = None, api_client=None) -> str:
        """Generate subtitle content - FAIL FAST if API client missing"""
        
        if not api_client:
            raise ValueError("API client required for subtitle generation - fail-fast architecture does not allow fallbacks")
        
        result = self.generator.generate(material, material_data or {}, api_client=api_client)
        
        if not result.success:
            raise ValueError(f"Subtitle generation failed for {material}: {result.error_message}")
        
        return result.content


def generate_subtitle_content(material: str, material_data: Dict = None, api_client=None) -> str:
    """Generate subtitle content - FAIL FAST architecture"""
    
    if not api_client:
        raise ValueError("API client required for subtitle content generation - fail-fast architecture does not allow fallbacks")
    
    generator = SubtitleGenerator()
    return generator.generate(material, material_data, api_client)
