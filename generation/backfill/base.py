"""
Base Backfill Generator

Abstract base class for generators that permanently populate source YAML files.

Unlike export enrichers (temporary), backfill generators:
1. Read source YAML files
2. Generate/enrich data
3. Write back to source YAML (permanent)

Architecture:
- Atomic writes (temp file + rename)
- Dry-run support
- ALWAYS overwrite existing content (mandatory for structural variation)
- Progress tracking and statistics

Policy Compliance:
- YAML source is single source of truth
- No hardcoded values
- Fail-fast on errors

IMPORTANT: Backfill generators ALWAYS regenerate content, even if fields
already exist. This ensures distinctive properties and structural patterns
are applied to all materials consistently.
- Preserve existing data

Usage:
    config = {
        'source_file': 'data/materials/Materials.yaml',
        'items_key': 'materials',
        'field': 'produces_compounds'
    }
    generator = MyBackfillGenerator(config)
    stats = generator.backfill_all()
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict
import yaml


class BaseBackfillGenerator(ABC):
    """
    Base class for generators that populate source YAML permanently.
    
    Backfill generators enrich source data once, making enrichment permanent.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize backfill generator.
        
        Args:
            config: Generator config with source_file, field, etc.
        """
        self.config = config
        self.source_file = Path(config['source_file'])
        if 'items_key' not in config:
            raise KeyError("Missing required config key: items_key")
        self.items_key = config['items_key']
        self.field = config.get('field')
        if 'dry_run' not in config:
            raise KeyError("Missing required config key: dry_run")
        if not isinstance(config['dry_run'], bool):
            raise TypeError(
                f"Invalid config type for dry_run: expected bool, got {type(config['dry_run']).__name__}"
            )
        self.dry_run = config['dry_run']
        self.item_filter = config.get('item_filter')
        
        # Validate source file exists
        if not self.source_file.exists():
            raise FileNotFoundError(f"Source file not found: {self.source_file}")
    
    @abstractmethod
    def populate(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate/enrich data for one item.
        
        Args:
            item_data: Item dict from source YAML
        
        Returns:
            Modified item dict (with new/enriched fields)
        """
        pass
    
    def backfill_all(self) -> Dict[str, int]:
        """
        Backfill all items in source YAML file.
        
        Returns:
            Stats dict: {processed, modified, skipped, errors}
        """
        print(f"\\n{'='*80}")
        print(f"🔄 BACKFILLING: {self.__class__.__name__}")
        print(f"{'='*80}")
        print(f"Source: {self.source_file}")
        print(f"Field: {self.field}")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'WRITE'}")
        print()
        
        # Load source YAML
        data = self._load_source()
        if self.items_key not in data:
            raise KeyError(
                f"Missing required top-level key '{self.items_key}' in source file: {self.source_file}"
            )

        items = data[self.items_key]
        if not isinstance(items, dict):
            raise ValueError(
                f"Expected '{self.items_key}' to be a dictionary in {self.source_file}, got {type(items).__name__}"
            )
        
        stats = {'processed': 0, 'modified': 0, 'skipped': 0, 'errors': 0}
        
        # Process each item
        for item_id, item_data in items.items():
            # Skip if item_filter specified and doesn't match
            if self.item_filter and item_id != self.item_filter:
                continue
                
            try:
                # Check if already populated
                if self._should_skip(item_data):
                    stats['skipped'] += 1
                    print(f"   ⏭️  {item_id}: already populated")
                    continue
                
                # Generate/enrich data
                modified_data = self.populate(item_data)
                
                # Update in-memory data
                items[item_id] = modified_data
                stats['processed'] += 1
                stats['modified'] += 1
                print(f"   ✅ {item_id}: populated")
                
            except Exception as e:
                stats['errors'] += 1
                print(f"   ❌ {item_id}: error - {e}")
        
        # Write back to source YAML (if not dry run)
        if not self.dry_run and stats['modified'] > 0:
            self._write_source(data)
            print(f"\\n💾 Saved {stats['modified']} changes to {self.source_file}")
        elif self.dry_run and stats['modified'] > 0:
            print(f"\\n🔍 DRY RUN: Would save {stats['modified']} changes")
        
        # Print summary
        print(f"\\n{'='*80}")
        print(f"📊 BACKFILL SUMMARY")
        print(f"{'='*80}")
        print(f"Processed: {stats['processed']}")
        print(f"Modified:  {stats['modified']}")
        print(f"Skipped:   {stats['skipped']}")
        print(f"Errors:    {stats['errors']}")
        print(f"{'='*80}\\n")
        
        return stats
    
    def _should_skip(self, item_data: Dict[str, Any]) -> bool:
        """
        Check if item already has the field populated.
        
        Args:
            item_data: Item data dict
        
        Returns:
            True if should skip (already populated), False otherwise
        """
        if not self.field:
            return False
        
        # Check if field exists and is not empty
        value = item_data.get(self.field)
        if value is None:
            return False
        
        # Check if empty list/dict
        if isinstance(value, (list, dict)) and len(value) == 0:
            return False
        
        # Check if empty string
        if isinstance(value, str) and value.strip() == '':
            return False
        
        return True
    
    def _load_source(self) -> Dict[str, Any]:
        """
        Load source YAML file.
        
        Returns:
            Parsed YAML data
        """
        with open(self.source_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _write_source(self, data: Dict[str, Any]) -> None:
        """
        Write data back to source YAML file (atomic write).
        
        Args:
            data: Complete YAML data to write
        """
        # Atomic write: write to temp file, then rename
        temp_file = self.source_file.with_suffix('.tmp')
        
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump(
                    data,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                    width=120
                )
            
            # Atomic rename
            temp_file.replace(self.source_file)
            
        except Exception as e:
            # Clean up temp file on error
            if temp_file.exists():
                temp_file.unlink()
            raise RuntimeError(f"Failed to write source file: {e}") from e
