"""
Enricher Registry and Base Classes

Plugin system for enriching frontmatter with linked data.
Part of Export System Consolidation (Phase 1).

Enrichers automatically fill missing fields in linkage arrays by looking up
data from source YAML files (Materials.yaml, Compounds.yaml, etc.).

Example:
    If produces_compounds has:
        - id: carbon-monoxide
          concentration_range: null
    
    CompoundLinkageEnricher fills from Compounds.yaml:
        - id: carbon-monoxide
          concentration_range: "100-500 ppm"
          hazard_class: "Toxic Gas"
          exposure_limits: {...}

Architecture:
- ENRICHER_REGISTRY: Maps enricher type string → class
- BaseLinkageEnricher: Abstract base for all linkage enrichers
- Specific enrichers: CompoundLinkageEnricher, MaterialLinkageEnricher, etc.
- TimestampEnricher: Non-linkage enricher for timestamp fields

Usage:
    from export.enrichment.registry import create_enrichers
    
    configs = [
        {'type': 'compound_linkage', 'field': 'produces_compounds', ...},
        {'type': 'timestamp', 'fields': ['datePublished', 'dateModified']}
    ]
    
    enrichers = create_enrichers(configs)
    for enricher in enrichers:
        frontmatter = enricher.enrich(frontmatter)
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# Import base enricher class
from export.enrichers.base import BaseEnricher
from export.enrichers.cleanup.field_cleanup_enricher import FieldCleanupEnricher
from export.enrichers.grouping.contaminant_materials_grouping_enricher import (
    ContaminantMaterialsGroupingEnricher,
)
from export.enrichers.linkage.author_enricher import AuthorEnricher
from export.enrichers.linkage.relationship_grouping_enricher import (
    RelationshipGroupingEnricher,
)
from export.enrichers.linkage.relationship_renaming_enricher import (
    RelationshipRenamingEnricher,
)
from export.enrichers.linkage.relationships_enricher import DomainLinkagesEnricher

# Import enrichers
from export.enrichers.linkage.slug_enricher import DomainLinkagesSlugEnricher
from export.enrichers.linkage.universal_linkage_enricher import UniversalLinkageEnricher
from export.enrichers.linkage.universal_restructure_enricher import (
    UniversalRestructureEnricher,
)
from export.enrichers.metadata.breadcrumb_enricher import BreadcrumbEnricher
from export.enrichers.metadata.name_enricher import NameEnricher
from export.enrichers.settings.material_category_enricher import MaterialCategoryEnricher  # Dec 19, 2025

logger = logging.getLogger(__name__)


class BaseLinkageEnricher(BaseEnricher):
    """
    Base class for linkage enrichers.
    
    Linkage enrichers auto-fill missing fields in relationships arrays
    by looking up data from source YAML files.
    
    Common pattern:
    1. Load source data (Materials.yaml, Compounds.yaml, etc.)
    2. For each item in specified linkage field:
        - Extract item ID
        - Look up full data in source
        - Copy configured default fields if missing
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize linkage enricher.
        
        Args:
            config: Enricher config with keys:
                - field: Linkage field name (e.g., 'produces_compounds')
                - source: Path to source YAML (e.g., 'data/compounds/Compounds.yaml')
                - defaults: List of field names to copy if missing
        
        Raises:
            ValueError: If required config keys missing
        """
        super().__init__(config)
        
        # Validate config
        required = ['field', 'source', 'defaults']
        missing = [k for k in required if k not in config]
        if missing:
            raise ValueError(f"Missing required config keys: {', '.join(missing)}")
        
        self.field = config['field']
        self.source_file = Path(config['source'])
        self.defaults = config['defaults']
        
        # Lazy-loaded source data
        self._source_data: Optional[Dict] = None
    
    def _load_source_data(self) -> Dict[str, Any]:
        """
        Load source data file.
        
        Returns:
            Dict containing source data
        
        Raises:
            FileNotFoundError: If source file doesn't exist
        """
        if self._source_data is None:
            if not self.source_file.exists():
                raise FileNotFoundError(f"Source file not found: {self.source_file}")
            
            logger.debug(f"Loading source data: {self.source_file}")
            with open(self.source_file, 'r', encoding='utf-8') as f:
                self._source_data = yaml.safe_load(f)
        
        return self._source_data
    
    def enrich(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich linkage field with missing data from source.
        
        Args:
            frontmatter: Input frontmatter dict
        
        Returns:
            Enriched frontmatter (modified)
        """
        # Check if linkage field exists
        if self.field not in frontmatter:
            logger.debug(f"Field '{self.field}' not in frontmatter, skipping enrichment")
            return frontmatter
        
        linkage_items = frontmatter[self.field]
        if not linkage_items:
            return frontmatter
        
        # Load source data
        source_data = self._load_source_data()
        
        # Enrich each item
        enriched_items = []
        for item in linkage_items:
            enriched_item = self._enrich_item(item, source_data)
            enriched_items.append(enriched_item)
        
        frontmatter[self.field] = enriched_items
        
        logger.debug(
            f"Enriched {len(enriched_items)} items in field '{self.field}'"
        )
        
        return frontmatter
    
    @abstractmethod
    def _enrich_item(
        self,
        item: Dict[str, Any],
        source_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enrich single linkage item.
        
        Args:
            item: Linkage item dict (e.g., {'id': 'carbon-monoxide'})
            source_data: Full source data dict
        
        Returns:
            Enriched item dict
        """
        pass


class CompoundLinkageEnricher(BaseLinkageEnricher):
    """
    Enrich compound linkages (produces_compounds, related_compounds).
    
    Auto-fills missing fields from Compounds.yaml:
    - concentration_range
    - hazard_class
    - exposure_limits
    - control_measures
    - etc.
    
    Based on Phase 2 compound enrichment pattern (proven architecture).
    """
    
    def _enrich_item(
        self,
        item: Dict[str, Any],
        source_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add missing compound fields from Compounds.yaml.
        
        Args:
            item: Compound linkage item
            source_data: Full Compounds.yaml data
        
        Returns:
            Enriched compound item
        """
        compound_id = item.get('id')
        if not compound_id:
            logger.warning("Compound item missing 'id' field")
            return item
        
        # Get compound data
        compounds = source_data.get('compounds', {})
        compound_data = compounds.get(compound_id)
        
        if not compound_data:
            logger.warning(f"Compound '{compound_id}' not found in source")
            return item
        
        # Add configured defaults if missing
        for field in self.defaults:
            if field not in item and field in compound_data:
                item[field] = compound_data[field]
                logger.debug(f"Added {field} to compound {compound_id}")
        
        return item


class MaterialLinkageEnricher(BaseLinkageEnricher):
    """
    Enrich material linkages (related_materials, found_in_materials).
    
    Auto-fills missing fields from Materials.yaml:
    - category
    - subcategory
    - thermal_conductivity
    - reflectivity
    - etc.
    """
    
    def _enrich_item(
        self,
        item: Dict[str, Any],
        source_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add missing material fields from Materials.yaml.
        
        Args:
            item: Material linkage item
            source_data: Full Materials.yaml data
        
        Returns:
            Enriched material item
        """
        material_id = item.get('id')
        if not material_id:
            logger.warning("Material item missing 'id' field")
            return item
        
        # Get material data
        materials = source_data.get('materials', {})
        material_data = materials.get(material_id)
        
        if not material_data:
            logger.warning(f"Material '{material_id}' not found in source")
            return item
        
        # Add configured defaults if missing
        for field in self.defaults:
            if field not in item and field in material_data:
                item[field] = material_data[field]
                logger.debug(f"Added {field} to material {material_id}")
        
        return item


class ContaminantLinkageEnricher(BaseLinkageEnricher):
    """
    Enrich contaminant linkages (removes_contaminants, related_contaminants).
    
    Auto-fills missing fields from Contaminants.yaml:
    - category
    - subcategory
    - commonality_score
    - removal_effectiveness
    - etc.
    """
    
    def _enrich_item(
        self,
        item: Dict[str, Any],
        source_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add missing contaminant fields from Contaminants.yaml.
        
        Args:
            item: Contaminant linkage item
            source_data: Full Contaminants.yaml data
        
        Returns:
            Enriched contaminant item
        """
        contaminant_id = item.get('id')
        if not contaminant_id:
            logger.warning("Contaminant item missing 'id' field")
            return item
        
        # Get contaminant data
        contaminants = source_data.get('contaminants', {})
        contaminant_data = contaminants.get(contaminant_id)
        
        if not contaminant_data:
            logger.warning(f"Contaminant '{contaminant_id}' not found in source")
            return item
        
        # Add configured defaults if missing
        for field in self.defaults:
            if field not in item and field in contaminant_data:
                item[field] = contaminant_data[field]
                logger.debug(f"Added {field} to contaminant {contaminant_id}")
        
        return item


class SettingsLinkageEnricher(BaseLinkageEnricher):
    """
    Enrich settings linkages (related_settings).
    
    Auto-fills missing fields from Settings.yaml:
    - power_watts
    - pulse_frequency_hz
    - recommended_for
    - etc.
    """
    
    def _enrich_item(
        self,
        item: Dict[str, Any],
        source_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add missing settings fields from Settings.yaml.
        
        Args:
            item: Settings linkage item
            source_data: Full Settings.yaml data
        
        Returns:
            Enriched settings item
        """
        settings_id = item.get('id') or item.get('material_name')
        if not settings_id:
            logger.warning("Settings item missing 'id' or 'material_name' field")
            return item
        
        # Get settings data
        settings = source_data.get('settings', {})
        settings_data = settings.get(settings_id)
        
        if not settings_data:
            logger.warning(f"Settings '{settings_id}' not found in source")
            return item
        
        # Add configured defaults if missing
        for field in self.defaults:
            if field not in item and field in settings_data:
                item[field] = settings_data[field]
                logger.debug(f"Added {field} to settings {settings_id}")
        
        return item


class TimestampEnricher(BaseEnricher):
    """
    Add/update timestamp fields.
    
    Non-linkage enricher that ensures timestamp fields exist.
    Commonly used fields:
    - datePublished: When content was first published
    - dateModified: When content was last updated
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize timestamp enricher.
        
        Args:
            config: Config with 'fields' key (list of field names to set)
        """
        super().__init__(config)
        self.fields = config.get('fields', ['datePublished', 'dateModified'])
    
    def enrich(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add timestamps to frontmatter.
        
        Args:
            frontmatter: Input frontmatter dict
        
        Returns:
            Frontmatter with timestamps (modified)
        """
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        for field in self.fields:
            if field not in frontmatter:
                frontmatter[field] = timestamp
                logger.debug(f"Added timestamp field: {field}")
        
        return frontmatter


# Registry mapping enricher type → class
ENRICHER_REGISTRY = {
    'universal_restructure': UniversalRestructureEnricher,  # Consolidates all restructure enrichers (Dec 19, 2025)
    'universal_linkage': UniversalLinkageEnricher,  # Consolidates all linkage enrichers (Dec 19, 2025)
    'relationship_renaming': RelationshipRenamingEnricher,  # Change 3: Dec 19, 2025
    'field_cleanup': FieldCleanupEnricher,  # Changes 2 & 5: Dec 19, 2025
    'contaminant_materials_grouping': ContaminantMaterialsGroupingEnricher,  # Change 4: Dec 19, 2025
    'compound_linkage': CompoundLinkageEnricher,  # Legacy - use universal_linkage
    'material_linkage': MaterialLinkageEnricher,  # Legacy - use universal_linkage
    'contaminant_linkage': ContaminantLinkageEnricher,  # Legacy - use universal_linkage
    'settings_linkage': SettingsLinkageEnricher,  # Legacy - use universal_linkage
    'timestamp': TimestampEnricher,
    'author': AuthorEnricher,
    'name': NameEnricher,  # Adds name field from id if missing
    'material_category': MaterialCategoryEnricher,  # Adds category/subcategory from Materials.yaml (Dec 19, 2025)
    'relationships': DomainLinkagesEnricher,
    'relationship_grouping': RelationshipGroupingEnricher,
    'relationships_slug': DomainLinkagesSlugEnricher,
    'breadcrumb': BreadcrumbEnricher,  # Generates breadcrumb navigation arrays
}

def create_enrichers(configs: List[Dict[str, Any]]) -> List[BaseEnricher]:
    """
    Create enricher instances from config list.
    
    Args:
        configs: List of enricher configs from domain YAML
            Each config needs 'type' key matching ENRICHER_REGISTRY
    
    Returns:
        List of initialized enricher instances (in config order)
    
    Raises:
        ValueError: If enricher type not found in registry
    
    Example:
        configs = [
            {'type': 'compound_linkage', 'field': 'produces_compounds', ...},
            {'type': 'timestamp', 'fields': ['datePublished']}
        ]
        enrichers = create_enrichers(configs)
    """
    enrichers = []
    
    for config in configs:
        enricher_type = config.get('type')
        
        if not enricher_type:
            logger.warning(f"Enricher config missing 'type': {config}")
            continue
        
        if enricher_type not in ENRICHER_REGISTRY:
            raise ValueError(
                f"Unknown enricher type: {enricher_type}\n"
                f"Available types: {', '.join(ENRICHER_REGISTRY.keys())}"
            )
        
        enricher_class = ENRICHER_REGISTRY[enricher_type]
        enricher = enricher_class(config)
        enrichers.append(enricher)
        
        logger.debug(f"Created enricher: {enricher_class.__name__}")
    
    return enrichers
