"""
Personality Intensity Parameter

Controls how frequently personal opinions and perspectives appear.
Uses preset prompts from YAML for clean dictionary lookups.
"""

from typing import Dict, Any, Optional
from processing.parameters.base import Scale10Parameter, ParameterCategory


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
