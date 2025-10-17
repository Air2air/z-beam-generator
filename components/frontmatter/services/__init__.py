"""
Frontmatter generation services.

Extracted services for specialized frontmatter generation tasks:
- PropertyDiscoveryService: Determines which properties to research
- PropertyResearchService: Coordinates property value research
- TemplateService: Handles formatting and template conversions
- PipelineProcessService: Handles environmental, regulatory, and application discovery
"""

from components.frontmatter.services.property_discovery_service import PropertyDiscoveryService

__all__ = ['PropertyDiscoveryService']
