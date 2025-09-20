#!/usr/bin/env python3
"""
Component Generation Helper

Utility functions to assist with component generation in the workflow.
"""

import logging
from typing import Dict, Optional, List

from run import COMPONENT_CONFIG
from utils.component_mode import get_component_mode, should_use_api

logger = logging.getLogger(__name__)

def get_required_api_components(component_types: List[str]) -> List[str]:
    """
    Determine which components in the list require API access.
    
    Args:
        component_types: List of component types to check
        
    Returns:
        List of component types that require API access
    """
    api_components = []
    
    for component_type in component_types:
        component_config = COMPONENT_CONFIG.get(component_type, {})
        api_provider = component_config.get("api_provider", "none")
        data_provider = component_config.get("data_provider", "static")
        
        # Component requires API if it has a non-"none" API provider and is in hybrid mode
        if api_provider != "none" and data_provider == "hybrid":
            api_components.append(component_type)
            
    return api_components

def preload_required_apis(component_types: List[str]) -> Dict[str, str]:
    """
    Get list of required API providers for the given component types.
    
    Args:
        component_types: List of component types to check
        
    Returns:
        Dict mapping component types to required API providers
    """
    required_apis = {}
    
    for component_type in component_types:
        component_config = COMPONENT_CONFIG.get(component_type, {})
        api_provider = component_config.get("api_provider", "none")
        data_provider = component_config.get("data_provider", "static")
        
        # Only include components that need API access
        if api_provider != "none" and data_provider == "hybrid":
            required_apis[component_type] = api_provider
            
    return required_apis

def optimize_component_ordering(component_types: List[str]) -> List[str]:
    """
    Optimize the order of component generation based on dependencies.
    
    Args:
        component_types: List of component types to order
        
    Returns:
        Optimized list of component types
    """
    # Create an optimized order based on dependencies
    prioritized = []
    remaining = component_types.copy()
    
    # Process frontmatter first if it's in the list
    if "frontmatter" in remaining:
        prioritized.append("frontmatter")
        remaining.remove("frontmatter")
    
    # Add components with highest priority (based on COMPONENT_CONFIG)
    sorted_by_priority = sorted(
        remaining,
        key=lambda c: COMPONENT_CONFIG.get(c, {}).get("priority", 100)
    )
    
    prioritized.extend(sorted_by_priority)
    
    return prioritized
