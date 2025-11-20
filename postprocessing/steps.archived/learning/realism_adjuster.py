"""Realism Adjuster Step

Get parameter adjustments for realism failures.
Pass 4, Step 4.3 of validation pipeline.
"""

from typing import Dict, Any
from postprocessing.steps.base_step import BaseStep


class RealismAdjuster(BaseStep):
    """Get realism-based parameter adjustments"""
    
    def __init__(self, realism_optimizer):
        super().__init__()
        self.optimizer = realism_optimizer
    
    def _validate_inputs(self, context: Dict[str, Any]):
        if 'realism_result' not in context:
            raise ValueError("Missing 'realism_result' in context")
    
    def _execute_logic(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Get adjustments if realism score < 7.0"""
        realism_score = context['realism_result']['score']
        
        if realism_score >= 7.0:
            return {}  # No adjustments needed
        
        try:
            adjustments = self.optimizer.get_adjustments(realism_score)
            self.logger.info(f"🎯 Realism adjustments: {len(adjustments)} parameters")
            return adjustments
            
        except Exception as e:
            self.logger.warning(f"Realism adjustment failed: {e}")
            return {}
