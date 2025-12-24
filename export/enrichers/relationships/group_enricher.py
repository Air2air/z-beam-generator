"""
Relationship Group Enricher

Groups flat relationships into hierarchical categories:
- technical: Material compatibility, contaminant removal, compound production
- safety: Regulatory compliance, PPE, hazards, exposure limits
- operational: Challenges, applications, equipment, best practices
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class RelationshipGroupEnricher:
    """Groups flat relationships into technical/safety/operational categories."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the enricher.
        
        Args:
            config: Enricher configuration containing relationship_groups mapping
        """
        self.config = config or {}
        self.groups_config = self.config.get('relationship_groups', {})
        
    def enrich(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Group flat relationships into hierarchical structure.
        
        Args:
            entity: Entity data with flat relationships
            
        Returns:
            Updated entity with grouped relationships
        """
        relationships = entity.get('relationships', {})
        if not relationships:
            return entity
        
        # Initialize grouped structure
        grouped = {
            'technical': {},
            'safety': {},
            'operational': {}
        }
        
        # Track which fields were grouped
        grouped_fields = set()
        
        # Categorize fields based on config
        for group_name, field_names in self.groups_config.items():
            if group_name not in grouped:
                logger.warning(f"Unknown group: {group_name}")
                continue
                
            for field in field_names:
                if field in relationships:
                    grouped[group_name][field] = relationships[field]
                    grouped_fields.add(field)
        
        # Keep ungrouped fields at root level (for backwards compatibility)
        ungrouped = {}
        for field, value in relationships.items():
            if field not in grouped_fields:
                ungrouped[field] = value
        
        # Remove empty groups
        grouped = {k: v for k, v in grouped.items() if v}
        
        # Merge grouped and ungrouped
        final_relationships = {**grouped, **ungrouped}
        
        # Update entity
        entity['relationships'] = final_relationships
        
        # Log grouping summary
        if grouped:
            logger.debug(
                f"Grouped relationships: "
                f"technical={len(grouped.get('technical', {}))}, "
                f"safety={len(grouped.get('safety', {}))}, "
                f"operational={len(grouped.get('operational', {}))}"
            )
        
        return entity
    
    def get_name(self) -> str:
        """Return enricher name for logging."""
        return "RelationshipGroupEnricher"
