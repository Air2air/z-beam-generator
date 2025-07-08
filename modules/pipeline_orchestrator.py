import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class PipelineOrchestrator:
    def __init__(self, config):
        self.config = config
        self.modules = {}
        self._initialize_modules()
    
    def _initialize_modules(self):
        """Initialize enabled pipeline modules"""
        pipeline_modules = self.config.get("pipeline_modules", {})
        
        for module_name, module_config in pipeline_modules.items():
            if module_config.get("enabled", False):
                logger.info(f"🔧 Initializing module: {module_name}")
                self.modules[module_name] = self._create_module(module_name, module_config)
    
    def execute_stage(self, stage_name, context):
        """Execute all modules for a given stage"""
        logger.info(f"🎯 Executing stage: {stage_name}")
        results = {}
        
        for module_name, module in self.modules.items():
            module_config = self.config["pipeline_modules"][module_name]
            
            if module_config.get("stage") == stage_name:
                logger.info(f"▶️  Running module: {module_name}")
                results[module_name] = module.execute(context)
                logger.info(f"✅ Module {module_name} completed")
        
        return results
    
    def _create_module(self, module_name, module_config):
        """Factory method for creating modules"""
        if module_name == "metadata":
            from modules.metadata.metadata_generator import MetadataGenerator
            return MetadataGenerator(self.config, module_config)
        
        raise ValueError(f"Unknown module: {module_name}")