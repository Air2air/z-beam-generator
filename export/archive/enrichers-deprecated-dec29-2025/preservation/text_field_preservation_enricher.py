"""
Text Field Preservation Enricher - Ensures text content fields are preserved in frontmatter.

CRITICAL FIX (Dec 23, 2025): health_effects and other generated text fields were disappearing
during export despite being present in source data. All enrichers/generators preserved the field,
but it was missing from final frontmatter.

Root cause unknown after investigation. This enricher explicitly preserves critical text fields.

Text fields to preserve:
- health_effects (compounds): Generated text content about health impacts
- description (all domains): Primary descriptive text
- caption (all domains): Short summary text
"""

import logging
from typing import Any, Dict

from export.enrichers.base import BaseEnricher

logger = logging.getLogger(__name__)


class TextFieldPreservationEnricher(BaseEnricher):
    """
    Explicitly preserve generated text content fields from source data.
    
    This enricher reloads source data and ensures critical text fields
    that were generated are preserved in frontmatter.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize text field preservation enricher.
        
        Args:
            config: Enricher config with:
                - source_file: Path to source YAML file
                - items_key: Root key in source YAML (e.g., 'compounds')
                - text_fields: List of text field names to preserve
        """
        super().__init__(config)
        
        self.source_file = config.get('source_file')
        self.items_key = config.get('items_key', 'compounds')
        self.text_fields = config.get('text_fields', [])
        
        logger.info(f"Initialized TextFieldPreservationEnricher: {len(self.text_fields)} fields")
    
    def enrich(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preserve text fields from source data.
        
        Args:
            frontmatter: Frontmatter dict to enrich
        
        Returns:
            Frontmatter with text fields preserved
        """
        if not self.text_fields:
            return frontmatter
        
        # Get item ID
        item_id = frontmatter.get('id')
        if not item_id:
            logger.warning("No 'id' field in frontmatter, skipping text preservation")
            return frontmatter
        
        # Load source data
        from pathlib import Path
        import yaml
        
        source_path = Path(self.source_file)
        if not source_path.exists():
            logger.error(f"Source file not found: {source_path}")
            return frontmatter
        
        with open(source_path, 'r') as f:
            source_data = yaml.safe_load(f)
        
        # Get item from source
        items = source_data.get(self.items_key, {})
        item_data = items.get(item_id)
        
        if not item_data:
            logger.warning(f"Item '{item_id}' not found in source {self.items_key}")
            return frontmatter
        
        # Preserve each text field
        preserved_count = 0
        for field in self.text_fields:
            if field in item_data and item_data[field]:
                # Only copy if field is missing or empty in frontmatter
                if field not in frontmatter or not frontmatter[field]:
                    frontmatter[field] = item_data[field]
                    preserved_count += 1
                    logger.debug(f"Preserved {field} for {item_id} ({len(str(item_data[field]))} chars)")
        
        if preserved_count > 0:
            logger.info(f"Preserved {preserved_count} text fields for {item_id}")
        
        return frontmatter
