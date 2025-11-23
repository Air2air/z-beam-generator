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

from generation.core.component_specs import ComponentRegistry, DomainContext
from generation.core.sentence_calculator import SentenceCalculator

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
    
    @staticmethod
    def _load_technical_profiles() -> Dict:
        """Load technical profiles from YAML file (cached)."""
        if PromptBuilder._technical_profiles_cache is None:
            import yaml
            profiles_path = os.path.join('prompts', 'profiles', 'technical_profiles.yaml')
            if os.path.exists(profiles_path):
                with open(profiles_path, 'r', encoding='utf-8') as f:
                    PromptBuilder._technical_profiles_cache = yaml.safe_load(f)
                logger.debug(f"Loaded technical profiles from {profiles_path}")
            else:
                logger.warning(f"Technical profiles not found at {profiles_path}, using fallback")
                PromptBuilder._technical_profiles_cache = {}
        return PromptBuilder._technical_profiles_cache
    
    @staticmethod
    def _load_rhythm_profiles() -> Dict:
        """Load rhythm profiles from YAML file (cached)."""
        if PromptBuilder._rhythm_profiles_cache is None:
            import yaml
            profiles_path = os.path.join('prompts', 'profiles', 'rhythm_profiles.yaml')
            if os.path.exists(profiles_path):
                with open(profiles_path, 'r', encoding='utf-8') as f:
                    PromptBuilder._rhythm_profiles_cache = yaml.safe_load(f)
                logger.debug(f"Loaded rhythm profiles from {profiles_path}")
            else:
                logger.warning(f"Rhythm profiles not found at {profiles_path}, using fallback")
                PromptBuilder._rhythm_profiles_cache = {}
        return PromptBuilder._rhythm_profiles_cache
    
    @staticmethod
    def _get_technical_guidance(voice_params: Optional[Dict[str, float]], enrichment_params: Optional[Dict], component_type: str = "caption") -> str:
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
        
        # Fallback if profiles not loaded or component not found
        if not profiles or 'profiles' not in profiles or component_type not in profiles['profiles']:
            logger.warning(f"Technical profile not found for {component_type}, using fallback")
            return "Include measurements naturally when they help explain the result."
        
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
        
        # Get guidance from profile
        technical_approach = component_profile.get('technical_approach', {})
        guidance = technical_approach.get(level, '')
        
        if not guidance:
            logger.warning(f"No {level} guidance for {component_type}, using fallback")
            return "Include measurements naturally when they help explain the result."
        
        logger.debug(f"Using {level} technical guidance for {component_type}")
        return guidance.strip()
    
    @staticmethod
    def _get_sentence_guidance(voice_params: Optional[Dict[str, float]], length: int, component_type: str = "caption") -> str:
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
        
        # Fallback if profiles not loaded or component not found
        if not profiles or 'profiles' not in profiles or component_type not in profiles['profiles']:
            logger.warning(f"Rhythm profile not found for {component_type}, using fallback")
            return "Mix sentence lengths naturally."
        
        component_profile = profiles['profiles'][component_type]
        
        # Calculate rhythm pattern level
        rhythm_variation = voice_params.get('sentence_rhythm_variation', 0.5) if voice_params else 0.5
        
        # Determine pattern: consistent or varied
        pattern = 'varied' if rhythm_variation > 0.7 else 'consistent'
        
        # Get guidance from profile
        rhythm_patterns = component_profile.get('rhythm_patterns', {})
        guidance = rhythm_patterns.get(pattern, '')
        
        if not guidance:
            logger.warning(f"No {pattern} rhythm pattern for {component_type}, using fallback")
            return "Mix sentence lengths naturally."
        
        logger.debug(f"Using {pattern} rhythm pattern for {component_type} ({length} words)")
        return guidance.strip()

    @staticmethod
    def _load_anti_ai_rules() -> str:
        """
        Load anti-AI rules from prompts/rules/anti_ai_rules.txt.
        
        Returns:
            Anti-AI rules string
            
        Raises:
            FileNotFoundError: If prompts/rules/anti_ai_rules.txt doesn't exist
        """
        rules_path = os.path.join('prompts', 'rules', 'anti_ai_rules.txt')
        with open(rules_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    
    @staticmethod
    def _load_component_template(component_type: str) -> Optional[str]:
        """
        Load component-specific prompt template from prompts/components/{component}.txt.
        
        Args:
            component_type: Component type (subtitle, caption, etc.)
            
        Returns:
            Template string or None if file doesn't exist
        """
        template_path = os.path.join('prompts', 'components', f'{component_type}.txt')
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        return None
    
    @staticmethod
    def build_unified_prompt(
        topic: str,  # Renamed from 'material' for generality
        voice: Dict,
        length: Optional[int] = None,
        facts: str = "",
        context: str = "",
        component_type: str = "subtitle",
        domain: str = "materials",
        voice_params: Optional[Dict[str, float]] = None,  # NEW: Voice parameters from config
        enrichment_params: Optional[Dict] = None,  # Phase 3+: Technical intensity control
        variation_seed: Optional[int] = None,
        humanness_layer: Optional[str] = None  # NEW: Universal Humanness Layer instructions
    ) -> str:
        """
        Build unified prompt combining all elements.
        
        Args:
            topic: Subject matter (material name, historical event, recipe, etc.)
            voice: Voice profile dict
            length: Target word count (uses component default if None)
            facts: Formatted facts string
            context: Additional domain-specific context
            component_type: Type of content (subtitle, caption, description, etc.)
            domain: Content domain (materials, history, recipes, etc.)
            variation_seed: Optional seed for variation (defeats caching)
            humanness_layer: Dynamic humanness instructions from HumannessOptimizer (NEW)
            
        Returns:
            Complete prompt string
        """
        # Get component specification
        try:
            spec = ComponentRegistry.get_spec(component_type)
        except KeyError as e:
            logger.warning(f"{e}. Falling back to generic template.")
            spec = None
        
        # Get domain context
        try:
            domain_ctx = DomainContext.get_domain(domain)
        except ValueError as e:
            logger.warning(f"{e}. Using default materials domain.")
            domain_ctx = DomainContext.materials()
        
        # Use component default length if not specified
        if length is None:
            length = spec.default_length if spec else 100
        
        # Option C: Add ±30% randomization to length for natural variation
        # Use material name hash as seed for consistent but varied results per material
        if variation_seed is None:
            # Generate seed from topic name for per-material consistency
            variation_seed = hash(topic) % (2**31)
        
        random.seed(variation_seed)
        variation_factor = random.uniform(0.7, 1.3)  # ±30% (increased from ±20%)
        length = int(length * variation_factor)
        logger.debug(f"Length randomization: base × {variation_factor:.2f} = {length} words (seed={variation_seed})")
        
        # Extract voice characteristics
        country = voice.get('country', 'USA')
        author = voice.get('author', 'Expert')
        
        linguistic = voice.get('linguistic_characteristics', {})
        sentence_patterns = linguistic.get('sentence_structure', {}).get('patterns', [])
        esl_traits = "; ".join(sentence_patterns[:2]) if sentence_patterns else "Natural regional patterns"
        
        # Extract sentence style guidance from voice profile for this component
        # NEW LOCATION: voice.sentence_structure.{component_type}
        sentence_structure = voice.get('sentence_structure', {})
        sentence_style = sentence_structure.get(component_type, '')
        
        # Fallback to old location for backward compatibility
        if not sentence_style:
            generation_constraints = voice.get('generation_constraints', {})
            component_constraints = generation_constraints.get(component_type, {})
            sentence_style = component_constraints.get('sentence_style', '')
        
        # Build prompt using spec-driven template
        if spec:
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
                humanness_layer=humanness_layer  # NEW: Universal Humanness Layer
            )
        else:
            # Fallback to legacy generic prompt
            return PromptBuilder._build_generic_prompt(
                topic, author, country, esl_traits, length, facts, context
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
        humanness_layer: Optional[str] = None  # NEW: Universal Humanness Layer
    ) -> str:
        """
        Build prompt using component specification and domain context.
        
        This is the new flexible approach that works for any component type
        and content domain without hardcoding templates.
        
        Args:
            humanness_layer: Dynamic humanness instructions from HumannessOptimizer
        """
        # Build context section based on domain
        context_section = f"""TOPIC: {topic} ({domain_ctx.domain})

FACTUAL INFORMATION:
{facts if facts else f"[{domain_ctx.example_facts}]"}

DOMAIN GUIDANCE: {domain_ctx.focus_template}"""

        if context:
            context_section += f"\n\nADDITIONAL CONTEXT:\n{context}"
        
        # Load component-specific template if available
        component_template = PromptBuilder._load_component_template(spec.name)
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
            component_context = component_template.format(
                author=author,
                material=topic,
                country=country,
                length=length,
                technical_guidance=technical_guidance,
                sentence_guidance=sentence_guidance,
                facts=facts,
                context=facts if facts else context  # Use facts as context for template
            )
            # Template contains all content instructions (focus, format, style)
            context_section = f"""{component_context}

{context_section}"""
        
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
        
        # NOTE: Emotional tone now controlled by prompts/anti_ai_rules.txt and persona files
        # Dynamic emotional_tone parameter removed per Option A architecture decision
        
        if not spec.end_punctuation:
            requirements.append("- NO period at end")
        
        requirements_section = "\n".join(requirements)
        
        # Build voice section with dynamic sentence structure guidance from author profile
        # Phase 2: Apply voice_params to control personality intensity
        # NOTE: Voice/tone enforcement handled by subjective evaluator, not prompt instructions
        voice_section = f"""VOICE: {author} from {country}
- Regional patterns: {esl_traits}"""
        
        # CRITICAL: Extract and apply persona voice instructions
        if voice:
            # Core voice instruction (mandatory technical style, no theatrical elements)
            core_instruction = voice.get('core_voice_instruction', '').strip()
            if core_instruction:
                voice_section += f"\n- Core Style: {core_instruction}"
            
            # Tonal restraint (objective technical documentation mandate)
            tonal_restraint = voice.get('tonal_restraint', '').strip()
            if tonal_restraint:
                voice_section += f"\n- Tone Requirements: {tonal_restraint}"
            
            # Technical verbs required
            tech_verbs = voice.get('technical_verbs_required', [])
            if tech_verbs:
                voice_section += f"\n- Required Verbs: {', '.join(tech_verbs[:6])}"
            
            # Forbidden casual phrases
            forbidden = voice.get('forbidden_casual', [])
            if forbidden:
                voice_section += f"\n- FORBIDDEN Phrases: {', '.join(forbidden[:8])}"
        
        # Check if modular parameters are enabled
        use_modular = voice_params.get('_use_modular', False) if voice_params else False
        parameter_instances = voice_params.get('_parameter_instances', {}) if voice_params else {}
        
        if use_modular and parameter_instances:
            # MODULAR MODE: Use parameter instances to generate guidance
            logger.debug(f"Using modular parameters: {list(parameter_instances.keys())}")
            
            # Determine content length category for parameters
            if length <= 30:
                content_length = 'short'
            elif length <= 100:
                content_length = 'medium'
            else:
                content_length = 'long'
            
            # Collect guidance from each parameter instance
            for param_name, param_instance in sorted(parameter_instances.items()):
                try:
                    guidance = param_instance.generate_prompt_guidance(content_length)
                    if guidance:
                        voice_section += f"\n{guidance}"
                        logger.debug(f"Added modular guidance from {param_name}")
                except Exception as e:
                    logger.warning(f"Failed to generate guidance from {param_name}: {e}")
            
        else:
            # LEGACY MODE: Inline parameter logic (original implementation)
            logger.debug("Using legacy inline parameter logic")
            
            # Apply voice parameter intensity if provided
            trait_freq = voice_params.get('trait_frequency', 0.5) if voice_params else 0.5
            if trait_freq < 0.3:
                voice_section += "\n- Voice intensity: Subtle - minimize author personality, keep neutral"
            elif trait_freq < 0.7:
                voice_section += "\n- Voice intensity: Moderate - apply traits naturally"
            else:
                voice_section += "\n- Voice intensity: Strong - emphasize author personality throughout"
        
            # DYNAMIC SENTENCE CALCULATION: Use sentence_rhythm_variation parameter first
            rhythm_variation = voice_params.get('sentence_rhythm_variation', 0.5) if voice_params else 0.5
            
            if rhythm_variation < 0.3:
                # Low variation: Uniform, consistent sentence lengths
                if length <= 30:
                    voice_section += "\n- Sentence structure: Keep sentences consistent (8-12 words); maintain uniform rhythm"
                elif length <= 100:
                    voice_section += "\n- Sentence structure: Use consistent sentence lengths (12-16 words); avoid dramatic variation"
                else:
                    voice_section += "\n- Sentence structure: Maintain steady rhythm (14-18 words per sentence); consistent flow"
            elif rhythm_variation < 0.7:
                # Moderate variation: Mix short and medium
                if length <= 30:
                    voice_section += "\n- Sentence structure: Mix short (5-8 words) and medium (10-14 words) sentences naturally"
                elif length <= 100:
                    voice_section += "\n- Sentence structure: Balance short and medium sentences; vary rhythm naturally"
                else:
                    voice_section += "\n- Sentence structure: Mix short, medium, and longer sentences for natural flow"
            else:
                # High variation: Dramatic differences in sentence length
                if length <= 30:
                    voice_section += "\n- Sentence structure: WILD variation - mix very short (3-5 words) with much longer (15-20 words); unpredictable rhythm"
                elif length <= 100:
                    voice_section += "\n- Sentence structure: DRAMATIC variation - alternate between very short (3-6 words) and long (18-25 words); avoid patterns"
                else:
                    voice_section += "\n- Sentence structure: EXTREME variation - range from tiny (2-4 words) to extended (25+ words); chaotic, unpredictable rhythm"
            
            # Fallback to grammar_norms if available (legacy support)
            grammar_norms = voice.get('grammar_norms', {}) if voice else {}
            if grammar_norms and rhythm_variation == 0.5:  # Only use as fallback at default setting
                sentence_guidance = SentenceCalculator.get_sentence_guidance(length, grammar_norms)
                logger.debug(f"Using grammar_norms fallback: {sentence_guidance}")
            
            # Add jargon removal guidance based on jargon_removal parameter
            jargon_level = voice_params.get('jargon_removal', 0.5) if voice_params else 0.5
            
            # NOTE: jargon_level is "jargon_REMOVAL" so HIGH value = REMOVE jargon
            if jargon_level > 0.7:
                # High jargon removal: Plain language only
                voice_section += "\n- Technical terminology: AVOID jargon completely; use plain language (say 'strong material' not 'MPa', 'laser wavelength' not '1064nm', 'material stiffness' not 'Young's modulus')"
            elif jargon_level > 0.3:
                # Moderate: Essential terms only
                voice_section += "\n- Technical terminology: Use essential terms but explain when needed; prefer clarity over precision"
            else:
                # Low jargon removal: Allow technical terminology
                voice_section += "\n- Technical terminology: Use industry-standard terms (ISO, ASTM, specifications, certifications)"
            
            # Add imperfection guidance based on imperfection_tolerance parameter
            imperfection = voice_params.get('imperfection_tolerance', 0.5) if voice_params else 0.5
            
            if imperfection < 0.3:
                # Low tolerance: Perfect grammar
                voice_section += "\n- Perfect grammar and structure required; no imperfections"
            elif imperfection < 0.7:
                # Moderate: Some natural imperfections
                voice_section += "\n- Natural imperfections allowed (makes text more human)"
            else:
                # High tolerance: Embrace imperfections
                voice_section += """
- EMBRACE natural imperfections:
  * Occasional informal contractions (gonna, wanna)
  * Minor article quirks ("the steel" vs "steel")
  * Slight awkward phrasings that feel human
  * Fragment sentences for emphasis
  * Starting sentences with And, But, Or
  * Deliberate informality and speech patterns"""
            
            # Add professional voice guidance based on professional_voice parameter
            professional_level = voice_params.get('professional_voice', 0.5) if voice_params else 0.5
            
            if professional_level < 0.3:
                # Low professional: Casual vocabulary
                voice_section += "\n- Vocabulary level: CASUAL - use informal language (kinda, stuff, pretty good, sorta, really nice)"
            elif professional_level < 0.7:
                # Moderate: Balanced professional
                voice_section += "\n- Vocabulary level: Professional but accessible; avoid extremes (casual or overly formal)"
            else:
                # High professional: Formal vocabulary
                voice_section += "\n- Vocabulary level: HIGHLY FORMAL - use sophisticated language (consequently, therefore, pursuant to, facilitate, utilize)"
        
        # Common voice elements (applies to both modular and legacy modes)
        voice_section += """
- Mix formal and conversational
- Vary sentence openings and structures naturally
- Occasional article flexibility (ESL style)"""
        
        # NOTE: Personality traits now controlled by persona files only
        # Dynamic personality parameters removed per Option A architecture decision
        
        # Phase 3+: Technical language guidance moved to REQUIREMENTS section for higher priority
        
        # Phase 3B: Load anti-AI rules (static from file)
        # NOTE: Rule strictness now controlled by prompts/anti_ai_rules.txt only
        # Dynamic structural_predictability parameter removed per Option A architecture decision
        try:
            anti_ai = PromptBuilder._load_anti_ai_rules()
                
        except Exception as e:
            logger.warning(f"Failed to load anti_ai_rules.txt: {e}. Using embedded fallback.")
            anti_ai = """CRITICAL - AVOID AI PATTERNS & ADD VARIATION:
- BANNED PHRASES: "facilitates", "enables", "leverages", "demonstrates", "exhibits", "optimal", "enhanced", "robust", "comprehensive"
- BANNED CONNECTORS: "paired with", "relies on", "thrives on", "swear by", "testament to"
- BANNED STRUCTURES: "while maintaining/preserving/ensuring", "across diverse/various/multiple"
- NO formulaic structures (e.g., "X does Y while preserving Z")
- NO abstract transitions ("results suggest", "data indicate")
- VARY opening words dramatically - start each sentence differently
- VARY sentence structures - mix questions, statements, fragments
- BALANCE technical data with accessible language (don't frontload numbers)
- ADD conversational elements but NATURALLY (occasional "though", "but", "yet" for flow)
- USE active voice predominantly
- MIX precision with approximation ("around 2.7", "roughly 237")
- INCLUDE qualitative descriptions alongside quantitative data
- PREFER concrete verbs: "use", "need", "work", "choose", "apply" over abstract ones"""
        
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
        
        # Assemble complete prompt
        prompt = f"""You are {author}, writing a {spec.name} about {topic}.

{context_section}

{voice_section}
{humanness_section}
REQUIREMENTS:
{requirements_section}

{anti_ai}{enrichment_hints}

REMEMBER: Every generation should feel unique. Vary your approach, opening, and structure.{variation_note}

Generate {spec.name} for {topic}:"""
        
        return prompt
    
    # Legacy method - kept for backward compatibility
    @staticmethod
    def _build_subtitle_prompt(
        material: str,
        author: str,
        country: str,
        esl_traits: str,
        length: int,
        facts: str
    ) -> str:
        """Build subtitle-specific prompt"""
        # Calculate length range using config word_count_variation
        from generation.config.config_loader import ProcessingConfig
        config = ProcessingConfig()
        variation = config.config.get('word_count_variation', 0.10)  # Default ±10%
        
        min_length = int(length * (1.0 - variation))
        max_length = int(length * (1.0 + variation))
        
        return f"""You are {author}, writing a subtitle about laser cleaning {material}.

MATERIAL FACTS:
{facts}

VOICE: {country} technical writer
- Subtle regional patterns: {esl_traits}
- Mix formal and conversational
- Vary sentence structure naturally
- Occasional article flexibility (e.g., "Preserve integrity" vs "Preserve the integrity")

REQUIREMENTS:
- Length: {min_length}-{max_length} words (aim for natural flow, not exact count)
- Professional but natural
- No period at end
- Focus on {material}'s unique characteristics
- Avoid formulaic patterns like "Laser cleaning removes X while preserving Y"

Generate 3 different variations and pick the most natural-sounding one:"""
    
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
