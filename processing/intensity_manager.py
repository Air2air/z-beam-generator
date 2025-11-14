"""
Intensity Manager - Simplified 4-slider control system

Loads settings from config.yaml and converts 0-100 intensity values
into specific generation parameters.

Usage:
    from processing.intensity_manager import IntensityManager
    
    manager = IntensityManager()
    settings = manager.get_all_settings()
    prompt = manager.build_intensity_instruction()
"""

import logging
from pathlib import Path
from typing import Dict
import yaml

logger = logging.getLogger(__name__)


class IntensityManager:
    """
    Manages 4-slider intensity system from centralized config.
    
    Converts simple 0-100 values into detailed generation parameters:
    1. Author voice intensity (0-100)
    2. Technical language intensity (0-100)
    3. Length variation range (0-100)
    4. AI avoidance intensity (0-100)
    """
    
    def __init__(self, config_path: Path = None):
        """
        Initialize intensity manager.
        
        Args:
            config_path: Path to config.yaml (default: processing/config.yaml)
        """
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
        logger.info(
            f"Intensity Manager: "
            f"voice={self.get_author_voice()}, "
            f"tech={self.get_technical_language()}, "
            f"length={self.get_length_variation()}, "
            f"ai={self.get_ai_avoidance()}"
        )
    
    def _load_config(self) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                logger.debug(f"Loaded config from {self.config_path}")
                return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise
    
    def reload_config(self):
        """Reload configuration from disk"""
        self.config = self._load_config()
        logger.info("Configuration reloaded")
    
    # ============================================================================
    # SLIDER VALUE GETTERS (0-100)
    # ============================================================================
    
    def get_author_voice(self) -> int:
        """Get author voice intensity (0-100)"""
        return self.config.get('author_voice_intensity', 50)
    
    def get_technical_language(self) -> int:
        """Get technical language intensity (0-100)"""
        return self.config.get('technical_language_intensity', 50)
    
    def get_length_variation(self) -> int:
        """Get length variation range (0-100)"""
        return self.config.get('length_variation_range', 50)
    
    def get_ai_avoidance(self) -> int:
        """Get AI avoidance intensity (0-100)"""
        return self.config.get('ai_avoidance_intensity', 50)
    
    def get_sentence_rhythm(self) -> int:
        """Get sentence rhythm variation (0-100)"""
        return self.config.get('sentence_rhythm_variation', 50)
    
    def get_imperfection_tolerance(self) -> int:
        """Get imperfection tolerance (0-100)"""
        return self.config.get('imperfection_tolerance', 50)
    
    def get_personality_intensity(self) -> int:
        """Get personality intensity (0-100)"""
        return self.config.get('personality_intensity', 40)
    
    def get_context_specificity(self) -> int:
        """Get context specificity (0-100)"""
        return self.config.get('context_specificity', 55)
    
    def get_structural_predictability(self) -> int:
        """Get structural predictability (0-100)"""
        return self.config.get('structural_predictability', 45)
    
    def get_engagement_style(self) -> int:
        """Get engagement style (0-100)"""
        return self.config.get('engagement_style', 35)
    
    # ============================================================================
    # SLIDER VALUE SETTERS
    # ============================================================================
    
    def set_author_voice(self, value: int):
        """Set author voice intensity (0-100)"""
        self._validate_intensity(value)
        self.config['author_voice_intensity'] = value
        logger.info(f"Author voice intensity set to: {value}")
    
    def set_technical_language(self, value: int):
        """Set technical language intensity (0-100)"""
        self._validate_intensity(value)
        self.config['technical_language_intensity'] = value
        logger.info(f"Technical language intensity set to: {value}")
    
    def set_length_variation(self, value: int):
        """Set length variation range (0-100)"""
        self._validate_intensity(value)
        self.config['length_variation_range'] = value
        logger.info(f"Length variation range set to: {value}")
    
    def set_ai_avoidance(self, value: int):
        """Set AI avoidance intensity (0-100)"""
        self._validate_intensity(value)
        self.config['ai_avoidance_intensity'] = value
        logger.info(f"AI avoidance intensity set to: {value}")
    
    def set_sentence_rhythm(self, value: int):
        """Set sentence rhythm variation (0-100)"""
        self._validate_intensity(value)
        self.config['sentence_rhythm_variation'] = value
        logger.info(f"Sentence rhythm variation set to: {value}")
    
    def set_imperfection_tolerance(self, value: int):
        """Set imperfection tolerance (0-100)"""
        self._validate_intensity(value)
        self.config['imperfection_tolerance'] = value
        logger.info(f"Imperfection tolerance set to: {value}")
    
    def set_personality_intensity(self, value: int):
        """Set personality intensity (0-100)"""
        self._validate_intensity(value)
        self.config['personality_intensity'] = value
        logger.info(f"Personality intensity set to: {value}")
    
    def set_context_specificity(self, value: int):
        """Set context specificity (0-100)"""
        self._validate_intensity(value)
        self.config['context_specificity'] = value
        logger.info(f"Context specificity set to: {value}")
    
    def set_structural_predictability(self, value: int):
        """Set structural predictability (0-100)"""
        self._validate_intensity(value)
        self.config['structural_predictability'] = value
        logger.info(f"Structural predictability set to: {value}")
    
    def set_engagement_style(self, value: int):
        """Set engagement style (0-100)"""
        self._validate_intensity(value)
        self.config['engagement_style'] = value
        logger.info(f"Engagement style set to: {value}")
    
    def _validate_intensity(self, value: int):
        """Validate intensity value is 0-100"""
        if not isinstance(value, int) or value < 0 or value > 100:
            raise ValueError(f"Intensity must be 0-100, got: {value}")
    
    # ============================================================================
    # PARAMETER CONVERSION (0-100 → specific settings)
    # ============================================================================
    
    def get_author_voice_params(self) -> Dict:
        """
        Convert author voice intensity to parameters.
        
        Returns:
            Dict with trait_frequency, quirk_rate, formality, vocabulary
        """
        intensity = self.get_author_voice()
        
        # Linear interpolation between min and max
        if intensity <= 30:  # Light
            return {
                'trait_frequency': f"{0.1 + (intensity/30)*0.1:.1f}-{0.2 + (intensity/30)*0.2:.1f}",
                'quirk_rate': 0.05 + (intensity/30)*0.10,
                'formality': 75 + (intensity/30)*10,
                'vocabulary_uniqueness': 65 + (intensity/30)*15
            }
        elif intensity <= 60:  # Moderate
            scaled = (intensity - 30) / 30
            return {
                'trait_frequency': f"{0.2 + scaled*0.2:.1f}-{0.4 + scaled*0.1:.1f}",
                'quirk_rate': 0.15 + scaled*0.05,
                'formality': 85 + scaled*3,
                'vocabulary_uniqueness': 80 + scaled*3
            }
        else:  # Strong
            scaled = (intensity - 60) / 40
            return {
                'trait_frequency': f"{0.4 + scaled*0.3:.1f}-{0.5 + scaled*0.2:.1f}",
                'quirk_rate': 0.20 + scaled*0.10,
                'formality': 88 + scaled*7,
                'vocabulary_uniqueness': 83 + scaled*7
            }
    
    def get_technical_params(self) -> Dict:
        """
        Convert technical language intensity to parameters.
        
        Returns:
            Dict with units_per_sentence, jargon_level, complexity, etc.
        """
        intensity = self.get_technical_language()
        
        if intensity <= 30:  # Accessible
            return {
                'units_per_sentence': 0.2 + (intensity/30)*0.2,
                'jargon_level': 'minimal',
                'sentence_length': f"{12 + (intensity/30)*2:.0f}-{16 + (intensity/30)*2:.0f} words",
                'active_voice_pct': 80 - (intensity/30)*5,
                'data_density': 'low'
            }
        elif intensity <= 60:  # Balanced
            scaled = (intensity - 30) / 30
            return {
                'units_per_sentence': 0.4 + scaled*0.3,
                'jargon_level': 'moderate',
                'sentence_length': f"{14 + scaled*3:.0f}-{18 + scaled*4:.0f} words",
                'active_voice_pct': 75 - scaled*15,
                'data_density': 'medium'
            }
        else:  # Expert
            scaled = (intensity - 60) / 40
            return {
                'units_per_sentence': 0.7 + scaled*0.3,
                'jargon_level': 'full',
                'sentence_length': f"{17 + scaled*3:.0f}-{22 + scaled*4:.0f} words",
                'active_voice_pct': 60 - scaled*15,
                'data_density': 'high'
            }
    
    def get_length_params(self) -> Dict:
        """
        Convert length variation to tolerance percentage.
        
        Returns:
            Dict with tolerance_pct and enforcement_level
        """
        intensity = self.get_length_variation()
        
        # Linear mapping: 0→±5%, 50→±20%, 100→±50%
        tolerance_pct = 5 + (intensity * 0.45)
        
        if intensity <= 30:
            enforcement = 'strict'
        elif intensity <= 60:
            enforcement = 'moderate'
        else:
            enforcement = 'relaxed'
        
        return {
            'tolerance_pct': tolerance_pct,
            'enforcement': enforcement,
            'description': f"±{tolerance_pct:.0f}% of target length"
        }
    
    def get_ai_avoidance_params(self) -> Dict:
        """
        Convert AI avoidance intensity to detection/variation parameters.
        
        Returns:
            Dict with temperature, retry_threshold, pattern_detection
        """
        intensity = self.get_ai_avoidance()
        
        # Higher avoidance = higher temperature, stricter detection
        base_temp = 0.7 + (intensity / 100) * 0.3  # 0.7 to 1.0
        detection_threshold = 0.4 - (intensity / 100) * 0.15  # 0.4 to 0.25
        
        if intensity <= 30:
            mode = 'relaxed'
        elif intensity <= 60:
            mode = 'balanced'
        else:
            mode = 'aggressive'
        
        return {
            'base_temperature': base_temp,
            'detection_threshold': detection_threshold,
            'mode': mode,
            'max_retries': 3 + (intensity // 25)  # 3-7 retries
        }
    
    def get_sentence_rhythm_params(self) -> Dict:
        """
        Convert sentence rhythm variation to CV% and distribution.
        
        Returns:
            Dict with coefficient_of_variation, sentence_mix, breathing_room
        """
        intensity = self.get_sentence_rhythm()
        
        # CV% (coefficient of variation): 0→15%, 50→30%, 100→60%
        cv_percent = 15 + (intensity * 0.45)
        
        # Sentence length distribution
        if intensity <= 30:
            mix = {'short': 20, 'medium': 60, 'long': 20}
            description = 'uniform'
        elif intensity <= 60:
            mix = {'short': 30, 'medium': 50, 'long': 20}
            description = 'natural'
        else:
            mix = {'short': 35, 'medium': 40, 'long': 25}
            description = 'high variation'
        
        return {
            'coefficient_of_variation': cv_percent,
            'sentence_mix': mix,
            'breathing_room_frequency': intensity / 100,  # 0-1 probability
            'description': description,
            'avoid_consecutive_similar': intensity > 40
        }
    
    def get_imperfection_params(self) -> Dict:
        """
        Convert imperfection tolerance to allowable "flaws".
        
        Returns:
            Dict with redundancy_tolerance, tangent_allowance, etc.
        """
        intensity = self.get_imperfection_tolerance()
        
        if intensity <= 30:
            mode = 'polished'
            redundancy = 0.0
            hedging = 0.0
        elif intensity <= 60:
            mode = 'natural'
            redundancy = 0.1 + (intensity - 30) / 300  # 0.1-0.2
            hedging = 0.15
        else:
            mode = 'authentic'
            redundancy = 0.2 + (intensity - 60) / 200  # 0.2-0.4
            hedging = 0.25
        
        return {
            'mode': mode,
            'redundancy_tolerance': redundancy,
            'hedging_frequency': hedging,
            'awkward_phrasing_ok': intensity > 50,
            'minor_repetition_ok': intensity > 40,
            'occasional_passive_ok': intensity > 30
        }
    
    def get_personality_params(self) -> Dict:
        """
        Convert personality intensity to opinion/experience markers.
        
        Returns:
            Dict with evaluative_frequency, preference_strength, etc.
        """
        intensity = self.get_personality_intensity()
        
        if intensity <= 30:
            voice = 'neutral'
            evaluative = 0.0
        elif intensity <= 60:
            voice = 'professional'
            evaluative = 0.1 + (intensity - 30) / 300  # 0.1-0.2
        else:
            voice = 'opinionated'
            evaluative = 0.2 + (intensity - 60) / 250  # 0.2-0.36
        
        return {
            'voice': voice,
            'evaluative_frequency': evaluative,
            'experience_markers': intensity > 50,
            'comparative_preference': intensity > 60,
            'subjective_assessments': intensity > 40,
            'implied_judgment': intensity > 55
        }
    
    def get_context_params(self) -> Dict:
        """
        Convert context specificity to concrete vs. abstract balance.
        
        Returns:
            Dict with scenario_frequency, edge_case_mention, etc.
        """
        intensity = self.get_context_specificity()
        
        if intensity <= 30:
            mode = 'abstract'
            scenarios = 0.1
        elif intensity <= 60:
            mode = 'balanced'
            scenarios = 0.2 + (intensity - 30) / 150  # 0.2-0.4
        else:
            mode = 'concrete'
            scenarios = 0.4 + (intensity - 60) / 100  # 0.4-0.8
        
        return {
            'mode': mode,
            'specific_scenario_frequency': scenarios,
            'named_application_contexts': intensity > 40,
            'practical_limitations': intensity > 50,
            'concrete_numbers': intensity > 45,
            'edge_case_depth': 'high' if intensity > 70 else 'medium' if intensity > 40 else 'low'
        }
    
    def get_structural_params(self) -> Dict:
        """
        Convert structural predictability to template-breaking allowance.
        
        Returns:
            Dict with template_adherence, opening_variety, etc.
        """
        intensity = self.get_structural_predictability()
        
        # Inverted: low predictability = high structure breaking
        if intensity <= 30:
            mode = 'formulaic'
            breaking = 0.8  # High template adherence
        elif intensity <= 60:
            mode = 'flexible'
            breaking = 0.5
        else:
            mode = 'organic'
            breaking = 0.2  # Low template adherence
        
        return {
            'mode': mode,
            'template_adherence': breaking,
            'opening_variety': 1 - breaking,
            'topic_sentence_flexibility': intensity > 40,
            'transition_diversity': intensity > 50,
            'single_sentence_paragraphs_ok': intensity > 60,
            'information_order_randomization': intensity > 55
        }
    
    def get_engagement_params(self) -> Dict:
        """
        Convert engagement style to reader-awareness level.
        
        Returns:
            Dict with direct_address, rhetorical_questions, etc.
        """
        intensity = self.get_engagement_style()
        
        if intensity <= 30:
            mode = 'detached'
            address = 0.0
        elif intensity <= 60:
            mode = 'professional'
            address = 0.05 + (intensity - 30) / 300  # 0.05-0.15
        else:
            mode = 'conversational'
            address = 0.15 + (intensity - 60) / 200  # 0.15-0.35
        
        return {
            'mode': mode,
            'direct_address_frequency': address,
            'rhetorical_questions': intensity > 50,
            'imperative_mood': intensity > 40,
            'anticipatory_phrasing': intensity > 45,
            'reader_context_assumptions': intensity > 60
        }
    
    # ============================================================================
    # UNIFIED INTERFACE
    # ============================================================================
    
    def get_all_settings(self) -> Dict:
        """
        Get all intensity settings as a single dict.
        
        Returns:
            Dict with all slider values and converted parameters
        """
        return {
            'sliders': {
                'author_voice': self.get_author_voice(),
                'technical_language': self.get_technical_language(),
                'length_variation': self.get_length_variation(),
                'ai_avoidance': self.get_ai_avoidance(),
                'sentence_rhythm': self.get_sentence_rhythm(),
                'imperfection_tolerance': self.get_imperfection_tolerance(),
                'personality': self.get_personality_intensity(),
                'context_specificity': self.get_context_specificity(),
                'structural_predictability': self.get_structural_predictability(),
                'engagement_style': self.get_engagement_style()
            },
            'author_voice': self.get_author_voice_params(),
            'technical': self.get_technical_params(),
            'length': self.get_length_params(),
            'ai_avoidance': self.get_ai_avoidance_params(),
            'sentence_rhythm': self.get_sentence_rhythm_params(),
            'imperfection': self.get_imperfection_params(),
            'personality': self.get_personality_params(),
            'context': self.get_context_params(),
            'structural': self.get_structural_params(),
            'engagement': self.get_engagement_params()
        }
    
    def build_intensity_instruction(self) -> str:
        """
        Build a prompt instruction string with current settings.
        
        Returns:
            String describing intensity requirements for AI generation
        """
        settings = self.get_all_settings()
        s = settings['sliders']
        
        instruction = f"""
GENERATION PARAMETERS (10-Slider System):

1. Author Voice: {s['author_voice']}/100
   - Regional traits: {settings['author_voice']['trait_frequency']} per paragraph
   - Formality: {settings['author_voice']['formality']:.0f}%

2. Technical Language: {s['technical_language']}/100
   - Measurements: {settings['technical']['units_per_sentence']:.1f} per sentence
   - Jargon: {settings['technical']['jargon_level']}
   - Sentence length: {settings['technical']['sentence_length']}

3. Length Tolerance: {s['length_variation']}/100
   - Range: {settings['length']['description']}

4. AI Avoidance: {s['ai_avoidance']}/100
   - Mode: {settings['ai_avoidance']['mode']}
   - Detection threshold: {settings['ai_avoidance']['detection_threshold']:.2f}

5. Sentence Rhythm: {s['sentence_rhythm']}/100
   - CV%: {settings['sentence_rhythm']['coefficient_of_variation']:.0f}%
   - Mix: {settings['sentence_rhythm']['description']}
   - Short/Med/Long: {settings['sentence_rhythm']['sentence_mix']['short']}/{settings['sentence_rhythm']['sentence_mix']['medium']}/{settings['sentence_rhythm']['sentence_mix']['long']}%

6. Imperfection Tolerance: {s['imperfection_tolerance']}/100
   - Mode: {settings['imperfection']['mode']}
   - Redundancy OK: {settings['imperfection']['redundancy_tolerance']:.1%}
   - Hedging frequency: {settings['imperfection']['hedging_frequency']:.0%}

7. Personality: {s['personality']}/100
   - Voice: {settings['personality']['voice']}
   - Evaluative language: {settings['personality']['evaluative_frequency']:.1%}
   - Experience markers: {'yes' if settings['personality']['experience_markers'] else 'no'}

8. Context Specificity: {s['context_specificity']}/100
   - Mode: {settings['context']['mode']}
   - Scenario frequency: {settings['context']['specific_scenario_frequency']:.1%}
   - Edge case depth: {settings['context']['edge_case_depth']}

9. Structural Predictability: {s['structural_predictability']}/100
   - Mode: {settings['structural']['mode']}
   - Template adherence: {settings['structural']['template_adherence']:.0%}
   - Opening variety: {settings['structural']['opening_variety']:.0%}

10. Engagement Style: {s['engagement_style']}/100
    - Mode: {settings['engagement']['mode']}
    - Direct address: {settings['engagement']['direct_address_frequency']:.1%}
    - Rhetorical questions: {'allowed' if settings['engagement']['rhetorical_questions'] else 'avoid'}
"""
        return instruction.strip()
    
    def apply_intensity_to_prompt(self, base_prompt: str, prepend: bool = True) -> str:
        """
        Apply intensity instructions to a prompt.
        
        Args:
            base_prompt: Original prompt text
            prepend: If True, add intensity instruction at start; if False, at end
        
        Returns:
            Modified prompt with intensity instructions
        """
        intensity_instruction = self.build_intensity_instruction()
        
        if prepend:
            return f"{intensity_instruction}\n\n{base_prompt}"
        else:
            return f"{base_prompt}\n\n{intensity_instruction}"
    
    # ============================================================================
    # SUMMARY & DISPLAY
    # ============================================================================
    
    def get_summary(self) -> str:
        """
        Get a human-readable summary of current settings.
        
        Returns:
            Formatted string with current configuration
        """
        settings = self.get_all_settings()
        sliders = settings['sliders']
        
        def bar(value: int, width: int = 20) -> str:
            """Create a text-based bar graph"""
            filled = int((value / 100) * width)
            return '█' * filled + '░' * (width - filled)
        
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║           INTENSITY MANAGER - 10 SLIDER SYSTEM               ║
╠══════════════════════════════════════════════════════════════╣
║ 1. Author Voice:                       {sliders['author_voice']:3d}/100         ║
║    {bar(sliders['author_voice'], 50):50s} ║
║    {self._get_voice_description(sliders['author_voice']):58s} ║
╠══════════════════════════════════════════════════════════════╣
║ 2. Technical Language:                 {sliders['technical_language']:3d}/100         ║
║    {bar(sliders['technical_language'], 50):50s} ║
║    {self._get_tech_description(sliders['technical_language']):58s} ║
╠══════════════════════════════════════════════════════════════╣
║ 3. Length Variation:                   {sliders['length_variation']:3d}/100         ║
║    {bar(sliders['length_variation'], 50):50s} ║
║    {settings['length']['description']:58s} ║
╠══════════════════════════════════════════════════════════════╣
║ 4. AI Avoidance:                       {sliders['ai_avoidance']:3d}/100         ║
║    {bar(sliders['ai_avoidance'], 50):50s} ║
║    {self._get_ai_description(sliders['ai_avoidance']):58s} ║
╠══════════════════════════════════════════════════════════════╣
║ 5. Sentence Rhythm:                    {sliders['sentence_rhythm']:3d}/100         ║
║    {bar(sliders['sentence_rhythm'], 50):50s} ║
║    {self._get_rhythm_description(sliders['sentence_rhythm']):58s} ║
╠══════════════════════════════════════════════════════════════╣
║ 6. Imperfection Tolerance:             {sliders['imperfection_tolerance']:3d}/100         ║
║    {bar(sliders['imperfection_tolerance'], 50):50s} ║
║    {self._get_imperfection_description(sliders['imperfection_tolerance']):58s} ║
╠══════════════════════════════════════════════════════════════╣
║ 7. Personality:                        {sliders['personality']:3d}/100         ║
║    {bar(sliders['personality'], 50):50s} ║
║    {self._get_personality_description(sliders['personality']):58s} ║
╠══════════════════════════════════════════════════════════════╣
║ 8. Context Specificity:                {sliders['context_specificity']:3d}/100         ║
║    {bar(sliders['context_specificity'], 50):50s} ║
║    {self._get_context_description(sliders['context_specificity']):58s} ║
╠══════════════════════════════════════════════════════════════╣
║ 9. Structural Predictability:          {sliders['structural_predictability']:3d}/100         ║
║    {bar(sliders['structural_predictability'], 50):50s} ║
║    {self._get_structural_description(sliders['structural_predictability']):58s} ║
╠══════════════════════════════════════════════════════════════╣
║ 10. Engagement Style:                  {sliders['engagement_style']:3d}/100         ║
║     {bar(sliders['engagement_style'], 50):50s} ║
║     {self._get_engagement_description(sliders['engagement_style']):58s} ║
╚══════════════════════════════════════════════════════════════╝
"""
        return summary.strip()
    
    def _get_voice_description(self, value: int) -> str:
        """Get description for voice intensity level"""
        if value <= 30:
            return "Minimal voice, nearly standard English"
        elif value <= 60:
            return "Balanced voice, noticeable but professional"
        else:
            return "Strong voice, authentic regional characteristics"
    
    def _get_tech_description(self, value: int) -> str:
        """Get description for technical intensity level"""
        if value <= 30:
            return "Accessible, minimal jargon"
        elif value <= 60:
            return "Balanced technical language"
        else:
            return "Expert, dense technical content"
    
    def _get_ai_description(self, value: int) -> str:
        """Get description for AI avoidance level"""
        if value <= 30:
            return "Relaxed, natural patterns OK"
        elif value <= 60:
            return "Moderate avoidance, balanced"
        else:
            return "Aggressive, maximum variation"
    
    def _get_rhythm_description(self, value: int) -> str:
        """Get description for sentence rhythm level"""
        if value <= 30:
            return "Uniform rhythm, consistent lengths"
        elif value <= 60:
            return "Natural variation, mixed lengths"
        else:
            return "High variation, dramatic shifts"
    
    def _get_imperfection_description(self, value: int) -> str:
        """Get description for imperfection tolerance level"""
        if value <= 30:
            return "Perfect, polished, flawless"
        elif value <= 60:
            return "Subtle natural variations"
        else:
            return "Noticeable quirks, authentic flaws"
    
    def _get_personality_description(self, value: int) -> str:
        """Get description for personality intensity level"""
        if value <= 30:
            return "Neutral observer, purely factual"
        elif value <= 60:
            return "Subtle professional opinions"
        else:
            return "Strong viewpoints, clear preferences"
    
    def _get_context_description(self, value: int) -> str:
        """Get description for context specificity level"""
        if value <= 30:
            return "Abstract principles, general statements"
        elif value <= 60:
            return "Mix of principles and examples"
        else:
            return "Highly specific scenarios, edge cases"
    
    def _get_structural_description(self, value: int) -> str:
        """Get description for structural predictability level"""
        if value <= 30:
            return "Highly formulaic, template-driven"
        elif value <= 60:
            return "Flexible structure, occasional patterns"
        else:
            return "Unpredictable, breaks conventions"
    
    def _get_engagement_description(self, value: int) -> str:
        """Get description for engagement style level"""
        if value <= 30:
            return "Detached, pure exposition"
        elif value <= 60:
            return "Professional-friendly"
        else:
            return "Conversational, direct address"


# Convenience function for quick access
def get_current_settings() -> Dict:
    """
    Quick access to current settings without instantiating manager.
    
    Returns:
        Dict with all current intensity settings
    """
    manager = IntensityManager()
    return manager.get_all_settings()


# Module-level singleton for efficiency
_manager_instance = None

def get_intensity_manager() -> IntensityManager:
    """
    Get singleton IntensityManager instance.
    
    Returns:
        Shared IntensityManager instance
    """
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = IntensityManager()
    return _manager_instance
