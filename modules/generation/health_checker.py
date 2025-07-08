#!/usr/bin/env python3
"""
API Health Checker - Validates API connectivity before generation
"""

import logging
import os
from modules import api_client

logger = logging.getLogger(__name__)

class APIHealthChecker:
    """Handles API health checks and connectivity validation"""
    
    def __init__(self, config):
        self.config = config
    
    def check_api_health(self):
        """Check API health before starting generation"""
        generation_provider = self.config.get('generation_provider')
        logger.info(f"🔍 Checking API health for {generation_provider}...")
        
        # Get provider configuration
        provider_models = self.config.get('provider_models', {})
        provider_config = provider_models.get(generation_provider, {})
        
        if not provider_config:
            raise RuntimeError(f"Provider configuration missing: {generation_provider}")
        
        # Format API keys
        api_keys = self._get_api_keys()
        if not api_keys:
            raise RuntimeError("No API keys configured for generation")
        
        # Simple health check
        test_result = api_client.call_ai_api(
            prompt=self.config.get('health_check_prompt', "Respond with 'OK' if you can process this request."),
            provider=generation_provider,
            model=provider_config.get('model'),
            api_keys=api_keys,
            temperature=self.config.get('health_check_temperature', 0.1),
            max_tokens=self.config.get('health_check_max_tokens', 10),
            url_template=provider_config.get('url_template')
        )
        
        if not test_result or 'OK' not in test_result.upper():
            raise RuntimeError(f"API health check failed for {generation_provider}")
        
        logger.info(f"✅ API health check passed for {generation_provider}")
    
    def _get_api_keys(self):
        """Get formatted API keys from environment"""
        api_key_mappings = self.config.get("api_key_mappings", {})
        api_keys = {}
        for prov, env_var in api_key_mappings.items():
            key = os.getenv(env_var)
            if key:
                api_keys[env_var] = key
        return api_keys