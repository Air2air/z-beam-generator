"""
Simplified Order Optimizer - Basic post-generation optimization
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SimpleOrderOptimizer:
    """Lightweight optimizer with basic post-generation options"""
    
    def __init__(self, config: Dict[str, Any], api_client):
        self.config = config
        self.api_client = api_client
        
        # Only load optimizers that are actually used
        self.optimizers = {}
        optimization_order = config.get("optimization_order", [])
        
        if "writing_samples" in optimization_order:
            from optimizers.writing_sample.writing_samples_optimizer import WritingSamplesOptimizer
            self.optimizers["writing_samples"] = WritingSamplesOptimizer(config, api_client)
        
        if "technical_authenticity" in optimization_order:
            from optimizers.technical_authenticity.technical_authenticity_optimizer import TechnicalAuthenticityOptimizer
            self.optimizers["technical_authenticity"] = TechnicalAuthenticityOptimizer(config, api_client)
        
        if "iterative" in optimization_order:
            from optimizers.iterative.iterative_optimizer import IterativeOptimizer
            self.optimizers["iterative"] = IterativeOptimizer(config, api_client)
    
    def optimize(self, content: str, metadata: Dict[str, Any]) -> str:
        """Apply optimizations in order"""
        optimization_order = self.config.get("optimization_order", [])
        
        current_content = content
        
        for optimizer_name in optimization_order:
            if optimizer_name in self.optimizers:
                logger.info(f"🔧 Applying {optimizer_name} optimization...")
                current_content = self.optimizers[optimizer_name].optimize(current_content, metadata)
            else:
                logger.warning(f"⚠️ Optimizer '{optimizer_name}' not available")
        
        return current_content