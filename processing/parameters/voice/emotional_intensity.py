"""
Emotional Intensity Parameter

Controls enthusiasm level and evocativeness.
Uses preset prompts from YAML for clean dictionary lookups.
"""

from typing import Dict, Any, Optional
from processing.parameters.base import Scale10Parameter, ParameterCategory


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
