"""Realism Evaluator Step

Evaluate realism using Grok API.
Pass 2, Step 2.2 of validation pipeline.
"""

from typing import Dict, Any
from postprocessing.steps.base_step import BaseStep


class RealismEvaluator(BaseStep):
    """Evaluate realism using subjective evaluator"""
    
    def __init__(self, subjective_evaluator):
        super().__init__()
        self.evaluator = subjective_evaluator
    
    def _validate_inputs(self, context: Dict[str, Any]):
        if 'content' not in context:
            raise ValueError("Missing 'content' in context")
        if 'component_type' not in context:
            raise ValueError("Missing 'component_type' in context")
    
    def _execute_logic(self, context: Dict[str, Any]) -> Dict[str, Any]:
        content = context['content']
        component_type = context['component_type']
        material_name = context.get('material_name', 'Unknown')
        
        result = self.evaluator.evaluate(content, material_name, component_type)
        
        return {
            'score': result.realism_score or 0.0,
            'voice_authenticity': result.voice_authenticity,
            'tonal_consistency': result.tonal_consistency,
            'ai_tendencies': result.ai_tendencies or [],
            'full_result': result
        }
