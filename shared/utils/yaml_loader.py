"""
Fast YAML Loader — shim.

Canonical implementation moved to shared.utils.yaml_utils.
This module preserves backward-compatible import paths.
"""

from shared.utils.yaml_utils import (  # noqa: F401
    YAML_LOADER_TYPE,
    dump_yaml_fast,
    get_loader_info,
    load_yaml_fast,
)

__all__ = ["dump_yaml_fast", "get_loader_info", "load_yaml_fast", "YAML_LOADER_TYPE"]
