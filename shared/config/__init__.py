#!/usr/bin/env python3
"""
Z-Beam Configuration Module

CONFIGURATION NOTE: All user configurations are now centralized in config/settings.py
This module imports from settings.py for backward compatibility.
"""

# Import configurations from settings.py (centralized location)
try:
    from .settings import (
        API_PROVIDERS,
        COMPONENT_CONFIG,
        AI_DETECTION_CONFIG,
        OPTIMIZER_CONFIG,
        get_optimizer_config,
        get_ai_detection_config,
        get_workflow_config,
        get_optimization_config,
        get_text_optimization_config,
        get_persona_config,
        get_dynamic_config_for_component,
        create_dynamic_ai_detection_config,
    )
except ImportError:
    # Fail fast if settings.py configurations are not available
    raise RuntimeError(
        "CONFIGURATION ERROR: settings.py not found or configurations not defined. "
        "All configurations must be defined in config/settings.py with no fallbacks."
    )

__all__ = [
    'API_PROVIDERS',
    'COMPONENT_CONFIG',
    'AI_DETECTION_CONFIG',
    'OPTIMIZER_CONFIG',
    'get_optimizer_config',
    'get_ai_detection_config',
    'get_workflow_config',
    'get_optimization_config',
    'get_text_optimization_config',
    'get_persona_config',
    'get_dynamic_config_for_component',
    'create_dynamic_ai_detection_config',
]
