"""
Structural Predictability Parameter

Controls how predictable vs varied the content structure is.
Uses preset prompts from YAML for clean dictionary lookups.
"""

from typing import Dict, Any, Optional
from processing.parameters.base import Scale10Parameter, ParameterCategory


class StructuralPredictability(Scale10Parameter):
    """
    Controls structural patterns from strict/consistent to unpredictable.
    
    Tier mapping:
    - LOW (1-3): Strict patterns, highly consistent structure
    - MODERATE (4-7): Some variation, flexible patterns
    - HIGH (8-10): Unpredictable structure, highly varied
    
    Prompts loaded from: processing/parameters/presets/structural_predictability.yaml
    """
    
    def __init__(self, config_value: int):
        super().__init__(config_value)
        self.prompts = self._load_prompts_from_yaml('structural_predictability.yaml')
    
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
            'name': 'structural_predictability',
            'category': ParameterCategory.VARIATION,
            'scale': '1-10',
            'maps_to': 'pattern_consistency'
        }
