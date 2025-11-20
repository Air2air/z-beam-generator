"""Sweet Spot Retriever Step

Retrieve optimal parameter ranges from historical data.
Pass 4, Step 4.1 of validation pipeline.
"""

from typing import Dict, Any
from postprocessing.steps.base_step import BaseStep


class SweetSpotRetriever(BaseStep):
    """Retrieve optimal parameter ranges from sweet spot analyzer"""
    
    def __init__(self, sweet_spot_analyzer):
        super().__init__()
        self.analyzer = sweet_spot_analyzer
    
    def _validate_inputs(self, context: Dict[str, Any]):
        pass  # No required inputs
    
    def _execute_logic(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Get sweet spot parameters (top 25% performers)"""
        try:
            sweet_spots = self.analyzer.find_sweet_spots(top_n_percent=25)
            
            adjustments = {}
            for param_name, sweet_spot in sweet_spots.items():
                if sweet_spot.confidence in ['high', 'medium']:
                    adjustments[param_name] = sweet_spot.optimal_median
            
            self.logger.info(f"📊 Sweet spot: {len(adjustments)} parameters")
            return adjustments
            
        except Exception as e:
            self.logger.warning(f"Sweet spot retrieval failed: {e}")
            return {}
