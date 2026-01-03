"""
Page Title Field Enricher - Generate page_title field for frontmatter

For domains that need a human-readable page title field for H1 display and SEO.
Generates page_title from name field using domain-specific formatting.

Created: December 20, 2025
Updated: December 29, 2025 - Migrated from 'title' to 'page_title'
Purpose: Add consistent page_title fields across all domains
"""

import logging
from typing import Any, Dict

from export.enrichers.base import BaseEnricher

logger = logging.getLogger(__name__)


class TitleEnricher(BaseEnricher):
    """
    Generate page_title field from name field.
    
    Page title generation strategies by domain:
    - materials: "{Name} Laser Cleaning" (e.g., "Aluminum Laser Cleaning")
    - contaminants: Uses existing page_title if present, otherwise generates from name
    - compounds: Uses name with display_name if available (e.g., "Acetaldehyde (C₂H₄O)")
    - settings: "{Name} Settings" (e.g., "Aluminum Settings")
    
    Config options:
        template: Page title template string with {name} placeholder (default: "{name}")
        use_display_name: For compounds, prefer display_name over name (default: False)
        skip_if_exists: Don't overwrite existing page_title field (default: True)
    
    Example:
        enrichments:
        - type: title
          template: "{name} Laser Cleaning"
          skip_if_exists: true
    
    Note: As of December 29, 2025, this enricher generates 'page_title' field.
          The deprecated 'title' field has been migrated to 'page_title'.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize title enricher.
        
        Args:
            config: Enricher config dict with:
                - template (str): Title template with {name} placeholder
                - use_display_name (bool): Use display_name for compounds
                - skip_if_exists (bool): Don't overwrite existing title
        """
        super().__init__(config)
        self.template = config.get('template', '{name}')
        self.use_display_name = config.get('use_display_name', False)
        self.skip_if_exists = config.get('skip_if_exists', True)
        logger.info(f"Initialized TitleEnricher with template: {self.template}")
    
    def enrich(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate page_title field.
        
        Args:
            frontmatter: Input frontmatter dict
        
        Returns:
            Frontmatter with page_title field added
        """
        # Skip if page_title exists and skip_if_exists is True
        if self.skip_if_exists and 'page_title' in frontmatter and frontmatter['page_title']:
            logger.debug(f"Page title already exists, skipping: {frontmatter['page_title']}")
            return frontmatter
        
        # Determine source field for page_title generation
        if self.use_display_name and 'display_name' in frontmatter:
            source_name = frontmatter['display_name']
            logger.debug(f"Using display_name for page_title: {source_name}")
        elif 'name' in frontmatter:
            source_name = frontmatter['name']
        else:
            logger.warning("No 'name' or 'display_name' field found for page_title generation")
            return frontmatter
        
        # Generate page_title from template
        page_title = self.template.format(name=source_name)
        frontmatter['page_title'] = page_title
        
        logger.debug(f"Generated page_title: {page_title}")
        
        return frontmatter
