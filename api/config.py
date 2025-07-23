# filepath: /Users/todddunning/Desktop/Z-Beam/z-beam-generator/api/config.py
"""
Configuration for API clients.
"""

import os
import logging
import json
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Default provider configurations - will be overridden by ARTICLE_CONTEXT
PROVIDER_CONFIGS = {
    "deepseek": {
        "endpoint": "https://api.deepseek.com/v1/chat/completions",
        "model": "deepseek-chat",  # Default model, will be overridden
        "max_tokens_limit": 4000,
        "temperature": 0.7,
        "top_p": 0.9,
        "frequency_penalty": 0,
        "presence_penalty": 0
    },
    "openai": {
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "model": "gpt-4",
        "max_tokens_limit": 4000,  # Reduce from 8000 to 4000
        "temperature": 0.7,
        "top_p": 0.9,
        "frequency_penalty": 0,
        "presence_penalty": 0
    },
    "gemini": {
        "endpoint": "https://generativelanguage.googleapis.com/v1beta/models",
        "model": "gemini-1.5-pro",  # Default model, will be overridden
        "max_tokens_limit": 8192,
        "temperature": 0.7,
        "top_p": 0.95,
        "frequency_penalty": 0,
        "presence_penalty": 0
    },
    "xai": {
        "endpoint": "https://api.xai.grok.net/v1/chat/completions",
        "model": "grok-3-latest",  # Default model, will be overridden
        "max_tokens_limit": 4096,
        "temperature": 0.7,
        "top_p": 0.9,
        "frequency_penalty": 0,
        "presence_penalty": 0
    }
}

# Add function to update configs from ARTICLE_CONTEXT
def update_provider_configs(article_context: Dict[str, Any]) -> None:
    """Update provider configurations from article context."""
    if not article_context:
        return
        
    # Get the global AI provider and options
    provider = article_context.get("ai_provider", "deepseek")
    options = article_context.get("options", {})
    
    # Update the provider config with the global options
    if provider in PROVIDER_CONFIGS and "model" in options:
        PROVIDER_CONFIGS[provider]["model"] = options["model"]
    
    # Update component-specific providers and options
    components = article_context.get("components", {})
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
    
    # Start with the base provider config
    if provider_name in PROVIDER_CONFIGS:
        config = PROVIDER_CONFIGS[provider_name].copy()
    else:
        config = PROVIDER_CONFIGS.get("deepseek", {}).copy()
        
    # Apply component-specific overrides if available
    if article_context and component:
        components = article_context.get("components", {})
        if component in components:
            comp_config = components[component]
            comp_provider = comp_config.get("provider")
            comp_options = comp_config.get("options", {})
            
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