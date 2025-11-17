"""
Length Variation Range Parameter

Controls word count flexibility and tolerance.
Uses preset prompts from YAML for clean dictionary lookups.
"""

from typing import Dict, Any, Optional
from processing.parameters.base import Scale10Parameter, ParameterCategory


class LengthVariationRange(Scale10Parameter):
    """
    Controls how much word count can vary from target length.
    
    Tier mapping:
    - LOW (1-3): Tight ±10% tolerance
    - MODERATE (4-7): Moderate ±30% tolerance
    - HIGH (8-10): Loose ±60% tolerance, natural flow prioritized
    
    Prompts loaded from: processing/parameters/presets/length_variation_range.yaml
    """
    
    def __init__(self, config_value: int):
        super().__init__(config_value)
        self.prompts = self._load_prompts_from_yaml('length_variation_range.yaml')
    
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
            'name': 'length_variation_range',
            'category': ParameterCategory.VARIATION,
            'scale': '1-10',
            'maps_to': 'word_count_flexibility'
        }
