"""Temperature Calculator Step

Calculate temperature adjustment based on Winston scores.
Pass 4, Step 4.2 of validation pipeline.
"""

from typing import Dict, Any
from postprocessing.steps.base_step import BaseStep


class TemperatureCalculator(BaseStep):
    """Calculate temperature adjustment"""
    
    def __init__(self, temperature_advisor):
        super().__init__()
        self.advisor = temperature_advisor
    
    def _validate_inputs(self, context: Dict[str, Any]):
        if 'winston_result' not in context:
            raise ValueError("Missing 'winston_result' in context")
    
    def _execute_logic(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Get temperature recommendation"""
        material_name = context.get('material_name', '')
        component_type = context.get('component_type', '')
        ai_score = context['winston_result']['ai_score']
        
        try:
            temp = self.advisor.get_recommendation(
                material_name,
                component_type,
                ai_score
            )
            
            if temp:
                self.logger.info(f"🌡️  Temperature: {temp}")
                return {'temperature': temp}
            return {}
            
        except Exception as e:
            self.logger.warning(f"Temperature calculation failed: {e}")
            return {}
