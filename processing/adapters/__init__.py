"""
Data Source Adapters

Abstracts data source access (Materials.yaml, Regions.yaml, etc.)
to enable orchestrator reuse across different content types.
"""

from .base import DataSourceAdapter
from .materials_adapter import MaterialsAdapter

__all__ = ['DataSourceAdapter', 'MaterialsAdapter']
