"""Subjective Checker Step

Check for subjective language violations.
Pass 2, Step 2.4 of validation pipeline.
"""

from typing import Dict, Any
from postprocessing.steps.base_step import BaseStep


class SubjectiveChecker(BaseStep):
    """Check for subjective language"""
    
    def __init__(self, subjective_validator):
        super().__init__()
        self.validator = subjective_validator
    
    def _validate_inputs(self, context: Dict[str, Any]):
        if 'content' not in context:
            raise ValueError("Missing 'content' in context")
        if 'component_type' not in context:
            raise ValueError("Missing 'component_type' in context")
    
    def _execute_logic(self, context: Dict[str, Any]) -> Dict[str, Any]:
        content = context['content']
        component_type = context['component_type']
        
        result = self.validator.validate(content, component_type)
        
        violations = result.get('violations', [])
        
        return {
            'violations': len(violations),
            'details': violations,
            'passes': len(violations) == 0
        }
