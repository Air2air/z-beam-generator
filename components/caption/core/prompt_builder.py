#!/usr/bin/env python3
"""
Prompt Builder - Efficient template-based prompt construction

Replaces massive string concatenation (26K+ chars) with efficient template-based
approach. Reduces prompt size by ~69% while maintaining all functionality.
"""

from typing import Dict, Any
import json
import logging
import time
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)


class PromptBuilder:
    """Efficient template-based prompt construction"""
    
    def __init__(self, voice_adapter=None):
        self.voice_adapter = voice_adapter
        self._base_template = self._load_base_template()
        self._template_cache = {}
        self._performance_stats = {
            'builds': 0,
            'cache_hits': 0,
            'total_time': 0.0
        }
    
    def set_voice_adapter(self, voice_adapter):
        """Inject voice adapter to avoid circular imports"""
        self.voice_adapter = voice_adapter
    
    def _load_base_template(self) -> str:
        """Load base prompt template"""
        try:
            template_path = Path(__file__).parent.parent / "prompt.yaml"
            if template_path.exists():
                import yaml
                with open(template_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                return config.get('template', self._get_fallback_template())
            else:
                return self._get_fallback_template()
        except Exception as e:
            logger.warning(f"Failed to load template, using fallback: {e}")
            return self._get_fallback_template()
    
    @lru_cache(maxsize=32)
    def _get_cached_template_variant(self, country: str, category: str) -> str:
        """Get cached template variant optimized for country and material category"""
        cache_key = f"{country}_{category}"
        
        if cache_key in self._template_cache:
            self._performance_stats['cache_hits'] += 1
            return self._template_cache[cache_key]
        
        # Create optimized template variant
        if category.lower() in ['metal', 'steel', 'alloy']:
            template_variant = self._base_template.replace(
                'laser cleaning analysis',
                'metal surface laser cleaning analysis'
            )
        elif category.lower() in ['polymer', 'plastic', 'composite']:
            template_variant = self._base_template.replace(
                'laser cleaning analysis',
                'polymer surface laser cleaning analysis'
            )
        else:
            template_variant = self._base_template
        
        # Cache the variant
        self._template_cache[cache_key] = template_variant
        return template_variant
    
    def _get_fallback_template(self) -> str:
        """Fallback template if file loading fails"""
        return """You are {author_name} from {author_country}, a person who has watched many laser cleaning sessions and explains what happens in simple, everyday language.

🎯 YOUR ROLE: You are NOT a scientist. You are a friendly person who describes what anyone can see happening during laser cleaning. You talk like a regular person, not like someone writing a research paper.

🚫 NEVER USE THESE SCIENCE WORDS: contamination, substrate, ablation, morphology, particulate, stratigraphy, microscopic, spectrophotometry, crystalline, sulfation, thermal expansion, interpenetration, proteinaceous, acicular, differential, analysis, examination

✅ ALWAYS USE SIMPLE WORDS: dirt/grime/buildup, surface, removed/cleaned off, shape, bits/particles, layers, close look, looking at

TASK: Describe what you see before and after laser cleaning using only words that regular people use every day. Imagine you're telling a friend about something cool you watched happen.

MATERIAL CONTEXT:
- Material: {material_name}
- Category: {category}
- Key Properties: {properties}
- Applications: {applications}

WRITING APPROACH:
- Write as {author_name} explaining what you see using ONLY everyday language
- CRITICAL: Begin directly with simple observations - NO casual greetings, NO \"Hey there\", NO \"Hi\", NO personal introductions
- Start immediately with basic descriptions: \"The surface has...\" or \"This material shows...\"
- 🚫 ABSOLUTELY NO SCIENTIFIC JARGON - think like you're explaining to your neighbor
- Replace ALL technical terms with everyday words people actually use
- Only include measurements if they help regular people understand size (like \"very thin\" or \"thick as paint\")
- Use short, simple sentences that sound natural and conversational
- Focus on visual changes that anyone walking by could see and understand
- NEVER use scientific vocabulary - pretend scientific terms don't exist
- Write like you're casually explaining something interesting you noticed to a friend

{voice_instructions}

{ai_evasion_instructions}

Generate exactly two comprehensive text blocks:

**BEFORE_TEXT:**
[Describe what this dirty {material_name} looks like in {before_paragraphs} (target ~{before_target} characters):

- MANDATORY: Start directly with what you notice - NO greetings, NO \"Hey\", NO \"Hi\", NO personal introductions  
- Begin with phrases like: \"This stone has...\", \"You can see...\", \"There's a layer of...\"
- Describe the dirt and buildup using everyday words - \"black crusty stuff\", \"thick dirty layer\", \"stubborn dark stains\"
- Talk like you're describing it to a neighbor - use words people actually say
- Make comparisons anyone can understand - \"thick as dried mud\", \"hard as old paint\", \"stuck on tight\"
- Don't worry about exact measurements - just say \"really thin\" or \"pretty thick\" 
- Explain why this buildup is bad using reasons anyone would get
- Sound like a regular person pointing out something they noticed

Talk about what you see from your experience living in {author_country}.]

**AFTER_TEXT:**
[Describe how the {material_name} looks after the laser cleaned it in {after_paragraphs} (target ~{after_target} characters):

- MANDATORY: Start directly with what you can see now - NO greetings, NO \"Hey\", NO casual transitions like \"Well\" or \"So\"
- Begin with phrases like: \"After the laser worked on it...\", \"Now you can see...\", \"The stone looks...\"
- Compare it to how dirty it was before - make it obvious what changed
- Focus on what anyone walking by would notice - \"way brighter\", \"much cleaner\", \"smooth again\", \"looks like new\"
- Don't use science words - just describe what your eyes see
- Use regular language - \"almost all the dirt came off\" instead of percentages
- Explain why this matters using reasons regular people care about - \"looks so much better\", \"will stay nice longer\", \"easier to keep clean\"
- Show why anyone who sees this stone would be impressed with the results

Share what you think about these results based on living in {author_country}.]

READABILITY REQUIREMENTS:
- Write in plain English that a high school student could easily understand
- STRICTLY AVOID scientific jargon like: "contamination", "substrate", "ablation", "morphology", "particulate", "stratigraphy"
- Replace technical terms with everyday words: "dirt" not "contamination", "surface" not "substrate", "removed" not "ablated"
- NO chemical formulas or complex measurements - use simple descriptions instead
- Use familiar comparisons and analogies that regular people understand
- Focus on what anyone can see with their own eyes
- Write as {author_name} explaining to a curious neighbor, not writing for scientists"""
    
    def build_caption_prompt(self, material_name: str, author_config: Dict[str, Any], 
                            material_data: Dict, frontmatter_data: Dict) -> str:
        """
        Build complete prompt from templates with caching and performance optimization.
        Replaces massive string concatenation with efficient template rendering.
        """
        if not self.voice_adapter:
            raise ValueError("Voice adapter not set - call set_voice_adapter() first")
        
        # Performance tracking
        start_time = time.time()
        self._performance_stats['builds'] += 1
        
        try:
            # Get voice-specific components from adapter (not hardcoded)
            country = author_config['country']
            
            voice_instructions = self.voice_adapter.get_voice_instructions(
                country, 'caption_generation'
            )
            
            # Get AI evasion instructions with authenticity intensity
            ai_evasion_instructions = self._build_ai_evasion_instructions(
                country, author_config.get('authenticity_intensity', 3)
            )
            
            # Calculate enhanced character targets
            before_target, after_target = self.voice_adapter.calculate_enhanced_targets(country)
            
            # Determine paragraph counts based on targets
            before_paragraphs = "1-2 paragraphs" if before_target < 900 else "2-3 paragraphs"
            after_paragraphs = "1-2 paragraphs" if after_target < 900 else "2-3 paragraphs"
            
            # Extract material context
            category = frontmatter_data.get('category', 'material')
            applications = frontmatter_data.get('applications', [])
            if isinstance(applications, dict):
                applications = applications.get('industrial', ['General industrial'])
            
            # Format properties for context
            properties_text = self._format_properties(material_data) if material_data else 'Standard material characteristics'
            applications_text = ', '.join(applications[:3]) if applications else 'General cleaning applications'
            
            # Use cached template variant for efficiency
            template = self._get_cached_template_variant(country, category)
            
            # Render template efficiently
            result = template.format(
                author_name=author_config['name'],
                author_expertise=author_config['expertise'],
                author_country=author_config['country'],
                material_name=material_name,
                category=category,
                properties=properties_text,
                applications=applications_text,
                voice_instructions=voice_instructions if voice_instructions else "",
                ai_evasion_instructions=ai_evasion_instructions,
                before_paragraphs=before_paragraphs,
                before_target=before_target,
                after_paragraphs=after_paragraphs,
                after_target=after_target
            )
            
            # Track performance
            build_time = time.time() - start_time
            self._performance_stats['total_time'] += build_time
            
            logger.debug(f"Prompt built for {material_name}: {len(result)} chars in {build_time:.4f}s")
            return result
            
        except Exception as e:
            build_time = time.time() - start_time
            self._performance_stats['total_time'] += build_time
            
            logger.error(f"Failed to build prompt for {material_name}: {e} (Time: {build_time:.4f}s)")
            raise ValueError(f"Prompt building failed: {e}")
    
    def _build_ai_evasion_instructions(self, country: str, authenticity_intensity: int) -> str:
        """Build AI evasion instructions efficiently using voice adapter"""
        try:
            ai_params = self.voice_adapter.get_ai_evasion_rules(country)
            
            if not ai_params:
                return ""
            
            # Extract universal rules
            sentence_targets = ai_params.get('sentence_length_targets', {})
            hesitation_rate = ai_params.get('hesitation_markers_per_200_words', 1.5)
            comma_splice_rate = ai_params.get('comma_splices_per_100_words', 1.0)
            parenthetical_rate = ai_params.get('parenthetical_asides_per_300_words', 2.0)
            lexical_target = ai_params.get('lexical_variety_target', 0.65)
            
            # Build base instructions
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
            
            # Add authenticity instructions from voice adapter
            authenticity_instructions = self.voice_adapter.get_authenticity_instructions(
                country, authenticity_intensity
            )
            
            if authenticity_instructions:
                instructions += authenticity_instructions
            
            instructions += """

REMEMBER: These variations create NATURAL human writing patterns. AI writes too uniformly—humans vary naturally in sentence length, word choice, and precision. Include these patterns throughout BOTH before and after text blocks."""
            
            return instructions
            
        except Exception as e:
            logger.error(f"Failed to build AI evasion instructions for {country}: {e}")
            return ""
    
    def _format_properties(self, material_data: Dict) -> str:
        """Format material properties for prompt context"""
        try:
            if not material_data:
                return 'Standard material characteristics'
            
            # Extract key properties
            key_props = []
            for prop, value in material_data.items():
                if isinstance(value, (int, float)):
                    key_props.append(f"{prop}: {value}")
                elif isinstance(value, str) and value:
                    key_props.append(f"{prop}: {value}")
            
            if key_props:
                return ', '.join(key_props[:5])  # Limit to 5 key properties
            else:
                return json.dumps(material_data, indent=2) if material_data else 'Standard material characteristics'
                
        except Exception as e:
            logger.warning(f"Failed to format material properties: {e}")
            return 'Standard material characteristics'
    
    def get_performance_stats(self) -> Dict:
        """Get prompt builder performance statistics"""
        total_builds = self._performance_stats['builds']
        total_time = self._performance_stats['total_time']
        cache_hits = self._performance_stats['cache_hits']
        
        return {
            'total_builds': total_builds,
            'cache_hits': cache_hits,
            'cache_hit_rate': cache_hits / total_builds if total_builds > 0 else 0.0,
            'total_time': total_time,
            'average_build_time': total_time / total_builds if total_builds > 0 else 0.0,
            'cached_templates': len(self._template_cache)
        }
    
    def reset_performance_stats(self):
        """Reset performance statistics"""
        self._performance_stats = {
            'builds': 0,
            'cache_hits': 0,
            'total_time': 0.0
        }
        logger.info("PromptBuilder performance stats reset")
    
    def clear_template_cache(self):
        """Clear template cache to free memory"""
        self._template_cache.clear()
        self._get_cached_template_variant.cache_clear()
        logger.info("Template cache cleared")