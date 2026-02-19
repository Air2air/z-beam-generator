"""Backward-compatibility shim for compounds data loader import path.

Legacy imports expected:
    from domains.compounds.data_loader_v2 import CompoundsDataLoader

Canonical location:
    domains.compounds.loaders.data_loader_v2
"""

from domains.compounds.loaders.data_loader_v2 import *  # noqa: F401,F403
