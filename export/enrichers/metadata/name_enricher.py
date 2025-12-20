"""
Name Field Enricher - Ensure name field exists in frontmatter

For domains where the source data doesn't include a 'name' field but uses
the item key as the display name (e.g., Settings), this enricher copies
the id field to the name field.

Created: December 19, 2025
Purpose: Fix settings frontmatter missing name field
"""

import logging
from typing import Any, Dict

from export.enrichers.base import BaseEnricher

logger = logging.getLogger(__name__)


class NameEnricher(BaseEnricher):
    """
    Ensure name field exists in frontmatter.
    
    If the item doesn't have a 'name' field but has an 'id' field,
    copies the id to name. This is common for domains like settings
    where the YAML key is the display name.
    
    Example:
        Settings.yaml:
            Aluminum:  # Key is the display name
                machine_settings: {...}
        
        After enrichment:
            id: Aluminum
            name: Aluminum  # Added by this enricher
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize name enricher.
        
        Args:
            config: Enricher config (no special keys required)
        """
        super().__init__(config)
        logger.info("Initialized NameEnricher")
    
    def enrich(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add name field if missing.
        
        Args:
            frontmatter: Input frontmatter dict
        
        Returns:
            Frontmatter with name field guaranteed to exist
        """
        # If name already exists, nothing to do
        if 'name' in frontmatter and frontmatter['name']:
            return frontmatter
        
        # If original name was preserved (from slugification), use it
        if '_original_name' in frontmatter:
            frontmatter['name'] = frontmatter['_original_name']
            del frontmatter['_original_name']  # Clean up temporary field
            logger.debug(f"Added name field from original name: {frontmatter['name']}")
        # Otherwise, if id exists, copy it to name
        elif 'id' in frontmatter:
            frontmatter['name'] = frontmatter['id']
            logger.debug(f"Added name field from id: {frontmatter['id']}")
        else:
            logger.warning("Frontmatter missing both 'name' and 'id' fields")
        
        return frontmatter
