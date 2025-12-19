"""
Library Enrichment Integration for Universal Exporter

Integrates modular library system with frontmatter generation.
Processes relationships.<library_type> and enriches with full library data.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from .enricher_registry import EnricherRegistry

logger = logging.getLogger(__name__)


class LibraryEnrichmentProcessor:
    """Processes library enrichments during frontmatter generation."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize with domain configuration.
        
        Args:
            config: Domain config with library_enrichments section
        """
        self.config = config
        self.enabled = config.get('library_enrichments', {}).get('enabled', False)
        self.enrichments = config.get('library_enrichments', {}).get('enrichments', [])
        
        # Initialize enrichers
        self.enrichers = {}
        if self.enabled:
            self._initialize_enrichers()
    
    def _initialize_enrichers(self):
        """Initialize all enrichers needed for this domain."""
        for enrich_config in self.enrichments:
            library_type = enrich_config.get('type')
            if library_type:
                enricher = EnricherRegistry.get_enricher(library_type)
                if enricher:
                    self.enrichers[library_type] = enricher
                else:
                    logger.warning(f"Enricher not found for library type: {library_type}")
    
    def process_item(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process all library enrichments for an item.
        
        Args:
            item_data: Source item data with relationships
            
        Returns:
            Enriched item data with library details added
        """
        if not self.enabled:
            logger.debug(f"Library enrichment DISABLED (enabled={self.enabled})")
            return item_data
        
        logger.debug(f"Library processor ENABLED, processing {len(self.enrichments)} enrichment configs")
            
        enriched = item_data.copy()
        relationships = item_data.get('relationships', {})
        
        logger.debug(f"Item has relationships: {bool(relationships)}")
        if relationships:
            logger.debug(f"Relationship keys: {list(relationships.keys())}")
        
        for enrich_config in self.enrichments:
            library_type = enrich_config.get('type')
            relationship_field = enrich_config.get('relationship_field', '').replace('relationships.', '')
            output_field = enrich_config.get('output_field')
            
            logger.debug(f"   Processing config: {library_type} -> {output_field}")
            
            if not all([library_type, relationship_field, output_field]):
                logger.warning(f"   ⚠️  Incomplete config: type={library_type}, field={relationship_field}, output={output_field}")
                continue
                
            # Get relationship data
            rel_data = relationships.get(relationship_field, [])
            if not rel_data:
                logger.debug(f"   ⚠️  No data in relationships.{relationship_field}")
                continue
                
            # Ensure it's a list
            if not isinstance(rel_data, list):
                rel_data = [rel_data]
            
            # Debug: Log what we're passing
            logger.debug(f"Processing {library_type}: {type(rel_data)} with {len(rel_data)} entries")
            if rel_data:
                logger.debug(f"  First entry type: {type(rel_data[0])}, value: {rel_data[0]}")
            
            # Get enricher
            enricher = self.enrichers.get(library_type)
            if not enricher:
                logger.warning(f"   ⚠️  No enricher found for {library_type}")
                continue
                
            # Enrich data
            try:
                enriched_data = enricher.enrich(rel_data)
                if enriched_data:
                    enriched[output_field] = enriched_data
                    logger.debug(f"✅ Enriched {output_field} with {len(enriched_data)} entries")
                else:
                    logger.warning(f"   ⚠️  Enricher returned empty data for {library_type}")
            except Exception as e:
                logger.error(f"Error enriching {library_type}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                
        return enriched
    
    def get_enrichment_summary(self, item_data: Dict[str, Any]) -> Dict[str, int]:
        """
        Get summary of what would be enriched.
        
        Args:
            item_data: Source item data
            
        Returns:
            Dict of library_type -> count of entries that would be enriched
        """
        summary = {}
        
        if not self.enabled:
            return summary
            
        relationships = item_data.get('relationships', {})
        
        for enrich_config in self.enrichments:
            library_type = enrich_config.get('type')
            relationship_field = enrich_config.get('relationship_field', '').replace('relationships.', '')
            
            rel_data = relationships.get(relationship_field, [])
            if not isinstance(rel_data, list):
                rel_data = [rel_data] if rel_data else []
                
            summary[library_type] = len(rel_data)
            
        return summary
