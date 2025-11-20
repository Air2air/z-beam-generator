"""Winston Gate Checker

Check if Winston AI score passes threshold (< 33%).
Pass 3, Step 3.1 of validation pipeline.
"""

from typing import Dict, Any
from postprocessing.steps.base_step import BaseStep


class WinstonGateChecker(BaseStep):
    """Check Winston gate: AI score < 33%"""
    
    def __init__(self, threshold: float = 0.33):
        super().__init__()
        self.threshold = threshold
    
    def _validate_inputs(self, context: Dict[str, Any]):
        if 'winston_result' not in context:
            raise ValueError("Missing 'winston_result' in context")
    
    def _execute_logic(self, context: Dict[str, Any]) -> Dict[str, Any]:
        ai_score = context['winston_result']['ai_score']
        
        passed = ai_score < self.threshold
        
        return {
            'passed': passed,
            'ai_score': ai_score,
            'threshold': self.threshold,
            'gate_name': 'winston'
        }
