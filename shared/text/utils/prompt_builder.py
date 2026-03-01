"""
Unified Prompt Builder

Combines material facts, voice traits, and anti-AI instructions
into single prompt to minimize detection.

Single-pass generation reduces "AI layers" that detectors flag.

Now supports flexible component types and content domains through
ComponentRegistry and DomainContext.
"""

import logging
import os
import random
from typing import Dict, Optional

from shared.text.utils.component_specs import ComponentRegistry, DomainContext
from shared.text.utils.prompt_registry_service import PromptRegistryService

logger = logging.getLogger(__name__)


class PromptBuilder:
    """
    Builds unified prompts for AI-resistant generation.
    
    Key strategies:
    - Inject real facts to ground content
    - Add ESL voice traits from start
    - Include deliberate imperfections
    - Vary structure dynamically
    - Avoid formulaic patterns
    
    Now supports:
    - Dynamic component types via ComponentRegistry
    - Multiple content domains via DomainContext
    - Flexible prompt building without hardcoding
    """
    
    _technical_profiles_cache = None  # Cache for technical profiles
    _rhythm_profiles_cache = None  # Cache for rhythm profiles
    _text_field_config_cache = None  # Cache for generation/text_field_config.yaml
    _shared_text_prompt_core_cache = None  # Cache for catalog.shared.textPromptCore
    _sentence_structure_cache = None  # Cache for shared/config/sentence_structure.yaml
    
    @staticmethod
    def _load_technical_profiles() -> Dict:
        """Load technical profiles from YAML file (cached)."""
        if PromptBuilder._technical_profiles_cache is None:
            import yaml
            profiles_path = os.path.join('prompts', 'registry', 'technical_profiles.yaml')
            if not os.path.exists(profiles_path):
                raise FileNotFoundError(
                    f"Technical profiles file not found or invalid at prompts/registry/technical_profiles.yaml. "
                    "Fail-fast architecture requires this file."
                )
            with open(profiles_path, 'r', encoding='utf-8') as f:
                PromptBuilder._technical_profiles_cache = yaml.safe_load(f)
            logger.debug(f"Loaded technical profiles from {profiles_path}")
        return PromptBuilder._technical_profiles_cache
    
    @staticmethod
    def _load_rhythm_profiles() -> Dict:
        """Load rhythm profiles from YAML file (cached)."""
        if PromptBuilder._rhythm_profiles_cache is None:
            import yaml
            profiles_path = os.path.join('prompts', 'registry', 'rhythm_profiles.yaml')
            if not os.path.exists(profiles_path):
                raise FileNotFoundError(
                    f"Rhythm profiles file not found or invalid at prompts/registry/rhythm_profiles.yaml. "
                    "Fail-fast architecture requires this file."
                )
            with open(profiles_path, 'r', encoding='utf-8') as f:
                PromptBuilder._rhythm_profiles_cache = yaml.safe_load(f)
            logger.debug(f"Loaded rhythm profiles from {profiles_path}")
        return PromptBuilder._rhythm_profiles_cache

    @staticmethod
    def _load_text_field_config() -> Dict:
        """Load centralized text field config from YAML file (cached)."""
        if PromptBuilder._text_field_config_cache is None:
            import yaml

            config_path = os.path.join('generation', 'text_field_config.yaml')
            if not os.path.exists(config_path):
                raise FileNotFoundError(
                    f"Text field config not found at {config_path}. "
                    "Fail-fast architecture requires this file."
                )

            with open(config_path, 'r', encoding='utf-8') as file_handle:
                PromptBuilder._text_field_config_cache = yaml.safe_load(file_handle)

            if not PromptBuilder._text_field_config_cache:
                raise ValueError(f"Text field config is empty: {config_path}")

        return PromptBuilder._text_field_config_cache

    @staticmethod
    def _load_shared_text_prompt_core() -> str:
        """Load reusable centralized text prompting core from prompt catalog (cached)."""
        if PromptBuilder._shared_text_prompt_core_cache is None:
            PromptBuilder._shared_text_prompt_core_cache = PromptRegistryService.get_shared_text_prompt_core().strip()

            if not PromptBuilder._shared_text_prompt_core_cache:
                raise ValueError("Shared text prompt core is empty in prompts/registry/prompt_catalog.yaml")

        return PromptBuilder._shared_text_prompt_core_cache

    @staticmethod
    def _load_sentence_structure_config() -> Dict:
        """Load centralized sentence structure config (cached)."""
        if PromptBuilder._sentence_structure_cache is None:
            import yaml

            config_path = os.path.join('shared', 'config', 'sentence_structure.yaml')
            if not os.path.exists(config_path):
                raise FileNotFoundError(
                    f"Sentence structure config not found at {config_path}. "
                    "Fail-fast architecture requires this file."
                )

            with open(config_path, 'r', encoding='utf-8') as file_handle:
                PromptBuilder._sentence_structure_cache = yaml.safe_load(file_handle)

            if not PromptBuilder._sentence_structure_cache:
                raise ValueError(f"Sentence structure config is empty: {config_path}")

            if not isinstance(PromptBuilder._sentence_structure_cache, dict):
                raise TypeError(
                    f"Sentence structure config must be a mapping: {config_path}"
                )

        return PromptBuilder._sentence_structure_cache
    
    @staticmethod
    def _get_technical_guidance(voice_params: Optional[Dict[str, float]], enrichment_params: Optional[Dict], component_type: str = "micro") -> str:
        """
        Returns technical guidance from profiles YAML file.
        
        Args:
            voice_params: Voice parameters (for jargon_removal)
            enrichment_params: Enrichment parameters (for technical_intensity)
            component_type: Component type for profile lookup
            
        Returns:
            Technical guidance string from profile
        """
        # Load profiles
        profiles = PromptBuilder._load_technical_profiles()
        
        # FAIL-FAST: No fallbacks permitted per .github/copilot-instructions.md
        if not profiles or 'profiles' not in profiles:
            raise FileNotFoundError(
                f"Technical profiles file not found or invalid at prompts/registry/technical_profiles.yaml. "
                f"This file is REQUIRED for all text generation. NO FALLBACKS permitted."
            )
        
        if component_type not in profiles['profiles']:
            # Component doesn't use technical profiles - return empty string (not a fallback)
            logger.debug(f"Component '{component_type}' does not use technical profiles (not in profiles YAML)")
            return ""
        
        component_profile = profiles['profiles'][component_type]
        
        # Calculate intensity level
        jargon_removal = voice_params.get('jargon_removal', 0.5) if voice_params else 0.5
        tech_intensity = enrichment_params.get('technical_intensity', 0.22) if enrichment_params else 0.22
        
        # Determine level: minimal, moderate, or detailed
        if jargon_removal > 0.7 or tech_intensity < 0.3:
            level = 'minimal'
        elif tech_intensity < 0.7:
            level = 'moderate'
        else:
            level = 'detailed'
        
        # Get guidance from profile - FAIL-FAST if missing
        technical_approach = component_profile.get('technical_approach', {})
        guidance = technical_approach.get(level, '')
        
        if not guidance:
            raise ValueError(
                f"No '{level}' technical guidance found for component '{component_type}'. "
                f"Profile exists but missing technical_approach.{level} entry. "
                f"Fix prompts/registry/technical_profiles.yaml. "
                f"NO FALLBACKS permitted."
            )
        
        logger.debug(f"Using {level} technical guidance for {component_type}")
        return guidance.strip()
    
    @staticmethod
    def _get_sentence_guidance(voice_params: Optional[Dict[str, float]], length: int, component_type: str = "micro") -> str:
        """
        Returns sentence structure guidance from rhythm profiles YAML file.
        
        Args:
            voice_params: Voice parameters (for rhythm_variation)
            length: Target content length in words
            component_type: Component type for profile lookup
            
        Returns:
            Sentence structure guidance string from profile
        """
        # Load profiles
        profiles = PromptBuilder._load_rhythm_profiles()
        
        # FAIL-FAST: No fallbacks permitted per .github/copilot-instructions.md
        if not profiles or 'profiles' not in profiles:
            raise FileNotFoundError(
                f"Rhythm profiles file not found or invalid at prompts/registry/rhythm_profiles.yaml. "
                f"This file is REQUIRED for all text generation. NO FALLBACKS permitted."
            )
        
        if component_type not in profiles['profiles']:
            # Component doesn't use rhythm profiles - return empty string (not a fallback)
            logger.debug(f"Component '{component_type}' does not use rhythm profiles (not in profiles YAML)")
            return ""
        
        component_profile = profiles['profiles'][component_type]
        
        # Calculate rhythm pattern level
        rhythm_variation = voice_params.get('sentence_rhythm_variation', 0.5) if voice_params else 0.5
        
        # Determine pattern: consistent or varied
        pattern = 'varied' if rhythm_variation > 0.7 else 'consistent'
        
        # Get guidance from profile
        rhythm_patterns = component_profile.get('rhythm_patterns', {})
        guidance = rhythm_patterns.get(pattern, '')
        
        if not guidance:
            raise ValueError(
                f"No '{pattern}' rhythm pattern for component '{component_type}'. "
                "Fix prompts/registry/rhythm_profiles.yaml. NO FALLBACKS permitted."
            )
        
        logger.debug(f"Using {pattern} rhythm pattern for {component_type} ({length} words)")
        return guidance.strip()

    @staticmethod
    def _build_voice_instruction(
        author: str,
        country: str,
        esl_traits: str,
        voice: Optional[Dict],
        voice_params: Optional[Dict[str, float]],
        length: int
    ) -> str:
        """
        Build complete voice instruction section from persona data.
        
        This extracts voice instructions from persona files and formats them
        for injection into domain prompt templates via {voice_instruction} placeholder.
        
        Args:
            author: Author name
            country: Author country
            esl_traits: ESL linguistic patterns
            voice: Full voice/persona dict (MANDATORY - must not be None)
            voice_params: Voice parameters (intensity, rhythm, etc.)
            length: Target word count
            
        Returns:
            Formatted voice instruction string
            
        Raises:
            ValueError: If voice dict is None or empty (fail-fast requirement)
        """
        # MANDATORY: Voice instructions must be present for all text generation
        if not voice:
            raise ValueError(
                f"Voice instructions are MANDATORY for all text generation. "
                f"Author '{author}' from '{country}' has no voice/persona data loaded. "
                f"Check that persona file exists in shared/voice/profiles/"
            )
        
        # VOICE INSTRUCTION CENTRALIZATION POLICY:
        # Voice instructions ONLY exist in shared/voice/profiles/*.yaml
        # They are injected directly into domain prompts via {voice_instruction} placeholder
        # Humanness layer provides structural variation only (separate concern)
        
        # Extract voice instructions from persona
        core_voice = voice.get('core_voice_instruction', '')
        tonal_restraint = voice.get('tonal_restraint', '')
        forbidden = voice.get('forbidden_phrases', [])
        
        voice_section = f"""AUTHOR: {author} from {country}
- Regional patterns: {esl_traits}

VOICE INSTRUCTIONS (from shared/voice/profiles/{author.lower().replace(' ', '_').replace(',', '').replace('.', '')}.yaml):
{core_voice}"""
        
        if tonal_restraint:
            voice_section += f"\n\n{tonal_restraint}"
        
        if forbidden:
            forbidden_str = "\n".join([f"  - {phrase}" for phrase in forbidden])
            voice_section += f"\n\n**FORBIDDEN PHRASES** (never use these):\n{forbidden_str}"
        
        # GLOBAL VOICE ENFORCEMENT (applies to all domains automatically)
        # Single source of truth - edit once, propagates everywhere
        voice_section += f"""\n\n🔥 VOICE COMPLIANCE REQUIREMENT (MANDATORY):
You MUST write as {author} from {country} using the EXACT linguistic patterns specified above. 
This is not optional—your writing must demonstrate the specific EFL traits, sentence structures, 
vocabulary choices, and grammatical patterns detailed for your nationality. Generic technical 
English is unacceptable.

CRITICALLY: Use the specific voice patterns from your profile (cleft structures, preposition 
extensions, phrasal verbs, article omission, temporal markers, etc.) throughout—at least 1-2 
distinctive markers per paragraph as specified in your voice instructions."""
        
        # NO voice instruction duplication - violates Voice Instruction Centralization Policy
        # Humanness layer will inject full persona through {voice_instruction} placeholder
        
        return voice_section

    @staticmethod
    def _load_component_template(component_type: str, domain: str) -> Optional[str]:
        """
        Load component-specific prompt template from section_display_schema.yaml.
        
        SCHEMA-ONLY APPROACH:
        Source: data/schemas/section_display_schema.yaml (REQUIRED)
        Loads from sections.{component_type}.prompt field
        
        Args:
            component_type: Component type (contaminatedBy, healthEffects, etc.)
            domain: Domain name (materials, contaminants, settings)
            
        Returns:
            Template string or None if not found in schema
            
        Raises:
            FileNotFoundError: If schema doesn't exist or can't be loaded
        """
        if not domain:
            raise ValueError("Domain is required to load component templates")

        try:
            prompt_text = PromptRegistryService.get_schema_prompt(
                domain=domain,
                component_type=component_type,
                include_descriptor=False,
            )
            if prompt_text:
                logger.debug(f"✅ Loaded prompt from schema registry service: {domain}.{component_type}")
                return prompt_text.strip()

            logger.debug(f"Component not in schema: {domain}.{component_type}")
            return None
        except Exception as e:
            logger.error(f"Failed to load section prompt for {domain}.{component_type}: {e}")
            raise FileNotFoundError(
                "Could not load section prompt via PromptRegistryService. "
                f"Domain: {domain}, component: {component_type}, error: {e}"
            )
    
    @staticmethod
    def build(context: 'PromptContext', **kwargs) -> str:
        """
        Build prompt using PromptContext object (NEW unified interface).
        
        This is the preferred method for new code. Extracts parameters from
        PromptContext and delegates to build_unified_prompt().
        
        Args:
            context: PromptContext object with all generation parameters
            **kwargs: Additional parameters to override context values
            
        Returns:
            Complete prompt string
            
        Example:
            >>> from shared.text.prompt_context import PromptContext
            >>> context = PromptContext(
            ...     topic="Aluminum",
            ...     voice=voice_dict,
            ...     length=50,
            ...     component_type="description",
            ...     domain="materials"
            ... )
            >>> prompt = PromptBuilder.build(context)
        """
        # Extract parameters from context
        params = {
            'topic': context.topic,
            'voice': context.voice,
            'length': context.length,
            'component_type': context.component_type,
            'domain': context.domain,
            'facts': context.facts or "",
            'context': context.context or "",
            'voice_params': context.voice_params,
            'enrichment_params': context.enrichment_params,
            'variation_seed': context.variation_seed,
            'humanness_layer': context.humanness_layer,
            'faq_count': context.faq_count,
            'item_data': context.item_data
        }
        
        # Allow kwargs to override context values
        params.update(kwargs)
        
        return PromptBuilder.build_unified_prompt(**params)
    
    @staticmethod
    def build_unified_prompt(
        topic: str,  # Renamed from 'material' for generality
        voice: Dict,
        length: Optional[int] = None,
        facts: str = "",
        context: str = "",
        component_type: str = "micro",
        domain: str = "materials",
        voice_params: Optional[Dict[str, float]] = None,  # NEW: Voice parameters from config
        enrichment_params: Optional[Dict] = None,  # Phase 3+: Technical intensity control
        variation_seed: Optional[int] = None,
        humanness_layer: Optional[str] = None,  # NEW: Universal Humanness Layer instructions
        faq_count: Optional[int] = None,  # For FAQ generation
        item_data: Optional[Dict] = None  # NEW: Full item data for template placeholders
    ) -> str:
        """
        Build unified prompt combining all elements.
        
        Args:
            topic: Subject matter (material name, historical event, recipe, etc.)
            voice: Voice profile dict
            length: Target word count (uses component default if None)
            facts: Formatted facts string
            context: Additional domain-specific context
            component_type: Type of content (micro, description, faq, etc.)
            domain: Content domain (materials, history, recipes, etc.)
            variation_seed: Optional seed for variation (defeats caching)
            humanness_layer: Dynamic humanness instructions from HumannessOptimizer (NEW)
            item_data: Full item data dict for extracting template placeholders (NEW)
            
        Returns:
            Complete prompt string
        """
        # Get component specification (fail-fast)
        spec = ComponentRegistry.get_spec(component_type)

        # Get domain context (fail-fast)
        domain_ctx = DomainContext.get_domain(domain)
        
        # Use component default length if not specified
        if length is None:
            length = spec.default_length
        
        # SINGLE SOURCE OF TRUTH: Length variation calculated here ONLY.
        # Use call-provided seed when present (for traceability); otherwise use fresh entropy.
        if variation_seed is None:
            variation_seed = random.SystemRandom().randint(0, 2**31 - 1)

        rng = random.Random(variation_seed)
        text_field_config = PromptBuilder._load_text_field_config()
        randomization_cfg = text_field_config.get('randomization_range')
        if not isinstance(randomization_cfg, dict):
            raise ValueError(
                "Missing required config block: randomization_range in generation/text_field_config.yaml"
            )

        min_factor = randomization_cfg.get('min_factor')
        max_factor = randomization_cfg.get('max_factor')
        if not isinstance(min_factor, (int, float)) or not isinstance(max_factor, (int, float)):
            raise ValueError(
                "text_length_randomization.min_factor and max_factor must be numeric"
            )
        if min_factor <= 0 or max_factor <= 0 or min_factor > max_factor:
            raise ValueError(
                f"Invalid text_length_randomization range: min_factor={min_factor}, max_factor={max_factor}"
            )

        variation_factor = rng.uniform(float(min_factor), float(max_factor))
        length = int(length * variation_factor)
        logger.info(f"📏 Length variation: {length} words (base × {variation_factor:.2f}, seed={variation_seed})")
        
        # Extract voice characteristics
        country = voice.get('country', 'USA')
        author = voice.get('author', 'Expert')
        
        linguistic = voice.get('linguistic_characteristics', {})
        sentence_patterns = linguistic.get('sentence_structure', {}).get('patterns', [])
        esl_traits = "; ".join(sentence_patterns[:2]) if sentence_patterns else "Natural regional patterns"
        
        # Extract sentence style guidance from shared config + voice profile
        # NEW LOCATION: voice.sentence_structure.{component_type}
        sentence_config = PromptBuilder._load_sentence_structure_config()
        shared_sentence_structure = sentence_config.get('components')
        if not isinstance(shared_sentence_structure, dict):
            raise TypeError(
                "shared/config/sentence_structure.yaml must contain 'components' mapping"
            )

        sentence_structure = dict(shared_sentence_structure)
        voice_sentence_structure = voice.get('sentence_structure', {})
        if voice_sentence_structure:
            if not isinstance(voice_sentence_structure, dict):
                raise TypeError("voice.sentence_structure must be a dictionary when provided")
            sentence_structure.update(voice_sentence_structure)
        sentence_key_candidates = [component_type]
        if component_type in ('pageDescription', 'page_description'):
            sentence_key_candidates.append('description')
        if component_type == 'caption':
            sentence_key_candidates.append('micro')

        sentence_style = ''
        for key in sentence_key_candidates:
            value = sentence_structure.get(key, '')
            if value:
                sentence_style = value
                break

        if not sentence_style:
            generation_constraints = voice.get('generation_constraints', {})
            if not isinstance(generation_constraints, dict):
                raise TypeError("voice.generation_constraints must be a dictionary when provided")

            constraint_aliases = []
            if component_type in ('pageDescription', 'page_description', 'description'):
                constraint_aliases.append('text')
            if component_type in ('micro', 'caption'):
                constraint_aliases.append('micro')
            if component_type == 'faq':
                constraint_aliases.append('faq')

            for key in constraint_aliases:
                constraint_value = generation_constraints.get(key)
                if constraint_value:
                    if isinstance(constraint_value, dict):
                        parts = [f"{k}={v}" for k, v in constraint_value.items()]
                        sentence_style = f"Use {key} sentence style constraints: " + ", ".join(parts)
                    else:
                        sentence_style = f"Use {key} sentence style constraints: {constraint_value}"
                    break
        
        if not sentence_style:
            raise ValueError(
                f"Missing sentence_structure for component '{component_type}' in voice profile. "
                "Fail-fast architecture requires explicit component sentence style."
            )
        
        return PromptBuilder._build_spec_driven_prompt(
            topic=topic,
            author=author,
            country=country,
            esl_traits=esl_traits,
            sentence_style=sentence_style,
            length=length,
            facts=facts,
            context=context,
            spec=spec,
            domain_ctx=domain_ctx,
            voice_params=voice_params,  # NEW: Pass to spec builder
            enrichment_params=enrichment_params,  # Phase 3+: Technical intensity
            variation_seed=variation_seed,
            voice=voice,  # NEW: Pass full voice profile for grammar_norms access
            humanness_layer=humanness_layer,  # NEW: Universal Humanness Layer
            faq_count=faq_count,  # Pass FAQ count
            item_data=item_data  # NEW: Pass item_data for template placeholders
        )
    
    @staticmethod
    def _build_spec_driven_prompt(
        topic: str,
        author: str,
        country: str,
        esl_traits: str,
        sentence_style: str,
        length: int,
        facts: str,
        context: str,
        spec,  # ComponentSpec
        domain_ctx,  # DomainContext
        voice_params: Optional[Dict[str, float]] = None,  # NEW: Voice parameters
        enrichment_params: Optional[Dict] = None,  # Phase 3+: Technical intensity
        variation_seed: Optional[int] = None,
        voice: Optional[Dict] = None,  # NEW: Full voice profile for grammar_norms access
        humanness_layer: Optional[str] = None,  # NEW: Universal Humanness Layer
        faq_count: Optional[int] = None,  # For FAQ generation
        item_data: Optional[Dict] = None  # NEW: Full item data for template placeholders
    ) -> str:
        """
        Build prompt using component specification and domain context.
        
        This is the new flexible approach that works for any component type
        and content domain without hardcoding templates.
        
        Args:
            humanness_layer: Dynamic humanness instructions from HumannessOptimizer
        """
        # Build context section based on domain
        # NO EXAMPLES - facts come from actual data only
        facts_section = f"FACTUAL INFORMATION:\n{facts}" if facts else ""
        context_section = f"""TOPIC: {topic} ({domain_ctx.domain})

{facts_section}

DOMAIN GUIDANCE: {domain_ctx.focus_template}""".strip()

        if context:
            context_section += f"\n\nADDITIONAL CONTEXT:\n{context}"
        
        # Build voice_instruction FIRST (before template formatting)
        # This needs to be built early so it can be injected into component templates
        voice_instruction = PromptBuilder._build_voice_instruction(
            author=author,
            country=country,
            esl_traits=esl_traits,
            voice=voice,
            voice_params=voice_params,
            length=length
        )
        
        # Load component-specific template if available (domain-specific first)
        component_template = PromptBuilder._load_component_template(spec.name, domain_ctx.domain)
        voice_injected_via_template = False
        if component_template:
            # NEW: Build dynamic guidance sections based on config
            technical_guidance = PromptBuilder._get_technical_guidance(
                voice_params=voice_params,
                enrichment_params=enrichment_params,
                component_type=spec.name
            )
            
            sentence_guidance = PromptBuilder._get_sentence_guidance(
                voice_params=voice_params,
                length=length,
                component_type=spec.name
            )
            
            # Replace placeholders in template
            # Set default FAQ count if not provided
            if faq_count is None:
                faq_count = 3  # Default FAQ count
            
            # Build template parameters dict with all possible placeholders
            # CRITICAL: These are OPTIONAL placeholders for cross-domain compatibility.
            # Templates that use placeholders not listed here MUST provide them via facts/context.
            # Empty strings allow templates to use {placeholder} without KeyError IF the value is optional.
            
            # Extract from item_data if provided, otherwise use defaults/empty
            item_data = item_data or {}
            
            template_params = {
                'author': author,
                'author_name': author,  # Alias for postprocess templates
                'author_country': country,  # Explicit country for postprocess
                'material': topic,
                'material_name': topic,  # Alias for postprocess templates
                'identifier': topic,  # Generic identifier
                'contaminant': topic,  # For contaminants domain
                'contaminant_name': topic,  # Alias for contaminants
                'country': country,
                'length': length,
                'technical_guidance': technical_guidance,
                'sentence_guidance': sentence_guidance,
                'facts': facts,
                'properties': facts,  # Alias - properties are in facts
                'context': facts if facts else context,
                'faq_count': faq_count,
                'voice_instruction': voice_instruction,  # CRITICAL: Must be present
                # Extract from item_data (postprocess and domain-specific)
                'category': item_data.get('category', ''),
                'subcategory': item_data.get('subcategory', ''),
                'context_notes': item_data.get('context_notes', ''),
                'description': item_data.get('description', ''),
                'machine_settings': item_data.get('machine_settings', ''),
                'challenges': item_data.get('challenges', ''),
                'existing_content': item_data.get('existing_content', ''),  # For postprocess templates
                'valid_materials': ', '.join(item_data.get('valid_materials', []))  # For contaminants cross-linking
            }
            
            # FAIL-FAST: No try/except fallback. If template requires a placeholder not in
            # template_params, generation MUST fail with KeyError.
            component_context = component_template.format(**template_params)
            voice_injected_via_template = '{voice_instruction}' in component_template
            # Template contains all content instructions (focus, format, style)
            context_section = f"""{component_context}

{context_section}"""

        # Ensure voice instructions are ALWAYS present (centralized source of truth).
        # If a component template omits {voice_instruction}, inject the rendered persona block here.
        if not voice_injected_via_template:
            context_section = f"""{context_section}

VOICE INSTRUCTIONS:
{voice_instruction}"""

        shared_text_prompt_core = PromptBuilder._load_shared_text_prompt_core()
        
        # Build requirements section with dynamic sentence structure guidance
        # Override terminology based on technical_intensity (0.0-1.0 normalized)
        tech_intensity = enrichment_params.get('technical_intensity', 0.22) if enrichment_params else 0.22
        
        if tech_intensity < 0.15:  # Very low (slider 1-2)
            # Level 1: Override to prevent any specs
            terminology = "Qualitative descriptions only; NO numbers, units, or measurements"
        else:
            # Level 2-10: Use domain default
            terminology = domain_ctx.terminology_style
        
        # Length is specified in humanness_layer (when provided), not here
        # This prevents duplication and conflicting length instructions
        requirements = [
            f"- Terminology: {terminology}"
        ]
        
        # Phase 3+: Add CRITICAL technical language requirement based on enrichment_params
        if enrichment_params:
            tech_intensity = enrichment_params.get('technical_intensity', 0.22)  # 0.0-1.0 normalized
            if tech_intensity < 0.15:  # Very low (slider 1-2)
                # Level 1: NO technical specs at all - REINFORCE THIS MULTIPLE TIMES
                requirements.append("\n🚫 CRITICAL REQUIREMENT - TECHNICAL LANGUAGE:")
                requirements.append("- ABSOLUTELY NO technical specifications, measurements, numbers with units, or property values")
                requirements.append("- Examples of FORBIDDEN content: '1941 K', '8.8 g/cm³', '500 J/kg·K', '19.3 g/cm³', '110 GPa', '400 MPa', '41,000,000 S/m'")
                requirements.append("- ONLY use qualitative descriptions: 'heat-resistant', 'dense', 'strong', 'conductive', 'durable'")
                requirements.append("- Focus on benefits, applications, and characteristics WITHOUT precise values")
                requirements.append("- ⚠️ THIS OVERRIDES ALL OTHER INSTRUCTIONS - NO EXCEPTIONS")
            elif tech_intensity < 0.5:  # Low-medium (slider 3-5)
                # Level 2: Minimal specs (1-2 max)
                requirements.append("\n⚠️ TECHNICAL LANGUAGE: Minimal specs only (1-2 max, prefer conceptual)")
            # High (slider 6-10): Allow 3-5 specs (no restriction needed)
        
        # NOTE: Emotional tone controlled by base.txt system template and persona files
        # Dynamic emotional_tone parameter removed per Option A architecture decision
        
        if not spec.end_punctuation:
            requirements.append("- NO period at end")

        # PageDescription-specific phrase guardrails to reduce repeated quality failures.
        if spec.name == 'pageDescription':
            requirements.append("- Do NOT use these phrases: 'stands out', 'in practice', 'presents a challenge', 'critical pitfall'")
            requirements.append("- Use direct, concrete phrasing without transition clichés")
        
        requirements_section = "\n".join(requirements)
        
        # Voice section already built via voice_instruction at line 406
        # and injected into component template via {voice_instruction} placeholder
        # NO DUPLICATION - voice appears only once in final prompt
        
        # Phase 3+: Technical language guidance moved to REQUIREMENTS section for higher priority
        
        # Phase 3B: Anti-AI rules are now in base.txt system template
        # The humanness_layer already contains comprehensive anti-AI guidance
        # This section is kept minimal to avoid prompt bloat
        anti_ai = ""  # Rules consolidated into base.txt and humanness_layer
        
        # Component-specific enrichment hints are in prompt templates
        # NO content instructions in code - see Content Instruction Policy
        enrichment_hints = ""
        
        # Add variation seed to defeat caching (if provided)
        variation_note = ""
        if variation_seed is not None:
            variation_note = f"\n\n[Generation ID: {variation_seed} - ignore this, just for tracking]"
        
        # Inject Universal Humanness Layer (between context and requirements)
        humanness_section = ""
        if humanness_layer:
            humanness_section = f"\n\n{humanness_layer}\n"
        
        # Schema-based components require explicit OUTPUT FORMAT
        # List of schema-based components that use title/description structure
        schema_components = {
            'contaminatedBy', 'relatedMaterials', 'materialCharacteristics',
            'laserMaterialInteraction', 'physicalProperties', 'appearanceVariations',
            'healthEffects', 'exposureLimits', 'ppeRequirements', 'emergencyResponse',
            'storageRequirements', 'regulatoryStandards', 'regulatoryClassification',
            'industryApplications', 'commonChallenges', 'detectionMethods',
            'preventionStrategies', 'removalMethods', 'environmentalImpact',
            'continuousMonitoring', 'reactivity', 'producedByMaterials',
            'producedFromContaminants', 'relatedContaminants', 'relatedCompounds'
        }
        
        output_format_section = ""
        if spec.name in schema_components:
            output_format_section = """

    OUTPUT FORMAT:
Title: [Write a 3-5 word concise title here]

Description: [Write the full description here]

    Use exactly two labeled lines. The first line must start with "Title:" and the second line must start with "Description:"."""
        
        # Assemble complete prompt
        # NOTE: Voice instructions already in context_section via {voice_instruction} placeholder
        # No generic "be unique" override that negates specific voice rules
        # NOTE: Template already includes author context - no "You are" prefix needed
        prompt = f"""{context_section}

    SHARED CORE GUIDANCE:
    {shared_text_prompt_core}
{humanness_section}
REQUIREMENTS:
{requirements_section}
{output_format_section}

{anti_ai}{enrichment_hints}{variation_note}

Generate {spec.name} for {topic}:"""
        
        return prompt
    
    # Legacy method - kept for backward compatibility
    # Component-specific prompt methods REMOVED (November 18, 2025)
    # All content instructions now ONLY in prompts/*.txt templates
    # Use _load_prompt_template(component_type) for generic template loading
    # See: Component Discovery Policy + Content Instruction Policy
    
    @staticmethod
    def _build_generic_prompt(
        material: str,
        author: str,
        country: str,
        esl_traits: str,
        length: int,
        facts: str,
        context: str
    ) -> str:
        """Build generic content prompt"""
        return f"""You are {author}, a technical writer from {country}, writing about {material}.

MATERIAL INFORMATION:
{facts}

ADDITIONAL CONTEXT:
{context}

VOICE CHARACTERISTICS:
- {esl_traits}
- Length: Aim for natural expression (length will vary naturally)
- Mix technical and accessible language
- Natural flow with varied sentence structures
- Subtle regional flavor
- Occasional minor imperfections (natural for ESL)

Write factual, grounded content. Avoid AI-like uniformity. Be human.

Generate text:"""
    
    @staticmethod
    def adjust_on_failure(prompt: str, failure_reason: str, attempt: int) -> str:
        """
        Dynamically adjust prompt based on detection failure.
        
        Args:
            prompt: Original prompt
            failure_reason: Why detection failed
            attempt: Attempt number
            
        Returns:
            Modified prompt
        """
        adjustments = []
        
        if "too uniform" in failure_reason or "repetitive" in failure_reason or attempt > 1:
            adjustments.append("🚨 CRITICAL - OUTPUT TOO UNIFORM:")
            adjustments.append("- Start with a COMPLETELY different approach (question? comparison? surprising fact?)")
            adjustments.append("- Avoid leading with material name + technical specs")
            adjustments.append("- Try: benefit-first, application-first, or problem-solution structure")
            adjustments.append("- Mix sentence lengths: one short (5 words), one medium (10-12), one longer")
        
        if "ai score" in failure_reason or "formulaic" in failure_reason or attempt > 2:
            adjustments.append("🚨 AI PATTERNS DETECTED:")
            adjustments.append("- BANNED phrases: 'enables', 'facilitates', 'leverages', 'demonstrates', 'provides'")
            adjustments.append("- BANNED structure: 'X with Y property for Z application'")
            adjustments.append("- ADD conversational connectors: 'though', 'but', 'yet', 'while'")
            adjustments.append("- USE approximations: 'around', 'roughly', 'nearly', 'about'")
            adjustments.append("- INCLUDE qualitative: 'lightweight yet strong', 'surprisingly durable'")
            adjustments.append("- TRY unexpected opening: Don't start with the obvious")
        
        if attempt >= 3:
            adjustments.append("🔥 FINAL ATTEMPT - MAXIMUM VARIATION:")
            adjustments.append("- Completely break from previous patterns")
            adjustments.append("- Use fragment sentences if natural")
            adjustments.append("- Add rhetorical elements")
            adjustments.append("- Consider contrarian or unexpected angle")
            adjustments.append("- Prioritize readability over technical precision")
        
        if adjustments:
            return prompt + "\n\n" + "\n".join(adjustments) + "\n"
        
        return prompt
