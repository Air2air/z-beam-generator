"""
Z-Beam CLI Package

Modular CLI components extracted from run.py for better organization:
- api_config.py: API provider configuration and client creation
- component_config.py: Component orchestration and configuration
- cleanup_commands.py: Cleanup functionality
"""

from api.client_manager import create_api_client, get_api_client_for_component

from .api_config import get_api_providers

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

__all__ = [
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
]
