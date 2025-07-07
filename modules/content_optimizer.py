#!/usr/bin/env python3
"""
Content Optimization Module - Google E-A-T Enhancement
Applies optimization prompts to enhance Expertise, Authoritativeness, and Trustworthiness
"""

import json
import logging
from pathlib import Path
from modules import api_client

logger = logging.getLogger(__name__)

class ContentOptimizer:
    """Handles E-A-T content optimization for generated sections"""
    
    def __init__(self, config):
        self.config = config
        self.optimization_enabled = config.get('enable_optimization', True)
        self.max_iterations = config.get('optimization_iterations', 1)
        self.prompts_directory = Path("prompts")
        
    def optimize_section(self, content, section_name, section_type, material):
        """
        Optimize a single section for Google E-A-T requirements
        
        Args:
            content: Raw generated content
            section_name: Name of section (e.g., "Introduction")
            section_type: Type of section for context
            material: Material being discussed (e.g., "Hafnium")
            
        Returns:
            Optimized content string
        """
        
        if not self.optimization_enabled:
            logger.info("🔧 Optimization disabled - returning original content")
            return content
        
        # Enhanced start logging
        optimization_provider = self.config.get('optimization_provider')
        logger.info(f"🔧 Optimizing section '{section_name}' using provider: {optimization_provider}")
        logger.info(f"🔧 Section type: {section_type} | Material: {material}")
        
        try:
            # HEALTH CHECK FOR OPTIMIZATION PROVIDER
            if not self._check_optimization_provider_health():
                logger.error(f"❌ Optimization provider {optimization_provider} health check failed")
                logger.info("🔄 Returning original content due to provider unavailability")
                return content
            
            # Load optimization prompt
            optimization_prompt = self._load_optimization_prompt(
                content, section_type, material
            )
            prompt_length = len(optimization_prompt)
            logger.info(f"📋 Optimization prompt loaded: {prompt_length} characters")
            
            # Get optimization provider config
            provider_models = self.config.get('provider_models', {})
            provider_config = provider_models.get(optimization_provider, {})
            model_name = provider_config.get('model', 'unknown')
            logger.info(f"🤖 Using optimization model: {model_name}")
            
            if not provider_config:
                logger.error(f"❌ No configuration found for optimization provider: {optimization_provider}")
                return content
            
            # Format API keys
            api_key_mappings = self.config.get("api_key_mappings", {})
            api_keys = {}
            for prov, env_var in api_key_mappings.items():
                import os
                key = os.getenv(env_var)
                if key:
                    api_keys[env_var] = key
            
            # Apply optimization with enhanced logging
            for iteration in range(self.max_iterations):
                logger.info(f"🔧 E-A-T optimization iteration {iteration + 1}/{self.max_iterations}")
                logger.info(f"🔧 Provider: {optimization_provider} | Model: {model_name} | Temp: 0.3")
                
                try:
                    import time
                    start_time = time.time()
                    
                    result = api_client.call_ai_api(
                        prompt=optimization_prompt,
                        provider=optimization_provider,
                        model=provider_config.get('model'),
                        api_keys=api_keys,
                        temperature=0.3,  # Lower temperature for optimization consistency
                        max_tokens=self.config.get('max_tokens', 4096),
                        url_template=provider_config.get('url_template'),
                        backoff_factor=2.0
                    )
                    
                    # Enhanced completion logging
                    response_time = time.time() - start_time
                    
                    if result and result.strip():
                        optimized_content = result.strip()
                        
                        # Detailed optimization results
                        original_words = len(content.split())
                        optimized_words = len(optimized_content.split())
                        word_change = optimized_words - original_words
                        change_sign = "+" if word_change > 0 else ""
                        
                        logger.info(f"✅ E-A-T optimization complete in {response_time:.1f}s")
                        logger.info(f"📊 Words: {original_words} → {optimized_words} ({change_sign}{word_change})")
                        logger.info(f"🎯 Optimization ratio: {optimized_words/original_words:.2f}x")
                        
                        return optimized_content
                    else:
                        logger.warning(f"⚠️ Optimization iteration {iteration + 1} returned empty result after {response_time:.1f}s")
                        
                except Exception as e:
                    logger.error(f"❌ Optimization iteration {iteration + 1} failed: {e}")
                    
            # Enhanced failure logging
            logger.warning(f"⚠️ All {self.max_iterations} optimization attempts failed for '{section_name}'")
            logger.info(f"🔄 Returning original content ({len(content.split())} words)")
            return content
            
        except Exception as e:
            logger.error(f"❌ Content optimization failed for section '{section_name}': {e}")
            return content

    def _load_optimization_prompt(self, content, section_type, material):
        """Load and format the E-A-T optimization prompt from optimizations.json"""
        
        try:
            # Load prompt from optimizations.json file
            prompt_file = self.prompts_directory / "optimizations.json"
            
            if not prompt_file.exists():
                logger.error(f"❌ Optimization prompt file not found: {prompt_file}")
                raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
            
            with open(prompt_file, 'r', encoding='utf-8') as f:
                optimizations_data = json.load(f)
            
            # Get the E-A-T optimization prompt (default for now)
            eat_optimization = optimizations_data.get('eat_optimization')
            if not eat_optimization:
                logger.error(f"❌ 'eat_optimization' not found in {prompt_file}")
                raise KeyError("'eat_optimization' section not found in optimizations.json")
            
            # Format prompt with content
            formatted_prompt = eat_optimization['prompt'].format(
                content=content,
                section_type=section_type,
                material=material
            )
            
            logger.info(f"📋 Loaded optimization: {eat_optimization['name']} v{eat_optimization['version']}")
            return formatted_prompt
            
        except Exception as e:
            logger.error(f"❌ Failed to load optimization prompt: {e}")
            raise
    
    def _check_optimization_provider_health(self):
        """
        Check if the optimization provider is healthy and available
        
        Returns:
            bool: True if provider is healthy, False otherwise
        """
        
        optimization_provider = self.config.get('optimization_provider')
        logger.info(f"🔍 Checking optimization provider health: {optimization_provider}")
        
        try:
            # Get provider configuration
            provider_models = self.config.get('provider_models', {})
            provider_config = provider_models.get(optimization_provider, {})
            
            if not provider_config:
                logger.error(f"❌ No configuration found for optimization provider: {optimization_provider}")
                return False
            
            # Get API keys
            api_key_mappings = self.config.get("api_key_mappings", {})
            api_keys = {}
            for prov, env_var in api_key_mappings.items():
                import os
                key = os.getenv(env_var)
                if key:
                    api_keys[env_var] = key
            
            # Simple health check prompt
            health_check_prompt = "Hello, this is a health check. Please respond with 'OK'."
            
            import time
            start_time = time.time()
            
            # Make health check API call
            result = api_client.call_ai_api(
                prompt=health_check_prompt,
                provider=optimization_provider,
                model=provider_config.get('model'),
                api_keys=api_keys,
                temperature=0.1,  # Very low temperature for consistent response
                max_tokens=50,    # Small token limit for quick response
                url_template=provider_config.get('url_template'),
                backoff_factor=1.5
            )
            
            response_time = time.time() - start_time
            
            if result and result.strip():
                logger.info(f"✅ Optimization provider health check passed in {response_time:.1f}s")
                logger.info(f"🔌 Provider {optimization_provider} is available for optimization")
                return True
            else:
                logger.error(f"❌ Optimization provider health check failed: Empty response from {optimization_provider}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Optimization provider health check failed for {optimization_provider}: {e}")
            return False