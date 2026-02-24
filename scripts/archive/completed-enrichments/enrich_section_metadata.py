#!/usr/bin/env python3
"""
Enrich sectionMetadata in source data using section display schema.

This script populates comprehensive sectionMetadata WITHOUT voice processing,
using data/schemas/section_display_schema.yaml as the authoritative source.

Core Principle 0.6 Compliance:
- Reads from schema file (defines what each section type should have)
- Writes to source YAML (icon, order, variant stored at generation time)
- Export just reads source data (no lookups needed)

Usage:
    python3 scripts/enrichment/enrich_section_metadata.py --dry-run  # Preview
    python3 scripts/enrichment/enrich_section_metadata.py            # Apply
"""

import yaml
from pathlib import Path
import tempfile
import shutil
import argparse


def load_section_display_schema():
    """Load section display metadata schema (authoritative source)."""
    schema_file = 'data/schemas/section_display_schema.yaml'
    with open(schema_file, 'r') as f:
        schema = yaml.safe_load(f)
    
    return schema.get('sections', {}), schema.get('defaults', {})


def enrich_sectionmetadata(data, items_key, section_schema, schema_defaults, domain_name):
    """Enrich sectionMetadata with comprehensive information from schema."""
    items = data[items_key]
    enriched_count = 0
    
    for item_name, item_data in items.items():
        rels = item_data.get('relationships', {})
        
        for group_name, group_data in rels.items():
            if not isinstance(group_data, dict):
                continue
            
            for section_name, section_data in group_data.items():
                if not isinstance(section_data, dict) or '_section' not in section_data:
                    continue
                
                # Get current metadata
                _sec = section_data['_section']
                current_meta = _sec.get('sectionMetadata', {})
                
                # Build section key for lookup
                section_key = f"{group_name}.{section_name}"
                
                # Get definition from schema (or use defaults)
                section_def = section_schema.get(section_key, {})
                
                # Build enriched metadata
                enriched_meta = {
                    'relationshipType': section_name,  # Primary identifier
                    'group': group_name,               # Relationship group
                    'domain': domain_name,             # Source domain
                }
                
                # Add schema-defined display metadata
                enriched_meta['icon'] = section_def.get('icon', schema_defaults.get('icon', 'circle-help'))
                enriched_meta['order'] = section_def.get('order', schema_defaults.get('order', 999))
                enriched_meta['variant'] = section_def.get('variant', schema_defaults.get('variant', 'default'))
                
                # Add description if in schema
                if 'description' in section_def:
                    enriched_meta['schemaDescription'] = section_def['description']
                
                # Preserve existing notes (different from schema description)
                if current_meta.get('notes'):
                    enriched_meta['notes'] = current_meta['notes']
                
                # Preserve any custom metadata
                for key, value in current_meta.items():
                    if key not in enriched_meta and not key.startswith('_'):
                        enriched_meta[key] = value
                
                # Update if changed
                if enriched_meta != current_meta:
                    _sec['sectionMetadata'] = enriched_meta
                    enriched_count += 1
    
    return enriched_count


def process_domain(domain_config, section_schema, schema_defaults, dry_run=False):
    """Process a single domain."""
    domain_name = domain_config['name']
    data_file = domain_config['data_file']
    items_key = domain_config['items_key']
    
    print(f"\n{'='*80}")
    print(f"Processing: {domain_name.upper()}")
    print(f"{'='*80}")
    
    # Load source data
    with open(data_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Enrich metadata
    enriched_count = enrich_sectionmetadata(data, items_key, section_schema, schema_defaults, domain_name)
    
    print(f"  Enriched {enriched_count} section metadata blocks")
    
    if enriched_count > 0 and not dry_run:
        # Create backup
        backup_path = f"{data_file}.backup"
        shutil.copy2(data_file, backup_path)
        print(f"  📦 Backup: {backup_path}")
        
        # Save atomically
        temp_fd, temp_path = tempfile.mkstemp(
            suffix='.yaml',
            dir=Path(data_file).parent,
            text=True
        )
        try:
            with open(temp_fd, 'w', encoding='utf-8') as f:
                yaml.dump(
                    data,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                    width=1000
                )
            shutil.move(temp_path, data_file)
            print(f"  ✅ Saved: {data_file}")
        except Exception as e:
            Path(temp_path).unlink(missing_ok=True)
            raise e
    elif enriched_count == 0:
        print(f"  ✅ All metadata already enriched")
    
    return enriched_count


def main():
    parser = argparse.ArgumentParser(
        description='Enrich sectionMetadata in source data from section display schema'
    )
    parser.add_argument('--dry-run', action='store_true', help='Preview without saving')
    args = parser.parse_args()
    
    domains = [
        {
            'name': 'materials',
            'data_file': 'data/materials/Materials.yaml',
            'items_key': 'materials'
        },
        {
            'name': 'contaminants',
            'data_file': 'data/contaminants/Contaminants.yaml',
            'items_key': 'contaminants'
        },
        {
            'name': 'compounds',
            'data_file': 'data/compounds/Compounds.yaml',
            'items_key': 'compounds'
        },
        {
            'name': 'settings',
            'data_file': 'data/settings/Settings.yaml',
            'items_key': 'settings'
        }
    ]
    
    print('='*80)
    if args.dry_run:
        print('DRY RUN - PREVIEW MODE')
    else:
        print('ENRICHING SECTIONMETADATA FROM SECTION DISPLAY SCHEMA')
    print('='*80)
    print('\nCore Principle 0.6 Compliance:')
    print('  • Schema defines display properties (data/schemas/section_display_schema.yaml)')
    print('  • Enrichment writes to source YAML (icon, order, variant stored at generation)')
    print('  • Export reads from source data (no schema lookups needed)')
    print('\nNO voice processing applied (pure metadata enrichment)')
    
    # Load schema once (shared across all domains)
    section_schema, schema_defaults = load_section_display_schema()
    print(f'\n📋 Loaded {len(section_schema)} section type definitions from schema')
    
    total_enriched = 0
    for domain_config in domains:
        if Path(domain_config['data_file']).exists():
            enriched = process_domain(domain_config, section_schema, schema_defaults, args.dry_run)
            total_enriched += enriched
        else:
            print(f"\n⚠️  Missing file: {domain_config['data_file']}")
    
    print(f"\n{'='*80}")
    if args.dry_run:
        print(f"PREVIEW COMPLETE: {total_enriched} sections would be enriched")
        print("Run without --dry-run to apply changes")
    else:
        print(f"✅ ENRICHMENT COMPLETE: {total_enriched} sections enriched")
    print('='*80)


if __name__ == '__main__':
    main()
