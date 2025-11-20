"""Readability Checker Step

Check content readability.
Pass 2, Step 2.3 of validation pipeline.
"""

from typing import Dict, Any
from postprocessing.steps.base_step import BaseStep


class ReadabilityChecker(BaseStep):
    """Check content readability"""
    
    def __init__(self, readability_validator):
        super().__init__()
        self.validator = readability_validator
    
    def _validate_inputs(self, context: Dict[str, Any]):
        if 'content' not in context:
            raise ValueError("Missing 'content' in context")
    
    def _execute_logic(self, context: Dict[str, Any]) -> Dict[str, Any]:
        content = context['content']
        
        passes = self.validator.validate(content)
        
        return {
            'passes': passes,
            'details': {}
        }
