"""Pattern Recorder Step

Update learned_patterns.yaml with evaluation results.
Pass 5, Step 5.1 of validation pipeline.
"""

from typing import Dict, Any
from postprocessing.steps.base_step import BaseStep


class PatternRecorder(BaseStep):
    """Record patterns to learned_patterns.yaml"""
    
    def __init__(self, subjective_evaluator):
        super().__init__()
        self.evaluator = subjective_evaluator
    
    def _validate_inputs(self, context: Dict[str, Any]):
        if 'realism_result' not in context:
            raise ValueError("Missing 'realism_result' in context")
        if 'content' not in context:
            raise ValueError("Missing 'content' in context")
        if 'accepted' not in context:
            raise ValueError("Missing 'accepted' in context (True/False)")
    
    def _execute_logic(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Update pattern learner"""
        try:
            pattern_learner = self.evaluator._get_pattern_learner()
            
            full_result = context['realism_result'].get('full_result')
            if hasattr(full_result, '__dict__'):
                evaluation_dict = full_result.__dict__
            else:
                evaluation_dict = full_result or {}
            
            pattern_learner.update_from_evaluation(
                evaluation_result=evaluation_dict,
                content=context['content'],
                accepted=context['accepted'],
                component_type=context.get('component_type', ''),
                material_name=context.get('material_name', '')
            )
            
            self.logger.info(f"📚 Pattern recorded (accepted={context['accepted']})")
            return {'recorded': True}
            
        except Exception as e:
            self.logger.warning(f"Pattern recording failed: {e}")
            return {'recorded': False, 'error': str(e)}
