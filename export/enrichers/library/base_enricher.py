"""
Base enricher class for library-based data expansion.

Implements common functionality for all library enrichers:
- Loading library YAML files
- Relationship parsing
- Override application
- Caching for performance
"""

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class BaseLibraryEnricher:
    """Base class for all library enrichers."""
    
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
        
        for key, value in overrides.items():
            if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                # Recursive merge for nested dicts
                result[key] = self._merge_dicts(result[key], value)
            else:
                # Direct override
                result[key] = value
                
        return result
    
    def _merge_dicts(self, base: Dict, override: Dict) -> Dict:
        """Recursively merge two dictionaries."""
        result = base.copy()
        for key, value in override.items():
            if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                result[key] = self._merge_dicts(result[key], value)
            else:
                result[key] = value
        return result
    
    def enrich(self, relationships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich relationship data with full library entries.
        
        Args:
            relationships: List of relationship references from frontmatter
            
        Returns:
            List of enriched relationship data
        """
        enriched = []
        
        for rel in relationships:
            entry_id = rel.get('id')
            if not entry_id:
                continue
                
            # Get base library entry
            entry_data = self.get_entry(entry_id)
            if not entry_data:
                continue
                
            # Apply any overrides
            overrides = rel.get('overrides', {})
            if overrides:
                entry_data = self.apply_overrides(entry_data, overrides)
                
            enriched.append(entry_data)
            
        return enriched
