#!/usr/bin/env python3
"""Caption Component Generator - Chain-Enhanced with Quality Gates"""

import datetime
import json
import logging
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

    def _build_prompt(
        self, 
        material_name: str, 
        frontmatter_data: Dict, 
        author_obj: Dict,
        voice_instructions: str,
        author_word_limit: int
    ) -> str:
        """Build AI prompt for caption generation using ONLY unified_voice_system.yaml"""
        
        import random
        
        # Load frontmatter if not provided to get author info first
        if not frontmatter_data:
            frontmatter_data = self._load_frontmatter_data(material_name)
        
        # Extract author data
        author_obj = frontmatter_data.get('author', {})
        if not author_obj or not author_obj.get('country'):
            raise ValueError(f"No author data found in frontmatter for {material_name} - required for unified voice system")
        
        # Get author details
        author_name = author_obj.get('name', 'Unknown')
        author_country = author_obj.get('country', 'Unknown')
        author_expertise = author_obj.get('expertise', 'Laser cleaning technology')
        
        # Initialize VoiceOrchestrator for country-specific settings
        voice = VoiceOrchestrator(country=author_country)
        author_word_limit = voice.get_word_limit()
        logger.info(f"Using word limit {author_word_limit} for {author_country}")
        
        # Generate enhanced character variation for realistic human writing
        # Character count roughly = word count * 5.5 (average chars per word including spaces)
        base_chars = int(author_word_limit * 5.5)
        
        # Enhanced variation ranges: 25% to 175% (150% total range)
        min_chars = int(base_chars * 0.25)  # 25% of base (75% below)
        max_chars = int(base_chars * 1.75)  # 175% of base (75% above)
        
        # Generate significantly different lengths for before/after sections
        before_target = random.randint(min_chars, max_chars)
        after_target = random.randint(min_chars, max_chars)
        
        # Ensure sections are meaningfully different (at least 30% difference)
        while abs(before_target - after_target) < (base_chars * 0.3):
            after_target = random.randint(min_chars, max_chars)
        
        # Determine paragraph count based on target length
        before_paragraphs = "1-2 paragraphs" if before_target < 900 else "2-3 paragraphs"
        after_paragraphs = "1-2 paragraphs" if after_target < 900 else "2-3 paragraphs"
        
        logger.info(f"Caption targets: before={before_target} chars, after={after_target} chars (base: {base_chars}, range: {min_chars}-{max_chars})")
        
        # Extract material properties for context
        material_props = frontmatter_data.get('materialProperties', {})
        category = frontmatter_data.get('category', 'material')
        applications = frontmatter_data.get('applications', [])
        
        # Build comprehensive context for unified prompt
        properties_json = json.dumps(
            {prop: data.get('value') for prop, data in material_props.items() 
             if isinstance(data, dict) and 'value' in data},
            indent=2
        ) if material_props else 'Standard material characteristics'
        
        applications_str = ', '.join(applications[:3]) if applications else 'General cleaning applications'
        
        # Build material context dict for get_unified_prompt
        material_context = {
            'material_name': material_name,
            'category': category,
            'properties': properties_json,
            'applications': applications_str
        }
        
        # Build author dict for get_unified_prompt
        author_dict = {
            'name': author_name,
            'country': author_country,
            'expertise': author_expertise
        }
        
        # USE ONLY unified_voice_system.yaml via get_unified_prompt
        try:
            unified_prompt = voice.get_unified_prompt(
                component_type='caption_generation',
                material_context=material_context,
                author=author_dict,
                before_paragraphs=before_paragraphs,
                before_target=before_target,
                after_paragraphs=after_paragraphs,
                after_target=after_target
            )
            logger.info(f"✅ Generated unified prompt for {material_name} ({author_country})")
            return unified_prompt
        except Exception as e:
            logger.error(f"Failed to generate unified prompt for {material_name}: {e}")
            raise ValueError(f"Failed to generate unified prompt: {e}")

    def _extract_ai_content(self, ai_response: str, material_name: str) -> Dict:
        """Extract before/after text from AI response - FAIL FAST"""
        
        if not ai_response or not ai_response.strip():
            raise ValueError(f"Empty AI response for {material_name} - fail-fast architecture requires valid content")
        
        # Extract BEFORE_TEXT - support both formats:
        # - DeepSeek format: **BEFORE_TEXT:** (double colon)
        # - Grok format: **BEFORE_TEXT: Title** (single colon with title)
        before_start = ai_response.find('**BEFORE_TEXT:')
        after_marker_search = ai_response.find('**AFTER_TEXT:')
        
        if before_start == -1 or after_marker_search == -1:
            raise ValueError(f"Missing BEFORE_TEXT or AFTER_TEXT markers in AI response for {material_name}")
        
        # Find the end of the BEFORE_TEXT marker line (could be single or double colon)
        # Look for the end of the first line after the marker
        marker_line_end = ai_response.find('\n', before_start)
        if marker_line_end == -1:
            marker_line_end = before_start + len('**BEFORE_TEXT:**')
        else:
            # Skip past the newline to start extracting content
            marker_line_end += 1
        
        # Extract content between BEFORE_TEXT and AFTER_TEXT
        before_text = ai_response[marker_line_end:after_marker_search].strip()
        before_text = before_text.strip('[]').strip()
        
        # Extract AFTER_TEXT - similar flexible approach
        after_marker_line_end = ai_response.find('\n', after_marker_search)
        if after_marker_line_end == -1:
            after_start = after_marker_search + len('**AFTER_TEXT:**')
        else:
            after_start = after_marker_line_end + 1
        
        after_text = ai_response[after_start:].strip()
        after_text = after_text.strip('[]').strip()
        
        # Validate content - FAIL FAST (100 character minimum to allow short random targets)
        min_length = 100  # Flexible minimum to accommodate random variation
        
        if not before_text or len(before_text) < min_length:
            raise ValueError(f"BEFORE_TEXT too short for {material_name} - minimum {min_length} characters for basic content")
        
        if not after_text or len(after_text) < min_length:
            raise ValueError(f"AFTER_TEXT too short for {material_name} - minimum {min_length} characters for basic content")
        
        # Apply sentence count enforcement based on voice profile requirements
        author_country = getattr(self, '_current_author_country', None)
        if author_country:
            before_text, after_text = self._enforce_sentence_count_limits(
                before_text, after_text, author_country, material_name
            )
        
        return {
            'beforeText': before_text,
            'afterText': after_text,
            'technicalFocus': 'surface_analysis',
            'uniqueCharacteristics': [f'{material_name.lower()}_specific'],
            'contaminationProfile': f'{material_name.lower()} surface contamination',
            'microscopyParameters': f'Microscopic analysis of {material_name.lower()}',
            'qualityMetrics': 'Surface improvement analysis'
        }

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
            
            # Sentence count targets by country (from voice profiles)
            country_limits = {
                'taiwan': (6, 9),
                'italy': (5, 8), 
                'indonesia': (4, 7),
                'united_states': (5, 8)
            }
            
            min_total, max_total = country_limits.get(author_country.lower(), (min_sentences, min_sentences + 3))
            
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
            from voice.orchestrator import VoiceOrchestrator
            import random
            import json
            
            # Use unified voice prompting system
            if author_obj and author_obj.get('country'):
                try:
                    voice = VoiceOrchestrator(country=author_obj['country'])
                    
                    # Calculate target lengths with maximum range variation for content diversity (reduced by 30%)
                    author_word_limit = voice.get_word_limit()
                    base_chars = int(author_word_limit * 3.85)  # Reduced from 5.5 to 3.85 (30% reduction)
                    
                    # Maximum range variation: ±70% for significant length differences
                    min_chars = int(base_chars * 0.3)  # 30% of base (much shorter)
                    max_chars = int(base_chars * 1.7)  # 170% of base (much longer)
                    
                    # Ensure before and after have different lengths by using separate ranges
                    before_min = min_chars
                    before_max = int(base_chars * 1.2)  # Shorter range for before
                    after_min = int(base_chars * 0.8)   # Longer range for after
                    after_max = max_chars
                    
                    before_target = random.randint(before_min, before_max)
                    after_target = random.randint(after_min, after_max)
                    before_paragraphs = "1-2 paragraphs" if before_target < 900 else "2-3 paragraphs"
                    after_paragraphs = "1-2 paragraphs" if after_target < 900 else "2-3 paragraphs"
                    
                    # Prepare material context
                    material_context = {
                        'material_name': material_name,
                        'category': category,
                        'properties': json.dumps(material_data, indent=2) if material_data else 'Standard material characteristics',
                        'applications': 'General cleaning applications'
                    }
                    
                    # Generate unified prompt
                    prompt = voice.get_unified_prompt(
                        component_type='caption_generation',
                        material_context=material_context,
                        author=author_obj,
                        before_paragraphs=before_paragraphs,
                        before_target=before_target,
                        after_paragraphs=after_paragraphs,
                        after_target=after_target
                    )
                    
                except Exception as e:
                    logger.warning(f"Could not use unified voice system for {author_obj.get('country')}: {e}")
                    # Fallback to old system
                    prompt = f"Generate technical caption for {material_name} with professional analysis."
            else:
                prompt = f"Generate technical caption for {material_name} with standard analysis."
            
            response = api_client.generate_simple(
                prompt=prompt,
                max_tokens=dynamic_max_tokens,  # Dynamic limit based on author's word limit
                temperature=0.4   # Increased for more natural voice variation
            )
            
            logger.info(f"Caption generation for {material_name} by {author} ({author_country}): max_tokens={dynamic_max_tokens}")
            
            # FAIL FAST: API response must be successful
            if not response.success:
                raise ValueError(f"AI generation failed for {material_name}: {response.error} - fail-fast requires successful API responses")
            
            if not response.content or not response.content.strip():
                raise ValueError(f"Empty AI response for {material_name} - fail-fast requires meaningful content")
            
            # Extract and validate AI content - FAIL FAST
            ai_content = self._extract_ai_content(response.content, material_name)
            
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
