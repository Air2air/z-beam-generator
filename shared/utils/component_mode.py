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
    if component_type not in COMPONENT_CONFIG:
        raise ValueError(f"Unknown component type: {component_type}")

    component_config = COMPONENT_CONFIG[component_type]
    if "data_provider" not in component_config:
        raise ValueError(
            f"Component '{component_type}' missing required config key: data_provider"
        )

    configured_mode = component_config["data_provider"]
    if configured_mode not in {"hybrid", "static", "frontmatter"}:
        raise ValueError(
            f"Invalid data_provider '{configured_mode}' for component '{component_type}'"
        )

    if configured_mode == "hybrid" and api_client is None:
        raise ValueError(
            f"Component '{component_type}' requires api_client for hybrid mode"
        )

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
