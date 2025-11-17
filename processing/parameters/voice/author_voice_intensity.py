"""
Author Voice Intensity Parameter

Controls how strongly author personality and regional voice traits show through.
Uses preset prompts from YAML for clean dictionary lookups.
"""

from typing import Dict, Any, Optional
from processing.parameters.base import Scale10Parameter, ParameterCategory


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
