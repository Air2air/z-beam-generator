#!/usr/bin/env python3
"""
Versioning System Package

Centralized versioning for all Z-Beam components.
"""

from .generator import (
    VersionGenerator,
    get_version_generator,
    stamp_component_output,  # Simple API: stamp_component_output(component_name, content)
    stamp_component_output_full,  # Full API for backward compatibility
)

__version__ = "1.0.0"
__all__ = [
    "VersionGenerator",
    "get_version_generator",
    "stamp_component_output",  # Simple normalized API
    "stamp_component_output_full",  # Full API for special cases
]
