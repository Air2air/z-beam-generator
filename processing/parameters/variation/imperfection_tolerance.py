"""
Imperfection Tolerance Parameter

Controls how much natural imperfection is allowed in generated content.
Uses preset prompts from YAML for clean dictionary lookups.
"""

from typing import Dict, Any, Optional
from processing.parameters.base import Scale10Parameter, ParameterCategory


class ImperfectionTolerance(Scale10Parameter):
    """
    Controls natural imperfection level in generated content.
    
    Tier mapping:
    - LOW (1-3): Perfect grammar and structure required
    - MODERATE (4-7): Some natural imperfections allowed
    - HIGH (8-10): Embrace authentic imperfections
    
    Prompts loaded from: processing/parameters/presets/imperfection_tolerance.yaml
    """
    
    def __init__(self, config_value: int):
        super().__init__(config_value)
        self.prompts = self._load_prompts_from_yaml('imperfection_tolerance.yaml')
    
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
            'name': 'imperfection_tolerance',
            'category': ParameterCategory.VARIATION,
            'scale': '1-10',
            'description': 'Controls how much natural imperfection is allowed in generated content',
            'maps_to': 'voice_params',
            'examples': {
                'low': 'Perfect grammar and structure',
                'moderate': 'Natural imperfections allowed',
                'high': 'Embrace authentic imperfections'
            }
        }
