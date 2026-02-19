"""Backward-compatible import path for contaminants data loader v2.

This module preserves legacy imports:
    from domains.contaminants.data_loader_v2 import ...

Canonical implementation lives in:
    domains.contaminants.loaders.data_loader_v2
"""

from domains.contaminants.loaders.data_loader_v2 import (
    ContaminantsDataLoader,
    PatternDataLoader,
    load_pattern_data,
)

__all__ = ["ContaminantsDataLoader", "PatternDataLoader", "load_pattern_data"]
