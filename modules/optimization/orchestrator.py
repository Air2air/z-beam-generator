#!/usr/bin/env python3
"""
Optimization Orchestrator - Main coordinator for optimization pipeline
"""

import logging
from .pipeline_manager import OptimizationPipelineManager
from .prompt_builder import OptimizationPromptBuilder
from .step_executor import OptimizationStepExecutor

logger = logging.getLogger(__name__)

class OptimizationOrchestrator:
    """Main orchestrator for optimization pipeline"""
    
    def __init__(self, config):
        self.config = config
        self.pipeline_manager = OptimizationPipelineManager(config)
        self.prompt_builder = OptimizationPromptBuilder()
        self.step_executor = OptimizationStepExecutor(config)
        
        # Auto-detect optimization availability
        self.optimization_enabled = self.pipeline_manager.is_optimization_enabled()
        logger.info(f"🔧 Optimization auto-detected: {'enabled' if self.optimization_enabled else 'disabled'}")
    
    def optimize_section(self, content, section_name, section_type, material):
        """Run complete optimization pipeline for a section"""
        
        if not self.optimization_enabled:
            logger.info("🔧 Optimization disabled - returning original content")
            return content
        
        logger.info(f"🎯 Starting optimization pipeline for section: {section_name}")
        
        # Load optimization steps
        optimization_steps = self.pipeline_manager.load_optimization_pipeline()
        
        current_content = content
        original_words = len(content.split())
        optimization_history = []
        
        # Execute each step
        for step in optimization_steps:
            step_name = step['key']
            step_config = step['config']
            
            logger.info(f"🔧 Applying step {step_config['order']}: {step_config['name']}")
            logger.info(f"📝 Step details: {step_config.get('description', 'No description available')}")
            
            # Create bundled prompt
            bundled_prompt = self.prompt_builder.create_bundled_prompt(
                previous_content=current_content,
                optimization_config=step_config,
                section_context={
                    "name": section_name,
                    "type": section_type,
                    "material": material,
                    "previous_steps": optimization_history.copy(),
                    "target_words": self.config.get('default_section_words', 150)
                }
            )
            
            # Execute step
            optimized_content = self.step_executor.execute_step(
                bundled_prompt, step_name, step_config, section_name
            )
            
            # Validate result
            if not optimized_content or not optimized_content.strip():
                logger.error(f"❌ GENERATION FAILED: {step_config['name']} returned empty content")
                raise RuntimeError(f"Optimization step '{step_config['name']}' failed for section '{section_name}'")
            
            # Log results
            before_words = len(current_content.split())
            after_words = len(optimized_content.split())
            word_change = after_words - before_words
            change_sign = "+" if word_change > 0 else ""
            
            logger.info(f"✅ {step_config['name']}: {before_words}→{after_words} ({change_sign}{word_change})")
            
            # Update for next iteration
            current_content = optimized_content
            optimization_history.append(step_name)
        
        # Final results
        final_words = len(current_content.split())
        total_change = final_words - original_words
        change_sign = "+" if total_change > 0 else ""
        
        logger.info(f"🎯 Optimization pipeline complete: {original_words}→{final_words} ({change_sign}{total_change})")
        return current_content