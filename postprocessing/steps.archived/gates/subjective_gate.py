"""Subjective Gate Checker

Check if subjective language has zero violations.
Pass 3, Step 3.4 of validation pipeline.
"""

from typing import Dict, Any
from postprocessing.steps.base_step import BaseStep


class SubjectiveGateChecker(BaseStep):
    """Check Subjective gate: zero violations"""
    
    def _validate_inputs(self, context: Dict[str, Any]):
        if 'subjective_result' not in context:
            raise ValueError("Missing 'subjective_result' in context")
    
    def _execute_logic(self, context: Dict[str, Any]) -> Dict[str, Any]:
        violations = context['subjective_result']['violations']
        
        passed = violations == 0
        
        return {
            'passed': passed,
            'violations': violations,
            'gate_name': 'subjective'
        }
