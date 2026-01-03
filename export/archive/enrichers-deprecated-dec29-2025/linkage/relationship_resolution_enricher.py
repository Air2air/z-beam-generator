"""
Relationship Resolution Enricher

Integrates RelationshipResolver into export pipeline to hydrate minimal 
relationship references with full page data.

This enricher:
1. Detects relationship arrays with minimal references (id + context only)
2. Resolves each reference to full relationship object (id, title, url, category, etc.)
3. Preserves context-specific fields (frequency, severity, typical_context)
4. Returns enriched frontmatter with full relationship objects

Part of Relationship Normalization Architecture (Phase 1).
"""

import logging
from typing import Any, Dict, List
from pathlib import Path

from export.enrichers.base import BaseEnricher
from shared.relationships.resolver import RelationshipResolver

logger = logging.getLogger(__name__)


class RelationshipResolutionEnricher(BaseEnricher):
    """
    Enriches minimal relationship references with full page data.
    
    Converts:
        {'id': 'rust', 'frequency': 'common'}
    To:
        {'id': 'rust', 'title': 'Metal Oxidation / Rust', 
         'url': '/contaminants/...', 'category': 'metal-oxide',
         'subcategory': 'oxidation', 'frequency': 'common'}
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize enricher with configuration.
        
        Args:
            config: Enricher config from domain YAML with keys:
                - relationships: Maps relationship field names to target domains
                    Example: {
                        'applicable_contaminants': 'contaminants',
                        'produced_by_contaminants': 'contaminants',
                        'related_materials': 'materials'
                    }
                - data_dir: Path to data directory (default: 'data')
        """
        super().__init__(config)
        data_dir = config.get('data_dir', 'data')
        self.resolver = RelationshipResolver(data_dir)
        self.relationship_config = config.get('relationships', {})
        
    @property
    def name(self) -> str:
        return "RelationshipResolution"
        
    def enrich(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve all minimal relationship references to full objects.
        
        Args:
            frontmatter: Frontmatter dict with relationships field
            
        Returns:
            Enriched frontmatter with resolved relationships
        """
        if 'relationships' not in frontmatter:
            return frontmatter
            
        relationships = frontmatter['relationships']
        resolved_count = 0
        
        # Iterate through configured relationship fields
        for rel_field, target_domain in self.relationship_config.items():
            if rel_field not in relationships:
                continue
                
            rel_refs = relationships[rel_field]
            
            # Skip if not a list or empty
            if not isinstance(rel_refs, list) or not rel_refs:
                continue
                
            # Check if these are minimal references (need resolution)
            if self._needs_resolution(rel_refs):
                try:
                    # Resolve all references
                    resolved = self.resolver.resolve_relationships(
                        rel_refs, 
                        target_domain
                    )
                    relationships[rel_field] = resolved
                    resolved_count += len(resolved)
                    logger.debug(
                        f"Resolved {len(resolved)} {rel_field} references "
                        f"from {target_domain}"
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to resolve {rel_field} references: {e}",
                        exc_info=True
                    )
                    # Keep original references if resolution fails
                    
        if resolved_count > 0:
            logger.info(f"Resolved {resolved_count} total relationship references")
            
        return frontmatter
        
    def _needs_resolution(self, rel_list: List[Dict[str, Any]]) -> bool:
        """
        Check if relationship list contains minimal references (needs resolution).
        
        A relationship needs resolution if it has 'id' but missing derived fields
        like 'title', 'url', 'category'.
        
        Args:
            rel_list: List of relationship dicts
            
        Returns:
            True if list contains minimal references, False if already full objects
        """
        if not rel_list:
            return False
            
        # Check first item as sample
        first_rel = rel_list[0]
        
        # Must have 'id' to be a reference
        if 'id' not in first_rel:
            return False
            
        # If missing derived fields, needs resolution
        derived_fields = ['title', 'url', 'category']
        missing_fields = [f for f in derived_fields if f not in first_rel]
        
        # If missing 2+ derived fields, definitely needs resolution
        # (allows for occasional missing field like 'url')
        return len(missing_fields) >= 2


def create_relationship_resolution_enricher(
    domain_config: Dict[str, Any]
) -> RelationshipResolutionEnricher:
    """
    Factory function to create enricher from domain config.
    
    Expected config format:
        enrichments:
          - type: relationship_resolution
            config:
              relationships:
                applicable_contaminants: contaminants
                produced_by_contaminants: contaminants
                related_materials: materials
    
    Args:
        domain_config: Full domain config dict
        
    Returns:
        Configured RelationshipResolutionEnricher instance
        
    Raises:
        KeyError: If required config keys missing
    """
    # Extract relationship config from enrichments
    enrichments = domain_config.get('enrichments', [])
    
    for enrichment in enrichments:
        if enrichment.get('type') == 'relationship_resolution':
            relationship_config = enrichment.get('config', {}).get('relationships', {})
            return RelationshipResolutionEnricher(relationship_config)
            
    # If not found in config, return enricher with empty config (no-op)
    logger.warning(
        "No relationship_resolution enrichment config found, "
        "enricher will be inactive"
    )
    return RelationshipResolutionEnricher({})
