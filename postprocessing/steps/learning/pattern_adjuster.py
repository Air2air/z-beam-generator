"""Pattern Adjuster Step

Get adjustments from learned patterns.
Pass 4, Step 4.4 of validation pipeline.
"""

from typing import Dict, Any
from postprocessing.steps.base_step import BaseStep


class PatternAdjuster(BaseStep):
    """Get pattern-based parameter adjustments"""
    
    def __init__(self, pattern_learner):
        super().__init__()
        self.learner = pattern_learner
    
    def _validate_inputs(self, context: Dict[str, Any]):
        if 'component_type' not in context:
            raise ValueError("Missing 'component_type' in context")
    
    def _execute_logic(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Get pattern-based adjustments"""
        component_type = context['component_type']
        
        try:
            adjustments = self.learner.get_adjustments(component_type)
            if adjustments:
                self.logger.info(f"🧩 Pattern adjustments: {len(adjustments)} parameters")
            return adjustments
            
        except Exception as e:
            self.logger.warning(f"Pattern adjustment failed: {e}")
            return {}
