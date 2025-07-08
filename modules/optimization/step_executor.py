#!/usr/bin/env python3
"""
Optimization Step Executor - Executes individual optimization steps
"""

import logging
import os
from modules import api_client

logger = logging.getLogger(__name__)

class OptimizationStepExecutor:
    """Executes individual optimization steps"""
    
    def __init__(self, config):
        self.config = config
    
    def execute_step(self, bundled_prompt, step_name, step_config, section_name):
        """Execute a single optimization step"""
        
        # Get step-specific or default temperature
        temperature = self.config.get('step_temperatures', {}).get(
            step_name, 
            self.config.get('optimization_temperature', 0.3)
        )
        
        # Get provider and model
        optimization_provider = self.config.get('optimization_provider', 'DEEPSEEK')
        provider_models = self.config.get('provider_models', {})
        provider_config = provider_models.get(optimization_provider, {})
        
        if not provider_config:
            raise RuntimeError(f"Provider configuration missing: {optimization_provider}")
        
        # Format API keys (same as SectionGenerator)
        api_key_mappings = self.config.get("api_key_mappings", {})
        api_keys = {}
        for prov, env_var in api_key_mappings.items():
            key = os.getenv(env_var)
            if key:
                api_keys[f"{prov}_API_KEY"] = key
        
        if not api_keys:
            raise RuntimeError("No API keys configured for optimization")
        
        logger.info(f"🔧 Making optimization API call for step: {step_name}")
        
        # ✅ Use the EXACT same method call as SectionGenerator
        result = api_client.call_ai_api(
            prompt=bundled_prompt,
            provider=optimization_provider,
            model=provider_config.get('model'),
            api_keys=api_keys,
            temperature=temperature,
            max_tokens=self.config.get('max_tokens', 4000),
            url_template=provider_config.get('url_template'),
            backoff_factor=self.config.get('backoff_factor', 2.0),
            max_retries=self.config.get('max_retries', 3),
            timeout=self.config.get('timeout', 60)
        )
        
        if not result or not result.strip():
            raise RuntimeError(f"Empty response from optimization API for step: {step_name}")
        
        return result.strip()