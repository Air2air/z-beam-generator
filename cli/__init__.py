#!/usr/bin/env python3
"""
Z-Beam CLI Module

Command-line interface components for the Z-Beam content generation system.
"""

from api.client_manager import create_api_client, get_api_client_for_component

# Configuration now centralized in run.py
def get_api_providers():
    """Get API providers from config - single source of truth"""
    try:
        from run import API_PROVIDERS
        return API_PROVIDERS
    except ImportError:
        return {}

# Removed check_environment import to avoid circular dependency
from .cleanup_commands import (
    clean_content_components,
    run_cleanup_report,
    run_cleanup_scan,
    run_root_cleanup,
)
from .component_config import show_component_configuration, get_components_sorted_by_priority, get_enabled_components

# Import COMPONENT_CONFIG from run.py (user-settable configs)
try:
    from run import COMPONENT_CONFIG
except ImportError:
    COMPONENT_CONFIG = {}

# New modular CLI components
from .commands import (
    run_test_suite,
    test_api_connectivity,
    list_available_materials,
    show_system_status,
    show_cache_statistics,
    show_cache_info,
    clear_api_cache,
    disable_persistent_cache,
    preload_api_cache,
    clean_generated_content,
    run_cleanup_scan,
    generate_cleanup_report,
    run_root_cleanup,
    run_content_batch_generation,
    run_optimization,
    run_batch_generation,
)

from .argument_parser import create_argument_parser, show_help
from .config_display import show_configuration

__all__ = [
    # Legacy API functions
    "get_api_providers",
    "create_api_client",
    "get_api_client_for_component",
    "COMPONENT_CONFIG",
    "show_component_configuration",
    "get_components_sorted_by_priority",
    "get_enabled_components",
    "clean_content_components",
    "run_cleanup_scan",
    "run_cleanup_report",
    "run_root_cleanup",

    # New modular CLI components
    'run_test_suite',
    'test_api_connectivity',
    'list_available_materials',
    'show_system_status',
    'show_cache_statistics',
    'show_cache_info',
    'clear_api_cache',
    'disable_persistent_cache',
    'preload_api_cache',
    'clean_generated_content',
    'run_content_batch_generation',
    'run_optimization',
    'run_batch_generation',

    # Utilities
    'create_argument_parser',
    'show_help',
    'show_configuration',
]
