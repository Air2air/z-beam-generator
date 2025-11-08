#!/usr/bin/env python3
"""
Voice Orchestrator - Central API for Voice Management

Provides unified interface for retrieving country-specific voice instructions
for all text-based content generation components.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import yaml
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


class VoiceOrchestrator:
    """
    Orchestrates voice instructions for content generation components.
    
    Manages country-specific linguistic patterns and propagates consistent
    voice across all text-based components.
    """
    
    # Country name normalization
    COUNTRY_MAP = {
        "taiwan": "taiwan",
        "italy": "italy",
        "indonesia": "indonesia",
        "united states": "united_states",
        "united_states": "united_states",
        "united states (california)": "united_states",
        "usa": "united_states",
        "us": "united_states",
    }
    
    def __init__(self, country: str):
        """
        Initialize voice orchestrator for specific country.
        
        Args:
            country: Author's country (e.g., "Taiwan", "Italy", "Indonesia", "United States")
        
        Raises:
            ValueError: If country is invalid or profile not found
        """
        self.country_raw = country
        self.country = self._normalize_country(country)
        self.profile = self._load_profile()
        self.base_voice = self._load_base_voice()
        self.component_config = self._load_component_config()
    
    def _normalize_country(self, country: str) -> str:
        """Normalize country name to profile filename"""
        country_lower = country.lower().strip()
        
        if country_lower not in self.COUNTRY_MAP:
            raise ValueError(
                f"Unsupported country '{country}'. "
                f"Supported: Taiwan, Italy, Indonesia, United States. "
                f"Fail-fast architecture requires valid country profiles."
            )
        
        return self.COUNTRY_MAP[country_lower]
    
    @lru_cache(maxsize=10)
    def _load_profile(self) -> Dict[str, Any]:
        """
        Load country-specific voice profile.
        
        Returns:
            Voice profile dictionary
        
        Raises:
            FileNotFoundError: If profile file doesn't exist
            ValueError: If profile is invalid
        """
        profile_path = Path(__file__).parent / "profiles" / f"{self.country}.yaml"
        
        if not profile_path.exists():
            raise FileNotFoundError(
                f"Voice profile not found: {profile_path}. "
                f"Fail-fast architecture requires complete voice profiles."
            )
        
        with open(profile_path, 'r', encoding='utf-8') as f:
            profile = yaml.safe_load(f)
        
        # Validate profile structure - voice_adaptation removed (component-specific)
        required_keys = [
            "name", "author", "country", "linguistic_characteristics",
            "signature_phrases"
        ]
        
        for key in required_keys:
            if key not in profile:
                raise ValueError(
                    f"Invalid voice profile for {self.country}: missing '{key}'. "
                    f"Fail-fast architecture requires complete profiles."
                )
        
        return profile
    
    @lru_cache(maxsize=5)
    def _load_base_voice(self) -> Dict[str, Any]:
        """Load base voice characteristics"""
        base_path = Path(__file__).parent / "base" / "voice_base.yaml"
        if not base_path.exists():
            logger.warning(f"Base voice file not found: {base_path}")
            return {}
        
        with open(base_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _load_unified_voice_system(self) -> Dict[str, Any]:
        """Load unified voice prompting system"""
        unified_path = Path(__file__).parent / "prompts" / "unified_voice_system.yaml"
        if not unified_path.exists():
            logger.warning(f"Unified voice system not found: {unified_path}")
            return {}
        
        with open(unified_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    @lru_cache(maxsize=1)
    def _load_component_config(self) -> Dict[str, Any]:
        """
        Load component voice configuration.
        
        Returns:
            Component config dictionary mapping component types to voice parameters
        
        Raises:
            FileNotFoundError: If component_config.yaml not found
        """
        config_path = Path(__file__).parent / "component_config.yaml"
        
        if not config_path.exists():
            logger.warning(f"Component config not found: {config_path}, using defaults")
            return {"default": {"intensity_level": "level_3_moderate"}}
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def get_component_config(self, component_type: str) -> Dict[str, Any]:
        """
        Get voice configuration for specific component type.
        
        Args:
            component_type: Component type (caption, subtitle, description, etc.)
        
        Returns:
            Component-specific voice config with intensity, formality, etc.
        """
        config = self.component_config.get(component_type)
        
        if not config:
            logger.warning(f"No config found for component '{component_type}', using default")
            config = self.component_config.get('default', {
                'intensity_level': 'level_3_moderate',
                'formality': 'professional',
                'target_audience': 'educated non-specialists'
            })
        
        logger.info(f"Component config for '{component_type}': intensity={config.get('intensity_level')}, audience={config.get('target_audience')}")
        return config
    
    def get_voice_for_component(
        self, 
        component_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get voice instructions for specific component type.
        
        Args:
            component_type: Type of component (caption, text, tags, etc.)
            context: Optional context (material, technical_level, etc.)
        
        Returns:
            Complete voice instructions as formatted string
        """
        context = context or {}
        
        # NOTE: voice_adaptation removed - component-specific adaptations
        # belong in component config files, not voice profiles
        adaptation = {}
        
        # Build voice instructions (linguistic patterns only)
        instructions = self._build_voice_instructions(
            adaptation=adaptation,
            context=context
        )
        
        return instructions
    
    def get_unified_prompt(
        self,
        component_type: str,
        material_context: Dict[str, Any],
        author: Dict[str, Any],
        **kwargs
    ) -> str:
        """
        Generate complete prompt using voice_base.yaml + country profile layering.
        
        Args:
            component_type: Type of component (microscopy_description for captions)
            material_context: Material name, category, properties, etc.
            author: Author name, country, expertise, etc.
            **kwargs: Additional template variables (section_focus, target_words, etc.)
        
        Returns:
            Complete formatted prompt string
        """
        # Load base voice foundations
        base_voice = self._load_base_voice()
        if not base_voice:
            raise ValueError("voice/base/voice_base.yaml not found - fail-fast requires base voice")
        
        # Get country profile (already loaded in __init__)
        country_profile = self.profile
        
        # Build layered prompt for microscopy description
        if component_type == 'microscopy_description':
            return self._build_microscopy_prompt(
                base_voice=base_voice,
                country_profile=country_profile,
                material_context=material_context,
                author=author,
                **kwargs
            )
        # Build layered prompt for subtitle/tagline
        elif component_type == 'subtitle':
            return self._build_subtitle_prompt(
                base_voice=base_voice,
                country_profile=country_profile,
                material_context=material_context,
                author=author,
                **kwargs
            )
        # Build layered prompt for FAQ answers
        elif component_type == 'technical_faq_answer':
            return self._build_faq_prompt(
                base_voice=base_voice,
                country_profile=country_profile,
                material_context=material_context,
                author=author,
                **kwargs
            )
        else:
            raise ValueError(f"Component type '{component_type}' not supported with voice_base.yaml system")
    
    def _build_microscopy_prompt(
        self,
        base_voice: Dict,
        country_profile: Dict,
        material_context: Dict,
        author: Dict,
        **kwargs
    ) -> str:
        """
        Build microscopy description prompt by layering base + country voice.
        
        Template structure:
        1. Role definition (from country profile)
        2. Base voice principles (from voice_base.yaml)
        3. Country-specific linguistic patterns (from profile)
        4. Material context
        5. Section-specific focus
        6. Output requirements
        """
        # Extract parameters
        section_focus = kwargs.get('section_focus', 'surface analysis')
        section_instruction = kwargs.get('section_instruction', '')
        target_words = kwargs.get('target_words', 30)
        style_guidance = kwargs.get('style_guidance', 'focused description')
        paragraph_count = kwargs.get('paragraph_count', '1 paragraph')
        
        # 1. ROLE DEFINITION
        author_name = author.get('name', 'Technical Expert')
        author_country = author.get('country', 'usa')
        author_expertise = author.get('expertise', 'laser cleaning technology')
        
        role_section = f"""You are {author_name}, a {author_expertise} expert from {author_country}, writing for a general audience."""
        
        # 2. BASE VOICE PRINCIPLES (from voice_base.yaml)
        core_principles = base_voice.get('core_principles', {})
        forbidden_patterns = base_voice.get('forbidden_patterns', {})
        laser_context = base_voice.get('laser_cleaning_context', {})
        
        # Extract section-specific guidance
        if 'before' in section_focus.lower() or 'contaminated' in section_focus.lower():
            section_rules = laser_context.get('before_state_focus', {})
        else:
            section_rules = laser_context.get('after_state_focus', {})
        
        # Build base guidance text
        base_guidance = self._format_base_guidance(core_principles, forbidden_patterns, section_rules, base_voice)
        
        # 3. COUNTRY-SPECIFIC LINGUISTIC PATTERNS
        linguistic = country_profile.get('linguistic_characteristics', {})
        country_voice = self._format_country_voice(linguistic, author_country)
        
        # 4. MATERIAL CONTEXT
        material_name = material_context.get('material_name', 'material')
        category = material_context.get('category', 'material')
        properties = material_context.get('properties', 'Standard material characteristics')
        applications = material_context.get('applications', 'General cleaning applications')
        
        # 5. BUILD COMPLETE PROMPT FROM YAML ONLY
        prompt = f"""{role_section}

{base_guidance}

{country_voice}

MATERIAL CONTEXT:
- Material: {material_name}
- Category: {category}
- Properties: {properties}
- Applications: {applications}

ANALYSIS FOCUS:
- Section focus: {section_focus}
- Task: {section_instruction}

LENGTH TARGET:
- Target: {target_words} words
- Style: {style_guidance}
- Structure: {paragraph_count}

Generate {section_focus} description now."""
        
        return prompt
    
    def _build_subtitle_prompt(
        self,
        base_voice: Dict,
        country_profile: Dict,
        material_context: Dict,
        author: Dict,
        **kwargs
    ) -> str:
        """
        Build subtitle/tagline prompt with country-specific voice.
        
        Uses component_config.yaml to determine intensity and formality.
        """
        # Get component-specific configuration
        config = self.get_component_config('subtitle')
        
        # Extract parameters (kwargs override config)
        target_words = kwargs.get('target_words', config.get('word_count_range', [8, 12])[0])
        
        # Get intensity level from config
        intensity_level = config.get('intensity_level', 'level_2_light')
        formality = config.get('formality', 'professional-engaging')
        target_audience = config.get('target_audience', 'technical professionals')
        
        # Get material specificity requirement from component config
        material_specificity = self.component_config.get('material_specificity_requirement', '')
        
        # Author context
        author_name = author.get('name', 'Expert')
        author_country = author.get('country', 'usa')
        
        # Material context
        material_name = material_context.get('material_name', 'material')
        material_category = material_context.get('category', '')
        material_subcategory = material_context.get('subcategory', '')
        
        # Get country-specific style
        linguistic = country_profile.get('linguistic_characteristics', {})
        vocab = linguistic.get('vocabulary_patterns', {})
        country_formality = vocab.get('formality_level', 'professional')
        
        # Get intensity instructions from voice_base.yaml
        intensity_rules = base_voice.get('technical_authority_intensity', {}).get(intensity_level, {})
        intensity_desc = intensity_rules.get('description', 'Balanced technical communication')
        
        # Build prompt with material specificity requirement
        prompt = f"""You are {author_name} from {author_country}, writing a subtitle for {material_name} laser cleaning content.

MATERIAL CONTEXT:
- Material: {material_name}
- Category: {material_category}
- Subcategory: {material_subcategory}

MATERIAL SPECIFICITY REQUIREMENT:
{material_specificity}

TASK: Write a {target_words}-word professional subtitle/tagline.

VOICE GUIDANCE ({author_country.upper()}):
- Formality: {formality} (country style: {country_formality})
- Target Audience: {target_audience}
- Technical Intensity: {intensity_level}
  {intensity_desc}

REQUIREMENTS:
- Exactly {target_words} words (±2 tolerance)
- Single phrase (no period at end)
- Professional tone suitable for industrial audience
- Reveal something UNIQUE and SPECIFIC about {material_name}
- Compare to related materials if relevant ({material_category}/{material_subcategory})

Write the subtitle now:"""
        
        return prompt
    
    def _build_faq_prompt(
        self,
        base_voice: Dict,
        country_profile: Dict,
        material_context: Dict[str, Any],
        author: Dict[str, Any],
        **kwargs
    ) -> str:
        """Build FAQ answer prompt with voice layering"""
        # Extract context - support both 'name' and 'material_name' keys
        material_name = material_context.get('material_name') or material_context.get('name', 'Unknown Material')
        material_category = material_context.get('category', 'Unknown')
        question = kwargs.get('question', '')
        focus_points = kwargs.get('focus_points', '')
        focus_points = kwargs.get('focus_points', '')
        property_values = kwargs.get('property_values', {})
        target_words = kwargs.get('target_words', 200)
        
        # Extract properties and settings from material_context if provided
        properties_str = material_context.get('properties', '')
        settings_str = material_context.get('machine_settings', '')
        applications_str = material_context.get('applications', '')
        
        # Extract author info
        author_name = author.get('name', 'Unknown')
        author_country = author.get('country', 'USA')
        author_expertise = author.get('expertise', 'Laser Technology')
        
        # Extract country profile characteristics
        linguistic = country_profile.get('linguistic_characteristics', {})
        formality = linguistic.get('formality_level', 'professional')
        country_formality = linguistic.get('formality_indicators', {}).get('style', 'neutral')
        
        # Get language policy from country profile (support both old and new field names)
        output_language = country_profile.get('output_language', 'English')
        language_instruction = country_profile.get('language_instruction', '')
        language_policy = country_profile.get('language_policy', language_instruction or 'All content must be in English.')
        forbidden_langs = country_profile.get('forbidden_output_languages', country_profile.get('forbidden_languages', []))
        
        # Build language enforcement section
        language_warning = ""
        if forbidden_langs:
            forbidden_list = ', '.join(forbidden_langs)
            language_warning = f"""
🚫 CRITICAL LANGUAGE REQUIREMENT:
- OUTPUT LANGUAGE: {output_language} ONLY
- FORBIDDEN: {forbidden_list}
- {language_policy}
- Use linguistic PATTERNS from {author_country} culture in ENGLISH text
- NEVER write in {forbidden_langs[0] if forbidden_langs else 'non-English languages'}
"""
        
        # Extract voice examples from profile (new structure)
        voice_examples = country_profile.get('voice_examples', {}).get('faq', [])
        if not voice_examples:
            # Fallback to general examples if FAQ-specific not available
            voice_examples = country_profile.get('voice_examples', {}).get('general', [])
        
        # Build voice-specific pattern guidance from examples
        voice_patterns = ""
        if voice_examples:
            # Show 2-3 concrete examples from the profile
            voice_patterns = "\n".join([f"  • {example}" for example in voice_examples[:3]])
        
        # Build prompt with material specificity and property values
        prompt = f"""You are {author_name} from {author_country}, a {author_expertise} expert answering a technical FAQ about {material_name} laser cleaning.
{language_warning}
MATERIAL CONTEXT:
- Material: {material_name}
- Category: {material_category}
- Applications: {applications_str}

QUESTION TO ANSWER:
{question}

FOCUS POINTS:
{focus_points}

MATERIAL PROPERTIES:
{properties_str if properties_str else self._format_property_values(property_values)}

MACHINE SETTINGS:
{settings_str if settings_str else 'Standard laser cleaning parameters'}

VOICE & STYLE - MANDATORY ({author_country.upper()}):
✅ REQUIRED: Write in the style of these examples from your voice profile:
{voice_patterns}

📋 VOICE REQUIREMENTS:
- MATCH the linguistic patterns shown in the examples above
- Use the same sentence structures and phrasing style
- Apply {author_country} language patterns naturally (1-2 per answer)
- Formality level: {formality}

LENGTH REQUIREMENTS:
- Target: {target_words} words (20-60 word range)
- Write 1-3 sentences maximum
- Natural length variation across different questions

WRITING STYLE:
- Reference specific values (fluence, power, wavelength) when relevant
- Focus on technical accuracy while maintaining your voice
- Avoid formulaic phrases like "It's important to note"

CONTENT REQUIREMENTS:
- Cite 1-2 specific technical values when relevant (J/cm², W, mm/s, μm, °C, ppm)
- Address {material_name} specifically - use material properties in context
- Balance precision with readability
- Focus on actionable, practical information
- Connect recommendations to material behavior or characteristics

Write a technical answer using your natural voice patterns (1-3 sentences, 20-60 words):"""
        
        return prompt
    
    def _format_property_values(self, property_values: Dict) -> str:
        """Format property values for FAQ prompt"""
        if not property_values:
            return "(No specific property values provided)"
        
        lines = []
        for prop_name, prop_data in property_values.items():
            if isinstance(prop_data, dict):
                value = prop_data.get('value', 'N/A')
                unit = prop_data.get('unit', '')
                min_val = prop_data.get('min', '')
                max_val = prop_data.get('max', '')
                
                if min_val and max_val:
                    lines.append(f"- {prop_name}: {value} {unit} (range: {min_val}-{max_val} {unit})")
                else:
                    lines.append(f"- {prop_name}: {value} {unit}")
            else:
                lines.append(f"- {prop_name}: {prop_data}")
        
        return '\n'.join(lines) if lines else "(No specific property values provided)"
    
    def _format_base_guidance(self, core_principles: Dict, forbidden_patterns: Dict, section_rules: Dict, base_voice: Dict = None) -> str:
        """Format base voice guidance from voice_base.yaml"""
        lines = []
        
        # Extract intensity rules from technical_writing_standards and include in prompt
        if base_voice:
            tech_standards = base_voice.get('technical_writing_standards', {})
            intensity_system = tech_standards.get('technical_authority_intensity', {})
            
            if intensity_system:
                lines.append("TECHNICAL INTENSITY SELECTION:")
                if 'instruction' in intensity_system:
                    lines.append(intensity_system['instruction'])
                if 'selection_rules' in intensity_system:
                    lines.append(intensity_system['selection_rules'])
                lines.append("")  # Blank line
        
        # Extract all rules from section_rules (before_state_focus or after_state_focus)
        if section_rules:
            # Title and focus
            if 'title' in section_rules:
                lines.append(f"{section_rules['title']}")
            if 'primary_focus' in section_rules:
                lines.append(f"Focus: {section_rules['primary_focus']}")
            
            lines.append("")  # Blank line
            
            # Required content
            if 'required_content' in section_rules:
                lines.append("Required content:")
                for item in section_rules['required_content']:
                    lines.append(f"- {item}")
                lines.append("")
            
            # Technical authority
            if 'technical_authority' in section_rules:
                lines.append("Technical authority:")
                for item in section_rules['technical_authority']:
                    lines.append(f"- {item}")
                lines.append("")
            
            # Strictly forbidden
            if 'strictly_forbidden' in section_rules:
                lines.append("Strictly forbidden:")
                for item in section_rules['strictly_forbidden']:
                    lines.append(f"- {item}")
        
        return '\n'.join(lines)
    
    def _format_country_voice(self, linguistic: Dict, country: str) -> str:
        """Format country-specific voice characteristics from profile YAML"""
        lines = [f"VOICE ({country.upper()}):"]
        
        # Sentence structure patterns
        if 'sentence_structure' in linguistic:
            sent_struct = linguistic['sentence_structure']
            if 'patterns' in sent_struct:
                patterns = sent_struct['patterns']
                lines.append("Linguistic patterns:")
                for pattern in patterns[:3]:  # Include top 3 patterns
                    lines.append(f"- {pattern}")
            
            if 'tendencies' in sent_struct:
                tendencies = sent_struct['tendencies']
                if tendencies:
                    lines.append("Tendencies:")
                    for tendency in tendencies[:2]:  # Top 2 tendencies
                        lines.append(f"- {tendency}")
        
        # Vocabulary patterns
        if 'vocabulary_patterns' in linguistic:
            vocab = linguistic['vocabulary_patterns']
            if 'formality_level' in vocab:
                lines.append(f"Formality: {vocab['formality_level']}")
        
        return '\n'.join(lines)
    
    def _build_voice_instructions(
        self,
        adaptation: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """
        Build complete voice instructions from profile and context.
        
        Args:
            adaptation: Component-specific adaptation settings
            context: Generation context
        
        Returns:
            Formatted voice instructions string
        """
        linguistic = self.profile.get("linguistic_characteristics", {})
        
        # Build instruction sections
        sections = []
        
        # 1. Role and Authority
        sections.append(self._build_role_section(adaptation))
        
        # 2. Linguistic Patterns
        sections.append(self._build_linguistic_section(linguistic))
        
        # 3. Voice Characteristics
        sections.append(self._build_voice_characteristics_section(linguistic))
        
        # 4. Component-Specific Guidelines
        if adaptation:
            sections.append(self._build_adaptation_section(adaptation))
        
        # 5. Signature Phrases
        sections.append(self._build_signature_phrases_section())
        
        return "\n\n".join(filter(None, sections))
    
    def _build_role_section(self, adaptation: Dict[str, Any]) -> str:
        """Build role and authority section"""
        author = self.profile.get("author", "Technical Expert")
        country = self.profile.get("country", self.country_raw)
        
        focus = adaptation.get("focus", "technical analysis")
        style = adaptation.get("style", "professional communication")
        
        return f"""VOICE ROLE:
You are {author} from {country}, communicating technical expertise with authentic voice.

Focus: {focus}
Style: {style}
Authority: Technical expert with country-specific communication patterns"""
    
    def _build_linguistic_section(self, linguistic: Dict[str, Any]) -> str:
        """Build linguistic patterns section"""
        sentence = linguistic.get("sentence_structure", {})
        vocab = linguistic.get("vocabulary_patterns", {})
        grammar = linguistic.get("grammar_characteristics", {})
        
        patterns = sentence.get("patterns", [])
        tendencies = sentence.get("tendencies", [])
        natural_vars = sentence.get("natural_variations", [])
        
        sections = ["LINGUISTIC PATTERNS:"]
        
        if patterns:
            sections.append("\nSentence Structure Examples:")
            for pattern in patterns[:3]:
                sections.append(f"  - {pattern}")
        
        if tendencies:
            sections.append("\nCommunication Tendencies:")
            for tendency in tendencies:
                sections.append(f"  - {tendency}")
        
        if natural_vars:
            sections.append("\nNatural Variations (authentic patterns):")
            for var in natural_vars:
                sections.append(f"  - {var}")
        
        # Vocabulary preferences
        if vocab:
            preferred = vocab.get("preferred_terms", {})
            if preferred:
                sections.append("\nPreferred Vocabulary:")
                for category, terms in preferred.items():
                    if isinstance(terms, list) and terms:
                        sections.append(f"  {category.title()}: {', '.join(terms[:4])}")
        
        return "\n".join(sections)
    
    def _build_voice_characteristics_section(self, linguistic: Dict[str, Any]) -> str:
        """Build voice characteristics section"""
        cultural = linguistic.get("cultural_communication", {})
        
        if not cultural:
            return ""
        
        tone = cultural.get("tone", "professional")
        emphasis = cultural.get("emphasis_style", "technical accuracy")
        perspective = cultural.get("perspective", "expert analysis")
        
        return f"""VOICE CHARACTERISTICS:
Tone: {tone}
Emphasis: {emphasis}
Perspective: {perspective}"""
    
    def _build_adaptation_section(self, adaptation: Dict[str, Any]) -> str:
        """Build component-specific adaptation section"""
        if not adaptation:
            return ""
        
        word_limit = adaptation.get("word_limit")
        focus = adaptation.get("focus")
        style = adaptation.get("style")
        
        sections = ["COMPONENT-SPECIFIC GUIDELINES:"]
        
        if word_limit:
            sections.append(f"Word Limit: {word_limit} words")
        if focus:
            sections.append(f"Content Focus: {focus}")
        if style:
            sections.append(f"Writing Style: {style}")
        
        return "\n".join(sections)
    
    def _build_signature_phrases_section(self) -> str:
        """Build signature phrases section"""
        phrases = self.profile.get("signature_phrases", [])
        
        if not phrases:
            return ""
        
        return f"""SIGNATURE EXPRESSIONS:
Consider incorporating these natural expressions when appropriate:
{chr(10).join(f'  - "{phrase}"' for phrase in phrases[:5])}"""
    
    def get_word_limit(self) -> int:
        """
        Get word limit for this country's voice.
        
        NOTE: This method is deprecated - word limits should be managed by
        component-specific configuration, not voice profiles.
        Kept for backward compatibility only.
        
        Returns:
            Word limit as integer (defaults by country for legacy support)
        """
        logger.warning(
            "get_word_limit() is deprecated - word limits belong in component config, "
            "not voice profiles. See components/{component}/config/ for word limits."
        )
        
        # Default limits by country (for backward compatibility)
        defaults = {
            "taiwan": 266,
            "italy": 266,
            "indonesia": 175,
            "united_states": 196
        }
        
        return defaults.get(self.country, 240)
    
    def get_quality_thresholds(self) -> Dict[str, float]:
        """
        Get quality thresholds for this voice profile.
        
        Returns:
            Dictionary of threshold values
        """
        return self.profile.get("quality_thresholds", {
            "formality_minimum": 70,
            "technical_accuracy_minimum": 85,
            "linguistic_authenticity_minimum": 70
        })
    
    def get_signature_phrases(self) -> list:
        """Get list of signature phrases for this country"""
        return self.profile.get("signature_phrases", [])
    
    def get_faq_variation_guidance(self) -> str:
        """
        Get FAQ-specific variation guidance from voice profile.
        
        Returns variation requirements from voice_adaptation.faq_generation
        section of the profile, formatted as prompt guidance.
        
        Returns:
            str: Formatted variation guidance or empty string if none needed
        """
        voice_adaptation = self.profile.get("voice_adaptation", {})
        faq_config = voice_adaptation.get("faq_generation", {})
        
        if not faq_config:
            return ""
        
        variation_reqs = faq_config.get("critical_variation_requirements", {})
        if not variation_reqs:
            return ""
        
        # Build formatted guidance
        country_name = self.profile.get("name", self.country_raw).split()[0]  # Get country part
        guidance_lines = [
            "━" * 70,
            f"🎯 CRITICAL: NATURAL VARIATION REQUIREMENT ({country_name} Voice)",
            "━" * 70
        ]
        
        # Add warning if present
        if "warning" in variation_reqs:
            guidance_lines.append(f"⚠️  WARNING: {variation_reqs['warning']}")
            guidance_lines.append("")
        
        # Add length distribution requirements
        length_dist = variation_reqs.get("mandatory_length_distribution", {})
        if length_dist:
            guidance_lines.append("MANDATORY ANSWER LENGTH DISTRIBUTION:")
            guidance_lines.append(length_dist.get("description", ""))
            
            for category in ["short_answers", "concise_answers", "medium_answers", "standard_answers", "long_answers", "comprehensive_answers"]:
                if category in length_dist:
                    cat_data = length_dist[category]
                    cat_name = category.replace("_", " ").title()
                    guidance_lines.append(f"{len(guidance_lines) - 6}. {cat_name}:")
                    guidance_lines.append(f"   - Range: {cat_data.get('range', 'N/A')}")
                    guidance_lines.append(f"   - Count: {cat_data.get('count', 'N/A')}")
                    guidance_lines.append(f"   - Purpose: {cat_data.get('purpose', 'N/A')}")
            guidance_lines.append("")
        
        # Add forbidden patterns
        forbidden = variation_reqs.get("forbidden_patterns", [])
        if forbidden:
            guidance_lines.append("FORBIDDEN PATTERNS:")
            for pattern in forbidden:
                guidance_lines.append(f"- ❌ {pattern}")
            guidance_lines.append("")
        
        # Add required targets
        targets = variation_reqs.get("required_targets", {})
        if targets:
            guidance_lines.append("REQUIRED TARGETS:")
            for key, value in targets.items():
                key_formatted = key.replace("_", " ").title()
                guidance_lines.append(f"- ✅ {key_formatted}: {value}")
            guidance_lines.append("")
        
        # Add sentence starter diversity
        starters = variation_reqs.get("sentence_starter_diversity", {})
        if starters:
            guidance_lines.append("SENTENCE STARTER DIVERSITY:")
            if "max_this_usage" in starters:
                guidance_lines.append(f"- Maximum {starters['max_this_usage']} of sentences starting with \"This\"")
            if "varied_openings" in starters:
                openings = ", ".join(f"\"{o}\"" for o in starters["varied_openings"])
                guidance_lines.append(f"- Vary openings: {openings}")
            for key, value in starters.items():
                if key not in ["max_this_usage", "varied_openings"]:
                    key_formatted = key.replace("_", " ").title()
                    guidance_lines.append(f"- {key_formatted}: {value}")
        
        guidance_lines.append("━" * 70)
        
        return "\n".join(guidance_lines)
    
    def get_profile_summary(self) -> Dict[str, Any]:
        """
        Get summary of voice profile.
        
        Returns:
            Dictionary with key profile information
        """
        linguistic = self.profile.get("linguistic_characteristics", {})
        cultural = linguistic.get("cultural_communication", {})
        
        return {
            "country": self.profile.get("country"),
            "author": self.profile.get("author"),
            "tone": cultural.get("tone", "professional"),
            "formality": linguistic.get("vocabulary_patterns", {}).get("formality_level", "professional"),
            "signature_phrases_count": len(self.profile.get("signature_phrases", []))
        }


    def _build_voice_characteristics(self, unified_system: Dict[str, Any]) -> str:
        """Build voice characteristics section from unified system"""
        voice_templates = unified_system.get('voice_characteristics_templates', {})
        country_template = voice_templates.get(self.country)
        
        if not country_template:
            return "Standard technical communication guidelines apply."
        
        # Get voice profile parameters
        adaptation = self.profile.get('voice_adaptation', {}).get('caption_generation', {})
        ai_params = self.profile.get('ai_evasion_parameters', {})
        
        # Get all template variables needed
        author_specific = ai_params.get('author_specific', {})
        sentence_targets = ai_params.get('sentence_length_targets', {})
        
        return country_template['template'].format(
            word_limit=adaptation.get('word_limit', 300),
            minimum_sentences=adaptation.get('validation_requirements', {}).get('minimum_sentences', 5),
            measurement_first_rate=author_specific.get('measurement_first_rate', 40),
            phrasal_verb_density=author_specific.get('phrasal_verb_density', 4.0),
            active_voice_rate=author_specific.get('active_voice_rate', 85),
            emphatic_pronoun_limit=author_specific.get('emphatic_pronoun_limit', 2),
            very_short=sentence_targets.get('very_short', 15),
            medium=sentence_targets.get('medium', 35),
            long=sentence_targets.get('long', 35),
            very_long=sentence_targets.get('very_long', 15),
            academic_hedging_frequency=author_specific.get('academic_hedging_frequency', 2),
            serial_comma_usage=author_specific.get('serial_comma_usage', 85),
            lexical_variety_target=ai_params.get('lexical_variety_target', 0.65),
            hesitation_markers_per_200_words=ai_params.get('hesitation_markers_per_200_words', 1.5),
            comma_splices_per_100_words=ai_params.get('comma_splices_per_100_words', 1.0),
            parenthetical_asides_per_300_words=ai_params.get('parenthetical_asides_per_300_words', 2.0)
        )
    
    def _build_ai_evasion_instructions(self, unified_system: Dict[str, Any]) -> str:
        """Build AI evasion instructions from unified system"""
        evasion_templates = unified_system.get('ai_evasion_templates', {})
        detectability_templates = unified_system.get('ai_detectability_avoidance_templates', {})
        
        # Get AI detectability avoidance instructions (NEW - critical for human-like output)
        universal_detection = detectability_templates.get('universal_detection_avoidance', {}).get('template', '')
        country_detection = detectability_templates.get('country_detection_avoidance', {}).get(self.country, {}).get('template', '')
        
        # Get traditional evasion templates
        universal = evasion_templates.get('natural_variation', {}).get('template', '')
        country_specific = evasion_templates.get('country_specific', {}).get(self.country, {}).get('template', '')
        
        ai_params = self.profile.get('ai_evasion_parameters', {})
        
        # Format universal instructions
        universal_formatted = universal.format(
            very_short=ai_params.get('sentence_length_targets', {}).get('very_short', 20),
            medium=ai_params.get('sentence_length_targets', {}).get('medium', 40),
            long=ai_params.get('sentence_length_targets', {}).get('long', 30),
            very_long=ai_params.get('sentence_length_targets', {}).get('very_long', 10),
            lexical_variety_target=ai_params.get('lexical_variety_target', 0.75),
            hesitation_markers_per_200_words=ai_params.get('hesitation_markers_per_200_words', 1.0),
            comma_splices_per_100_words=ai_params.get('comma_splices_per_100_words', 1.5),
            parenthetical_asides_per_300_words=ai_params.get('parenthetical_asides_per_300_words', 2.5)
        )
        
        # Format country-specific instructions
        author_specific = ai_params.get('author_specific', {})
        sentence_targets = ai_params.get('sentence_length_targets', {})
        
        # Build complete format context with all possible variables
        format_context = {
            **author_specific,
            'minimum_sentences': self.profile.get('voice_adaptation', {}).get('caption_generation', {}).get('validation_requirements', {}).get('minimum_sentences', 5),
            'very_short': sentence_targets.get('very_short', 15),
            'medium': sentence_targets.get('medium', 35),
            'long': sentence_targets.get('long', 35),
            'very_long': sentence_targets.get('very_long', 15),
            'lexical_variety_target': ai_params.get('lexical_variety_target', 0.65),
            'hesitation_markers_per_200_words': ai_params.get('hesitation_markers_per_200_words', 1.5),
            'comma_splices_per_100_words': ai_params.get('comma_splices_per_100_words', 1.0),
            'parenthetical_asides_per_300_words': ai_params.get('parenthetical_asides_per_300_words', 2.0)
        }
        country_formatted = country_specific.format(**format_context) if country_specific else ''
        
        # Combine all instructions: detectability avoidance (priority) + traditional evasion
        return f"{universal_detection}\n\n{country_detection}\n\n{universal_formatted}\n\n{country_formatted}".strip()
    
    def _build_ai_detectability_avoidance(self, unified_system: Dict[str, Any]) -> str:
        """Build AI detectability avoidance instructions"""
        detectability_templates = unified_system.get('ai_detectability_avoidance_templates', {})
        
        # Get universal and country-specific detectability avoidance
        universal_detection = detectability_templates.get('universal_detection_avoidance', {}).get('template', '')
        country_detection = detectability_templates.get('country_detection_avoidance', {}).get(self.country, {}).get('template', '')
        
        return f"{universal_detection}\n\n{country_detection}".strip()
    
    def _get_country_voice_markers(self, unified_system: Dict[str, Any]) -> str:
        """Get country-specific voice markers from profile data (detailed linguistic patterns)"""
        if not self.profile:
            logger.warning(f"No profile loaded for {self.country}")
            # Fallback to unified system if profile not available
            country_markers = unified_system.get('country_voice_markers', {})
            country_data = country_markers.get(self.country, {})
            if country_data:
                standards = country_data.get('standards', '')
                voice_chars = country_data.get('voice_characteristics', '')
                return f"{voice_chars}\n\nSTANDARDS TO REFERENCE: {standards}"
            return ""
        
        # Extract detailed linguistic characteristics from profile
        writing_chars = self.profile.get('writing_characteristics', {})
        linguistic_chars = self.profile.get('linguistic_characteristics', {})
        
        # Build comprehensive voice instructions from profile data
        voice_instructions = []
        
        # Add author and country context
        author = self.profile.get('author', 'Unknown')
        country = self.profile.get('country', 'Unknown')
        voice_instructions.append(f"{country.upper()} VOICE ({author}):")
        
        # Sentence length requirements (critical for voice distinctiveness)
        sentence_length = writing_chars.get('sentence_length', '')
        if sentence_length:
            voice_instructions.append(f"- SENTENCE LENGTH: {sentence_length}")
        
        # Paragraph structure
        paragraph_structure = writing_chars.get('paragraph_structure', '')
        if paragraph_structure:
            voice_instructions.append(f"- PARAGRAPH STRUCTURE: {paragraph_structure}")
        
        # Transition style
        transition_style = writing_chars.get('transition_style', '')
        if transition_style:
            voice_instructions.append(f"- TRANSITIONS: {transition_style}")
        
        # Technical balance
        technical_balance = writing_chars.get('technical_balance', '')
        if technical_balance:
            voice_instructions.append(f"- TECHNICAL BALANCE: {technical_balance}")
        
        # Voice preference
        voice_preference = writing_chars.get('voice_preference', '')
        if voice_preference:
            voice_instructions.append(f"- VOICE PREFERENCE: {voice_preference}")
        
        # Structural markers (country-specific linguistic patterns)
        structural_markers = writing_chars.get('structural_markers', [])
        if structural_markers:
            voice_instructions.append("- STRUCTURAL MARKERS:")
            for marker in structural_markers[:5]:  # Top 5 markers
                voice_instructions.append(f"  • {marker}")
        
        # Add standards based on country (from unified_voice_system.yaml mapping)
        standards_map = {
            'taiwan': 'CNS (Chinese National Standards), BSMI certification',
            'italy': 'UNI EN ISO standards, ENEA protocols',
            'indonesia': 'SNI (Indonesian National Standard)',
            'united_states': 'ASTM, ASME standards'
        }
        
        country_key = self.country.lower().replace(' ', '_')
        standards = standards_map.get(country_key, '')
        if standards:
            voice_instructions.append(f"- STANDARDS TO REFERENCE: {standards}")
        
        # Add key sentence structure patterns
        sentence_structure = linguistic_chars.get('sentence_structure', {})
        patterns = sentence_structure.get('patterns', [])
        if patterns:
            voice_instructions.append("- SENTENCE PATTERNS (use naturally):")
            for pattern in patterns[:3]:  # Top 3 patterns
                voice_instructions.append(f"  • {pattern}")
        
        return "\n".join(voice_instructions)

# Convenience function for quick access
def get_voice_instructions(country: str, component_type: str, context: Optional[Dict] = None) -> str:
    """
    Quick access function to get voice instructions.
    
    Args:
        country: Author's country
        component_type: Component type (caption, text, tags)
        context: Optional context dictionary
    
    Returns:
        Voice instructions string
    """
    orchestrator = VoiceOrchestrator(country=country)
    return orchestrator.get_voice_for_component(component_type, context)


if __name__ == "__main__":
    # Test voice orchestrator
    print("🎭 Voice Orchestrator Test\n" + "=" * 60)
    
    for country in ["Taiwan", "Italy", "Indonesia", "United States"]:
        try:
            voice = VoiceOrchestrator(country=country)
            summary = voice.get_profile_summary()
            
            print(f"\n{country}:")
            print(f"  Author: {summary['author']}")
            print(f"  Word Limit: {summary['word_limit']}")
            print(f"  Tone: {summary['tone']}")
            print(f"  Formality: {summary['formality']}")
            print(f"  Signature Phrases: {summary['signature_phrases_count']}")
            
        except Exception as e:
            print(f"\n{country}: ❌ {e}")
