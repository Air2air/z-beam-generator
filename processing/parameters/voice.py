"""
Voice Parameters

Consolidated module containing all voice-related parameters.
Consolidation: 6 files → 1 file (Nov 18, 2025)
"""

from typing import Dict, Any, Optional
from processing.parameters.base import Scale10Parameter, ParameterCategory


class JargonRemoval(Scale10Parameter):
    """
    Controls technical terminology vs plain language usage.
    
    Tier mapping:
    - LOW (1-3): Technical terminology encouraged
    - MODERATE (4-7): Balance technical and plain language
    - HIGH (8-10): Plain language only, avoid jargon
    
    Prompts loaded from: processing/parameters/presets/jargon_removal.yaml
    """
    
    def __init__(self, config_value: int):
        super().__init__(config_value)
        self.prompts = self._load_prompts_from_yaml('jargon_removal.yaml')
    
    def generate_prompt_guidance(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Select preset prompt based on tier.
        
        Args:
            context: Not used for this parameter (tier-only)
            
        Returns:
            Preset prompt string from YAML
        """
        # Simple dictionary lookup
        tier_prompts = self.prompts.get(self.tier.value, {})
        return tier_prompts.get('default', '')
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            'name': 'jargon_removal',
            'category': ParameterCategory.VOICE,
            'scale': '1-10',
            'description': 'Controls how much technical terminology vs plain language is used',
            'maps_to': 'voice_params',
            'examples': {
                'low': 'Technical terminology encouraged (ISO, ASTM, specs)',
                'moderate': 'Balance technical and plain language',
                'high': 'Plain language only, avoid jargon completely'
            }
        }


class ProfessionalVoice(Scale10Parameter):
    """
    Controls vocabulary formality level.
    
    Tier mapping:
    - LOW (1-3): Casual, conversational vocabulary
    - MODERATE (4-7): Balanced professional tone
    - HIGH (8-10): Highly formal, sophisticated vocabulary
    
    Prompts loaded from: processing/parameters/presets/professional_voice.yaml
    """
    
    def __init__(self, config_value: int):
        super().__init__(config_value)
        self.prompts = self._load_prompts_from_yaml('professional_voice.yaml')
    
    def generate_prompt_guidance(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Select preset prompt based on tier.
        
        Args:
            context: Not used for this parameter (tier-only)
            
        Returns:
            Preset prompt string from YAML
        """
        # Simple dictionary lookup
        tier_prompts = self.prompts.get(self.tier.value, {})
        return tier_prompts.get('default', '')
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            'name': 'professional_voice',
            'category': ParameterCategory.VOICE,
            'scale': '1-10',
            'description': 'Controls vocabulary level from casual to highly formal',
            'maps_to': 'voice_params',
            'examples': {
                'low': 'Casual vocabulary (kinda, stuff, pretty good)',
                'moderate': 'Professional but accessible',
                'high': 'Highly formal (consequently, facilitate, utilize)'
            }
        }


class PersonalityIntensity(Scale10Parameter):
    """
    Controls the frequency of personal opinions and perspectives.
    
    Tier mapping:
    - LOW (1-3): Purely factual, no personal opinions
    - MODERATE (4-7): Occasional personal insights and perspectives
    - HIGH (8-10): Frequent personal opinions throughout
    
    Prompts loaded from: processing/parameters/presets/personality_intensity.yaml
    """
    
    def __init__(self, config_value: int):
        super().__init__(config_value)
        self.prompts = self._load_prompts_from_yaml('personality_intensity.yaml')
    
    def generate_prompt_guidance(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Select preset prompt based on tier.
        
        Args:
            context: Generation context (unused for this parameter)
            
        Returns:
            Prompt string for this tier
        """
        tier_prompts = self.prompts.get(self.tier.value, {})
        return tier_prompts.get('default', '')
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return parameter metadata"""
        return {
            'name': 'personality_intensity',
            'category': ParameterCategory.VOICE,
            'scale': '1-10',
            'maps_to': 'opinion_rate'
        }


class EmotionalIntensity(Scale10Parameter):
    """
    Controls emotional tone from clinical/neutral to evocative/enthusiastic.
    
    Tier mapping:
    - LOW (1-3): Clinical, neutral, emotionless
    - MODERATE (4-7): Balanced, appropriate enthusiasm
    - HIGH (8-10): Evocative, enthusiastic, emotionally engaging
    
    Prompts loaded from: processing/parameters/presets/emotional_intensity.yaml
    """
    
    def __init__(self, config_value: int):
        super().__init__(config_value)
        self.prompts = self._load_prompts_from_yaml('emotional_intensity.yaml')
    
    def generate_prompt_guidance(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Select preset prompt based on tier.
        
        Args:
            context: Generation context (unused for this parameter)
            
        Returns:
            Prompt string for this tier
        """
        tier_prompts = self.prompts.get(self.tier.value, {})
        return tier_prompts.get('default', '')
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return parameter metadata"""
        return {
            'name': 'emotional_intensity',
            'category': ParameterCategory.VOICE,
            'scale': '1-10',
            'maps_to': 'enthusiasm_level'
        }


class AuthorVoiceIntensity(Scale10Parameter):
    """
    Controls the strength of author personality and regional voice traits.
    
    Tier mapping:
    - LOW (1-3): Minimal personality traits, subtle regional characteristics
    - MODERATE (4-7): Balanced personality presence, natural regional voice
    - HIGH (8-10): Strong personality, emphasized cultural/linguistic traits
    
    Prompts loaded from: processing/parameters/presets/author_voice_intensity.yaml
    """
    
    def __init__(self, config_value: int):
        super().__init__(config_value)
        self.prompts = self._load_prompts_from_yaml('author_voice_intensity.yaml')
    
    def generate_prompt_guidance(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Select preset prompt based on tier.
        
        Args:
            context: Generation context (unused for this parameter)
            
        Returns:
            Prompt string for this tier
        """
        # Simple dictionary lookup
        tier_prompts = self.prompts.get(self.tier.value, {})
        return tier_prompts.get('default', '')
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return parameter metadata"""
        return {
            'name': 'author_voice_intensity',
            'category': ParameterCategory.VOICE,
            'scale': '1-10',
            'maps_to': 'trait_frequency'
        }


class EngagementStyle(Scale10Parameter):
    """
    Controls reader engagement level from formal to conversational.
    
    Tier mapping:
    - LOW (1-3): Formal, distant, third-person only
    - MODERATE (4-7): Professional but accessible
    - HIGH (8-10): Highly conversational with frequent direct address
    
    Prompts loaded from: processing/parameters/presets/engagement_style.yaml
    """
    
    def __init__(self, config_value: int):
        super().__init__(config_value)
        self.prompts = self._load_prompts_from_yaml('engagement_style.yaml')
    
    def generate_prompt_guidance(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Select preset prompt based on tier.
        
        Args:
            context: Generation context (unused for this parameter)
            
        Returns:
            Prompt string for this tier
        """
        tier_prompts = self.prompts.get(self.tier.value, {})
        return tier_prompts.get('default', '')
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return parameter metadata"""
        return {
            'name': 'engagement_style',
            'category': ParameterCategory.VOICE,
            'scale': '1-10',
            'maps_to': 'reader_address_rate'
        }


__all__ = [
    'JargonRemoval',
    'ProfessionalVoice', 
    'PersonalityIntensity',
    'EmotionalIntensity',
    'AuthorVoiceIntensity',
    'EngagementStyle'
]
