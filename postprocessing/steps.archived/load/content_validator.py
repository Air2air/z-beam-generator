"""Content Validator Step

Validates loaded content is not empty/corrupted.
Pass 1, Step 1.2 of validation pipeline.
"""

from typing import Dict, Any
from postprocessing.steps.base_step import BaseStep


class ContentValidator(BaseStep):
    """Validate content integrity"""
    
    def _validate_inputs(self, context: Dict[str, Any]):
        """Validate content exists in context"""
        if 'content' not in context:
            raise ValueError("Missing 'content' in context")
    
    def _execute_logic(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate content is usable"""
        content = context['content']
        
        # Check not None
        if content is None:
            raise ValueError("Content is None")
        
        # Check not empty
        if not content or len(content.strip()) == 0:
            raise ValueError("Content is empty or whitespace-only")
        
        # Check reasonable length (at least 10 chars)
        if len(content) < 10:
            raise ValueError(f"Content too short: {len(content)} chars (minimum 10)")
        
        # Basic validation passed
        validation_result = {
            'valid': True,
            'length': len(content),
            'word_count': len(content.split()),
            'line_count': len(content.splitlines())
        }
        
        self.logger.info(
            f"✅ Content valid: {validation_result['length']} chars, "
            f"{validation_result['word_count']} words"
        )
        
        return validation_result
