"""
Unified Prompt Builder

Combines material facts, voice traits, and anti-AI instructions
into single prompt to minimize detection.

Single-pass generation reduces "AI layers" that detectors flag.

Now supports flexible component types and content domains through
ComponentRegistry and DomainContext.
"""

import logging
from typing import Dict, Optional

from processing.generation.component_specs import ComponentRegistry, DomainContext

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
    def build_unified_prompt(
        topic: str,  # Renamed from 'material' for generality
        voice: Dict,
        length: Optional[int] = None,
        facts: str = "",
        context: str = "",
        component_type: str = "subtitle",
        domain: str = "materials"
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
        
        # Build prompt using spec-driven template
        if spec:
            return PromptBuilder._build_spec_driven_prompt(
                topic=topic,
                author=author,
                country=country,
                esl_traits=esl_traits,
                length=length,
                facts=facts,
                context=context,
                spec=spec,
                domain_ctx=domain_ctx
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
        length: int,
        facts: str,
        context: str,
        spec,  # ComponentSpec
        domain_ctx  # DomainContext
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

FOCUS AREAS: {spec.focus_areas}
DOMAIN GUIDANCE: {domain_ctx.focus_template}"""

        if context:
            context_section += f"\n\nADDITIONAL CONTEXT:\n{context}"
        
        # Build requirements section
        requirements = [
            f"- Length: {length} words (range: {spec.min_length}-{spec.max_length})",
            f"- Format: {spec.format_rules}",
            f"- Style: {spec.style_notes}",
            f"- Terminology: {domain_ctx.terminology_style}"
        ]
        
        if not spec.end_punctuation:
            requirements.append("- NO period at end")
        
        requirements_section = "\n".join(requirements)
        
        # Build voice section
        voice_section = f"""VOICE: {author} from {country}
- Regional patterns: {esl_traits}
- Mix formal and conversational
- Vary sentence structure naturally
- Occasional article flexibility (ESL style)
- Natural imperfections allowed (makes text more human)"""
        
        # Build anti-AI section
        anti_ai = """CRITICAL - AVOID AI PATTERNS:
- No formulaic structures (e.g., "X does Y while preserving Z")
- No abstract transitions ("results suggest", "data indicate")
- Vary opening words and sentence patterns
- Mix short punchy sentences with longer explanatory ones
- Add specific details and concrete examples
- Use natural, conversational flow"""
        
        # Assemble complete prompt
        prompt = f"""You are {author}, writing a {spec.name} about {topic}.

{context_section}

{voice_section}

REQUIREMENTS:
{requirements_section}

{anti_ai}

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
        
        if "too uniform" in failure_reason or "repetitive" in failure_reason:
            adjustments.append("CRITICAL: Vary your sentence structures more. Start some sentences differently.")
            adjustments.append("Mix short punchy sentences with longer explanatory ones.")
        
        if "ai score" in failure_reason or attempt > 2:
            adjustments.append("Add more natural imperfections:")
            adjustments.append("- Occasional article omissions (ESL style)")
            adjustments.append("- Varied punctuation")
            adjustments.append("- Mix of formal/casual tone")
            adjustments.append("- Unique opening that breaks from patterns")
        
        if adjustments:
            return prompt + "\n\n🚨 ADDITIONAL REQUIREMENTS:\n" + "\n".join(adjustments)
        
        return prompt
