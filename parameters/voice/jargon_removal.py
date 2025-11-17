"""
Jargon Removal Parameter

Controls how much technical terminology vs plain language is used.
Uses preset prompts from YAML for clean dictionary lookups.
"""

from typing import Dict, Any, Optional
from parameters.base import Scale10Parameter, ParameterCategory


class JargonRemoval(Scale10Parameter):
    """
    Controls technical terminology vs plain language usage.
    
    Tier mapping:
    - LOW (1-3): Technical terminology encouraged
    - MODERATE (4-7): Balance technical and plain language
    - HIGH (8-10): Plain language only, avoid jargon
    
    Prompts loaded from: parameters/presets/jargon_removal.yaml
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
