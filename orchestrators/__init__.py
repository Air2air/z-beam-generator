"""
Orchestrators

Integration layer that coordinates across multiple domains.
Orchestrators are ALLOWED to import from multiple domains
as they serve as the integration points.

Per DOMAIN_INDEPENDENCE_POLICY.md:
"Orchestrators Can Access Multiple Domains - ALLOWED:
 Orchestrators coordinate across domains"
"""

from .data_orchestrator import (
    load_complete_materials_data,
    merge_materials_settings,
    DataOrchestrationError
)

__all__ = [
    'load_complete_materials_data',
    'merge_materials_settings',
    'DataOrchestrationError',
]
