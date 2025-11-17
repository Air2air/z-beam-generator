"""
Professional Voice Parameter

Controls vocabulary level from casual to highly formal.
Uses preset prompts from YAML for clean dictionary lookups.
"""

from typing import Dict, Any, Optional
from processing.parameters.base import Scale10Parameter, ParameterCategory


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
