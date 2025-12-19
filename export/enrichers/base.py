"""
Unified Base Classes for All Enrichers

Consolidated from:
- export/enrichment/base.py (BaseEnricher)
- export/enrichers/base_enricher.py (BaseLibraryEnricher)

Architecture:
- BaseEnricher: For linkage and metadata enrichers
- BaseLibraryEnricher: For library data enrichers

Part of Export System Consolidation Phase 3.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pathlib import Path
import yaml
from functools import lru_cache


class BaseEnricher(ABC):
    """
    Abstract base class for linkage and metadata enrichers.
    
    Enrichers modify existing fields in frontmatter by:
    - Adding missing fields to linkage entries
    - Filling timestamps
    - Enriching metadata
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


class BaseLibraryEnricher:
    """
    Base class for library-based data enrichers.
    
    Implements common functionality:
    - Loading library YAML files
    - Relationship parsing
    - Override application
    - Caching for performance
    """
    
    def __init__(self, library_file: Path):
        """
        Initialize enricher with library file path.
        
        Args:
            library_file: Path to the YAML library file
        """
        self.library_file = library_file
        self._library_data = None
        
    @property
    def library_data(self) -> Dict[str, Any]:
        """Lazy load library data."""
        if self._library_data is None:
            self._library_data = self._load_library()
        return self._library_data
    
    def _load_library(self) -> Dict[str, Any]:
        """Load library YAML file."""
        if not self.library_file.exists():
            raise FileNotFoundError(f"Library file not found: {self.library_file}")
            
        with open(self.library_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def get_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a library entry by ID.
        
        Args:
            entry_id: Unique identifier for the library entry
            
        Returns:
            Library entry dict or None if not found
        """
        # Must be implemented by subclass - library structure varies
        raise NotImplementedError("Subclass must implement get_entry()")
    
    def apply_overrides(
        self,
        base_data: Dict[str, Any],
        overrides: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply overrides to base library data.
        
        Args:
            base_data: Original library entry data
            overrides: Override values from relationship
            
        Returns:
            Merged data with overrides applied
        """
        result = base_data.copy()
        result.update(overrides)
        return result
    
    def enrich(self, frontmatter: Dict[str, Any], relationships: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Enrich frontmatter using library relationships.
        
        Args:
            frontmatter: Target frontmatter dict
            relationships: List of relationship dicts with library references
            
        Returns:
            Enriched frontmatter
        """
        # Must be implemented by subclass
        raise NotImplementedError("Subclass must implement enrich()")
