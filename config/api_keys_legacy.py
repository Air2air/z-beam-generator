#!/usr/bin/env python3
"""
Legacy API Keys Configuration - DEPRECATED

This file is preserved for backward compatibility only.
All new code should use config/unified_manager.py for configuration management.

MIGRATION PATH:
- OLD: from config.api_keys import API_KEYS
- NEW: from config.unified_manager import _config_manager; API_KEYS = _config_manager.API_KEYS
"""

import warnings
from config.unified_manager import _config_manager

# Issue deprecation warning
warnings.warn(
    "config.api_keys is deprecated. Use config.unified_manager instead.",
    DeprecationWarning,
    stacklevel=2
)

# Backward compatibility - delegate to unified manager
def load_api_keys():
    """DEPRECATED: Use config.unified_manager instead"""
    warnings.warn(
        "load_api_keys() is deprecated. Configuration is auto-loaded by unified_manager.",
        DeprecationWarning,
        stacklevel=2
    )
    return True

# Provide API_KEYS for backward compatibility
API_KEYS = _config_manager.API_KEYS
