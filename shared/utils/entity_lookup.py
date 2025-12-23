"""
Entity Lookup Utilities

Provides utilities for looking up full entity data from source YAML files
based on entity ID and type.

This supports the new relationship structure where items contain only
{id, entity_type} and full entity data must be loaded via lookup.

Usage:
    from shared/utils/entity_lookup import EntityLookup
    
    lookup = EntityLookup()
    entity = lookup.get_entity('aluminum-laser-cleaning', 'material')
    print(entity['name'])  # "Aluminum"
    print(entity['full_path'])  # "/materials/metal/non-ferrous/aluminum-laser-cleaning"
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from functools import lru_cache


# Domain source file mappings
DOMAIN_SOURCES = {
    'material': {
        'file': Path('data/materials/Materials.yaml'),
        'key': 'materials',
    },
    'compound': {
        'file': Path('data/compounds/Compounds.yaml'),
        'key': 'compounds',
    },
    'contaminant': {
        'file': Path('data/contaminants/Contaminants.yaml'),
        'key': 'contamination_patterns',
    },
    'setting': {
        'file': Path('data/settings/Settings.yaml'),
        'key': 'settings',
    },
}


class EntityLookup:
    """
    Lookup utility for loading entity data from source YAML files.
    
    Provides caching for performance and supports all entity types.
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize entity lookup.
        
        Args:
            base_path: Base path for data files (default: current directory)
        """
        self.base_path = base_path or Path('.')
        self._data_cache: Dict[str, Dict] = {}
    
    @lru_cache(maxsize=128)
    def _load_domain_data(self, entity_type: str) -> Dict[str, Any]:
        """
        Load data for a domain (cached).
        
        Args:
            entity_type: Entity type (material, compound, contaminant, setting)
        
        Returns:
            Dict of all entities in that domain
        
        Raises:
            ValueError: If entity type unknown
            FileNotFoundError: If source file not found
        """
        if entity_type not in DOMAIN_SOURCES:
            raise ValueError(
                f"Unknown entity type '{entity_type}'. "
                f"Must be one of: {', '.join(DOMAIN_SOURCES.keys())}"
            )
        
        source_config = DOMAIN_SOURCES[entity_type]
        file_path = self.base_path / source_config['file']
        
        if not file_path.exists():
            raise FileNotFoundError(f"Source file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return data[source_config['key']]
    
    def get_entity(self, entity_id: str, entity_type: str) -> Optional[Dict[str, Any]]:
        """
        Look up entity by ID and type.
        
        Args:
            entity_id: Entity ID (e.g., 'aluminum-laser-cleaning')
            entity_type: Entity type (material, compound, contaminant, setting)
        
        Returns:
            Entity data dict, or None if not found
        
        Example:
            lookup = EntityLookup()
            material = lookup.get_entity('aluminum-laser-cleaning', 'material')
            if material:
                print(material['name'])
                print(material['full_path'])
        """
        try:
            domain_data = self._load_domain_data(entity_type)
            return domain_data.get(entity_id)
        except (ValueError, FileNotFoundError) as e:
            print(f"Warning: Failed to lookup {entity_id}: {e}")
            return None
    
    def get_entity_card(
        self,
        entity_id: str,
        entity_type: str,
        context: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get card data for entity with context fallback.
        
        Args:
            entity_id: Entity ID
            entity_type: Entity type
            context: Optional context (e.g., 'contamination_context')
        
        Returns:
            Card variant dict, or None if not found
        
        Example:
            card = lookup.get_entity_card('aluminum-laser-cleaning', 'material', 'contamination_context')
            # Returns card.contamination_context if exists, else card.default
        """
        entity = self.get_entity(entity_id, entity_type)
        if not entity or 'card' not in entity:
            return None
        
        card = entity['card']
        
        # Try context-specific variant first
        if context and context in card:
            return card[context]
        
        # Fall back to default
        return card.get('default')
    
    def get_entity_url(self, entity_id: str, entity_type: str) -> Optional[str]:
        """
        Get URL for entity (from full_path).
        
        Args:
            entity_id: Entity ID
            entity_type: Entity type
        
        Returns:
            Full path (URL), or None if not found
        
        Example:
            url = lookup.get_entity_url('aluminum-laser-cleaning', 'material')
            # Returns: "/materials/metal/non-ferrous/aluminum-laser-cleaning"
        """
        entity = self.get_entity(entity_id, entity_type)
        if not entity:
            return None
        
        return entity.get('full_path')
    
    def get_entity_name(self, entity_id: str, entity_type: str) -> Optional[str]:
        """
        Get display name for entity.
        
        Args:
            entity_id: Entity ID
            entity_type: Entity type
        
        Returns:
            Display name, or None if not found
        
        Example:
            name = lookup.get_entity_name('aluminum-laser-cleaning', 'material')
            # Returns: "Aluminum"
        """
        entity = self.get_entity(entity_id, entity_type)
        if not entity:
            return None
        
        return entity.get('name', entity_id)
    
    def batch_get_entities(
        self,
        items: list[Dict[str, str]]
    ) -> list[Optional[Dict[str, Any]]]:
        """
        Look up multiple entities at once.
        
        Args:
            items: List of dicts with 'id' and 'entity_type' keys
        
        Returns:
            List of entity dicts (same order as input, None for not found)
        
        Example:
            items = [
                {'id': 'aluminum-laser-cleaning', 'entity_type': 'material'},
                {'id': 'pahs-compound', 'entity_type': 'compound'}
            ]
            entities = lookup.batch_get_entities(items)
        """
        results = []
        for item in items:
            entity = self.get_entity(item['id'], item['entity_type'])
            results.append(entity)
        return results
    
    def clear_cache(self):
        """Clear the internal data cache."""
        self._load_domain_data.cache_clear()
        self._data_cache.clear()


# Convenience singleton instance
_default_lookup = None

def get_default_lookup() -> EntityLookup:
    """Get default EntityLookup singleton."""
    global _default_lookup
    if _default_lookup is None:
        _default_lookup = EntityLookup()
    return _default_lookup


# Convenience functions using default lookup
def lookup_entity(entity_id: str, entity_type: str) -> Optional[Dict[str, Any]]:
    """Convenience function to lookup entity using default instance."""
    return get_default_lookup().get_entity(entity_id, entity_type)


def lookup_entity_card(
    entity_id: str,
    entity_type: str,
    context: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Convenience function to get entity card using default instance."""
    return get_default_lookup().get_entity_card(entity_id, entity_type, context)


def lookup_entity_url(entity_id: str, entity_type: str) -> Optional[str]:
    """Convenience function to get entity URL using default instance."""
    return get_default_lookup().get_entity_url(entity_id, entity_type)


def lookup_entity_name(entity_id: str, entity_type: str) -> Optional[str]:
    """Convenience function to get entity name using default instance."""
    return get_default_lookup().get_entity_name(entity_id, entity_type)
