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
        winston_human_score = context['winston_result']['human_score']
        realism_score = context['realism_result']['score']
        
        # Winston 60% + Realism 40% (convert realism 0-10 to 0-100)
        composite = (winston_human_score * 0.6) + (realism_score * 10 * 0.4)
        
        self.logger.info(
            f"📊 Composite: {composite:.1f}% "
            f"(Winston: {winston_human_score:.1f}%, Realism: {realism_score:.1f}/10)"
        )
        
        return round(composite, 2)
