"""
Universal Frontmatter Exporter

Configuration-driven exporter that replaces all domain-specific exporters.
Part of Export System Consolidation (Phase 1).

REPLACES:
- export/core/trivial_exporter.py (2,115 lines - materials)
- export/contaminants/trivial_exporter.py (372 lines)
- export/compounds/trivial_exporter.py (230 lines)
- export/settings/trivial_exporter.py (278 lines)
Total reduction: 3,285 lines → ~300 lines (91% reduction)

Architecture:
- Configuration-driven (YAML configs, not Python classes)
- Plugin-based enrichment system
- Plugin-based content generation
- Universal field ordering and validation

Usage:
    from export.core.universal_exporter import UniversalFrontmatterExporter
    from export.config.loader import load_domain_config
    
    config = load_domain_config('materials')
    exporter = UniversalFrontmatterExporter(config)
    exporter.export_all()
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from export.utils import load_domain_data, write_frontmatter
from export.utils.url_formatter import format_filename

logger = logging.getLogger(__name__)


class UniversalFrontmatterExporter:
    """
    Universal configuration-driven frontmatter exporter.
    
    Single class that handles all domain exports through configuration.
    Domain-specific behavior defined in YAML configs (export/config/*.yaml).
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize with domain configuration.
        
        Args:
            config: Domain configuration dict loaded from export/config/{domain}.yaml
                Required keys: domain, source_file, output_path, items_key
                Optional keys: enrichments, generators, id_field
        
        Raises:
            ValueError: If required config keys missing
        """
        self._validate_config(config)
        
        self.config = config
        self.domain = config['domain']
        self.source_file = Path(config['source_file'])
        self.output_path = Path(config['output_path'])
        self.items_key = config.get('items_key', self.domain)
        self.id_field = config.get('id_field', 'id')
        self.filename_suffix = config.get('filename_suffix', '')
        self.slugify_filenames = config.get('slugify_filenames', False)
        
        # Enrichment and generation configs
        self.enrichment_configs = config.get('enrichments', [])
        self.generator_configs = config.get('generators', [])
        self.library_enrichment_config = config.get('library_enrichments', {})
        
        # Lazy-loaded components
        self._enrichers: Optional[List] = None
        self._generators: Optional[List] = None
        self._library_processor: Optional[Any] = None
        self._domain_data: Optional[Dict] = None
        self._field_validator = None
        
        logger.info(f"Initialized UniversalFrontmatterExporter for domain: {self.domain}")
    
    def _validate_config(self, config: Dict) -> None:
        """
        Validate required configuration keys.
        
        Raises:
            ValueError: If required keys missing
        """
        required_keys = ['domain', 'source_file', 'output_path']
        missing_keys = [key for key in required_keys if key not in config]
        
        if missing_keys:
            raise ValueError(
                f"Missing required config keys: {', '.join(missing_keys)}\n"
                f"Required: {', '.join(required_keys)}"
            )
        
        # Validate paths exist
        source_file = Path(config['source_file'])
        if not source_file.exists():
            raise ValueError(f"Source file not found: {source_file}")
    
    @property
    def enrichers(self) -> List:
        """Lazy-load enrichers from config."""
        if self._enrichers is None:
            from export.enrichers.linkage.registry import create_enrichers
            self._enrichers = create_enrichers(self.enrichment_configs)
        return self._enrichers
    
    @property
    def generators(self) -> List:
        """Lazy-load generators from config."""
        if self._generators is None:
            from export.generation.registry import create_generators
            self._generators = create_generators(self.generator_configs)
        return self._generators
    
    @property
    def field_validator(self):
        """Lazy-load field validator."""
        if self._field_validator is None:
            from shared.validation.field_order import FrontmatterFieldOrderValidator
            self._field_validator = FrontmatterFieldOrderValidator()
        return self._field_validator
    
    @property
    def library_processor(self):
        """Lazy-load library enrichment processor."""
        if self._library_processor is None and self.library_enrichment_config.get('enabled', False):
            from export.enrichers.library import LibraryEnrichmentProcessor
            self._library_processor = LibraryEnrichmentProcessor(self.config)
        return self._library_processor
    
    def _load_domain_data(self) -> Dict[str, Any]:
        """
        Load source data from YAML file.
        
        Returns:
            Dict containing domain data
        
        Raises:
            FileNotFoundError: If source file doesn't exist
            yaml.YAMLError: If YAML parsing fails
        """
        if self._domain_data is None:
            # Use centralized data loader
            self._domain_data = load_domain_data(
                self.source_file,
                items_key=self.items_key
            )
        
        return self._domain_data
    
    def export_single(
        self,
        item_id: str,
        item_data: Dict[str, Any],
        force: bool = False
    ) -> bool:
        """
        Export single item to frontmatter file.
        
        Workflow:
        1. Check if output exists (skip if not forced)
        2. Build base frontmatter from item data
        3. Apply all configured enrichments (in order)
        4. Apply all configured generators (in order)
        5. Validate and order fields
        6. Write to YAML file
        
        Args:
            item_id: Unique identifier for item
            item_data: Item data dict from source YAML
            force: If True, overwrite existing files
        
        Returns:
            True if exported, False if skipped (exists and not forced)
        
        Raises:
            Exception: If export fails (enrichment, generation, or write error)
        """
        # Determine output filename from item_id (with optional slugification)
        filename = format_filename(
            item_id=item_id,
            suffix=self.filename_suffix,
            slugify_id=self.slugify_filenames
        )
        output_file = self.output_path / filename
        
        # Skip if exists and not forced
        if not force and output_file.exists():
            logger.debug(f"Skipping {item_id} (exists, not forced)")
            return False
        
        logger.debug(f"Exporting {item_id} to {output_file}")
        
        try:
            # Build base frontmatter (pass item_id for 'id' field per guide)
            frontmatter = self._build_base_frontmatter(item_data, item_id)
            
            # Apply enrichments (auto-fill linked data)
            for enricher in self.enrichers:
                frontmatter = enricher.enrich(frontmatter)
                logger.debug(f"Applied enricher: {enricher.__class__.__name__}")
            
            # Apply library enrichments (expand library relationships with full data)
            if self.library_processor:
                logger.debug(f"🔍 BEFORE library enrichment - frontmatter keys: {list(frontmatter.keys())}")
                if 'relationships' in frontmatter:
                    logger.debug(f"   relationships keys: {list(frontmatter['relationships'].keys())}")
                
                frontmatter = self.library_processor.process_item(frontmatter)
                logger.debug("Applied library enrichments")
                
                logger.debug(f"🔍 AFTER library enrichment - frontmatter keys: {list(frontmatter.keys())}")
                # Check if enriched fields were added
                enriched_fields = [k for k in frontmatter.keys() if k.endswith('_detail')]
                logger.debug(f"Enriched fields added: {enriched_fields}")
            
            # Apply generators (create derived content)
            for generator in self.generators:
                frontmatter = generator.generate(frontmatter)
                logger.debug(f"Applied generator: {generator.__class__.__name__}")
            
            # Validate and order fields (reorder_fields expects domain parameter)
            frontmatter = self.field_validator.reorder_fields(frontmatter, self.domain)
            
            # Convert OrderedDict to regular dict for YAML serialization
            frontmatter = dict(frontmatter)
            
            # Write to file
            self._write_frontmatter(output_file, frontmatter)
            
            logger.info(f"✅ Exported {item_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export {item_id}: {e}")
            raise
    
    def export_all(self, force: bool = True) -> Dict[str, bool]:
        """
        Export all items in domain to frontmatter files.
        
        Args:
            force: If True, overwrite existing files
        
        Returns:
            Dict mapping item_id → success (True if exported, False if skipped)
        
        Example:
            results = exporter.export_all(force=True)
            exported = sum(results.values())
            print(f"Exported {exported}/{len(results)} items")
        """
        logger.info(f"Starting batch export for {self.domain} domain (force={force})")
        
        results = {}
        data = self._load_domain_data()
        items = data[self.items_key]
        
        total = len(items)
        for idx, (item_id, item_data) in enumerate(items.items(), 1):
            try:
                success = self.export_single(item_id, item_data, force)
                results[item_id] = success
                
                if idx % 10 == 0:
                    logger.info(f"Progress: {idx}/{total} items processed")
                    
            except Exception as e:
                logger.error(f"Failed to export {item_id}: {e}")
                results[item_id] = False
        
        # Summary
        exported = sum(results.values())
        skipped = total - exported
        logger.info(
            f"Export complete: {exported} exported, {skipped} skipped, "
            f"{total} total"
        )
        
        return results
    
    def _build_base_frontmatter(
        self, 
        item_data: Dict[str, Any],
        item_id: str
    ) -> Dict[str, Any]:
        """
        Build base frontmatter structure from item data.
        
        Creates a copy of item data and ensures required Schema 5.0.0 fields.
        Per FRONTMATTER_FORMATTING_GUIDE.md, adds 'id' field as first field.
        
        Args:
            item_data: Source item data dict
            item_id: Unique identifier from source YAML key
        
        Returns:
            Base frontmatter dict with required fields
        """
        # Deep copy to avoid modifying source
        frontmatter = dict(item_data)
        
        # Add id field (per FRONTMATTER_FORMATTING_GUIDE.md - should be first field)
        frontmatter['id'] = item_id
        
        # Ensure required Schema 5.0.0 fields
        frontmatter.setdefault('schema_version', '5.0.0')
        frontmatter.setdefault('content_type', self.domain)
        
        # Add timestamps if missing
        now = datetime.utcnow().isoformat() + 'Z'
        frontmatter.setdefault('datePublished', now)
        frontmatter.setdefault('dateModified', now)
        
        return frontmatter
    
    def _write_frontmatter(
        self,
        output_file: Path,
        frontmatter: Dict[str, Any]
    ) -> None:
        """
        Write frontmatter dict to YAML file.
        
        Args:
            output_file: Output path
            frontmatter: Frontmatter dict (field-ordered)
        
        Raises:
            IOError: If write fails
        """
        # Convert OrderedDict to regular dict
        frontmatter = dict(frontmatter)
        
        # Use centralized YAML writer with SafeDumper
        write_frontmatter(output_file, frontmatter, create_dirs=True)
        
        logger.debug(f"Wrote {output_file} ({len(frontmatter)} fields)")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about domain data.
        
        Returns:
            Dict with stats: total_items, source_file, output_path, etc.
        """
        data = self._load_domain_data()
        items = data[self.items_key]
        
        return {
            'domain': self.domain,
            'total_items': len(items),
            'source_file': str(self.source_file),
            'output_path': str(self.output_path),
            'enrichments': len(self.enrichment_configs),
            'generators': len(self.generator_configs),
        }
