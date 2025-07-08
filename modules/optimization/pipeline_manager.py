#!/usr/bin/env python3
"""
Optimization Pipeline Manager - Handles step loading and execution order
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class OptimizationPipelineManager:
    """Manages loading and sorting optimization steps"""
    
    def __init__(self, config):
        self.config = config
        self.prompts_directory = Path(config.get('prompts_directory', "prompts"))
    
    def load_optimization_pipeline(self):
        """Load ALL optimization steps from JSON and sort by order"""
        prompt_file = self.prompts_directory / "optimizations.json"
        
        if not prompt_file.exists():
            logger.error(f"❌ Optimization file not found: {prompt_file}")
            raise FileNotFoundError(f"Optimization file not found: {prompt_file}")
        
        with open(prompt_file, 'r', encoding='utf-8') as f:
            optimizations_data = json.load(f)
        
        optimization_steps = []
        
        for key, config in optimizations_data.items():
            if 'prompt' in config:
                optimization_steps.append({
                    'key': key,
                    'config': config
                })
        
        optimization_steps.sort(key=lambda x: x['config'].get('order', 999))
        
        logger.info(f"📋 Loaded {len(optimization_steps)} optimization steps")
        for step in optimization_steps:
            step_config = step['config']
            logger.info(f"   Step {step_config.get('order', 'unordered')}: {step_config.get('name', 'Unnamed Step')}")
            logger.info(f"      Type: {step_config.get('type', 'unknown')} | Version: {step_config.get('version', 'unversioned')}")
        
        return optimization_steps
    
    def is_optimization_enabled(self):
        """Check if optimization is available"""
        try:
            steps = self.load_optimization_pipeline()
            return len(steps) > 0
        except (FileNotFoundError, KeyError, Exception):
            return False