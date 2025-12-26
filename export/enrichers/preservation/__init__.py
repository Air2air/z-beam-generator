"""Base class for export enrichers - provides common interface."""

from typing import Any, Dict


class BaseEnricher:
    """Base class for all export enrichers."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize enricher with configuration.
        
        Args:
            config: Enricher-specific configuration dict
        """
        self.config = config
    
    def enrich(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich frontmatter data.
        
        Args:
            data: Frontmatter dict to enrich
        
        Returns:
            Enriched frontmatter dict
        """
        raise NotImplementedError("Subclasses must implement enrich()")
