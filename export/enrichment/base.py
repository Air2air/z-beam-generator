"""
Base Enricher Class

Abstract base class for all enrichers in the export system.
Part of Export System Consolidation (Phase 2).

Enrichers enhance existing frontmatter by:
- Adding missing fields to linkage entries
- Filling timestamps
- Enriching metadata

Architecture:
- BaseEnricher: Abstract base requiring enrich() method
- Specific enrichers: CompoundLinkageEnricher, TimestampEnricher, etc.

Usage:
    class MyEnricher(BaseEnricher):
        def enrich(self, frontmatter):
            # Add missing data
            frontmatter['new_field'] = value
            return frontmatter
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseEnricher(ABC):
    """
    Abstract base class for all enrichers.
    
    Enrichers modify existing fields in frontmatter.
    Each enricher receives a config dict and implements enrich().
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize enricher with configuration.
        
        Args:
            config: Enricher config from domain YAML
                Common keys: type, field, source, defaults, etc.
        """
        self.config = config
    
    @abstractmethod
    def enrich(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich frontmatter by adding missing data.
        
        Args:
            frontmatter: Input frontmatter dict (modified in place)
        
        Returns:
            Enriched frontmatter (same object, modified)
            
        Raises:
            Can raise exceptions if enrichment fails critically
        """
        pass
