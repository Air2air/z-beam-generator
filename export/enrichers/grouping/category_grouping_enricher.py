"""
Category Grouping Enricher - Groups relationship items by category with section metadata.

This enricher transforms flat relationship lists into categorized groups:
- Groups items by their category field from source data
- Adds _section metadata (title, description, icon) per group
- Preserves all existing item metadata
- Reduces visual clutter by organizing 50+ items into 8-10 categories

Example transformation:
    Before:
        relationships:
          contaminated_by:
            presentation: card
            items:
              - id: rust-contamination
              - id: paint-contamination
              - id: oil-contamination
              # ... 46 more flat items
    
    After:
        relationships:
          contaminated_by:
            presentation: card
            _section:
              title: "Common Contaminants"
              description: "Types of contamination found on this material"
            groups:
              - category: "oxidation"
                _section:
                  title: "Oxidation & Corrosion"
                  description: "Rust, tarnish, and oxide layers"
                items:
                  - id: rust-contamination
              - category: "inorganic-coating"
                _section:
                  title: "Coatings & Paint"
                items:
                  - id: paint-contamination
              - category: "organic-residue"
                _section:
                  title: "Organic Residues"
                items:
                  - id: oil-contamination

Compatible with Card Restructure (December 2025).
"""

import logging
from typing import Dict, Any, List, Optional
from collections import defaultdict
import yaml

from export.enrichers.base import BaseEnricher

logger = logging.getLogger(__name__)


class CategoryGroupingEnricher(BaseEnricher):
    """
    Enricher that groups relationship items by category with section metadata.
    
    Configuration (in export/config/{domain}.yaml):
        - type: category_grouping
          module: export.enrichers.grouping.category_grouping_enricher
          class: CategoryGroupingEnricher
          relationships:
            contaminated_by:
              target_domain: contaminants
              source_file: data/contaminants/Contaminants.yaml
              source_key: contamination_patterns
              group_by: category
              main_section:
                title: "Common Contaminants"
                description: "Types of contamination found on this material"
              category_metadata:
                oxidation:
                  title: "Oxidation & Corrosion"
                  description: "Rust, tarnish, and oxide layers"
                organic-residue:
                  title: "Organic Residues"
                  description: "Adhesives, oils, greases, and polymers"
    
    This enricher should run LATE in the pipeline (after relationship enrichment
    is complete and items have presentation wrappers).
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize enricher.
        
        Args:
            config: Enricher config dict with 'relationships' key
        """
        super().__init__(config)
        self.relationship_configs = config.get('relationships', {})
        self.source_data_cache = {}  # Cache loaded source files
        logger.info(f"Initialized CategoryGroupingEnricher for {len(self.relationship_configs)} relationships")
    
    def _load_source_data(self, source_file: str, source_key: str) -> Dict[str, Any]:
        """
        Load and cache source data file.
        
        Args:
            source_file: Path to source YAML file (e.g., data/contaminants/Contaminants.yaml)
            source_key: Top-level key in YAML (e.g., contamination_patterns)
        
        Returns:
            Dictionary of entities from source file
        """
        cache_key = f"{source_file}:{source_key}"
        
        if cache_key not in self.source_data_cache:
            try:
                with open(source_file, 'r') as f:
                    data = yaml.safe_load(f)
                    self.source_data_cache[cache_key] = data.get(source_key, {})
                    logger.info(f"Loaded {len(self.source_data_cache[cache_key])} entities from {source_file}")
            except Exception as e:
                logger.error(f"Failed to load source data from {source_file}: {e}")
                self.source_data_cache[cache_key] = {}
        
        return self.source_data_cache[cache_key]
    
    def _get_entity_category(self, entity_id: str, source_data: Dict[str, Any]) -> str:
        """
        Get category for an entity ID from source data.
        
        Args:
            entity_id: Entity ID (without domain suffix, e.g., 'rust' not 'rust-contamination')
            source_data: Source data dictionary
        
        Returns:
            Category string, or 'other' if not found
        """
        # Try exact match first
        if entity_id in source_data:
            return source_data[entity_id].get('category', 'other')
        
        # Try with common suffixes removed
        for suffix in ['-contamination', '-laser-cleaning', '-compound', '-settings']:
            test_id = entity_id.replace(suffix, '')
            if test_id in source_data:
                return source_data[test_id].get('category', 'other')
        
        # Try adding suffixes
        for suffix in ['-contamination', '-laser-cleaning', '-compound', '-settings']:
            test_id = f"{entity_id}{suffix}"
            if test_id in source_data:
                return source_data[test_id].get('category', 'other')
        
        logger.debug(f"Category not found for entity: {entity_id}")
        return 'other'
    
    def _group_items_by_category(
        self, 
        items: List[Dict[str, Any]], 
        source_data: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group items by their category.
        
        Args:
            items: List of relationship items with 'id' fields
            source_data: Source data to lookup categories
        
        Returns:
            Dictionary mapping category -> list of items
        """
        grouped = defaultdict(list)
        
        for item in items:
            item_id = item.get('id')
            if not item_id:
                logger.warning(f"Item missing 'id' field: {item}")
                grouped['other'].append(item)
                continue
            
            category = self._get_entity_category(item_id, source_data)
            grouped[category].append(item)
        
        return dict(grouped)
    
    def enrich(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Group relationship items by category with section metadata.
        
        Args:
            frontmatter: Frontmatter dictionary
        
        Returns:
            Frontmatter with grouped relationships
        """
        if 'relationships' not in frontmatter:
            return frontmatter
        
        relationships = frontmatter['relationships']
        if not isinstance(relationships, dict):
            return frontmatter
        
        item_id = frontmatter.get('id', 'unknown')
        grouped_count = 0
        
        # Process each configured relationship
        for rel_name, rel_config in self.relationship_configs.items():
            if rel_name not in relationships:
                continue
            
            rel_data = relationships[rel_name]
            
            # Skip if not a wrapped relationship (needs presentation + items)
            if not isinstance(rel_data, dict) or 'items' not in rel_data:
                continue
            
            items = rel_data['items']
            if not items:
                continue
            
            # Load source data
            source_file = rel_config.get('source_file')
            source_key = rel_config.get('source_key')
            if not source_file or not source_key:
                logger.warning(f"Missing source_file or source_key for {rel_name}")
                continue
            
            source_data = self._load_source_data(source_file, source_key)
            if not source_data:
                logger.warning(f"No source data loaded for {rel_name}")
                continue
            
            # Group items by category
            grouped_items = self._group_items_by_category(items, source_data)
            
            # Skip if only one group (no benefit to grouping)
            if len(grouped_items) <= 1:
                logger.info(f"Skipping {rel_name} for {item_id}: only {len(grouped_items)} category")
                continue
            
            # Build groups structure
            groups = []
            category_metadata = rel_config.get('category_metadata', {})
            
            for category in sorted(grouped_items.keys()):
                cat_items = grouped_items[category]
                
                # Build group
                group = {
                    'category': category,
                    'items': cat_items
                }
                
                # Add category _section metadata if configured
                if category in category_metadata:
                    cat_meta = category_metadata[category]
                    group['_section'] = {}
                    if 'title' in cat_meta:
                        group['_section']['title'] = cat_meta['title']
                    if 'description' in cat_meta:
                        group['_section']['description'] = cat_meta['description']
                    if 'icon' in cat_meta:
                        group['_section']['icon'] = cat_meta['icon']
                
                groups.append(group)
            
            # Update relationship structure
            relationships[rel_name] = {
                'presentation': rel_data.get('presentation', 'card'),
                'groups': groups
            }
            
            # Add main section metadata if configured
            main_section = rel_config.get('main_section')
            if main_section:
                relationships[rel_name]['_section'] = main_section
            
            grouped_count += 1
            logger.info(f"Grouped {rel_name} for {item_id}: {len(items)} items → {len(groups)} categories")
        
        if grouped_count > 0:
            logger.info(f"Added category grouping to {grouped_count} relationships in {item_id}")
        
        return frontmatter
