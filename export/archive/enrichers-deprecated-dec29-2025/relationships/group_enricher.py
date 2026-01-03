"""
Relationship Group Enricher

Handles relationship categorization for frontmatter export.

NEW STRUCTURE (Dec 29, 2025):
- identity: Intrinsic properties (chemical/physical/composition)
- interactions: Cross-references (contaminated_by, affects_materials, etc.)
- operational: Practical usage (applications, challenges, parameters)
- safety: Health & compliance (regulatory, PPE, hazards, exposure)
- environmental: Environmental impact (toxicity, biodegradability)
- detection_monitoring: Detection methods and measurement
- visual: Visual characteristics (appearance data)
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class RelationshipGroupEnricher:
    """Pass through modern categorized relationships or group legacy flat structure."""
    
    # New semantic categories (Dec 29, 2025)
    MODERN_CATEGORIES = {
        'identity', 'interactions', 'operational', 'safety', 
        'environmental', 'detection_monitoring', 'visual'
    }
    
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
        Handle relationship categorization.
        
        If relationships are already categorized (using modern structure),
        pass them through as-is. Otherwise, group flat relationships.
        
        Args:
            entity: Entity data with relationships
            
        Returns:
            Updated entity with properly categorized relationships
        """
        relationships = entity.get('relationships', {})
        if not relationships:
            return entity
        
        # Check if already using modern categorized structure
        if self._is_modern_structure(relationships):
            logger.debug("Relationships already categorized with modern structure")
            return entity
        
        # Legacy path: group flat relationships
        return self._group_flat_relationships(entity, relationships)
    
    def _is_modern_structure(self, relationships: Dict[str, Any]) -> bool:
        """Check if relationships use modern categorized structure."""
        # If any top-level key is a modern category, assume it's categorized
        for key in relationships.keys():
            if key in self.MODERN_CATEGORIES:
                return True
        return False
    
    def _group_flat_relationships(self, entity: Dict[str, Any], 
                                  relationships: Dict[str, Any]) -> Dict[str, Any]:
        """
        Group flat relationships (legacy support).
        
        Args:
            entity: Entity data
            relationships: Flat relationships dict
            
        Returns:
            Updated entity with grouped relationships
        """
        # Initialize grouped structure (legacy categories)
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

    
    def get_name(self) -> str:
        """Return enricher name for logging."""
        return "RelationshipGroupEnricher"
