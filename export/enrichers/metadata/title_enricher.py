"""
Title Field Enricher - Generate title field for frontmatter

For domains that need a human-readable title field for H1 display.
Generates title from name field using domain-specific formatting.

Created: December 20, 2025
Purpose: Add consistent title fields across all domains
"""

import logging
from typing import Any, Dict

from export.enrichers.base import BaseEnricher

logger = logging.getLogger(__name__)


class TitleEnricher(BaseEnricher):
    """
    Generate title field from name field.
    
    Title generation strategies by domain:
    - materials: "{Name} Laser Cleaning" (e.g., "Aluminum Laser Cleaning")
    - contaminants: Uses existing title if present, otherwise generates from name
    - compounds: Uses name with display_name if available (e.g., "Acetaldehyde (C₂H₄O)")
    - settings: "{Name} Settings" (e.g., "Aluminum Settings")
    
    Config options:
        template: Title template string with {name} placeholder (default: "{name}")
        use_display_name: For compounds, prefer display_name over name (default: False)
        skip_if_exists: Don't overwrite existing title field (default: True)
    
    Example:
        enrichments:
        - type: title
          template: "{name} Laser Cleaning"
          skip_if_exists: true
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
        Generate and add title field.
        
        Args:
            frontmatter: Input frontmatter dict
        
        Returns:
            Frontmatter with title field added
        """
        # Skip if title exists and skip_if_exists is True
        if self.skip_if_exists and 'title' in frontmatter and frontmatter['title']:
            logger.debug(f"Title already exists, skipping: {frontmatter['title']}")
            return frontmatter
        
        # Determine source field for title generation
        if self.use_display_name and 'display_name' in frontmatter:
            source_name = frontmatter['display_name']
            logger.debug(f"Using display_name for title: {source_name}")
        elif 'name' in frontmatter:
            source_name = frontmatter['name']
        else:
            logger.warning("No 'name' or 'display_name' field found for title generation")
            return frontmatter
        
        # Generate title from template
        title = self.template.format(name=source_name)
        frontmatter['title'] = title
        
        logger.debug(f"Generated title: {title}")
        
        return frontmatter
