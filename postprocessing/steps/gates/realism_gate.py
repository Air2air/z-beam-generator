"""Realism Gate Checker

Check if realism score passes threshold (≥ 7.0).
Pass 3, Step 3.2 of validation pipeline.
"""

from typing import Dict, Any
from postprocessing.steps.base_step import BaseStep


class RealismGateChecker(BaseStep):
    """Check Realism gate: score ≥ 7.0"""
    
    def __init__(self, threshold: float = 7.0):
        super().__init__()
        self.threshold = threshold
    
    def _validate_inputs(self, context: Dict[str, Any]):
        if 'realism_result' not in context:
            raise ValueError("Missing 'realism_result' in context")
    
    def _execute_logic(self, context: Dict[str, Any]) -> Dict[str, Any]:
        score = context['realism_result']['score']
        
        passed = score >= self.threshold
        
        return {
            'passed': passed,
            'score': score,
            'threshold': self.threshold,
            'gate_name': 'realism'
        }
