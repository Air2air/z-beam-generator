"""
Variation Parameters

Consolidated module containing all variation-related parameters.
Consolidation: 4 files → 1 file (Nov 18, 2025)
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


class SentenceRhythmVariation(Scale10Parameter):
    """
    Controls sentence length variation in generated content.
    
    Tier mapping:
    - LOW (1-3): Uniform, consistent sentence lengths
    - MODERATE (4-7): Mix short and medium sentences
    - HIGH (8-10): Dramatic variation in sentence lengths
    
    Prompts loaded from: processing/parameters/presets/sentence_rhythm_variation.yaml
    """
    
    def __init__(self, config_value: int):
        super().__init__(config_value)
        self.prompts = self._load_prompts_from_yaml('sentence_rhythm_variation.yaml')
    
    def generate_prompt_guidance(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Select preset prompt based on tier and content length.
        
        Args:
            context: May contain 'length' (string: 'short', 'medium', 'long')
            
        Returns:
            Preset prompt string from YAML
        """
        length_category = context.get('length', 'medium')
        
        # If length is numeric, convert to category
        if isinstance(length_category, int):
            if length_category <= 30:
                length_category = 'short'
            elif length_category <= 100:
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


__all__ = [
    'ImperfectionTolerance',
    'LengthVariationRange',
    'SentenceRhythmVariation',
    'StructuralPredictability'
]
