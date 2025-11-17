"""
AI Avoidance Intensity Parameter

Controls AI detection evasion strategies.
Uses preset prompts from YAML for clean dictionary lookups.
"""

from typing import Dict, Any, Optional
from processing.parameters.base import Scale10Parameter, ParameterCategory


class AIAvoidanceIntensity(Scale10Parameter):
    """
    Controls aggressiveness of AI detection evasion techniques.
    
    Tier mapping:
    - LOW (1-3): Minimal evasion (faster, less human-like)
    - MODERATE (4-7): Balanced approach
    - HIGH (8-10): Aggressive evasion (slower, more human-like)
    
    Prompts loaded from: processing/parameters/presets/ai_avoidance_intensity.yaml
    """
    
    def __init__(self, config_value: int):
        super().__init__(config_value)
        self.prompts = self._load_prompts_from_yaml('ai_avoidance_intensity.yaml')
    
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
            'name': 'ai_avoidance_intensity',
            'category': ParameterCategory.AI_DETECTION,
            'scale': '1-10',
            'maps_to': 'detection_evasion'
        }
