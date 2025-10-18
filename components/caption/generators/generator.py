#!/usr/bin/env python3
"""Caption Component Generator - AI-Enhanced"""

import datetime
import json
import logging
from pathlib import Path
from typing import Dict, Optional
from generators.component_generators import APIComponentGenerator
from utils.config_loader import load_yaml_config
from voice.orchestrator import VoiceOrchestrator

logger = logging.getLogger(__name__)

class CaptionComponentGenerator(APIComponentGenerator):
    def __init__(self):
        super().__init__("caption")

    def _format_ai_evasion_instructions(self, ai_params: Dict, country: str) -> str:
        """Format AI-evasion parameters into prompt instructions"""
        if not ai_params:
            return ""
        
        # Extract universal rules
        sentence_targets = ai_params.get('sentence_length_targets', {})
        hesitation_rate = ai_params.get('hesitation_markers_per_200_words', 1.5)
        comma_splice_rate = ai_params.get('comma_splices_per_100_words', 1.0)
        parenthetical_rate = ai_params.get('parenthetical_asides_per_300_words', 2.0)
        lexical_target = ai_params.get('lexical_variety_target', 0.65)
        
        # Extract author-specific rules
        author_specific = ai_params.get('author_specific', {})
        
        instructions = f"""
CRITICAL ANTI-AI-DETECTION INSTRUCTIONS (Mandatory for Natural Human Writing):

1. SENTENCE LENGTH VARIATION (REQUIRED - No Monotonous Patterns):
   - Very short (5-8 words): ~{sentence_targets.get('very_short', 15)}% of sentences
   - Medium (10-18 words): ~{sentence_targets.get('medium', 35)}% of sentences  
   - Long (20-28 words): ~{sentence_targets.get('long', 35)}% of sentences
   - Very long (30+ words): ~{sentence_targets.get('very_long', 15)}% of sentences
   - MIX UNPREDICTABLY: SHORT → LONG → MEDIUM → SHORT (never uniform 15-20 word pattern)

2. NATURAL HUMAN IMPERFECTIONS (REQUIRED - {hesitation_rate} markers per 200 words):
   - Add subtle self-corrections: "approximately—or more precisely—15 µm"
   - Use em-dashes (—) for mid-sentence clarifications
   - Include hesitation words naturally: "or", "perhaps", "approximately"
   - These show human thought process, not AI perfection

3. PARENTHETICAL ASIDES (REQUIRED - {parenthetical_rate} per 300 words):
   - Add brief clarifications in parentheses: "(as observed in prior studies)"
   - Natural additions that provide context or qualification
   - Shows human tendency to add supplementary thoughts

4. LEXICAL VARIETY (REQUIRED - {int(lexical_target * 100)}% unique words):
   - Vary technical synonyms throughout: contamination → deposits → film → layer
   - Don't repeat exact phrases more than twice
   - Mix transition words: However → Yet → Though → Nevertheless
   - Natural vocabulary variation prevents robotic repetition

5. COMMA USAGE VARIATION (REQUIRED):
   - Vary comma density naturally across sentences
   - Include {comma_splice_rate} strategic comma splice per 100 words (informal connection)
   - Example: "Surface roughness increases, this creates adhesion issues"
   - Some sentences: zero commas | Others: 1-2 commas | Occasional: 3+ commas

6. MEASUREMENT PRECISION VARIATION (REQUIRED):
   - Mix decimal precision contextually: 15 µm → 14.7 µm → approximately 15 µm
   - Don't use uniform precision (e.g., always "15.0")
   - Natural reporting varies between round numbers and precise decimals"""

        # Add author-specific rules
        if author_specific:
            instructions += f"\n\n7. {country.upper()}-SPECIFIC PATTERNS (REQUIRED for Voice Authenticity):"
            
            if country.lower() == 'taiwan':
                article_rate = author_specific.get('optional_article_omission_rate', 70)
                topic_freq = author_specific.get('topic_comment_frequency', 60)
                instructions += f"""
   - Article omission in {article_rate}% of opportunities: "Surface shows improvement" (not "The surface")
   - Topic-comment structure in {topic_freq}% of sentences: "This layer, it has thickness of..."
   - Measurement-first emphasis: Start {author_specific.get('measurement_first_rate', 40)}% of technical sentences with measurements
   - Use commas for analytical pauses naturally"""
            
            elif country.lower() == 'indonesia':
                demo_rate = author_specific.get('demonstrative_clustering_rate', 50)
                repetition_rate = author_specific.get('emphatic_repetition_per_300_words', 2.5)
                instructions += f"""
   - Demonstrative starts: Begin {demo_rate}% of sentences with "This"
   - Emphatic repetition: Use ~{repetition_rate} repetition patterns per 300 words ("very-very good", "This... This...")
   - Simple connectors: Prefer "and/so/but" ({author_specific.get('simple_connector_preference', 80)}% of time) over "however/therefore"
   - Direct cause-effect: Simple "X happens, so Y occurs" patterns
   - Measurement repetition: Repeat key measurements for emphasis"""
            
            elif country.lower() == 'italy':
                passive_rate = author_specific.get('passive_voice_rate', 60)
                clause_density = author_specific.get('interrupted_clauses_per_sentence', 2.5)
                instructions += f"""
   - Passive voice: Use passive construction in {passive_rate}% of sentences
   - Interrupted clauses: Average {clause_density} nested clauses per sentence with mid-sentence qualifications
   - Adverbial intensification: {author_specific.get('adverbial_intensification_rate', 40)}% of sentences use adverbs (NOT emotives)
   - Subordinate clause density: ~{author_specific.get('subordinate_clause_density', 3.0)} subordinate clauses per 100 words
   - Formal sophisticated phrasing with measurement qualifications"""
            
            elif country.lower() in ['usa', 'united states']:
                active_rate = author_specific.get('active_voice_rate', 85)
                phrasal_density = author_specific.get('phrasal_verb_density', 4.0)
                instructions += f"""
   - Active voice: Use active construction in {active_rate}% of sentences
   - Phrasal verbs: ~{phrasal_density} phrasal verbs per 100 words ("exhibits", "consists of", "makes up")
   - Informal transitions: Use "So...", "Well,", "Now," naturally
   - Concrete nouns: Prefer specific over abstract terms
   - Direct measurement reporting: No hedging on technical values
   - Serial comma: 100% Oxford comma consistency"""
        
        instructions += """

REMEMBER: These variations create NATURAL human writing patterns. AI writes too uniformly—humans vary naturally in sentence length, word choice, and precision. Include these patterns throughout BOTH before and after text blocks."""
        
        return instructions

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
        """Build AI prompt for caption generation with voice profile integration"""
        
        import random
        
        # Load frontmatter if not provided to get author info first
        if not frontmatter_data:
            frontmatter_data = self._load_frontmatter_data(material_name)
        
        # Extract author country and load voice profile
        voice_instructions = ""
        ai_evasion_instructions = ""
        author_word_limit = 300  # Default fallback
        
        author_obj = frontmatter_data.get('author', {})
        if author_obj and author_obj.get('country'):
            try:
                country = author_obj['country']
                voice = VoiceOrchestrator(country=country)
                voice_instructions = voice.get_voice_for_component(
                    'caption_generation',
                    context={'material': material_name}
                )
                
                # Get author-specific word limit for percentage-based randomization
                author_word_limit = voice.get_word_limit()
                logger.info(f"Using word limit {author_word_limit} for {country}")
                
                # Extract AI-evasion parameters from voice profile
                profile = voice.profile
                ai_evasion_params = profile.get('ai_evasion_parameters', {})
                
                if ai_evasion_params:
                    # Format AI-evasion instructions
                    ai_evasion_instructions = self._format_ai_evasion_instructions(ai_evasion_params, country)
                    logger.info(f"Loaded AI-evasion parameters for {country}")
                
                logger.info(f"Loaded voice profile for {country} ({author_obj.get('name', 'Unknown')})")
            except Exception as e:
                logger.warning(f"Could not load voice profile for {author_obj.get('country')}: {e}")
                # Continue without voice instructions rather than failing
                voice_instructions = ""
                ai_evasion_instructions = ""
                author_word_limit = 300  # Fallback
        
        # Generate percentage-based random target lengths (±40% of author's word limit)
        # Character count roughly = word count * 5.5 (average chars per word including spaces)
        base_chars = int(author_word_limit * 5.5)
        min_chars = int(base_chars * 0.6)  # 60% of base (40% below)
        max_chars = int(base_chars * 1.4)  # 140% of base (40% above)
        
        before_target = random.randint(min_chars, max_chars)  # Percentage-based range for before text
        after_target = random.randint(min_chars, max_chars)   # Percentage-based range for after text
        
        # Determine paragraph count based on target length
        before_paragraphs = "1-2 paragraphs" if before_target < 900 else "2-3 paragraphs"
        after_paragraphs = "1-2 paragraphs" if after_target < 900 else "2-3 paragraphs"
        
        logger.info(f"Caption targets: before={before_target} chars, after={after_target} chars (base: {base_chars}, range: {min_chars}-{max_chars})")
        
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

        return f"""You are an analytical microscopist documenting surface characterization findings with technical precision and clarity.

TASK: Generate detailed microscopic analysis descriptions of {material_name} laser cleaning that document observable surface conditions and measurable transformations.

MATERIAL CONTEXT:
- Material: {material_name}
- Category: {category}
- Material Properties: {json.dumps(context_data['properties'], indent=2) if context_data['properties'] else 'Limited data available'}
- Applications: {', '.join(context_data['applications']) if context_data['applications'] else 'General cleaning'}

WRITING STANDARDS:
- Document what is directly observable at 500x magnification with technical specificity
- Use standard analytical terminology (SEM, XPS, EDX, Ra measurements) to establish credibility
- Include quantitative measurements with appropriate units when characterizing surfaces
- Maintain authoritative, professional tone—report findings rather than make claims
- Employ active voice construction where appropriate for direct, clear communication
- Focus on measurable surface characteristics: layer thickness, roughness values, contamination composition
- Connect observations to material performance: reflectivity changes, surface integrity, functional restoration
- Write with technical authority—precise language that demonstrates expertise without promotional tone

{voice_instructions if voice_instructions else ""}

{ai_evasion_instructions if ai_evasion_instructions else ""}

Generate exactly two comprehensive text blocks:

**BEFORE_TEXT:**
[Write a detailed microscopic analysis of the contaminated {material_name.lower()} surface in {before_paragraphs} (target ~{before_target} characters):

CRITICAL: Focus on specific contamination visible at 500x magnification. Describe what you would actually see through the microscope - layer thickness, surface texture, contamination patterns, and visual characteristics. Use accessible language while maintaining technical precision. Use objective, factual language - avoid emotional descriptors.

For shorter descriptions: Detail the most prominent contamination features and their microscopic appearance in 1-2 focused paragraphs.

For longer descriptions: Provide comprehensive microscopic analysis including contamination layer structure, surface appearance, and detailed visual characteristics across 2-3 paragraphs.

Write as a clear microscopic observation. Include specific measurements and visual details, but explain technical terms. Use paragraph breaks for clarity.]

**AFTER_TEXT:**
[Write a detailed microscopic analysis of the cleaned {material_name.lower()} surface in {after_paragraphs} (target ~{after_target} characters):

CRITICAL: Focus on the visual transformation visible at 500x magnification. Contrast the cleaned surface directly with the contaminated state, highlighting specific improvements in surface appearance. Use accessible language while maintaining technical precision. Use objective, factual language - avoid emotional descriptors.

For shorter descriptions: Emphasize the most significant visual differences and surface quality improvements in 1-2 focused paragraphs.

For longer descriptions: Provide comprehensive before/after comparison including surface changes, contamination removal evidence, and detailed visual transformation across 2-3 paragraphs.

Write as a clear comparative analysis. Include specific observations about what changed and how the surface now appears, but explain technical terms. Use paragraph breaks for clarity.]

Ensure all content is scientifically accurate but prioritize clarity and readability over technical complexity. Focus on practical benefits and visual results rather than showcasing scientific expertise."""

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
        
        return {
            'beforeText': before_text,
            'afterText': after_text,
            'technicalFocus': 'surface_analysis',
            'uniqueCharacteristics': [f'{material_name.lower()}_specific'],
            'contaminationProfile': f'{material_name.lower()} surface contamination',
            'microscopyParameters': f'Microscopic analysis of {material_name.lower()}',
            'qualityMetrics': 'Surface improvement analysis'
        }

    def _calculate_author_token_limit(self, author_country: str) -> int:
        """
        Calculate max_tokens based on author's word limit.
        
        Author word limits (per persona config):
        - Taiwan: 380 words → 456 tokens
        - Italy: 450 words → 540 tokens  
        - Indonesia: 250 words → 300 tokens
        - USA: 320 words → 384 tokens
        
        Using rough conversion: 1 token ≈ 0.75 words for technical content
        Formula: (word_limit / 0.75) * 0.9 safety margin
        """
        # Author word limits from OPTIMIZER_CONFIG personas
        word_limits = {
            "taiwan": 380,
            "italy": 450,
            "indonesia": 250,
            "usa": 320
        }
        
        country_key = author_country.lower()
        word_limit = word_limits.get(country_key, 320)  # Default to USA if unknown
        
        # Convert words to tokens with 10% safety margin
        # token_to_word_ratio ≈ 0.75 for technical content
        max_tokens = int((word_limit / 0.75) * 0.9)
        
        logger.info(f"Author {country_key}: word_limit={word_limit} → max_tokens={max_tokens}")
        
        return max_tokens

    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author_info: Optional[Dict] = None,
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
        category = frontmatter_data.get('category')
        if not category:
            raise ValueError(f"Material category required in frontmatter for {material_name} - fail-fast requires complete classification")
        
        # Calculate dynamic token limit based on author's word limit
        dynamic_max_tokens = self._calculate_author_token_limit(author_country)
        
        # Build AI prompt and generate content
        try:
            prompt = self._build_prompt(
                material_name, material_data, author_info, frontmatter_data, schema_fields
            )
            
            response = api_client.generate_simple(
                prompt=prompt,
                max_tokens=dynamic_max_tokens,  # Dynamic limit based on author's word limit
                temperature=0.2   # Reduced for more precise technical content
            )
            
            logger.info(f"Caption generation for {material_name} by {author} ({author_country}): max_tokens={dynamic_max_tokens}")
            
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
  {ai_content['beforeText']}

after_text: |
  {ai_content['afterText']}

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
