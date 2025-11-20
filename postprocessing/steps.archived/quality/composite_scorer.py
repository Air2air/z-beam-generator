"""Composite Scorer Step

Calculate composite quality score (Winston 60% + Realism 40%).
Pass 2, Step 2.5 of validation pipeline.
"""

from typing import Dict, Any
from postprocessing.steps.base_step import BaseStep


class CompositeScorer(BaseStep):
    """Calculate composite quality score"""
    
    def _validate_inputs(self, context: Dict[str, Any]):
        if 'winston_result' not in context:
            raise ValueError("Missing 'winston_result' in context")
        if 'realism_result' not in context:
            raise ValueError("Missing 'realism_result' in context")
    
    def _execute_logic(self, context: Dict[str, Any]) -> float:
        winston_human_score = context['winston_result']['human_score']  # 0-1.0 normalized
        realism_score = context['realism_result']['score']              # 0-10 scale
        
        # Normalize realism to 0-1.0 (divide by 10)
        realism_normalized = realism_score / 10.0
        
        # Winston 60% + Realism 40% (both now 0-1.0 scale)
        composite = (winston_human_score * 0.6) + (realism_normalized * 0.4)
        
        self.logger.info(
            f"📊 Composite: {composite:.3f} ({composite*100:.1f}%) "
            f"(Winston: {winston_human_score:.3f}/{winston_human_score*100:.1f}%, "
            f"Realism: {realism_score:.1f}/10)"
        )
        
        return round(composite, 4)
