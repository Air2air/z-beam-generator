"""
Dynamic Configuration Calculator

Automatically calculates technical parameters based on user-facing intensity sliders.
This creates a truly dynamic system where changing ONE slider ripples through
all relevant downstream settings.

Philosophy:
- User adjusts simple 0-100 sliders
- System calculates optimal technical parameters
- Everything stays in sync automatically
- No manual tuning of advanced settings needed

Usage:
    from processing.dynamic_config import DynamicConfig
    
    config = DynamicConfig()
    
    # Get dynamically calculated values
    temperature = config.calculate_temperature('subtitle')
    detection_threshold = config.calculate_detection_threshold()
    max_tokens = config.calculate_max_tokens('description')
"""

import math
from typing import Dict, Any
from processing.config.config_loader import get_config


class DynamicConfig:
    """
    Dynamic configuration calculator.
    
    Takes user-facing intensity sliders (0-100) and calculates
    optimal technical parameters for all downstream components.
    """
    
    def __init__(self, base_config=None):
        """
        Initialize dynamic config.
        
        Args:
            base_config: Optional ProcessingConfig to use (for author-specific configs)
        """
        self.base_config = base_config if base_config is not None else get_config()
    
    # =========================================================================
    # API GENERATION PARAMETERS (Dynamic)
    # =========================================================================
    
    def calculate_temperature(self, component_type: str = 'default') -> float:
        """
        Calculate optimal API temperature based on sliders.
        
        Higher imperfection + higher rhythm variation = higher temperature
        Higher structural predictability = lower temperature
        
        Logic:
        - Imperfection tolerance pushes toward randomness
        - Sentence rhythm needs variety → higher temp
        - Structural predictability wants consistency → lower temp
        
        Returns:
            Temperature between 0.5 and 1.1
        """
        imperfection = self.base_config.get_imperfection_tolerance()  # 0-100
        rhythm = self.base_config.get_sentence_rhythm_variation()  # 0-100
        structural = self.base_config.get_structural_predictability()  # 0-100
        
        # Base temperature from config
        base_temp = self.base_config.get_temperature()
        
        # Calculate adjustment (-0.2 to +0.2)
        # Higher imperfection + rhythm → increase temp
        # Higher structural (less predictable) → increase temp
        creativity_factor = (imperfection + rhythm + structural) / 300.0  # 0.0-1.0
        
        # Map to temperature adjustment
        temp_adjustment = (creativity_factor - 0.5) * 0.4  # -0.2 to +0.2
        
        calculated_temp = base_temp + temp_adjustment
        
        # Clamp to safe range
        return max(0.5, min(1.1, calculated_temp))
    
    def calculate_max_tokens(self, component_type: str) -> int:
        """
        Calculate optimal max tokens based on sliders.
        
        Higher length_variation = more tokens allowed
        Higher context_specificity = more tokens needed
        
        Returns:
            Max tokens for component
        """
        length_variation = self.base_config.get_length_variation_range()  # 0-100
        context = self.base_config.get_context_specificity()  # 0-100
        
        # Base tokens from config
        base_tokens = self.base_config.get_max_tokens(component_type)
        
        # Calculate multiplier (0.8 to 1.3)
        # High variation + high context = allow more tokens
        flexibility_factor = (length_variation + context) / 200.0  # 0.0-1.0
        multiplier = 0.8 + (flexibility_factor * 0.5)  # 0.8 to 1.3
        
        calculated_tokens = int(base_tokens * multiplier)
        
        return calculated_tokens
    
    def calculate_retry_behavior(self) -> Dict[str, Any]:
        """
        Calculate retry behavior based on sliders.
        
        Higher AI avoidance = more retries, bigger temp increases
        Lower imperfection = fewer retries (wants perfection)
        
        Returns:
            Dict with max_attempts and temp_increase
        """
        ai_avoidance = self.base_config.get_ai_avoidance_intensity()  # 0-100
        imperfection = self.base_config.get_imperfection_tolerance()  # 0-100
        
        # Base values
        base_attempts = self.base_config.get_max_attempts()
        base_temp_increase = self.base_config.get_retry_temperature_increase()
        
        # More AI avoidance → more retries (willing to try harder)
        # Less imperfection tolerance → fewer retries (strict, fail fast)
        persistence_factor = (ai_avoidance + imperfection) / 200.0  # 0.0-1.0
        
        # Adjust attempts (3-7 range)
        max_attempts = int(3 + (persistence_factor * 4))
        
        # Adjust temp increase (0.05-0.15 range)
        temp_increase = 0.05 + (persistence_factor * 0.10)
        
        return {
            'max_attempts': max_attempts,
            'retry_temperature_increase': round(temp_increase, 2)
        }
    
    # =========================================================================
    # DETECTION PARAMETERS (Dynamic)
    # =========================================================================
    
    def calculate_detection_threshold(self, strict_mode: bool = False) -> float:
        """
        Calculate AI detection threshold based on sliders.
        
        Higher AI avoidance = lower threshold (more sensitive)
        Higher imperfection = higher threshold (more lenient)
        
        Logic:
        - AI avoidance at 100 → very strict detection (threshold ~25)
        - AI avoidance at 0 → very lenient (threshold ~55)
        - Imperfection tolerance moderates this
        
        Returns:
            Threshold between 20 and 60
        """
        ai_avoidance = self.base_config.get_ai_avoidance_intensity()  # 0-100
        imperfection = self.base_config.get_imperfection_tolerance()  # 0-100
        
        # Base threshold
        base_threshold = self.base_config.get_ai_threshold(strict_mode)
        
        # Calculate adjustment
        # High AI avoidance → lower threshold (more strict)
        # High imperfection → higher threshold (more lenient)
        strictness_factor = (ai_avoidance - imperfection) / 100.0  # -1.0 to +1.0
        
        # Adjust threshold (-15 to +15)
        threshold_adjustment = strictness_factor * 15
        
        calculated_threshold = base_threshold - threshold_adjustment
        
        # Clamp to reasonable range
        return max(20, min(60, calculated_threshold))
    
    def calculate_repetition_sensitivity(self) -> Dict[str, int]:
        """
        Calculate repetition detection sensitivity based on sliders.
        
        Higher sentence rhythm variation = more tolerant of repetition
        Higher AI avoidance = less tolerant
        Higher imperfection = more tolerant
        
        Returns:
            Dict with word_frequency, critical, and structural thresholds
        """
        rhythm = self.base_config.get_sentence_rhythm_variation()  # 0-100
        ai_avoidance = self.base_config.get_ai_avoidance_intensity()  # 0-100
        imperfection = self.base_config.get_imperfection_tolerance()  # 0-100
        
        # Base thresholds
        base = self.base_config.get_repetition_thresholds()
        
        # Calculate tolerance (0.0 to 1.0)
        # High rhythm + high imperfection = more tolerant
        # High AI avoidance = less tolerant
        tolerance = ((rhythm + imperfection) / 200.0) - (ai_avoidance / 200.0)
        tolerance = (tolerance + 1.0) / 2.0  # Normalize to 0.0-1.0
        
        # Adjust thresholds
        # More tolerant = higher thresholds (allow more repetition)
        word_freq = int(base['word_frequency'] + (tolerance * 2))  # 3-5
        word_critical = int(base['word_frequency_critical'] + (tolerance * 3))  # 5-8
        structural = int(base['structural_repetition'] + (tolerance * 2))  # 2-4
        
        return {
            'word_frequency': max(2, min(6, word_freq)),
            'word_frequency_critical': max(4, min(9, word_critical)),
            'structural_repetition': max(2, min(5, structural))
        }
    
    def calculate_confidence_thresholds(self) -> Dict[str, float]:
        """
        Calculate confidence thresholds based on sliders.
        
        Higher AI avoidance = higher confidence requirements
        
        Returns:
            Dict with high and medium confidence thresholds
        """
        ai_avoidance = self.base_config.get_ai_avoidance_intensity()  # 0-100
        
        base = self.base_config.get_confidence_thresholds()
        
        # Higher AI avoidance → require higher confidence to accept
        adjustment = (ai_avoidance - 50) / 5  # -10 to +10
        
        return {
            'high': max(60, min(85, base['high'] + adjustment)),
            'medium': max(40, min(65, base['medium'] + adjustment))
        }
    
    # =========================================================================
    # VALIDATION PARAMETERS (Dynamic)
    # =========================================================================
    
    def calculate_readability_thresholds(self) -> Dict[str, float]:
        """
        Calculate readability thresholds based on sliders.
        
        Higher technical language = lower readability OK
        Higher engagement = higher readability wanted
        
        Returns:
            Dict with min and max Flesch scores
        """
        technical = self.base_config.get_technical_language_intensity()  # 0-100
        engagement = self.base_config.get_engagement_style()  # 0-100
        
        base = self.base_config.get_readability_thresholds()
        
        # High technical → lower min score OK (harder text acceptable)
        # High engagement → higher min score wanted (easier text)
        accessibility_factor = (engagement - technical) / 100.0  # -1.0 to +1.0
        
        # Adjust min score (-10 to +10)
        min_adjustment = accessibility_factor * 10
        
        return {
            'min': max(40, min(70, base['min'] + min_adjustment)),
            'max': base['max']  # Keep max unchanged
        }
    
    def calculate_grammar_strictness(self) -> float:
        """
        Calculate how strict grammar checking should be.
        
        Higher imperfection tolerance = more lenient
        Higher AI avoidance = more strict (AI uses perfect grammar)
        
        Returns:
            Leniency factor 0.0 (strict) to 1.0 (very lenient)
        """
        imperfection = self.base_config.get_imperfection_tolerance()  # 0-100
        ai_avoidance = self.base_config.get_ai_avoidance_intensity()  # 0-100
        
        # High imperfection → lenient
        # High AI avoidance → strict (to catch AI patterns)
        leniency = (imperfection / 100.0) - (ai_avoidance / 200.0)
        
        # Normalize to 0.0-1.0
        return max(0.0, min(1.0, (leniency + 0.5)))
    
    # =========================================================================
    # LENGTH CALCULATION (Dynamic)
    # =========================================================================
    
    def calculate_target_length_range(self, component_type: str) -> Dict[str, int]:
        """
        Calculate acceptable length range based on length_variation slider.
        
        Returns:
            Dict with min, target, max word counts
        """
        length_variation = self.base_config.get_length_variation_range()  # 0-100
        target = self.base_config.get_component_length(component_type)
        
        # Calculate variation percentage (10% to 60%)
        variation_pct = 0.10 + (length_variation / 100.0 * 0.50)
        
        variation_words = int(target * variation_pct)
        
        return {
            'min': target - variation_words,
            'target': target,
            'max': target + variation_words,
            'variation_pct': round(variation_pct * 100, 1)
        }
    
    # =========================================================================
    # VOICE INTENSITY PARAMETERS (Dynamic)
    # =========================================================================
    
    def calculate_voice_parameters(self) -> Dict[str, Any]:
        """
        Calculate voice-related parameters for prompt building.
        Uses 1-3 scale: 1→0.0, 2→0.5, 3→1.0
        
        Returns:
            Dict with trait frequencies, quirk rates, structural_predictability, emotional_tone, etc.
        """
        author_voice = self.base_config.get_author_voice_intensity()  # 1-3
        personality = self.base_config.get_personality_intensity()  # 1-3
        engagement = self.base_config.get_engagement_style()  # 1-3
        structural = self.base_config.get_structural_predictability()  # 1-3
        emotional = self.base_config.get_emotional_intensity()  # 1-3
        
        # Map 1-3 to 0.0/0.5/1.0
        def map_to_float(value: int) -> float:
            return (value - 1) * 0.5  # 1→0.0, 2→0.5, 3→1.0
        
        return {
            'trait_frequency': map_to_float(author_voice),
            'opinion_rate': map_to_float(personality),
            'reader_address_rate': map_to_float(engagement),
            'colloquialism_frequency': map_to_float(max(author_voice, personality)),  # Max of voice and personality
            'structural_predictability': map_to_float(structural),
            'emotional_tone': map_to_float(emotional)
        }
    
    def calculate_enrichment_params(self) -> Dict[str, Any]:
        """
        Calculate all parameters for DataEnricher fact formatting.
        Uses 1-3 scale: 1→0.0, 2→0.5, 3→1.0
        
        Returns:
            Dict with:
            - technical_intensity: 1-3 (controls spec density)
            - context_detail_level: 1-3 (controls description length)
            - fact_formatting_style: 'formal' | 'balanced' | 'conversational'
            - engagement_level: 1-3
        """
        technical = self.base_config.get_technical_language_intensity()  # 1-3
        context = self.base_config.get_context_specificity()  # 1-3
        engagement = self.base_config.get_engagement_style()  # 1-3
        
        # Determine fact formatting style based on engagement (1-3)
        if engagement == 1:
            formatting = 'formal'  # "2.7 g/cm³"
        elif engagement == 2:
            formatting = 'balanced'  # "roughly 2.7 g/cm³"
        else:
            formatting = 'conversational'  # "around 2.7 g/cm³ (pretty dense!)"
        
        return {
            'technical_intensity': technical,
            'context_detail_level': context,
            'fact_formatting_style': formatting,
            'engagement_level': engagement
        }
    
    def get_all_generation_params(self, component_type: str = 'subtitle') -> Dict[str, Any]:
        """
        Get ALL parameters needed for generation in one call.
        Orchestrator should call this once and pass bundles to components.
        
        ⚠️  IMPORTANT: Temperature and penalties returned here are FALLBACK ONLY.
        UnifiedOrchestrator ALWAYS uses database parameters as primary source.
        These calculated values are only used when NO database history exists.
        
        Args:
            component_type: Component being generated (subtitle, caption, faq, etc.)
            
        Returns:
            Dict containing all parameter bundles:
            - api_params: temperature, max_tokens, retry_behavior, penalties (FALLBACK VALUES)
            - enrichment_params: technical_intensity, context_detail_level, etc.
            - voice_params: trait_frequency, opinion_rate, etc.
            - validation_params: readability, grammar, detection thresholds
        """
        # Calculate API penalties dynamically based on humanness_intensity
        # Higher humanness = higher penalties to reduce repetition (which AI detectors flag)
        humanness = self.base_config.get_humanness_intensity()  # 1-10
        
        # Map humanness to penalty range
        # Low humanness (1-3): 0.0 penalties (fast, predictable)
        # Medium humanness (4-7): 0.3-0.6 penalties (balanced)
        # High humanness (8-10): 0.8-1.2 penalties (aggressive, varied)
        if humanness <= 3:
            frequency_penalty = 0.0
            presence_penalty = 0.0
        elif humanness <= 7:
            # Linear scale from 0.0 to 0.6
            frequency_penalty = (humanness - 3) / 4.0 * 0.6
            presence_penalty = (humanness - 3) / 4.0 * 0.6
        else:
            # Linear scale from 0.6 to 1.2
            frequency_penalty = 0.6 + (humanness - 7) / 3.0 * 0.6
            presence_penalty = 0.6 + (humanness - 7) / 3.0 * 0.6
        
        return {
            'api_params': {
                'temperature': self.calculate_temperature(component_type),
                'max_tokens': self.calculate_max_tokens(component_type),
                'retry_behavior': self.calculate_retry_behavior(),
                'penalties': {
                    'frequency_penalty': round(frequency_penalty, 2),
                    'presence_penalty': round(presence_penalty, 2)
                }
            },
            'enrichment_params': self.calculate_enrichment_params(),
            'voice_params': self.calculate_voice_parameters(),
            'validation_params': {
                'readability_thresholds': self.calculate_readability_thresholds(),
                'grammar_strictness': self.calculate_grammar_strictness(),
                'detection_threshold': self.calculate_detection_threshold(),
                'confidence_thresholds': self.calculate_confidence_thresholds()
            }
        }
    
    # =========================================================================
    # SUMMARY REPORT
    # =========================================================================
    
    def get_dynamic_settings_report(self, component_type: str = 'subtitle') -> str:
        """
        Generate human-readable report of all dynamically calculated settings.
        
        Args:
            component_type: Component to calculate for
            
        Returns:
            Formatted string report
        """
        lines = []
        lines.append("=" * 70)
        lines.append("DYNAMIC CONFIGURATION REPORT")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Component: {component_type}")
        lines.append("")
        
        # API Settings
        lines.append("🌐 API GENERATION (Calculated):")
        temp = self.calculate_temperature(component_type)
        tokens = self.calculate_max_tokens(component_type)
        retry = self.calculate_retry_behavior()
        lines.append(f"   Temperature:        {temp:.2f}")
        lines.append(f"   Max Tokens:         {tokens}")
        lines.append(f"   Max Attempts:       {retry['max_attempts']}")
        lines.append(f"   Retry Temp Increase: {retry['retry_temperature_increase']:.2f}")
        lines.append("")
        
        # Detection Settings
        lines.append("🔍 DETECTION (Calculated):")
        threshold = self.calculate_detection_threshold()
        threshold_strict = self.calculate_detection_threshold(strict_mode=True)
        rep = self.calculate_repetition_sensitivity()
        conf = self.calculate_confidence_thresholds()
        lines.append(f"   AI Threshold:       {threshold:.1f}")
        lines.append(f"   AI Threshold (strict): {threshold_strict:.1f}")
        lines.append(f"   Word Repetition:    {rep['word_frequency']}")
        lines.append(f"   Critical Repetition: {rep['word_frequency_critical']}")
        lines.append(f"   Structural Rep:     {rep['structural_repetition']}")
        lines.append(f"   High Confidence:    {conf['high']:.1f}")
        lines.append(f"   Medium Confidence:  {conf['medium']:.1f}")
        lines.append("")
        
        # Validation Settings
        lines.append("✓ VALIDATION (Calculated):")
        read = self.calculate_readability_thresholds()
        grammar = self.calculate_grammar_strictness()
        length = self.calculate_target_length_range(component_type)
        lines.append(f"   Min Readability:    {read['min']:.1f}")
        lines.append(f"   Grammar Leniency:   {grammar:.2f} (0=strict, 1=lenient)")
        lines.append(f"   Length Range:       {length['min']}-{length['max']} words")
        lines.append(f"   Target Length:      {length['target']} words")
        lines.append(f"   Variation:          ±{length['variation_pct']}%")
        lines.append("")
        
        # Voice Parameters
        lines.append("🎭 VOICE (Calculated):")
        voice = self.calculate_voice_parameters()
        lines.append(f"   Trait Frequency:    {voice['trait_frequency']:.2f}")
        lines.append(f"   Opinion Rate:       {voice['opinion_rate']:.2f}")
        lines.append(f"   Reader Address:     {voice['reader_address_rate']:.2f}")
        lines.append(f"   Colloquialisms:     {voice['colloquialism_frequency']:.2f}")
        lines.append("")
        
        lines.append("=" * 70)
        lines.append("All values calculated from 10 intensity sliders")
        lines.append("Change sliders → everything updates automatically")
        lines.append("=" * 70)
        
        return "\n".join(lines)


# Singleton for easy access
_dynamic_config = None


def get_dynamic_config() -> DynamicConfig:
    """Get global dynamic config instance."""
    global _dynamic_config
    if _dynamic_config is None:
        _dynamic_config = DynamicConfig()
    return _dynamic_config
