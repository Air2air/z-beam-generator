#!/usr/bin/env python3
"""Caption Component Generator - Chain-Enhanced with Quality Gates"""

import datetime
import json
import logging
import time
from pathlib import Path
from typing import Dict, Optional, List
from generators.component_generators import APIComponentGenerator
from utils.config_loader import load_yaml_config
from utils.requirements_loader import RequirementsLoader
from voice.orchestrator import VoiceOrchestrator

# Import the new chain components and grader
try:
    import sys
    sys.path.append(str(Path(__file__).parent.parent))
    from copilot_grader import CopilotQualityGrader
    from chain_generator_prototype import VoiceProfileSelector, ContextAnalyzer, RealTimeValidator
except ImportError:
    CopilotQualityGrader = None
    VoiceProfileSelector = None
    ContextAnalyzer = None
    RealTimeValidator = None

logger = logging.getLogger(__name__)

class CaptionComponentGenerator(APIComponentGenerator):
    def __init__(self):
        super().__init__("caption")

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

    def _build_single_section_prompt(
        self, 
        material_name: str, 
        frontmatter_data: Dict,
        section_type: str,  # "before" or "after"
        target_words: int,
        style_guidance: str,
        paragraph_count: str
    ) -> str:
        """Build AI prompt for a single caption section (before OR after) using Voice service
        
        Args:
            material_name: Name of the material
            frontmatter_data: Frontmatter data dictionary
            section_type: "before" (contaminated) or "after" (cleaned)
            target_words: Target word count for this section
            style_guidance: Style hint ("brief and focused", "moderate detail", "comprehensive")
            paragraph_count: Paragraph guidance ("1 concise paragraph", "1-2 paragraphs", etc.)
            
        Returns:
            Complete prompt string for single section generation
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
        
        # Determine section-specific context
        if section_type == "before":
            section_focus = "contaminated surface microscopy"
            section_instruction = "Describe the contaminated surface condition, contaminant characteristics, and surface degradation"
        else:  # after
            section_focus = "cleaned surface restoration"
            section_instruction = "Describe the cleaned surface condition, restoration quality, and material integrity"
        
        # Call Voice service to generate prompt
        try:
            prompt = voice.get_unified_prompt(
                component_type='microscopy_description',
                material_context=material_context,
                author=author_dict,
                section_focus=section_focus,
                section_instruction=section_instruction,
                target_words=target_words,
                style_guidance=style_guidance,
                paragraph_count=paragraph_count
            )
            logger.info(f"✅ Generated {section_type} prompt for {material_name} ({author_country}): {target_words}w, {style_guidance}")
            return prompt
        except Exception as e:
            logger.error(f"Failed to generate {section_type} prompt for {material_name}: {e}")
            raise ValueError(f"Failed to generate {section_type} prompt: {e}")

    def _extract_single_section_content(self, ai_response: str, material_name: str, section_type: str) -> str:
        """Extract single section text from AI response - FAIL FAST
        
        Args:
            ai_response: Raw AI response text
            material_name: Material being processed
            section_type: "before" or "after" for logging
            
        Returns:
            Cleaned section text
        """
        if not ai_response or not ai_response.strip():
            raise ValueError(f"Empty AI response for {material_name} {section_type} - fail-fast architecture requires valid content")
        
        # Clean the response - remove any formatting artifacts
        content = ai_response.strip()
        
        # Remove common AI response wrappers if present
        if content.startswith('**BEFORE_TEXT:**') or content.startswith('**AFTER_TEXT:**'):
            first_newline = content.find('\n')
            if first_newline != -1:
                content = content[first_newline+1:].strip()
        
        # Remove common wrapper patterns
        content = content.strip('[]').strip()
        
        # Validate content - FAIL FAST (100 character minimum to allow short random targets)
        min_length = 100  # Flexible minimum to accommodate random variation
        
        if not content or len(content) < min_length:
            raise ValueError(f"{section_type.upper()}_TEXT too short for {material_name} - minimum {min_length} characters for basic content")
        
        logger.info(f"Extracted {section_type} section: {len(content)} chars, {len(content.split())} words")
        return content

    def _enforce_sentence_count_limits(self, before_text: str, after_text: str, 
                                     author_country: str, material_name: str) -> tuple[str, str]:
        """
        Enforce sentence count limits based on voice profile requirements.
        
        Args:
            before_text: Generated before text
            after_text: Generated after text  
            author_country: Author's country for voice profile lookup
            material_name: Material name for logging
            
        Returns:
            Tuple of (trimmed_before_text, trimmed_after_text)
        """
        try:
            from voice.orchestrator import VoiceOrchestrator
            import re
            
            # Get voice profile requirements
            voice = VoiceOrchestrator(author_country)
            profile = voice.profile
            caption_adaptation = profile.get('voice_adaptation', {}).get('caption_generation', {})
            validation_req = caption_adaptation.get('validation_requirements', {})
            min_sentences = validation_req.get('minimum_sentences', 5)
            
            # PERCENTAGE-BASED sentence count enforcement
            # Allows sentence counts to scale with character targets (25%-175% variation)
            # This enables true word count variation while maintaining voice authenticity
            
            # Calculate expected sentence count from COMBINED before+after character targets
            # Stored in instance during prompt generation for consistency
            total_target_chars = getattr(self, '_current_char_target', None)
            
            if total_target_chars:
                # Average sentence length: 60-80 chars (including spaces/punctuation)
                # Use 70 chars as baseline for calculation
                baseline_sentence_count = total_target_chars / 70
                
                # Allow 50% below to 150% above baseline (wide variation range)
                min_total = max(3, int(baseline_sentence_count * 0.5))   # At least 3 sentences
                max_total = int(baseline_sentence_count * 2.5)           # Up to 250% of baseline
                
                logger.info(f"Percentage-based limits for {material_name}: "
                          f"target_chars={total_target_chars}, "
                          f"baseline_sentences={baseline_sentence_count:.1f}, "
                          f"range={min_total}-{max_total}")
            else:
                # Fallback to country-based limits if character targets not available
                country_limits = {
                    'taiwan': (12, 30),
                    'italy': (8, 22),
                    'indonesia': (8, 20),
                    'united_states': (10, 25)
                }
                min_total, max_total = country_limits.get(author_country.lower(), (min_sentences, min_sentences + 10))
                logger.warning(f"Using fallback country limits for {material_name}: {min_total}-{max_total}")
            
            # Split into sentences
            def split_sentences(text: str) -> list[str]:
                return [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
            
            before_sentences = split_sentences(before_text)
            after_sentences = split_sentences(after_text)
            total_sentences = len(before_sentences) + len(after_sentences)
            
            logger.info(f"Sentence count enforcement for {material_name} ({author_country}): "
                       f"{len(before_sentences)}+{len(after_sentences)}={total_sentences} "
                       f"(target: {min_total}-{max_total})")
            
            # If within limits, return unchanged
            if min_total <= total_sentences <= max_total:
                logger.info(f"✅ Sentence count compliant for {material_name}")
                return before_text, after_text
            
            # If over limit, trim sentences intelligently
            if total_sentences > max_total:
                sentences_to_remove = total_sentences - max_total
                logger.warning(f"⚠️ Trimming {sentences_to_remove} sentences from {material_name} "
                             f"({total_sentences} -> {max_total})")
                
                # Distribute removal between sections (prefer removing from longer section)
                if len(before_sentences) > len(after_sentences):
                    # Remove more from before section
                    before_remove = min(sentences_to_remove - sentences_to_remove // 2, 
                                      len(before_sentences) - 2)  # Keep at least 2 sentences
                    after_remove = sentences_to_remove - before_remove
                else:
                    # Remove more from after section  
                    after_remove = min(sentences_to_remove - sentences_to_remove // 2,
                                     len(after_sentences) - 2)  # Keep at least 2 sentences
                    before_remove = sentences_to_remove - after_remove
                
                # Trim sentences (remove from end to preserve opening technical phrases)
                if before_remove > 0:
                    before_sentences = before_sentences[:-before_remove]
                if after_remove > 0:
                    after_sentences = after_sentences[:-after_remove]
                
                # Reconstruct text
                before_text = '. '.join(before_sentences) + '.' if before_sentences else before_text
                after_text = '. '.join(after_sentences) + '.' if after_sentences else after_text
                
                new_total = len(before_sentences) + len(after_sentences)
                logger.info(f"✅ Trimmed {material_name} to {new_total} sentences "
                           f"({len(before_sentences)}+{len(after_sentences)})")
            
            # If under limit, log but don't modify (AI should generate enough content)
            elif total_sentences < min_total:
                logger.warning(f"⚠️ {material_name} has too few sentences ({total_sentences} < {min_total}) "
                             f"- consider adjusting prompts")
            
            return before_text, after_text
            
        except Exception as e:
            logger.error(f"Error in sentence count enforcement for {material_name}: {e}")
            # Return original text if enforcement fails
            return before_text, after_text

    def _calculate_author_token_limit(self, author_country: str) -> int:
        """
        Calculate max_tokens based on author's word limit.
        
        Author word limits (per persona config):
        - Taiwan: 380 words → 456 tokens
        - Italy: 450 words → 540 tokens  
        - Indonesia: 250 words → 300 tokens
        - USA: 196 words → 350 tokens
        
        Using rough conversion: 1 token ≈ 0.75 words for technical content
        Formula: (word_limit / 0.75) * 0.9 safety margin
        """
        # Author word limits from OPTIMIZER_CONFIG personas (reduced by 30%)
        word_limits = {
            "taiwan": 266,    # 380 * 0.7
            "italy": 315,     # 450 * 0.7
            "indonesia": 175, # 250 * 0.7
            "usa": 196        # 280 * 0.7
        }
        
        country_key = author_country.lower()
        word_limit = word_limits.get(country_key, 320)  # Default to USA if unknown
        
        # Convert words to tokens with generous margin for BEFORE + AFTER sections
        # token_to_word_ratio ≈ 0.75 for technical content
        # Reduced token limits by 30%
        if country_key == "usa":
            max_tokens = 800  # Maximum tokens for complete voice generation
        else:
            max_tokens = int((word_limit / 0.75) * 1.5)  # 1.5x multiplier for full voice preservation
        
        logger.info(f"Author {country_key}: word_limit={word_limit} → max_tokens={max_tokens}")
        
        return max_tokens

    def _validate_against_requirements(self, before_text: str, after_text: str, 
                                      author_country: str, material_name: str) -> List[str]:
        """
        Validate generated caption against requirements.yaml rules.
        
        Validates:
        - Text quality: prohibited patterns, formatting rules
        - Author voice: country-specific vocabulary and patterns
        - Quality thresholds: minimum standards
        
        Returns list of validation issues (empty if all pass)
        """
        issues = []
        loader = RequirementsLoader()
        
        # Combine texts for validation
        combined_text = f"{before_text} {after_text}"
        
        # 1. Check prohibited patterns
        markdown_patterns = loader.get_prohibited_text_patterns("markdown")
        for pattern in markdown_patterns:
            if pattern in combined_text:
                issues.append(f"Contains prohibited markdown pattern: '{pattern}'")
        
        placeholder_patterns = loader.get_prohibited_text_patterns("placeholders")
        for pattern in placeholder_patterns:
            if pattern.lower() in combined_text.lower():
                issues.append(f"Contains placeholder text: '{pattern}'")
        
        # 2. Check formatting rules
        if '  ' in combined_text:  # Double spaces
            issues.append("Contains double spaces")
        
        if combined_text != combined_text.strip():
            issues.append("Contains leading/trailing whitespace")
        
        # 3. Check author voice characteristics
        voice_req = loader.get_author_voice_requirements(author_country)
        if voice_req:
            vocab_indicators = voice_req.get('vocabulary_indicators', {})
            primary_vocab = vocab_indicators.get('primary', [])
            
            # Count primary vocabulary matches
            text_lower = combined_text.lower()
            matches = sum(1 for word in primary_vocab if word.lower() in text_lower)
            
            validation_thresholds = voice_req.get('validation_thresholds', {})
            min_indicators = validation_thresholds.get('minimum_indicators', 2)
            
            if matches < min_indicators:
                issues.append(f"Insufficient {author_country} voice indicators: {matches} < {min_indicators} (expected words like: {', '.join(primary_vocab[:3])})")
        
        # 4. Check minimum length
        if len(before_text) < 100:
            issues.append(f"beforeText too short: {len(before_text)} chars < 100 chars minimum")
        
        if len(after_text) < 100:
            issues.append(f"afterText too short: {len(after_text)} chars < 100 chars minimum")
        
        return issues

    def _write_caption_to_materials(self, material_name: str, caption_data: Dict) -> bool:
        """Write caption data to Materials.yaml under 'caption' key"""
        import yaml
        from pathlib import Path
        from datetime import datetime, timezone
        
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
            
            # Write caption data to the 'caption' key
            before_text = caption_data['before_text']
            after_text = caption_data['after_text']
            
            materials_section[actual_material_key]['caption'] = {
                'beforeText': before_text,
                'afterText': after_text,
                'generated': caption_data['generated'],
                'author': caption_data['author'],
                'generation_method': caption_data['generation_method'],
                'word_count': {
                    'before': len(before_text.split()),
                    'after': len(after_text.split())
                },
                'character_count': {
                    'before': len(before_text),
                    'after': len(after_text)
                }
            }
            
            # Write updated data (no backup needed for frequent updates)
            with open(materials_path, 'w', encoding='utf-8') as f:
                yaml.dump(materials_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            logger.info(f"✅ Caption data written to Materials.yaml → materials.{actual_material_key}.caption")
            return True
            
        except Exception as e:
            logger.error(f"Failed to write caption data to Materials.yaml: {e}")
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
        **kwargs  # Accept enforce_completeness and other optional parameters
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
        author_country = author_obj.get('country', 'usa')  # Default to USA if country not specified
        self._current_author_country = author_country  # Store for sentence count enforcement
        category = frontmatter_data.get('category')
        if not category:
            raise ValueError(f"Material category required in frontmatter for {material_name} - fail-fast requires complete classification")
        
        # Calculate dynamic token limit based on author's word limit
        dynamic_max_tokens = self._calculate_author_token_limit(author_country)
        
        # Build AI prompt and generate content using unified voice system
        try:
            import random
            
            # Use unified voice prompting system
            if author_obj and author_obj.get('country'):
                # Word range: 20-80 words per section (110-440 chars @ 5.5 chars/word)
                # Total caption range: 40-160 words
                min_section_chars = 110   # 20 words minimum per section
                max_section_chars = 440   # 80 words maximum per section
                
                # Each section gets independent range
                before_target = random.randint(min_section_chars, max_section_chars)
                after_target = random.randint(min_section_chars, max_section_chars)
                
                # Calculate word targets and style guidance
                before_words = int(before_target / 5.5)
                after_words = int(after_target / 5.5)
                
                # Before section guidance
                if before_target < 220:  # 20-40 words
                    before_paragraphs = "1 concise paragraph"
                    before_style = "brief and focused"
                elif before_target < 330:  # 40-60 words
                    before_paragraphs = "1-2 paragraphs"
                    before_style = "moderate detail"
                else:  # 60-80 words
                    before_paragraphs = "2 paragraphs"
                    before_style = "comprehensive and detailed"
                
                # After section guidance
                if after_target < 220:
                    after_paragraphs = "1 concise paragraph"
                    after_style = "brief and focused"
                elif after_target < 330:
                    after_paragraphs = "1-2 paragraphs"
                    after_style = "moderate detail"
                else:
                    after_paragraphs = "2 paragraphs"
                    after_style = "comprehensive and detailed"
                
                # Store combined character target for percentage-based sentence enforcement
                self._current_char_target = before_target + after_target
                logger.info(f"Caption targets: before={before_target} chars ({before_words}w, {before_style}), after={after_target} chars ({after_words}w, {after_style})")
                
                # ========================================
                # CAPTION-SPECIFIC DUAL GENERATION LOGIC
                # Voice is called TWICE independently via _build_single_section_prompt()
                # ========================================
                
                logger.info(f"🎭 Generating dual-section caption for {material_name}")
                logger.info(f"   Before: {before_words}w ({before_style}), After: {after_words}w ({after_style})")
                
                # CALL 1: Generate BEFORE section (contaminated surface)
                before_prompt = self._build_single_section_prompt(
                    material_name=material_name,
                    frontmatter_data=frontmatter_data,
                    section_type="before",
                    target_words=before_words,
                    style_guidance=before_style,
                    paragraph_count=before_paragraphs
                )
                
                # Add cache-busting for before section
                random_seed_before = random.randint(10000, 99999)
                timestamp_before = int(time.time() * 1000) % 100000
                before_prompt = before_prompt + f"\n\n[Generation ID: {random_seed_before}-{timestamp_before}]"
                
                before_response = api_client.generate_simple(
                    prompt=before_prompt,
                    max_tokens=dynamic_max_tokens // 2,  # Half for each section
                    temperature=0.7   # Natural variation
                )
                
                if not before_response.success:
                    raise ValueError(f"BEFORE generation failed for {material_name}: {before_response.error}")
                
                # Extract BEFORE content
                before_text = self._extract_single_section_content(before_response.content, material_name, "before")
                logger.info(f"✅ BEFORE section: {len(before_text.split())} words")
                
                # CALL 2: Generate AFTER section (cleaned surface)
                after_prompt = self._build_single_section_prompt(
                    material_name=material_name,
                    frontmatter_data=frontmatter_data,
                    section_type="after",
                    target_words=after_words,
                    style_guidance=after_style,
                    paragraph_count=after_paragraphs
                )
                
                # Add cache-busting for after section
                random_seed_after = random.randint(10000, 99999)
                timestamp_after = int(time.time() * 1000) % 100000
                after_prompt = after_prompt + f"\n\n[Generation ID: {random_seed_after}-{timestamp_after}]"
                
                after_response = api_client.generate_simple(
                    prompt=after_prompt,
                    max_tokens=dynamic_max_tokens // 2,  # Half for each section
                    temperature=0.7   # Natural variation
                )
                
                if not after_response.success:
                    raise ValueError(f"AFTER generation failed for {material_name}: {after_response.error}")
                
                # Extract AFTER content
                after_text = self._extract_single_section_content(after_response.content, material_name, "after")
                logger.info(f"✅ AFTER section: {len(after_text.split())} words")
                
                # Combine into caption content structure
                ai_content = {
                    'beforeText': before_text,
                    'afterText': after_text,
                    'technicalFocus': 'surface_analysis',
                    'uniqueCharacteristics': [f'{material_name.lower()}_specific'],
                    'contaminationProfile': f'{material_name.lower()} surface contamination',
                    'microscopyParameters': f'Microscopic analysis of {material_name.lower()}',
                    'qualityMetrics': 'Surface improvement analysis'
                }
                
                logger.info(f"📊 Caption complete: {len(before_text.split())} before + {len(after_text.split())} after = {len(before_text.split()) + len(after_text.split())} total words")
            else:
                raise ValueError(f"No author data available for {material_name} - fail-fast requires author information")
            
            # POST-PROCESSING VALIDATION using requirements.yaml
            validation_issues = self._validate_against_requirements(
                ai_content['beforeText'],
                ai_content['afterText'],
                author_country,
                material_name
            )
            
            if validation_issues:
                logger.warning(f"Caption validation issues for {material_name}:")
                for issue in validation_issues:
                    logger.warning(f"  - {issue}")
                # Don't fail-fast on validation warnings, but log them
                
        except Exception as e:
            logger.error(f"AI processing failed for {material_name}: {e}")
            raise ValueError(f"Caption generation failed for {material_name}: {e} - fail-fast architecture requires successful processing") from e
        
        # Write caption data directly to Materials.yaml
        caption_data = {
            'before_text': ai_content['beforeText'],
            'after_text': ai_content['afterText'],
            'generated': timestamp,
            'author': author,
            'generation_method': 'ai_research'
        }
        
        # Write to Materials.yaml
        success = self._write_caption_to_materials(material_name, caption_data)
        
        if not success:
            raise ValueError(f"Failed to write caption data to Materials.yaml for {material_name} - fail-fast requires successful data storage")
        
        return self._create_result(f"Caption data written to Materials.yaml for {material_name}", success=True)

    def generate_with_quality_assessment(
        self, 
        material_name: str, 
        material_data: Dict, 
        api_client=None,
        quality_threshold: int = 75
    ):
        """
        Generate caption with integrated quality assessment and retry logic.
        Uses chain-based approach with real-time validation and quality gates.
        """
        
        # Initialize chain components if available
        if CopilotQualityGrader:
            grader = CopilotQualityGrader()
            
            # Attempt generation with quality assessment
            for attempt in range(2):  # Max 2 attempts
                try:
                    # Generate using existing system
                    result = self.generate(material_name, material_data, api_client)
                    
                    if not result.success:
                        continue
                    
                    # Extract generated content for quality assessment
                    caption_data = self._extract_caption_data(result.content)
                    if not caption_data:
                        continue
                    
                    before_text = caption_data.get('before_text', '')
                    after_text = caption_data.get('after_text', '')
                    
                    # Determine expected country from frontmatter or default
                    expected_country = self._determine_country(material_data)
                    
                    # Assess quality
                    grade = grader.grade_caption(
                        material=material_name,
                        before_text=before_text,
                        after_text=after_text,
                        expected_country=expected_country
                    )
                    
                    # Log quality metrics
                    logger.info(f"Quality Assessment for {material_name}:")
                    logger.info(f"  Overall Score: {grade.overall_score}/100")
                    logger.info(f"  Voice Authenticity: {grade.voice_authenticity.overall_authenticity}/100")
                    logger.info(f"  AI Human-likeness: {grade.ai_detectability.human_likeness}/100")
                    logger.info(f"  Production Ready: {grade.production_ready}")
                    
                    # Check quality threshold
                    if grade.overall_score >= quality_threshold and grade.production_ready:
                        logger.info(f"✅ Quality gates passed for {material_name}")
                        
                        # Enhance result with quality metrics
                        enhanced_result = self._create_result(
                            result.content,
                            success=True,
                            metadata={
                                'quality_score': grade.overall_score,
                                'voice_authenticity': grade.voice_authenticity.overall_authenticity,
                                'ai_human_likeness': grade.ai_detectability.human_likeness,
                                'detected_country': grade.voice_authenticity.detected_country,
                                'production_ready': grade.production_ready,
                                'quality_assessment_enabled': True
                            }
                        )
                        return enhanced_result
                    else:
                        logger.warning(f"⚠️ Quality threshold not met for {material_name} (attempt {attempt + 1})")
                        logger.warning(f"  Score: {grade.overall_score}/{quality_threshold}")
                        if grade.recommendations:
                            logger.warning(f"  Recommendations: {grade.recommendations}")
                        
                        if attempt == 0:  # Try once more with different parameters
                            continue
                
                except Exception as e:
                    logger.error(f"Quality assessment failed for {material_name}: {e}")
                    if attempt == 0:
                        continue
                    break
            
            # If we reach here, quality assessment failed or threshold not met
            logger.warning(f"⚠️ Falling back to standard generation for {material_name}")
        
        # Fallback to standard generation without quality assessment
        return self.generate(material_name, material_data, api_client)
    
    def _extract_caption_data(self, content: str) -> Optional[Dict]:
        """Extract caption data from generation result"""
        try:
            # The content should contain the generated caption data
            # This is a simplified extraction - would need to match actual format
            if "Caption data written to Materials.yaml" in content:
                # Load from Materials.yaml to get the actual generated content
                materials_path = Path("data/Materials.yaml")
                if materials_path.exists():
                    import yaml
                    with open(materials_path, 'r') as f:
                        data = yaml.safe_load(f)
                    
                    # Extract material name from content (simplified)
                    for material, material_data in data['materials'].items():
                        if 'captions' in material_data:
                            return material_data['captions']
                
            return None
        except Exception as e:
            logger.error(f"Failed to extract caption data: {e}")
            return None
    
    def _determine_country(self, material_data: Dict) -> str:
        """Determine expected country from material data or frontmatter"""
        # Try to extract from frontmatter if available
        frontmatter = material_data.get('frontmatter', {})
        author_info = frontmatter.get('author', {})
        
        if isinstance(author_info, dict):
            country = author_info.get('country', '')
            if country:
                # Normalize country name
                country_map = {
                    'Taiwan': 'taiwan',
                    'Italy': 'italy', 
                    'Indonesia': 'indonesia',
                    'United States': 'united_states',
                    'USA': 'united_states'
                }
                return country_map.get(country, 'united_states')
        
        # Default fallback
        return 'united_states'


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
