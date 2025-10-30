"""
Frontmatter generation services.

Extracted services for specialized frontmatter generation tasks:
- PropertyManager: Unified property lifecycle management (replaces PropertyDiscoveryService + PropertyResearchService)
- TemplateService: Handles formatting and template conversions
- PipelineProcessService: Handles environmental, regulatory, and application discovery
"""

from components.frontmatter.services.property_manager import PropertyManager
from components.frontmatter.services.template_service import TemplateService
from components.frontmatter.services.pipeline_process_service import PipelineProcessService

__all__ = [
    'PropertyManager',
    'TemplateService',
    'PipelineProcessService'
]
