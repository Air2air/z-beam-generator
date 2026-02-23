"""
Generation-Time Metadata Provider

Adds metadata at the moment data is generated and saved to source YAML files.
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
    from generation.context.generation_metadata import enrich_for_generation
    
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


class GenerationMetadata:
    """Provides generation-time metadata, not at export time."""
    
    def __init__(self):
        """Initialize metadata provider with author registry."""
        self.authors = self._load_authors()
        
    def _load_authors(self) -> Dict:
        """Load author registry from Authors.yaml."""
        authors_file = Path('data/authors/Authors.yaml')
        if not authors_file.exists():
            raise FileNotFoundError(f"Author registry not found: {authors_file}")
        
        with open(authors_file, 'r') as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError("Authors.yaml must parse to a dictionary")
        if 'authors' not in data:
            raise KeyError("Authors.yaml missing required top-level key: 'authors'")
        if not isinstance(data['authors'], dict):
            raise TypeError("Authors.yaml key 'authors' must be a dictionary")

        return data['authors']
    
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
        # 1. Extract authorId (V6 Schema: reference only, not full object)
        if 'author' in item_data:
            item_data['authorId'] = self._extract_author_id(item_data['author'])
            del item_data['author']  # V6: Remove full author object
            logger.debug(f"  ✅ Author ID extracted for {identifier} (V6 format)")
        
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
    
    def _extract_author_id(self, author_data) -> int:
        """
        Extract author ID from author data (V6 Schema).
        
        Source Data Architecture:
        - Materials.yaml etc.: Store authorId (numeric reference: 1-4)
        - Export enriches to full author object for frontmatter
        - Frontend uses full author object from frontmatter
        
        Args:
            author_data: Either dict with 'id' key or direct int
            
        Returns:
            Author ID (1-4)
        """
        if isinstance(author_data, dict):
            author_id = author_data.get('id')
        elif isinstance(author_data, int):
            author_id = author_data
        else:
            author_id = None
        
        if not author_id:
            raise ValueError(f"Invalid author data: {author_data}. Must have 'id' field.")
        
        return author_id
    
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
        
        # Add category if present (skip for applications)
        if domain != 'applications' and 'category' in item_data:
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
_metadata_provider = None


def get_metadata_provider() -> GenerationMetadata:
    """Get singleton metadata provider instance."""
    global _metadata_provider
    if _metadata_provider is None:
        _metadata_provider = GenerationMetadata()
    return _metadata_provider


def enrich_for_generation(item_data: Dict[str, Any], identifier: str, domain: str) -> Dict[str, Any]:
    """
    Convenience function to add generation-time metadata.
    
    Args:
        item_data: Item data dict (modified in-place)
        identifier: Item identifier
        domain: Domain name
        
    Returns:
        Enhanced item_data (same object)
    """
    provider = get_metadata_provider()
    return provider.enrich(item_data, identifier, domain)
