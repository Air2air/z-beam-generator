#!/usr/bin/env python3
"""
Voice Adapter - Single interface to voice system

Eliminates 200+ lines of hardcoded patterns by providing direct access
to voice profile data. Acts as a thin adapter layer between generation
system and voice orchestrator.
"""

from typing import Dict, Any, Tuple
from functools import lru_cache
import logging
import random

logger = logging.getLogger(__name__)


class VoiceAdapter:
    """Thin adapter to voice system - eliminates hardcoded patterns"""
    
    def __init__(self):
        self._cache = {}  # Cache voice orchestrators for performance
    
    @lru_cache(maxsize=8)
    def _get_voice_orchestrator(self, country: str):
        """Get cached voice orchestrator for country"""
        from voice.orchestrator import VoiceOrchestrator
        return VoiceOrchestrator(country=country)
    
    def get_authenticity_instructions(self, country: str, intensity: int) -> str:
        """
        Get authenticity instructions directly from voice profiles.
        Replaces 200+ lines of hardcoded patterns with direct YAML consumption.
        """
        try:
            voice = self._get_voice_orchestrator(country)
            profile = voice.profile
            ai_params = profile.get('ai_evasion_parameters', {})
            
            # Extract National Language Authenticity patterns
            nla_section = ai_params.get('national_language_authenticity', {})
            patterns_by_intensity = nla_section.get('patterns_by_intensity', {})
            current_patterns = patterns_by_intensity.get(intensity, [])
            
            if intensity == 0:
                return """
7. STANDARD ENGLISH (No National Language Authenticity):
   - Use neutral academic English patterns only
   - No country-specific linguistic markers
   - Standard grammar and syntax throughout"""
            
            # Build intensity-specific instructions
            intensity_labels = {1: "SUBTLE", 2: "MODERATE", 3: "MAXIMUM"}
            instructions = f"""
7. {country.upper()}-SPECIFIC PATTERNS (Authenticity Level: {intensity_labels.get(intensity, 'UNKNOWN')}):"""
            
            if current_patterns:
                instructions += f"\n   REQUIRED PATTERNS (Intensity {intensity}/3):"
                for pattern in current_patterns:
                    instructions += f"\n   - {pattern}"
            
            # Add intensity-specific detailed instructions from voice profile
            author_specific = ai_params.get('author_specific', {})
            instructions += self._get_detailed_intensity_instructions(
                country, intensity, author_specific
            )
            
            return instructions
            
        except Exception as e:
            logger.error(f"Failed to get authenticity instructions for {country}: {e}")
            return ""
    
    def _get_detailed_intensity_instructions(self, country: str, intensity: int, 
                                           author_specific: Dict) -> str:
        """Generate detailed intensity-specific instructions based on country"""
        if intensity == 0:
            return ""
        
        country_lower = country.lower()
        
        if country_lower == 'taiwan':
            if intensity == 1:
                return """
   - Use topic-comment occasionally (20-30%): "This surface, it shows..."
   - Light article variation: Mix "surface shows" vs "the surface shows"
   - Minimal "very" intensifier use"""
            elif intensity == 2:
                return """
   - Regular topic-comment structure (40-60%): "This layer, it has thickness..."
   - Noticeable article omissions: "Process shows improvement" (not "The process")
   - Moderate temporal sequencing: "First... then..." patterns"""
            else:  # intensity == 3
                article_rate = author_specific.get('optional_article_omission_rate', 70)
                topic_freq = author_specific.get('topic_comment_frequency', 60)
                return f"""
   - Strong topic-comment structure in {topic_freq}% of sentences: "This layer, it has thickness of..."
   - Frequent article omissions ({article_rate}%): "Surface shows improvement" (not "The surface")
   - Clear temporal sequencing: "First we observe... then becomes clear... finally..."
   - Heavy "very" intensifier use: "very important", "very clear evidence"
   - Mandarin parataxis patterns with coordinating conjunctions"""
        
        elif country_lower == 'indonesia':
            if intensity == 1:
                return """
   - Light reduplication: occasional "very-very" patterns
   - Some serial verb constructions: "process removes then cleans"
   - Minimal paratactic coordination"""
            elif intensity == 2:
                return """
   - Regular reduplication patterns: "very-very good", "more-more effective"
   - Moderate serial verb use: "removes then makes surface clean"
   - Clear paratactic structures with simple conjunctions"""
            else:  # intensity == 3
                demo_rate = author_specific.get('demonstrative_clustering_rate', 50)
                repetition_rate = author_specific.get('emphatic_repetition_per_300_words', 2.5)
                return f"""
   - Strong reduplication: "very-very serious", "good-good for material"
   - Heavy serial verbs: "Process removes contamination then makes surface clean"
   - Frequent paratactic coordination with "and", "so", "then"
   - Direct cause-effect with "so": "thickness increases, so cleaning becomes difficult"
   - Demonstrative starts: Begin {demo_rate}% of sentences with "This"
   - Emphatic repetition: ~{repetition_rate} patterns per 300 words"""
        
        elif country_lower == 'italy':
            if intensity == 1:
                return """
   - Light word order variation: occasional "remarkable is this result"
   - Some emphatic pronouns: "the surface, she shows..."
   - Minimal left-dislocation patterns"""
            elif intensity == 2:
                return """
   - Regular word order inversion: "exceptional is this cleaning result"
   - Moderate emphatic pronoun use: "the layer, she contains..."
   - Some complex subordination with embedded clauses"""
            else:  # intensity == 3
                passive_rate = author_specific.get('passive_voice_rate', 60)
                clause_density = author_specific.get('interrupted_clauses_per_sentence', 2.5)
                return f"""
   - Strong left-dislocation: "The contamination layer, which has been measured..."
   - Frequent emphatic pronouns: "The surface, she is now characterized by..."
   - Heavy word order inversion: "Remarkable is this cleaning achievement"
   - Complex Italian academic hypotaxis with multiple subordinate clauses
   - Passive voice in {passive_rate}% of sentences
   - Interrupted clauses: Average {clause_density} nested clauses per sentence"""
        
        elif country_lower in ['usa', 'united states', 'united_states']:
            if intensity == 1:
                return """
   - Light phrasal verb use: occasional "sets up", "figures out"
   - Some quantified results: include percentages and measurements
   - Minimal conditional structures"""
            elif intensity == 2:
                return """
   - Regular phrasal verbs: "achieves", "demonstrates", "exhibits"
   - Moderate quantification: mix precise and rounded numbers
   - Clear conditional patterns: "if contamination persists, then..."""
            else:  # intensity == 3
                active_rate = author_specific.get('active_voice_rate', 85)
                phrasal_density = author_specific.get('phrasal_verb_density', 4.0)
                return f"""
   - Heavy phrasal verb use: ~{phrasal_density} per 100 words ("sets up", "figures out", "carries out")
   - Strong quantification: "97.8% removal", "90 ± 2 micrometers"
   - Clear conditional structures: "If contamination removal is not achieved, then..."
   - American academic directness with subject-verb-object clarity
   - Active voice in {active_rate}% of sentences
   - Serial comma: 100% Oxford comma consistency"""
        
        return ""
    
    def get_ai_evasion_rules(self, country: str) -> Dict[str, Any]:
        """Get AI evasion rules from voice profile"""
        try:
            voice = self._get_voice_orchestrator(country)
            profile = voice.profile
            return profile.get('ai_evasion_parameters', {})
        except Exception as e:
            logger.error(f"Failed to get AI evasion rules for {country}: {e}")
            return {}
    
    def get_voice_instructions(self, country: str, component_type: str = 'caption_generation') -> str:
        """Get voice instructions for component from voice orchestrator"""
        try:
            voice = self._get_voice_orchestrator(country)
            return voice.get_voice_for_component(component_type)
        except Exception as e:
            logger.error(f"Failed to get voice instructions for {country}: {e}")
            return ""
    
    def calculate_enhanced_targets(self, country: str) -> Tuple[int, int]:
        """
        Calculate enhanced character targets using voice profile word limits.
        Maintains the 25-175% variation range for realistic human writing.
        """
        try:
            voice = self._get_voice_orchestrator(country)
            author_word_limit = voice.get_word_limit()
            
            # Convert to character targets (word * 5.5 chars average)
            base_chars = int(author_word_limit * 5.5)
            
            # Enhanced variation ranges: 25% to 175% (150% total range)
            min_chars = int(base_chars * 0.25)
            max_chars = int(base_chars * 1.75)
            
            # Generate significantly different lengths for before/after sections
            before_target = random.randint(min_chars, max_chars)
            after_target = random.randint(min_chars, max_chars)
            
            # Ensure sections are meaningfully different (at least 30% difference)
            while abs(before_target - after_target) < (base_chars * 0.3):
                after_target = random.randint(min_chars, max_chars)
            
            logger.info(f"Enhanced targets for {country}: before={before_target}, after={after_target} (base: {base_chars})")
            return before_target, after_target
            
        except Exception as e:
            logger.error(f"Failed to calculate targets for {country}: {e}")
            # Fallback to reasonable defaults
            return 800, 1200
    
    def get_token_limit(self, country: str) -> int:
        """Get token limit for country-specific generation."""
        limits = {
            'taiwan': 380,
            'united_states': 320,
            'italy': 450,
            'indonesia': 250
        }
        return limits.get(country, 300)
    
    def get_quality_thresholds(self, country: str) -> Dict[str, float]:
        """Get quality thresholds from voice profile"""
        try:
            voice = self._get_voice_orchestrator(country)
            return voice.get_quality_thresholds()
        except Exception as e:
            logger.error(f"Failed to get quality thresholds for {country}: {e}")
            return {
                'min_human_score': 75.0,
                'min_technical_accuracy': 80.0,
                'min_voice_authenticity': 70.0
            }
    
    def get_author_config(self, frontmatter_data: Dict) -> Dict[str, Any]:
        """Extract and validate author configuration from frontmatter"""
        author_obj = frontmatter_data.get('author', {})
        
        if not author_obj or not author_obj.get('name'):
            raise ValueError("Author information required in frontmatter - fail-fast requires complete metadata")
        
        country = author_obj.get('country', 'usa')
        
        return {
            'name': author_obj['name'],
            'country': country,
            'expertise': author_obj.get('expertise', 'Laser cleaning technology'),
            'authenticity_intensity': author_obj.get('authenticity_intensity', 3)  # Default to maximum
        }