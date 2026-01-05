"""
Generation-Time Data Enricher

Enriches data at the moment it's generated and saved to source YAML files.
Complies with Core Principle 0.6: "No Build-Time Data Enhancement"

This module adds ALL metadata that was previously added during export:
- Expanded author objects (full registry data)
- Timestamps (datePublished, dateModified)
- Slugs and IDs
- Breadcrumbs (navigation hierarchy)

ARCHITECTURE:
- Called by DomainAdapter.write_component() BEFORE saving to YAML
- Enriches item_data dict in-place
- No fallbacks - fails fast if required data missing

Usage:
    from generation.enrichment.generation_time_enricher import enrich_for_generation
    
    item_data = {...}  # Incomplete data
    enrich_for_generation(item_data, identifier, domain)
    # item_data now has: author expansion, timestamps, id, breadcrumb
"""

import logging
import yaml
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class GenerationTimeEnricher:
    """Enriches data during generation, not at export time."""
    
    def __init__(self):
        """Initialize enricher with author registry."""
        self.authors = self._load_authors()
        
    def _load_authors(self) -> Dict:
        """Load author registry from Authors.yaml."""
        authors_file = Path('data/authors/Authors.yaml')
        if not authors_file.exists():
            raise FileNotFoundError(f"Author registry not found: {authors_file}")
        
        with open(authors_file, 'r') as f:
            data = yaml.safe_load(f)
        
        return data.get('authors', {})
    
    def enrich(self, item_data: Dict[str, Any], identifier: str, domain: str) -> Dict[str, Any]:
        """
        Enrich item data with all metadata (in-place modification).
        
        Args:
            item_data: Item data dict (modified in-place)
            identifier: Item identifier (e.g., "aluminum-laser-cleaning")
            domain: Domain name (e.g., "materials", "contaminants")
            
        Returns:
            Enriched item_data (same object, modified in-place)
        """
        # 1. Expand author (if present)
        if 'author' in item_data:
            item_data['author'] = self._expand_author(item_data['author'])
            logger.debug(f"  ✅ Author expanded for {identifier}")
        
        # 2. Add timestamps
        item_data = self._add_timestamps(item_data)
        logger.debug(f"  ✅ Timestamps added for {identifier}")
        
        # 3. Add id/slug
        item_data = self._add_id(item_data, identifier)
        logger.debug(f"  ✅ ID added for {identifier}")
        
        # 4. Generate breadcrumbs
        item_data = self._add_breadcrumbs(item_data, identifier, domain)
        logger.debug(f"  ✅ Breadcrumbs generated for {identifier}")
        
        return item_data
    
    def _expand_author(self, author_data: Dict) -> Dict:
        """
        Expand author ID to full author registry object.
        
        Replaces author.id with complete author metadata from registry.
        """
        if not isinstance(author_data, dict):
            return author_data
        
        author_id = author_data.get('id')
        if not author_id:
            return author_data
        
        # Look up full author data
        if author_id not in self.authors:
            logger.warning(f"  ⚠️  Author ID {author_id} not found in registry")
            return author_data
        
        registry_author = self.authors[author_id]
        
        # Merge: registry data + any custom overrides in item
        expanded = {**registry_author, **author_data}
        
        # Add author slug if not present
        if 'name' in expanded and 'slug' not in expanded:
            expanded['slug'] = expanded['name'].lower().replace(' ', '-')
        
        return expanded
    
    def _add_timestamps(self, item_data: Dict) -> Dict:
        """Add datePublished and dateModified timestamps."""
        now = datetime.now(timezone.utc).isoformat()
        
        # Only set datePublished if not already present
        if 'datePublished' not in item_data:
            item_data['datePublished'] = now
        
        # Always update dateModified
        item_data['dateModified'] = now
        
        return item_data
    
    def _add_id(self, item_data: Dict, identifier: str) -> Dict:
        """Add id field matching the YAML key."""
        if 'id' not in item_data:
            item_data['id'] = identifier
        
        return item_data
    
    def _add_breadcrumbs(self, item_data: Dict, identifier: str, domain: str) -> Dict:
        """
        Generate breadcrumb navigation array.
        
        Format: [{label: "Home", href: "/"}, {label: "Materials", href: "/materials"}, ...]
        """
        if 'breadcrumb' in item_data:
            return item_data  # Already has breadcrumbs
        
        breadcrumbs = [
            {'label': 'Home', 'href': '/'}
        ]
        
        # Add domain breadcrumb
        domain_label = domain.capitalize()
        breadcrumbs.append({'label': domain_label, 'href': f'/{domain}'})
        
        # Add category if present
        if 'category' in item_data:
            category = item_data['category']
            category_label = category.replace('-', ' ').title()
            breadcrumbs.append({
                'label': category_label,
                'href': f'/{domain}/{category}'
            })
        
        # Add current item (no href for current page)
        if 'name' in item_data:
            breadcrumbs.append({
                'label': item_data['name'],
                'href': None
            })
        
        item_data['breadcrumb'] = breadcrumbs
        
        return item_data


# Singleton instance
_enricher = None


def get_enricher() -> GenerationTimeEnricher:
    """Get singleton enricher instance."""
    global _enricher
    if _enricher is None:
        _enricher = GenerationTimeEnricher()
    return _enricher


def enrich_for_generation(item_data: Dict[str, Any], identifier: str, domain: str) -> Dict[str, Any]:
    """
    Convenience function to enrich data at generation time.
    
    Args:
        item_data: Item data dict (modified in-place)
        identifier: Item identifier
        domain: Domain name
        
    Returns:
        Enriched item_data (same object)
    """
    enricher = get_enricher()
    return enricher.enrich(item_data, identifier, domain)
