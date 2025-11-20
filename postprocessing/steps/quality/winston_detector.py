"""Winston Detector Step

Detect AI content using Winston API.
Pass 2, Step 2.1 of validation pipeline.
"""

from typing import Dict, Any
from postprocessing.steps.base_step import BaseStep


class WinstonDetector(BaseStep):
    """Detect AI content using Winston API"""
    
    def __init__(self, winston_client):
        super().__init__()
        self.client = winston_client
    
    def _validate_inputs(self, context: Dict[str, Any]):
        if 'content' not in context:
            raise ValueError("Missing 'content' in context")
    
    def _execute_logic(self, context: Dict[str, Any]) -> Dict[str, Any]:
        content = context['content']
        
        result = self.client.detect(content)
        
        return {
            'ai_score': result.get('ai_score', 1.0),
            'human_score': (1.0 - result.get('ai_score', 1.0)) * 100,
            'sentence_scores': result.get('sentences', [])
        }
