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
    from generation.config.dynamic_config import DynamicConfig
    
    config = DynamicConfig()
    
    # Get dynamically calculated values
    temperature = config.calculate_temperature('micro')
    detection_threshold = config.calculate_detection_threshold()
    max_tokens = config.calculate_max_tokens('description')
"""

import math
from typing import Dict, Any, Optional
from generation.config.config_loader import get_config
# from parameters.registry import get_registry  # NOTE: registry removed during reorganization
# from parameters.base import BaseParameter  # NOTE: not needed for current implementation


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
        self.use_modular = self.base_config.config.get('use_modular_parameters', False)
        self._parameter_instances: Optional[Dict[str, Any]] = None  # Changed from BaseParameter to Any
    
    # =========================================================================
    # API GENERATION PARAMETERS (Dynamic)
    # =========================================================================
    
    def calculate_temperature(self, component_type: str = 'default') -> float:
        """
        Calculate optimal API temperature based on component type and sliders.
        
        Component Types:
        - 'research': Low temp (0.1-0.3) for scientific accuracy and factual data
        - 'default': Dynamic temp (0.7-1.1) for human-like content
        
        For default/content generation:
        Higher imperfection + higher rhythm variation = higher temperature
        Higher structural predictability = lower temperature
        
        Logic:
        - Research needs precision → very low temp
        - Imperfection tolerance pushes toward randomness
        - Sentence rhythm needs variety → higher temp
        - Structural predictability wants consistency → lower temp
        
        Returns:
            Temperature between 0.1 and 1.1 depending on component type
        """
        # Research operations need low temperature for factual accuracy
        if component_type == 'research':
            return 0.3  # Low temp for scientific precision
        
        imperfection = self.base_config.get_imperfection_tolerance()  # 0-100
        rhythm = self.base_config.get_sentence_rhythm_variation()  # 0-100
        structural = self.base_config.get_structural_predictability()  # 0-100
        
        # Base temperature from config
        base_temp = self.base_config.get_temperature()
        
        # Calculate adjustment (0.0 to +0.3)
        # Higher imperfection + rhythm + structural → increase temp
        # Average of sliders (0-100 → 0.0-1.0)
        creativity_avg = (imperfection + rhythm + structural) / 300.0  # 0.0-1.0
        
        # Increase temperature by up to +0.3 based on slider values
        # At max sliders (100/100/100): +0.3, at min sliders (0/0/0): +0.0
        temp_adjustment = creativity_avg * 0.3  # 0.0 to +0.3
        
        calculated_temp = base_temp + temp_adjustment
        
        # Ensure minimum of 0.7 for human-like content, max of 1.1
        return max(0.7, min(1.1, calculated_temp))
    
    def calculate_max_tokens(self, component_type: str) -> int:
        """
        Calculate max tokens directly from word count target.
        
        NO MULTIPLIER - config_loader already converts words × 1.3 = tokens.
        Previously had 0.8-1.3 multiplier causing double-conversion:
        - 80 words → 104 tokens → 83 tokens (× 0.8) → truncated at 66 words
        
        Now returns tokens directly from config_loader conversion.
        
        Returns:
            Max tokens for component (from word target × 1.3)
        """
        # Get tokens from config (already converted from words)
        tokens = self.base_config.get_max_tokens(component_type)
        
        # Return directly - NO MULTIPLIER
        # Length variation is handled by config target, not runtime multiplication
        return tokens
    
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
        
        # Get retry ranges from config
        retry_config = self.base_config.config.get('dynamic_calculations', {}).get('retry', {})
        attempts_min = retry_config.get('attempts_min', 3)
        attempts_max = retry_config.get('attempts_max', 7)
        temp_min = retry_config.get('temp_increase_min', 0.05)
        temp_max = retry_config.get('temp_increase_max', 0.15)
        
        # Adjust attempts using config range
        max_attempts = int(attempts_min + (persistence_factor * (attempts_max - attempts_min)))
        
        # Adjust temp increase using config range
        temp_increase = temp_min + (persistence_factor * (temp_max - temp_min))
        
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
        
        # Get threshold ranges from config
        threshold_config = self.base_config.config.get('dynamic_calculations', {}).get('thresholds', {})
        adjustment_range = threshold_config.get('detection_adjustment_range', 15)
        min_threshold = threshold_config.get('detection_min', 20)
        max_threshold = threshold_config.get('detection_max', 60)
        
        # Adjust threshold using config range
        threshold_adjustment = strictness_factor * adjustment_range
        
        calculated_threshold = base_threshold - threshold_adjustment
        
        # Clamp using config min/max
        return max(min_threshold, min(max_threshold, calculated_threshold))
    
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
        
        # Get confidence adjustment range from config
        threshold_config = self.base_config.config.get('dynamic_calculations', {}).get('thresholds', {})
        adjustment_range = threshold_config.get('confidence_adjustment_range', 10)
        
        # Higher AI avoidance → require higher confidence to accept
        # Scale ai_avoidance (0-100) to adjustment range (e.g., -10 to +10)
        adjustment = (ai_avoidance - 50) / 50 * adjustment_range  # -adjustment_range to +adjustment_range
        
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
        
        # Get readability adjustment range from config
        threshold_config = self.base_config.config.get('dynamic_calculations', {}).get('thresholds', {})
        adjustment_range = threshold_config.get('readability_adjustment_range', 10)
        
        # High technical → lower min score OK (harder text acceptable)
        # High engagement → higher min score wanted (easier text)
        accessibility_factor = (engagement - technical) / 100.0  # -1.0 to +1.0
        
        # Adjust min score using config range
        min_adjustment = accessibility_factor * adjustment_range
        
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
    
    def get_parameter_instances(self) -> Dict[str, Any]:
        """
        Get or create modular parameter instances.
        
        NOTE: Modular parameters were removed during reorganization.
        This method now returns empty dict to avoid breaking existing code.
        
        Returns:
            Empty dict (legacy compatibility)
        """
        # Legacy code - modular parameters removed
        return {}
    
    def orchestrate_parameter_prompts(self, content_length: str = 'medium') -> str:
        """
        Orchestrate all modular parameter prompts into a single string.
        
        NOTE: Modular parameters were removed during reorganization.
        This method now returns empty string for legacy compatibility.
        
        Args:
            content_length: 'short', 'medium', or 'long' for length-sensitive parameters
            
        Returns:
            Empty string (legacy compatibility)
        """
        return ""
    
    def calculate_voice_parameters(self) -> Dict[str, Any]:
        """
        Calculate voice-related parameters for prompt building.
        All sliders use 1-10 scale, normalized to 0.0-1.0
        
        Returns:
            Dict with trait frequencies, quirk rates, structural_predictability, emotional_tone, etc.
            
            If use_modular_parameters=True, includes '_parameter_instances' key with
            BaseParameter objects that can generate dynamic prompt guidance.
        """
        author_voice = self.base_config.get_author_voice_intensity()  # 1-10
        personality = self.base_config.get_personality_intensity()  # 1-10
        engagement = self.base_config.get_engagement_style()  # 1-10
        structural = self.base_config.get_structural_predictability()  # 1-10
        emotional = self.base_config.get_emotional_intensity()  # 1-10
        sentence_rhythm = self.base_config.get_sentence_rhythm_variation()  # 1-10
        imperfection = self.base_config.get_imperfection_tolerance()  # 1-10
        jargon = self.base_config.config.get('jargon_removal', 7)  # 1-10
        professional = self.base_config.config.get('professional_voice', 5)  # 1-10
        
        # Map 1-10 to 0.0-1.0 for all parameters
        def map_10_to_float(value: int) -> float:
            return (value - 1) / 9.0  # 1→0.0, 10→1.0
        
        result = {
            'trait_frequency': map_10_to_float(author_voice),
            'opinion_rate': map_10_to_float(personality),
            'reader_address_rate': map_10_to_float(engagement),
            'colloquialism_frequency': map_10_to_float(max(author_voice, personality)),  # Max of voice and personality
            'structural_predictability': map_10_to_float(structural),
            'emotional_tone': map_10_to_float(emotional),
            'sentence_rhythm_variation': map_10_to_float(sentence_rhythm),
            'imperfection_tolerance': map_10_to_float(imperfection),
            'jargon_removal': map_10_to_float(jargon),
            'professional_voice': map_10_to_float(professional)
        }
        
        # Add parameter instances if modular mode enabled
        if self.use_modular:
            result['_parameter_instances'] = self.get_parameter_instances()
            result['_use_modular'] = True
        
        return result
    
    def calculate_enrichment_params(self) -> Dict[str, Any]:
        """
        Calculate all parameters for DataEnricher fact formatting.
        Uses 1-10 scale normalized to 0.0-1.0 (consistent with voice params)
        
        Returns:
            Dict with:
            - technical_intensity: 0.0-1.0 (controls spec density)
            - context_detail_level: 0.0-1.0 (controls description length)
            - fact_formatting_style: 'formal' | 'balanced' | 'conversational'
            - engagement_level: 0.0-1.0
        """
        technical = self.base_config.get_technical_language_intensity()  # 1-10
        context = self.base_config.get_context_specificity()  # 1-10
        engagement = self.base_config.get_engagement_style()  # 1-10
        
        # Map 1-10 to 0.0-1.0 for all parameters
        def map_10_to_float(value: int) -> float:
            return (value - 1) / 9.0  # 1→0.0, 10→1.0
        
        technical_normalized = map_10_to_float(technical)
        engagement_normalized = map_10_to_float(engagement)
        
        # Determine fact formatting style based on engagement (0.0-1.0)
        if engagement_normalized < 0.3:
            formatting = 'formal'  # "2.7 g/cm³"
        elif engagement_normalized < 0.7:
            formatting = 'balanced'  # "roughly 2.7 g/cm³"
        else:
            formatting = 'conversational'  # "around 2.7 g/cm³ (pretty dense!)"
        
        return {
            'technical_intensity': technical_normalized,
            'context_detail_level': map_10_to_float(context),
            'fact_formatting_style': formatting,
            'engagement_level': engagement_normalized
        }
    
    def get_all_generation_params(self, component_type: str = 'micro') -> Dict[str, Any]:
        """
        Get ALL parameters needed for generation in one call.
        Orchestrator should call this once and pass bundles to components.
        
        ⚠️  IMPORTANT: Temperature and penalties returned here are FALLBACK ONLY.
        UnifiedOrchestrator ALWAYS uses database parameters as primary source.
        These calculated values are only used when NO database history exists.
        
        Args:
            component_type: Component being generated (caption, faq, etc.)
            
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
        
        # Get penalty ranges from config
        penalties_config = self.base_config.config.get('dynamic_calculations', {}).get('penalties', {})
        
        # Map humanness to penalty range using config values
        # Low humanness (1-3): 0.0 penalties (fast, predictable)
        # Medium humanness (4-7): 0.0 to medium_max penalties (balanced)
        # High humanness (8-10): high_min to high_max penalties (aggressive, varied)
        if humanness <= 3:
            frequency_penalty = penalties_config.get('low_humanness', {}).get('frequency', 0.0)
            presence_penalty = penalties_config.get('low_humanness', {}).get('presence', 0.0)
        elif humanness <= 7:
            # Linear scale from 0.0 to medium_max
            medium_max = penalties_config.get('medium_humanness', {}).get('frequency_max', 0.6)
            frequency_penalty = (humanness - 3) / 4.0 * medium_max
            presence_penalty = (humanness - 3) / 4.0 * medium_max
        else:
            # Linear scale from high_min to high_max
            high_min = penalties_config.get('high_humanness', {}).get('frequency_min', 0.6)
            high_max = penalties_config.get('high_humanness', {}).get('frequency_max', 1.2)
            frequency_penalty = high_min + (humanness - 7) / 3.0 * (high_max - high_min)
            presence_penalty = high_min + (humanness - 7) / 3.0 * (high_max - high_min)
        
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
    
    def get_dynamic_settings_report(self, component_type: str = 'micro') -> str:
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
