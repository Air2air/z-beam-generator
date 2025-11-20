"""Readability Gate Checker

Check if readability passes.
Pass 3, Step 3.3 of validation pipeline.
"""

from typing import Dict, Any
from postprocessing.steps.base_step import BaseStep


class ReadabilityGateChecker(BaseStep):
    """Check Readability gate: must pass"""
    
    def _validate_inputs(self, context: Dict[str, Any]):
        if 'readability_result' not in context:
            raise ValueError("Missing 'readability_result' in context")
    
    def _execute_logic(self, context: Dict[str, Any]) -> Dict[str, Any]:
        passed = context['readability_result']['passes']
        
        return {
            'passed': passed,
            'gate_name': 'readability'
        }
