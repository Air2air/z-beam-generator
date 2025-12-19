"""
Slug Field Enricher
===================

Adds missing 'slug' fields to domain linkage entries.

Purpose:
- Ensures all linkage entries have Schema 5.0.0-compliant 'slug' field
- Extracts slug from existing URL field (last path segment)
- Works on nested arrays inside relationships

Architecture:
- Runs as part of enrichment phase (before generators)
- Operates on existing relationships structure
- Adds slug field only if missing (preserves existing slugs)
"""

import logging
from pathlib import Path
from typing import Any, Dict, List

from export.enrichers.base import BaseEnricher

logger = logging.getLogger(__name__)


class DomainLinkagesSlugEnricher(BaseEnricher):
    """
    Add slug fields to domain linkage entries.
    
    Processes all linkage types in relationships:
    - related_contaminants
    - related_materials
    - related_compounds
    - related_settings
    - produces_compounds
    - removes_contaminants
    - etc.
    
    For each entry without a slug field, extracts slug from URL.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize slug enricher.
        
        Args:
            config: Empty config (no configuration needed)
        """
        super().__init__(config)
    
    def enrich(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add slug fields to all domain linkage entries.
        
        Args:
            frontmatter: Input frontmatter dict
        
        Returns:
            Enriched frontmatter with slug fields added
        """
        # AGGRESSIVE LOGGING
        print("🔍 DomainLinkagesSlugEnricher.enrich() CALLED!")
        print(f"🔍 Frontmatter keys: {list(frontmatter.keys())}")
        
        # Check if relationships exists
        if 'relationships' not in frontmatter:
            print("❌ NO relationships in frontmatter!")
            logger.debug("No relationships found, skipping slug enrichment")
            return frontmatter
        
        print("✅ relationships FOUND in frontmatter")
        relationships = frontmatter['relationships']
        if not isinstance(relationships, dict):
            print(f"❌ relationships is not a dict! Type: {type(relationships)}")
            logger.warning("relationships is not a dict, skipping slug enrichment")
            return frontmatter
        
        print(f"✅ relationships is a dict with keys: {list(relationships.keys())}")
        
        # Track changes for logging
        total_processed = 0
        total_added = 0
        
        # Process each linkage type
        for linkage_type, linkage_list in relationships.items():
            print(f"📋 Processing linkage_type: {linkage_type}, list length: {len(linkage_list) if isinstance(linkage_list, list) else 'NOT A LIST'}")
            if not isinstance(linkage_list, list):
                continue
            
            for entry in linkage_list:
                if not isinstance(entry, dict):
                    continue
                
                total_processed += 1
                
                # Skip if slug already exists
                if 'slug' in entry:
                    continue
                
                # Extract slug from URL
                url = entry.get('url', '')
                if url:
                    slug = self._extract_slug_from_url(url)
                    if slug:
                        # DISABLED: Per Phase 1 migration, slug fields should not exist in relationships
                        # entry['slug'] = slug
                        # total_added += 1
                        # print(f"✅ Added slug '{slug}' to {linkage_type} entry (id={entry.get('id')})")  
                        # logger.debug(f"Added slug '{slug}' to {linkage_type} entry (id={entry.get('id')})")  
                        pass  # Slug enrichment disabled per FRONTMATTER_FORMATTING_SPECIFICATION Phase 1
        return frontmatter
    
    def _extract_slug_from_url(self, url: str) -> str:
        """
        Extract slug from URL (last path segment).
        
        Args:
            url: URL like '/materials/metal/non-ferrous/aluminum'
        
        Returns:
            Slug like 'aluminum'
        """
        if not url:
            return ''
        
        # Remove trailing slash
        url = url.rstrip('/')
        
        # Get last segment
        parts = url.split('/')
        if parts:
            slug = parts[-1]
            return slug
        
        return ''
