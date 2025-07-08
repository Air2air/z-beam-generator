#!/usr/bin/env python3
"""
Optimization Step Executor - Handles individual step execution
"""

import logging
import time
import os
from modules import api_client

logger = logging.getLogger(__name__)

class OptimizationStepExecutor:
    """Executes individual optimization steps via API"""
    
    def __init__(self, config):
        self.config = config
    
    def execute_step(self, bundled_prompt, step_name, step_config, section_name):
        """Execute optimization step with bundled prompt"""
        
        optimization_provider = self.config.get('optimization_provider')
        
        # Get provider configuration
        provider_models = self.config.get('provider_models', {})
        provider_config = provider_models.get(optimization_provider, {})
        
        if not provider_config:
            logger.error(f"❌ GENERATION FAILED: No configuration found for provider: {optimization_provider}")
            raise RuntimeError(f"Provider configuration missing: {optimization_provider}")
        
        # Format API keys
        api_key_mappings = self.config.get("api_key_mappings", {})
        api_keys = {}
        for prov, env_var in api_key_mappings.items():
            key = os.getenv(env_var)
            if key:
                api_keys[env_var] = key
        
        if not api_keys:
            logger.error(f"❌ GENERATION FAILED: No API keys available for optimization")
            raise RuntimeError("No API keys configured for optimization")
        
        # Make API call with bundled prompt
        start_time = time.time()
        
        # Get step-specific overrides
        step_temperatures = self.config.get('step_temperatures', {})
        step_max_tokens = self.config.get('step_max_tokens', {})
        
        temperature = step_config.get('temperature', 
                                    step_temperatures.get(step_name, 
                                                        self.config.get('optimization_temperature', 0.3)))
        
        max_tokens = step_config.get('max_tokens',
                                   step_max_tokens.get(step_name,
                                                     self.config.get('max_tokens', 4096)))
        
        result = api_client.call_ai_api(
            prompt=bundled_prompt,
            provider=optimization_provider,
            model=provider_config.get('model'),
            api_keys=api_keys,
            temperature=temperature,
            max_tokens=max_tokens,
            url_template=provider_config.get('url_template'),
            backoff_factor=self.config.get('backoff_factor', 2.0)
        )
        
        response_time = time.time() - start_time
        
        # STRICT VALIDATION - FAIL FAST ON EMPTY RESPONSE
        if not result or not result.strip():
            logger.error(f"❌ GENERATION FAILED: {step_config.get('name', 'Unknown Step')} returned empty response")
            logger.error(f"💀 API call succeeded but content is empty - aborting generation")
            raise RuntimeError(f"Empty response from optimization step: {step_config.get('name', step_name)}")
        
        logger.info(f"   ⏱️ {step_config.get('name', 'Unknown Step')} completed in {response_time:.1f}s")
        return result.strip()