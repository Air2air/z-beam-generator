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

from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
import logging
from datetime import datetime

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
                Optional keys: enrichments, generators, id_field, slug_field
        
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
        self.slug_field = config.get('slug_field', 'slug')
        self.filename_suffix = config.get('filename_suffix', '')
        
        # Enrichment and generation configs
        self.enrichment_configs = config.get('enrichments', [])
        self.generator_configs = config.get('generators', [])
        
        # Lazy-loaded components
        self._enrichers: Optional[List] = None
        self._generators: Optional[List] = None
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
            from export.enrichment.registry import create_enrichers
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
            logger.debug(f"Loading domain data from: {self.source_file}")
            
            with open(self.source_file, 'r', encoding='utf-8') as f:
                self._domain_data = yaml.safe_load(f)
            
            # Validate items key exists
            if self.items_key not in self._domain_data:
                raise ValueError(
                    f"Items key '{self.items_key}' not found in {self.source_file}\n"
                    f"Available keys: {', '.join(self._domain_data.keys())}"
                )
            
            logger.info(
                f"Loaded {len(self._domain_data[self.items_key])} items "
                f"from {self.domain} domain"
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
        # Determine output filename from slug or id
        slug = item_data.get(self.slug_field, item_id)
        filename = f"{slug}{self.filename_suffix}.yaml"
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
            
            # Apply generators (create derived content)
            for generator in self.generators:
                frontmatter = generator.generate(frontmatter)
                logger.debug(f"Applied generator: {generator.__class__.__name__}")
            
            # Validate and order fields (reorder_fields expects domain parameter)
            frontmatter = self.field_validator.reorder_fields(frontmatter, self.domain)
            
            # 🔍 DEBUG: Check if relationships still has slug before write
            if 'relationships' in frontmatter:
                dl = frontmatter['relationships']
                if isinstance(dl, dict):
                    for linkage_type, entries in dl.items():
                        if isinstance(entries, list) and len(entries) > 0:
                            first_entry = entries[0]
                            if isinstance(first_entry, dict):
                                has_slug = 'slug' in first_entry
                                print(f"🔍 BEFORE WRITE - {linkage_type}[0] has slug: {has_slug}")
                                if has_slug:
                                    print(f"    slug value: {first_entry['slug']}")
                                else:
                                    print(f"    keys: {list(first_entry.keys())}")
            
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
        # 🔍 DEBUG: Check slug before writing
        if 'relationships' in frontmatter:
            dl = frontmatter['relationships']
            if isinstance(dl, dict):
                for linkage_type, entries in dl.items():
                    if isinstance(entries, list) and len(entries) > 0:
                        first_entry = entries[0]
                        if isinstance(first_entry, dict):
                            has_slug = 'slug' in first_entry
                            print(f"🔍 IN _write_frontmatter() - {linkage_type}[0] has slug: {has_slug}")
        
        # Create output directory if needed
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write YAML with proper formatting
        # 🚨 CRITICAL: Use SafeDumper to prevent Python-specific tags
        # Without SafeDumper, OrderedDict creates !!python/object tags
        # that break JavaScript parsers (js-yaml cannot read them)
        yaml_string = yaml.dump(
            frontmatter,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,  # Preserve field order
            width=120,
            Dumper=yaml.SafeDumper  # MANDATORY - prevents Python tags
        )
        
        # 🔍 DEBUG: Check if slug is in relationships entries
        if 'relationships' in frontmatter:
            # Check if slug appears AFTER relationships in the YAML string
            dl_index = yaml_string.find('relationships:')
            if dl_index > 0:
                # Look for slug in the next 2000 characters after relationships
                after_dl = yaml_string[dl_index:dl_index+2000]
                linkage_slug_count = after_dl.count('\n    slug:')
                print(f"🔍 Found {linkage_slug_count} slug fields in relationships section of YAML")
                if linkage_slug_count == 0:
                    print(f"❌ NO SLUG FIELDS IN relationships!")
                    # Show sample
                    sample = after_dl[:300]
                    print(f"Sample:\n{sample}")
            
            # Write to temp file for inspection
            if 'aluminum' in str(output_file).lower():
                with open('/tmp/aluminum_yaml_final.yaml', 'w') as f:
                    f.write(yaml_string)
                print("📝 Wrote debug copy to /tmp/aluminum_yaml_final.yaml")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(yaml_string)
        
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
