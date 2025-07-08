#!/usr/bin/env python3
"""
Section Generator - Handles individual section content generation
"""

import logging
import os
from modules import api_client

logger = logging.getLogger(__name__)

class SectionGenerator:
    """Generates content for individual sections"""
    
    def __init__(self, config):
        self.config = config
    
    def generate_section_with_enhancement(self, section, material, eat_requirements):
        """Generate section content with E-A-T requirements integrated"""
        section_prompt = section['prompt']
        
        # Build enhanced prompt with E-A-T requirements
        enhanced_prompt = f"""{section_prompt.format(material=material)}

{eat_requirements}

TARGET: Generate approximately {self.config.get('default_section_words', 150)} words of high-quality, E-A-T compliant content."""
        
        return self._make_generation_api_call(enhanced_prompt, section['name'])
    
    def generate_section_standard(self, section, material):
        """Generate section content using standard prompt only"""
        section_prompt = section['prompt'].format(material=material)
        return self._make_generation_api_call(section_prompt, section['name'])
    
    def _make_generation_api_call(self, prompt, section_name):
        """Make API call for content generation"""
        generation_provider = self.config.get('generation_provider')
        
        # Get provider configuration
        provider_models = self.config.get('provider_models', {})
        provider_config = provider_models.get(generation_provider, {})
        
        if not provider_config:
            raise RuntimeError(f"Provider configuration missing: {generation_provider}")
        
        # Format API keys
        api_key_mappings = self.config.get("api_key_mappings", {})
        api_keys = {}
        for prov, env_var in api_key_mappings.items():
            key = os.getenv(env_var)
            if key:
                api_keys[f"{prov}_API_KEY"] = key  # ✅ Fix key format
        
        if not api_keys:
            raise RuntimeError("No API keys configured for generation")
        
        logger.info(f"📡 Making generation API call for section: {section_name}")
        
        # Make API call with ALL required parameters
        result = api_client.call_ai_api(
            prompt=prompt,
            provider=generation_provider,
            model=provider_config.get('model'),
            api_keys=api_keys,
            temperature=self.config.get('generation_temperature', 0.7),
            max_tokens=self.config.get('max_tokens', 4000),
            url_template=provider_config.get('url_template'),
            backoff_factor=self.config.get('backoff_factor', 2.0),  # ✅ Added
            max_retries=self.config.get('max_retries', 3),          # ✅ Added
            timeout=self.config.get('timeout', 60)                  # ✅ Added
        )
        
        if not result or not result.strip():
            raise RuntimeError(f"Empty response from generation API for section: {section_name}")
        
        return result.strip()