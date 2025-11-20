"""Composite Gate Checker

Check if all gates pass.
Pass 3, Step 3.5 of validation pipeline.
"""

from typing import Dict, Any
from postprocessing.steps.base_step import BaseStep


class CompositeGateChecker(BaseStep):
    """Check if all quality gates pass"""
    
    def _validate_inputs(self, context: Dict[str, Any]):
        required = ['winston_gate', 'realism_gate', 'readability_gate', 'subjective_gate']
        for key in required:
            if key not in context:
                raise ValueError(f"Missing '{key}' in context")
    
    def _execute_logic(self, context: Dict[str, Any]) -> Dict[str, Any]:
        gates = {
            'winston': context['winston_gate']['passed'],
            'realism': context['realism_gate']['passed'],
            'readability': context['readability_gate']['passed'],
            'subjective': context['subjective_gate']['passed']
        }
        
        all_passed = all(gates.values())
        failed_gates = [name for name, passed in gates.items() if not passed]
        
        if all_passed:
            self.logger.info("✅ ALL GATES PASSED")
        else:
            self.logger.warning(f"❌ Failed gates: {', '.join(failed_gates)}")
        
        return {
            'all_passed': all_passed,
            'failed_gates': failed_gates,
            'gate_details': gates
        }
