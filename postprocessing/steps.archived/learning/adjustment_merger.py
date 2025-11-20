"""Adjustment Merger Step

Merge adjustments from all learning systems with priority order.
Pass 4, Step 4.5 of validation pipeline.
"""

from typing import Dict, Any
from postprocessing.steps.base_step import BaseStep


class AdjustmentMerger(BaseStep):
    """Merge adjustments with priority: sweet_spot → temperature → realism → pattern"""
    
    def _validate_inputs(self, context: Dict[str, Any]):
        pass  # All inputs optional
    
    def _execute_logic(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Merge adjustments (last wins for conflicts)"""
        merged = {}
        
        # Priority 1: Sweet spot (base layer)
        if 'sweet_spot_adjustments' in context:
            merged.update(context['sweet_spot_adjustments'])
        
        # Priority 2: Temperature (overrides sweet spot temp)
        if 'temperature_adjustments' in context:
            merged.update(context['temperature_adjustments'])
        
        # Priority 3: Realism (overrides for realism failures)
        if 'realism_adjustments' in context:
            merged.update(context['realism_adjustments'])
        
        # Priority 4: Pattern (final override - proven patterns)
        if 'pattern_adjustments' in context:
            merged.update(context['pattern_adjustments'])
        
        self.logger.info(f"🔀 Merged {len(merged)} final adjustments")
        
        return merged
