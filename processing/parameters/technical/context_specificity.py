"""
Context Specificity Parameter

Controls depth of contextual information and level of detail.
Uses preset prompts from YAML for clean dictionary lookups.
"""

from typing import Dict, Any, Optional
from processing.parameters.base import Scale10Parameter, ParameterCategory


class ContextSpecificity(Scale10Parameter):
    """
    Controls depth of contextual information and level of detail.
    
    Tier mapping:
    - LOW (1-3): Brief context, minimal background
    - MODERATE (4-7): Balanced context with relevant details
    - HIGH (8-10): Comprehensive context with thorough explanations
    
    Prompts loaded from: processing/parameters/presets/context_specificity.yaml
    """
    
    def __init__(self, config_value: int):
        super().__init__(config_value)
        self.prompts = self._load_prompts_from_yaml('context_specificity.yaml')
    
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
            'name': 'context_specificity',
            'category': ParameterCategory.TECHNICAL,
            'scale': '1-10',
            'maps_to': 'context_depth'
        }
