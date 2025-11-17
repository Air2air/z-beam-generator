"""
Technical Language Intensity Parameter

Controls density of technical specifications and measurements.
Uses preset prompts from YAML for clean dictionary lookups.
"""

from typing import Dict, Any, Optional
from processing.parameters.base import Scale10Parameter, ParameterCategory


class TechnicalLanguageIntensity(Scale10Parameter):
    """
    Controls density of technical specifications and measurements.
    
    Tier mapping:
    - LOW (1-3): Minimal technical specs, focus on benefits
    - MODERATE (4-7): Key specifications included where relevant
    - HIGH (8-10): Detailed measurements and specs throughout
    
    Prompts loaded from: processing/parameters/presets/technical_language_intensity.yaml
    """
    
    def __init__(self, config_value: int):
        super().__init__(config_value)
        self.prompts = self._load_prompts_from_yaml('technical_language_intensity.yaml')
    
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
            'name': 'technical_language_intensity',
            'category': ParameterCategory.TECHNICAL,
            'scale': '1-10',
            'maps_to': 'spec_density'
        }
