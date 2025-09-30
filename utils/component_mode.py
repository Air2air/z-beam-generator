#!/usr/bin/env python3
"""
Component Mode Utility

Provides centralized logic for determining component generation mode
based on COMPONENT_CONFIG settings.
"""

import logging

# Import from the central configuration file
from run import COMPONENT_CONFIG

logger = logging.getLogger(__name__)

def get_component_mode(component_type: str, api_client=None) -> str:
    """
    Determine the mode a component should use for generation based on configuration.
    
    Args:
        component_type: The type of component (e.g., "metatags", "text")
        api_client: The API client, if provided
        
    Returns:
        str: The mode to use: "hybrid", "static", or "frontmatter"
    """
    # Get component configuration from central source
    component_config = COMPONENT_CONFIG.get(component_type, {})
    
    # Get the data provider setting
    configured_mode = component_config.get("data_provider", "hybrid")
    
    # If the configured mode is hybrid but no API client is provided, fall back to static
    if configured_mode == "hybrid" and api_client is None:
        logger.warning(f"Component {component_type} is configured for hybrid mode but no API client provided. Falling back to static mode.")
        return "static"
    
    return configured_mode

def should_use_api(component_type: str, api_client=None) -> bool:
    """
    Determine if a component should use API-based generation.
    
    Args:
        component_type: The type of component
        api_client: The API client, if provided
        
    Returns:
        bool: True if API should be used, False otherwise
    """
    mode = get_component_mode(component_type, api_client)
    return mode == "hybrid" and api_client is not None
