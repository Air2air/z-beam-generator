"""Database Logger Step

Log validation results to Winston feedback database.
Pass 5, Step 5.2 of validation pipeline.
"""

from typing import Dict, Any
from pathlib import Path
from postprocessing.steps.base_step import BaseStep


class DatabaseLogger(BaseStep):
    """Log results to Winston feedback database"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
    
    def _validate_inputs(self, context: Dict[str, Any]):
        if 'winston_result' not in context:
            raise ValueError("Missing 'winston_result' in context")
        if 'content' not in context:
            raise ValueError("Missing 'content' in context")
        if 'success' not in context:
            raise ValueError("Missing 'success' in context")
    
    def _execute_logic(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Log to database"""
        try:
            from postprocessing.detection.winston_feedback_db import WinstonFeedbackDatabase
            
            db_path = self.config.get('winston_feedback_db_path', 'z-beam.db')
            feedback_db = WinstonFeedbackDatabase(db_path)
            
            feedback_db.log_detection(
                content=context['content'],
                ai_score=context['winston_result']['ai_score'],
                human_score=context['winston_result']['human_score'],
                component_type=context.get('component_type', ''),
                material_name=context.get('material_name', ''),
                attempt_number=context.get('attempt', 1),
                success=context['success']
            )
            
            self.logger.info("💾 Logged to database")
            return {'logged': True}
            
        except Exception as e:
            self.logger.error(f"Database logging failed: {e}")
            return {'logged': False, 'error': str(e)}
