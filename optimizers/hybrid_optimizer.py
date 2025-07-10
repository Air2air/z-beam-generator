"""
Hybrid optimizer that can chain multiple optimization methods
"""
from typing import Dict, List, Any
from .base_optimizer import BaseOptimizer
from .iterative_optimizer import IterativeOptimizer
from .writing_samples_optimizer import WritingSamplesOptimizer
import logging

logger = logging.getLogger(__name__)

class HybridOptimizer(BaseOptimizer):
    """Optimizer that can chain multiple optimization methods"""
    
    def __init__(self, config: Dict[str, Any], api_client):
        """Initialize hybrid optimizer"""
        super().__init__(config, api_client)
        
        self.primary_method = config.get("optimization_method", "iterative")
        self.apply_writing_samples_final = config.get("apply_writing_samples_final", False)
        
        # Initialize optimizers based on configuration
        self.primary_optimizer = None
        self.writing_samples_optimizer = None
        
        self._initialize_optimizers(config, api_client)
        
        logger.info(f"🔧 HybridOptimizer initialized")
        logger.info(f"   📋 Primary method: {self.primary_method}")
        logger.info(f"   ✍️ Writing samples final: {self.apply_writing_samples_final}")
    
    def _initialize_optimizers(self, config: Dict[str, Any], api_client):
        """Initialize the required optimizers"""
        
        # Initialize primary optimizer
        if self.primary_method == "iterative":
            self.primary_optimizer = IterativeOptimizer(config, api_client)
            logger.info(f"✅ IterativeOptimizer initialized as primary")
        elif self.primary_method == "writing_samples":
            self.primary_optimizer = WritingSamplesOptimizer(config, api_client)
            logger.info(f"✅ WritingSamplesOptimizer initialized as primary")
        else:
            raise ValueError(f"❌ Unsupported optimization method: {self.primary_method}")
        
        # Initialize writing samples optimizer for final step if needed
        if self.apply_writing_samples_final:
            # If primary is already writing_samples, reuse it for final step
            if self.primary_method == "writing_samples":
                self.writing_samples_optimizer = self.primary_optimizer
                logger.info(f"✅ Reusing WritingSamplesOptimizer for final step (double pass)")
            else:
                self.writing_samples_optimizer = WritingSamplesOptimizer(config, api_client)
                logger.info(f"✅ WritingSamplesOptimizer initialized for final step")
    
    def optimize_sections(self, sections: List[Dict], context: Dict, config: Dict) -> List[Dict]:
        """ABSTRACT METHOD IMPLEMENTATION - Apply hybrid optimization with optional writing samples final step"""
        
        logger.info(f"🎯 HYBRID OPTIMIZATION STARTED for {context.get('material', 'unknown')}")
        logger.info(f"📊 Input sections: {len(sections)}")
        
        # PHASE 1: Apply primary optimization
        logger.info(f"🔄 PHASE 1: Primary optimization ({self.primary_method})")
        optimized_sections = self.primary_optimizer.optimize_sections(sections, context, config)
        logger.info(f"✅ Primary optimization completed")
        
        # PHASE 2: Apply writing samples final step (if configured)
        if self.apply_writing_samples_final and self.writing_samples_optimizer:
            logger.info(f"🔄 PHASE 2: Writing samples final optimization")
            
            if self.primary_method == "writing_samples":
                logger.info(f"📝 Double-pass: Running writing samples optimization again")
            
            optimized_sections = self.writing_samples_optimizer.optimize_sections(optimized_sections, context, config)
            logger.info(f"✅ Writing samples final optimization completed")
        
        logger.info(f"✅ HYBRID OPTIMIZATION COMPLETED")
        return optimized_sections
    
    def optimize(self, sections: List[Dict], context: Dict, config: Dict) -> List[Dict]:
        """Alias for optimize_sections to support both calling conventions"""
        return self.optimize_sections(sections, context, config)