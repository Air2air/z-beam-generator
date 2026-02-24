#!/usr/bin/env python3
"""
Source Data Field Normalization Script
======================================

Normalizes field ordering and removes export metadata from source YAML files.

PROBLEM:
- Inconsistent field ordering across domains
- Export metadata polluting source files (schemaVersion, contentType, fullPath, etc.)

SOLUTION:
- Standardize field order (id, name, category, author first)
- Remove export metadata (9 fields that should only be in frontmatter)
- Preserve all domain data (no data loss)

USAGE:
    # Dry-run (preview changes without modifying files)
    python3 scripts/tools/normalize_source_data_fields.py --domain materials --dry-run
    
    # Execute normalization (modifies files)
    python3 scripts/tools/normalize_source_data_fields.py --domain materials
    
    # Normalize all domains
    python3 scripts/tools/normalize_source_data_fields.py --all

SAFETY:
- Creates backup before modification (.backup-jan5-2026 suffix)
- Dry-run mode for previewing changes
- Validation checks for data loss
- Detailed logging of all changes

Related: SOURCE_DATA_NORMALIZATION_PLAN_JAN5_2026.md, Core Principle 0.6
"""

import argparse
import yaml
from pathlib import Path
from typing import Dict, Any, List, Tuple
import shutil
from datetime import datetime

# Export metadata fields to REMOVE from source (should only be in frontmatter)
EXPORT_METADATA_FIELDS = [
    'schemaVersion',
    'contentType',
    'pageTitle',
    'metaDescription',
    'pageDescription',
    'fullPath',
    'breadcrumb',
    'datePublished',
    'dateModified',
]

# Standard field order templates for each domain
FIELD_ORDER_TEMPLATES = {
    'materials': [
        'id',
        'name',
        'category',
        'subcategory',
        'author',
        'micro',
        'images',
        'characteristics',
        'properties',
        'contamination',
        'components',
        'relationships',
        'operational',
        'regulatory_standards',
        'metadata',
        'card',
        'eeat',
        'faq',
    ],
    'contaminants': [
        'id',
        'name',
        'title',
        'category',
        'subcategory',
        'author',
        'micro',
        'images',
        'valid_materials',
        'context_notes',
        'realism_notes',
        'relationships',
        'card',
        'faq',
    ],
    'compounds': [
        'id',
        'name',
        'display_name',
        'chemical_formula',
        'cas_number',
        'molecular_weight',
        'category',
        'subcategory',
        'author',
        'formula',
        'images',
        'exposure_guidelines',
        'detection_methods',
        'first_aid',
        'health_effects',
        'health_effects_keywords',
        'ppe_requirements',
        'regulatory_standards',
        'hazard_class',
        'monitoring_required',
        'typical_concentration_range',
        'sources_in_laser_cleaning',
        'relationships',
        'card',
        'metadata',
        'faq',
    ],
    'settings': [
        'id',
        'name',
        'category',
        'machine_settings',
        'application_notes',
        'safety_notes',
        'relationships',
    ],
    'applications': [
        'id',
        'name',
        'displayName',
        'category',
        'subcategory',
        'author',
        'micro',
        'images',
        'contentCards',
        'relationships',
        'card',
        'keywords',
        'slug',
        'faq',
    ],
}

# Domain configuration
DOMAIN_CONFIG = {
    'materials': {
        'file': 'data/materials/Materials.yaml',
        'root_key': 'materials',
    },
    'contaminants': {
        'file': 'data/contaminants/Contaminants.yaml',
        'root_key': 'contaminants',
    },
    'compounds': {
        'file': 'data/compounds/Compounds.yaml',
        'root_key': 'compounds',
    },
    'settings': {
        'file': 'data/settings/Settings.yaml',
        'root_key': 'settings',
    },
    'applications': {
        'file': 'data/applications/Applications.yaml',
        'root_key': 'applications',
    },
}


class SourceDataNormalizer:
    """Normalizes source YAML field ordering and removes export metadata."""
    
    def __init__(self, domain: str, dry_run: bool = False):
        self.domain = domain
        self.dry_run = dry_run
        self.config = DOMAIN_CONFIG[domain]
        self.field_order = FIELD_ORDER_TEMPLATES[domain]
        self.stats = {
            'items_processed': 0,
            'fields_reordered': 0,
            'fields_removed': 0,
            'export_metadata_removed': [],
        }
    
    def normalize(self) -> Dict[str, Any]:
        """Execute normalization process."""
        print(f"\n{'='*70}")
        print(f"NORMALIZING: {self.domain.upper()} Domain")
        print(f"File: {self.config['file']}")
        print(f"Mode: {'DRY-RUN (no changes)' if self.dry_run else 'LIVE (will modify file)'}")
        print('='*70)
        
        # Load source data
        filepath = Path(self.config['file'])
        if not filepath.exists():
            print(f"❌ ERROR: File not found: {filepath}")
            return self.stats
        
        with open(filepath) as f:
            data = yaml.safe_load(f)
        
        # Create backup before modification
        if not self.dry_run:
            backup_path = filepath.with_suffix('.yaml.backup-jan5-2026')
            shutil.copy2(filepath, backup_path)
            print(f"✅ Backup created: {backup_path}")
        
        # Process items
        root_key = self.config['root_key']
        items = data.get(root_key, {})
        
        print(f"\nProcessing {len(items)} items...")
        
        for item_id, item_data in items.items():
            if isinstance(item_data, dict):
                normalized_item = self._normalize_item(item_id, item_data)
                items[item_id] = normalized_item
                self.stats['items_processed'] += 1
        
        # Write normalized data
        if not self.dry_run:
            with open(filepath, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            print(f"\n✅ Normalized data written to: {filepath}")
        
        # Print statistics
        self._print_stats()
        
        return self.stats
    
    def _normalize_item(self, item_id: str, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize field order and remove export metadata for a single item."""
        original_fields = set(item_data.keys())
        
        # Remove export metadata fields
        export_metadata_found = []
        for field in EXPORT_METADATA_FIELDS:
            if field in item_data:
                export_metadata_found.append(field)
                self.stats['fields_removed'] += 1
        
        if export_metadata_found:
            self.stats['export_metadata_removed'].extend(export_metadata_found)
            if self.dry_run:
                print(f"\n  [{item_id}]")
                print(f"    Would remove: {', '.join(export_metadata_found)}")
        
        # Create normalized item with standard field order
        normalized = {}
        
        # Add fields in standard order
        for field in self.field_order:
            if field in item_data:
                normalized[field] = item_data[field]
        
        # Add any remaining fields not in standard order (preserve data)
        remaining_fields = []
        for field in item_data.keys():
            if field not in normalized and field not in EXPORT_METADATA_FIELDS:
                normalized[field] = item_data[field]
                remaining_fields.append(field)
        
        if remaining_fields:
            print(f"\n  [{item_id}]")
            print(f"    ⚠️  Non-standard fields (added at end): {', '.join(remaining_fields)}")
        
        # Check for reordering
        if list(item_data.keys()) != list(normalized.keys()):
            self.stats['fields_reordered'] += 1
        
        # Validate no data loss
        normalized_fields = set(normalized.keys())
        expected_fields = original_fields - set(EXPORT_METADATA_FIELDS)
        
        if normalized_fields != expected_fields:
            missing = expected_fields - normalized_fields
            extra = normalized_fields - expected_fields
            print(f"\n  ❌ VALIDATION ERROR [{item_id}]:")
            if missing:
                print(f"     Missing fields: {missing}")
            if extra:
                print(f"     Extra fields: {extra}")
        
        return normalized
    
    def _print_stats(self):
        """Print normalization statistics."""
        print(f"\n{'='*70}")
        print("NORMALIZATION STATISTICS")
        print('='*70)
        print(f"Items processed: {self.stats['items_processed']}")
        print(f"Items reordered: {self.stats['fields_reordered']}")
        print(f"Export metadata fields removed: {self.stats['fields_removed']}")
        
        if self.stats['export_metadata_removed']:
            removed_counts = {}
            for field in self.stats['export_metadata_removed']:
                removed_counts[field] = removed_counts.get(field, 0) + 1
            
            print("\nRemoved fields breakdown:")
            for field, count in sorted(removed_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"  - {field}: {count} items")
        
        print('='*70)


def main():
    parser = argparse.ArgumentParser(
        description='Normalize source YAML field ordering and remove export metadata',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview changes for materials (no modifications)
  python3 scripts/tools/normalize_source_data_fields.py --domain materials --dry-run
  
  # Execute normalization for materials
  python3 scripts/tools/normalize_source_data_fields.py --domain materials
  
  # Normalize all domains
  python3 scripts/tools/normalize_source_data_fields.py --all
        """
    )
    
    parser.add_argument(
        '--domain',
        choices=['materials', 'contaminants', 'compounds', 'settings', 'applications'],
        help='Domain to normalize'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Normalize all domains'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    
    args = parser.parse_args()
    
    if not args.domain and not args.all:
        parser.error("Must specify either --domain or --all")
    
    domains = list(DOMAIN_CONFIG.keys()) if args.all else [args.domain]
    
    print(f"\n{'#'*70}")
    print("SOURCE DATA NORMALIZATION TOOL")
    print(f"{'#'*70}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Mode: {'DRY-RUN' if args.dry_run else 'LIVE'}")
    print(f"Domains: {', '.join(domains)}")
    
    total_stats = {
        'items_processed': 0,
        'fields_reordered': 0,
        'fields_removed': 0,
    }
    
    for domain in domains:
        normalizer = SourceDataNormalizer(domain, dry_run=args.dry_run)
        stats = normalizer.normalize()
        
        total_stats['items_processed'] += stats['items_processed']
        total_stats['fields_reordered'] += stats['fields_reordered']
        total_stats['fields_removed'] += stats['fields_removed']
    
    print(f"\n{'#'*70}")
    print("TOTAL STATISTICS (All Domains)")
    print(f"{'#'*70}")
    print(f"Items processed: {total_stats['items_processed']}")
    print(f"Items reordered: {total_stats['fields_reordered']}")
    print(f"Export metadata fields removed: {total_stats['fields_removed']}")
    print(f"{'#'*70}")
    
    if args.dry_run:
        print("\n⚠️  DRY-RUN mode - No files were modified")
        print("Run without --dry-run to apply changes")
    else:
        print("\n✅ Normalization complete!")
        print("Backup files created with .backup-jan5-2026 suffix")


if __name__ == '__main__':
    main()
