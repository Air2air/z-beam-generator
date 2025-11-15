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
from typing import Dict, Optional

from processing.generation.component_specs import ComponentRegistry, DomainContext
from processing.generation.sentence_calculator import SentenceCalculator

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
    
    @staticmethod
    def _load_anti_ai_rules() -> str:
        """
        Load anti-AI rules from prompts/anti_ai_rules.txt.
        
        Returns:
            Anti-AI rules string
            
        Raises:
            FileNotFoundError: If prompts/anti_ai_rules.txt doesn't exist
        """
        rules_path = os.path.join('prompts', 'anti_ai_rules.txt')
        with open(rules_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    
    @staticmethod
    def _load_component_template(component_type: str) -> Optional[str]:
        """
        Load component-specific prompt template from prompts/{component}.txt.
        
        Args:
            component_type: Component type (subtitle, caption, etc.)
            
        Returns:
            Template string or None if file doesn't exist
        """
        template_path = os.path.join('prompts', f'{component_type}.txt')
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
        variation_seed: Optional[int] = None
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
                voice=voice  # NEW: Pass full voice profile for grammar_norms access
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
        voice: Optional[Dict] = None  # NEW: Full voice profile for grammar_norms access
    ) -> str:
        """
        Build prompt using component specification and domain context.
        
        This is the new flexible approach that works for any component type
        and content domain without hardcoding templates.
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
            # Replace placeholders in template
            component_context = component_template.format(
                author=author,
                material=topic,
                country=country
            )
            # Template contains all content instructions (focus, format, style)
            context_section = f"""{component_context}

{context_section}"""
        
        # Build requirements section with dynamic sentence structure guidance
        # Override terminology based on technical_intensity
        tech_intensity = enrichment_params.get('technical_intensity', 2) if enrichment_params else 2
        
        if tech_intensity == 1:
            # Level 1: Override to prevent any specs
            terminology = "Qualitative descriptions only; NO numbers, units, or measurements"
        else:
            # Level 2-3: Use domain default
            terminology = domain_ctx.terminology_style
        
        requirements = [
            f"- Length: {length} words (range: {spec.min_length}-{spec.max_length})",
            f"- Terminology: {terminology}"
        ]
        
        # Phase 3+: Add CRITICAL technical language requirement based on enrichment_params
        if enrichment_params:
            tech_intensity = enrichment_params.get('technical_intensity', 2)  # 1-3 scale
            if tech_intensity == 1:
                # Level 1: NO technical specs at all - REINFORCE THIS MULTIPLE TIMES
                requirements.append("\n🚫 CRITICAL REQUIREMENT - TECHNICAL LANGUAGE:")
                requirements.append("- ABSOLUTELY NO technical specifications, measurements, numbers with units, or property values")
                requirements.append("- Examples of FORBIDDEN content: '1941 K', '8.8 g/cm³', '500 J/kg·K', '19.3 g/cm³', '110 GPa', '400 MPa', '41,000,000 S/m'")
                requirements.append("- ONLY use qualitative descriptions: 'heat-resistant', 'dense', 'strong', 'conductive', 'durable'")
                requirements.append("- Focus on benefits, applications, and characteristics WITHOUT precise values")
                requirements.append("- ⚠️ THIS OVERRIDES ALL OTHER INSTRUCTIONS - NO EXCEPTIONS")
            elif tech_intensity == 2:
                # Level 2: Minimal specs (1-2 max)
                requirements.append("\n⚠️ TECHNICAL LANGUAGE: Minimal specs only (1-2 max, prefer conceptual)")
            # Level 3: Allow 3-5 specs (no restriction needed)
        
        # Phase 4: Add EMOTIONAL TONE requirement based on voice_params
        if voice_params:
            emotional_tone = voice_params.get('emotional_tone', 0.5)  # 0.0/0.5/1.0
            if emotional_tone == 0.0:
                # Level 1: Clinical, neutral
                requirements.append("\n🔬 EMOTIONAL TONE:")
                requirements.append("- Use clinical, objective, neutral language")
                requirements.append("- Focus on facts and practical benefits")
                requirements.append("- Avoid enthusiasm, excitement, or emotional appeals")
                requirements.append("- Examples: 'provides', 'offers', 'enables' NOT 'unlocks!', 'discover', 'amazing'")
            elif emotional_tone == 1.0:
                # Level 3: Evocative, enthusiastic
                requirements.append("\n✨ EMOTIONAL TONE:")
                requirements.append("- Use evocative, enthusiastic, emotionally engaging language")
                requirements.append("- Create excitement and emotional connection")
                requirements.append("- Use powerful verbs and vivid descriptions")
                requirements.append("- Examples: 'unlock', 'transform', 'discover', 'revolutionize', 'marvel at'")
            # Level 2 (0.5): Balanced - no specific guidance, AI decides naturally
        
        if not spec.end_punctuation:
            requirements.append("- NO period at end")
        
        requirements_section = "\n".join(requirements)
        
        # Build voice section with dynamic sentence structure guidance from author profile
        # Phase 2: Apply voice_params to control personality intensity
        voice_section = f"""VOICE: {author} from {country}
- Regional patterns: {esl_traits}"""
        
        # Apply voice parameter intensity if provided
        if voice_params:
            trait_freq = voice_params.get('trait_frequency', 0.5)
            if trait_freq < 0.3:
                voice_section += "\n- Voice intensity: Subtle - minimize author personality, keep neutral"
            elif trait_freq < 0.7:
                voice_section += "\n- Voice intensity: Moderate - apply traits naturally"
            else:
                voice_section += "\n- Voice intensity: Strong - emphasize author personality throughout"
        
        # DYNAMIC SENTENCE CALCULATION: Extract grammar_norms from voice profile
        grammar_norms = voice.get('grammar_norms', {}) if voice else {}
        if grammar_norms:
            # Calculate dynamic sentence target based on word count and grammar norms
            sentence_guidance = SentenceCalculator.get_sentence_guidance(length, grammar_norms)
            voice_section += f"\n- {sentence_guidance}"
            logger.debug(f"Using dynamic sentence calculation: {sentence_guidance}")
        elif sentence_style:
            # Fallback to explicit sentence_style from voice profile (backward compatibility)
            voice_section += f"\n- Sentence structure: {sentence_style}"
        else:
            # Fallback to config.yaml sentence_variation or generic guidance
            try:
                from processing.generation.component_specs import ComponentRegistry
                config = ComponentRegistry._load_config()
                sentence_variation = config.get('sentence_variation', {})
                component_variation = sentence_variation.get(spec.name, {})
                fallback_style = component_variation.get('style', '')
                
                if fallback_style:
                    voice_section += f"\n- Sentence structure: {fallback_style}"
                else:
                    # Ultimate fallback based on word count
                    if length <= 30:
                        voice_section += "\n- Sentence structure: Keep sentences concise and punchy; mix very short (3-5 words) with slightly longer statements"
                    elif length <= 100:
                        voice_section += "\n- Sentence structure: Balance short and medium sentences; vary rhythm naturally"
                    else:
                        voice_section += "\n- Sentence structure: Mix short, medium, and longer sentences for natural flow; avoid uniform length"
            except (FileNotFoundError, KeyError, ImportError) as e:
                # If config loading fails, log warning and use basic fallback
                logger.warning(f"Failed to load sentence variation config: {e}. Using length-based fallback.")
                if length <= 30:
                    voice_section += "\n- Sentence structure: Keep sentences concise and punchy; mix very short (3-5 words) with slightly longer statements"
                elif length <= 100:
                    voice_section += "\n- Sentence structure: Balance short and medium sentences; vary rhythm naturally"
                else:
                    voice_section += "\n- Sentence structure: Mix short, medium, and longer sentences for natural flow; avoid uniform length"
            except Exception as e:
                # Unexpected error - should not be silently swallowed
                logger.error(f"Unexpected error in sentence structure calculation: {e}")
                raise
        
        voice_section += """
- Mix formal and conversational
- Vary sentence openings and structures naturally
- Occasional article flexibility (ESL style)
- Natural imperfections allowed (makes text more human)"""
        
        # Phase 2: Add personality guidance based on voice_params
        personality_guidance = ""
        if voice_params:
            opinion_rate = voice_params.get('opinion_rate', 0.0)
            reader_address = voice_params.get('reader_address_rate', 0.0)
            colloquial = voice_params.get('colloquialism_frequency', 0.0)
            
            if opinion_rate > 0.5:
                personality_guidance += "\n- Include personal perspective or insight where appropriate (\"I find...\", \"In my experience...\")"
            if reader_address > 0.5:
                personality_guidance += "\n- Address reader directly using 'you' naturally (\"you'll notice\", \"you can\")"
            if colloquial > 0.6:
                personality_guidance += "\n- Use informal language and colloquialisms fitting the voice"
            
            # Add to voice section if any guidance generated
            if personality_guidance:
                voice_section += "\n\nPERSONALITY GUIDANCE:" + personality_guidance
        
        # Phase 3+: Technical language guidance moved to REQUIREMENTS section for higher priority
        
        # Phase 3B: Build anti-AI section with structural_predictability control
        try:
            anti_ai_full = PromptBuilder._load_anti_ai_rules()
            
            # Apply structural_predictability to vary rule strictness
            if voice_params:
                structural = voice_params.get('structural_predictability', 0.5)
                
                if structural < 0.3:
                    # Low = predictable = STRICT rules (all guidance)
                    anti_ai = f"""CRITICAL - STRICT AI AVOIDANCE (High Constraint):
{anti_ai_full}
- ADDITIONAL: Avoid all formulaic patterns listed above
- ADDITIONAL: Every sentence must start differently
- ADDITIONAL: Mix sentence lengths dramatically (3-20+ words)"""
                elif structural < 0.7:
                    # Medium = balanced (standard rules)
                    anti_ai = anti_ai_full
                else:
                    # High = unpredictable = MINIMAL rules (creative freedom)
                    anti_ai = """AVOID OBVIOUS AI PATTERNS:
- Vary sentence openings naturally
- Mix sentence lengths and structures
- Use conversational flow when appropriate"""
            else:
                # No voice_params = use standard rules
                anti_ai = anti_ai_full
                
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
        
        # Add component-specific enrichment hints
        enrichment_hints = ""
        if spec.name == "subtitle":
            enrichment_hints = """
SUBTITLE-SPECIFIC:
- Lead with benefit or application, NOT raw specs
- Vary structure: try questions, comparisons, or surprising facts
- Balance technical precision with readability
- Examples of good variation:
  * "Why does aerospace choose aluminum? That 2.7 g/cm³ density..."
  * "Aluminum bridges lightweight design with thermal performance..."
  * "From aircraft to packaging, aluminum's versatility stems from..."
- Avoid starting every subtitle with the material name"""
        elif spec.name == "troubleshooter":
            enrichment_hints = """
TROUBLESHOOTER-SPECIFIC:
- Start with the problem's impact, not just the technical cause
- Use conversational problem-solving language
- Vary diagnostic approaches (visual inspection, measurement, testing)
- Include "why this happens" explanations, not just "what to do"
- Mix preventive and reactive solutions"""
        
        # Add variation seed to defeat caching (if provided)
        variation_note = ""
        if variation_seed is not None:
            variation_note = f"\n\n[Generation ID: {variation_seed} - ignore this, just for tracking]"
        
        # Assemble complete prompt
        prompt = f"""You are {author}, writing a {spec.name} about {topic}.

{context_section}

{voice_section}

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
        return f"""You are {author}, writing a {length}-word subtitle about laser cleaning {material}.

MATERIAL FACTS:
{facts}

VOICE: {country} technical writer
- Subtle regional patterns: {esl_traits}
- Mix formal and conversational
- Vary sentence structure naturally
- Occasional article flexibility (e.g., "Preserve integrity" vs "Preserve the integrity")

REQUIREMENTS:
- {length} words (±2)
- Professional but natural
- No period at end
- Focus on {material}'s unique characteristics
- Avoid formulaic patterns like "Laser cleaning removes X while preserving Y"

Generate 3 different variations and pick the most natural-sounding one:"""
    
    @staticmethod
    def _build_caption_prompt(
        material: str,
        author: str,
        country: str,
        esl_traits: str,
        length: int,
        facts: str
    ) -> str:
        """Build microscopy caption prompt"""
        return f"""You are {author} from {country}, describing microscopy of {material} laser cleaning.

MATERIAL DATA:
{facts}

VOICE TRAITS:
- {esl_traits}
- Technical but accessible
- Mix short and long sentences
- Add subtle regional expressions
- Natural imperfections allowed

TASK: Write {length}-word description of surface analysis. Be specific, technical, but human.
Vary your phrasing - avoid repetitive patterns. Include 1-2 measurements when relevant.

Write description:"""
    
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
- {length} words target
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
