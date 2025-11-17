"""
Sentence Rhythm Variation Parameter

Controls how much sentence lengths vary within generated content.
Uses preset prompts from YAML for clean dictionary lookups.
"""

from typing import Dict, Any, Optional
from parameters.base import Scale10Parameter, ParameterCategory


class SentenceRhythmVariation(Scale10Parameter):
    """
    Controls sentence length variation in generated content.
    
    Tier mapping:
    - LOW (1-3): Uniform, consistent sentence lengths
    - MODERATE (4-7): Mix short and medium sentences
    - HIGH (8-10): Dramatic variation in sentence lengths
    
    Prompts loaded from: parameters/presets/sentence_rhythm_variation.yaml
    """
    
    def __init__(self, config_value: int):
        super().__init__(config_value)
        self.prompts = self._load_prompts_from_yaml('sentence_rhythm_variation.yaml')
    
    def generate_prompt_guidance(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Select preset prompt based on tier and content length.
        
        Args:
            context: Must contain 'length' (target word count)
            
        Returns:
            Preset prompt string from YAML
        """
        length = context.get('length', 50)
        
        # Determine length category
        if length <= 30:
            length_category = 'short'
        elif length <= 100:
            length_category = 'medium'
        else:
            length_category = 'long'
        
        # Simple dictionary lookup - no conditionals!
        tier_prompts = self.prompts.get(self.tier.value, {})
        return tier_prompts.get(length_category, '')
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            'name': 'sentence_rhythm_variation',
            'category': ParameterCategory.VARIATION,
            'scale': '1-10',
            'description': 'Controls how much sentence lengths vary within generated content',
            'maps_to': 'voice_params',
            'examples': {
                'low': 'Uniform, consistent sentence lengths',
                'moderate': 'Mix short and medium sentences',
                'high': 'Dramatic variation in sentence lengths'
            }
        }
