"""
Engagement Style Parameter

Controls how conversational vs formal the writing style is.
Uses preset prompts from YAML for clean dictionary lookups.
"""

from typing import Dict, Any, Optional
from processing.parameters.base import Scale10Parameter, ParameterCategory


class EngagementStyle(Scale10Parameter):
    """
    Controls reader engagement level from formal to conversational.
    
    Tier mapping:
    - LOW (1-3): Formal, distant, third-person only
    - MODERATE (4-7): Professional but accessible
    - HIGH (8-10): Highly conversational with frequent direct address
    
    Prompts loaded from: processing/parameters/presets/engagement_style.yaml
    """
    
    def __init__(self, config_value: int):
        super().__init__(config_value)
        self.prompts = self._load_prompts_from_yaml('engagement_style.yaml')
    
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
            'name': 'engagement_style',
            'category': ParameterCategory.VOICE,
            'scale': '1-10',
            'maps_to': 'reader_address_rate'
        }
