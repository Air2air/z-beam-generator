# filepath: /Users/todddunning/Desktop/Z-Beam/z-beam-generator/api/config.py
"""
Configuration for API clients.
"""

import os
import logging
import json
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Provider configurations - NO DEFAULTS, all values must be provided in ARTICLE_CONTEXT
PROVIDER_CONFIGS = {
    "deepseek": {
        "endpoint": "https://api.deepseek.com/v1/chat/completions"
    },
    "openai": {
        "endpoint": "https://api.openai.com/v1/chat/completions"
    },
    "gemini": {
        "endpoint": "https://generativelanguage.googleapis.com/v1beta/models"
    },
    "xai": {
        "endpoint": "https://api.xai.grok.net/v1/chat/completions"
    }
}

# Add function to update configs from ARTICLE_CONTEXT
def update_provider_configs(article_context: Dict[str, Any]) -> None:
    """Update provider configurations from article context."""
    if not article_context:
        raise ValueError("article_context must be provided")
        
    # Get the global AI provider and options - no fallbacks
    provider = article_context["ai_provider"]  # Must exist
    options = article_context["options"]  # Must exist
    
    # Update the provider config with the global options
    if provider in PROVIDER_CONFIGS and "model" in options:
        PROVIDER_CONFIGS[provider]["model"] = options["model"]
    
    # Update component-specific providers and options
    components = article_context["components"]  # Must exist
    for component_name, component_config in components.items():
        if "provider" in component_config and "options" in component_config:
            comp_provider = component_config["provider"]
            comp_options = component_config["options"]
            
            if comp_provider in PROVIDER_CONFIGS and "model" in comp_options:
                # Override just for this specific component call
                # This doesn't modify the base config
                logger.info(f"Component {component_name} using custom model: {comp_options['model']} for provider {comp_provider}")

def get_provider_config(provider: str, component: str = None, article_context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get configuration for the specified provider, optionally overridden for a component."""
    provider_name = provider.lower()
    
    # Start with the base provider config - no fallbacks
    config = PROVIDER_CONFIGS[provider_name].copy()  # Must exist
        
    # Apply component-specific overrides if available
    if article_context and component:
        components = article_context["components"]  # Must exist
        if component in components:
            comp_config = components[component]
            
            # Strict validation - no fallbacks
            comp_provider = comp_config["provider"] if "provider" in comp_config else None
            comp_options = comp_config["options"] if "options" in comp_config else {}
            
            # If this component uses this provider, apply its options
            if comp_provider == provider_name and comp_options:
                if "model" in comp_options:
                    config["model"] = comp_options["model"]
                if "temperature" in comp_options:
                    config["temperature"] = comp_options["temperature"]
                if "max_tokens" in comp_options:
                    config["max_tokens_limit"] = comp_options["max_tokens"]
    
    return config

# Add this alias to handle the naming mismatch
load_provider_config = get_provider_config  # Alias for backward compatibility