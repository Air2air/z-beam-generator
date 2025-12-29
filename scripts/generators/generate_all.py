#!/usr/bin/env python3
"""
Generate All Source Data Fields

Populates computed fields in source YAML files (Materials.yaml, etc.)
using registered generators.

Usage:
    # Generate all fields for all domains
    python3 scripts/generators/generate_all.py
    
    # Generate for specific domain
    python3 scripts/generators/generate_all.py --domain materials
    
    # Generate specific field types
    python3 scripts/generators/generate_all.py --generators slug,url,breadcrumb
    
    # Dry run (show what would be generated)
    python3 scripts/generators/generate_all.py --dry-run
    
    # Incremental (only items missing fields)
    python3 scripts/generators/generate_all.py --incremental
"""

import argparse
import sys
import yaml
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from scripts.generators.coordinator import GeneratorCoordinator
from scripts.generators.identifiers import SlugGenerator
from scripts.generators.identifiers.url_generator import URLGenerator
from scripts.generators.navigation import BreadcrumbGenerator


def load_domain_data(domain: str) -> tuple[Path, Dict[str, Any], str]:
    """
    Load source YAML data for domain.
    
    Args:
        domain: Domain name (materials, contaminants, etc.)
    
    Returns:
        Tuple of (yaml_file_path, data_dict, items_key)
    """
    domain_map = {
        'materials': ('data/materials/Materials.yaml', 'materials'),
        'contaminants': ('data/contaminants/Contaminants.yaml', 'contamination_patterns'),
        'compounds': ('data/compounds/Compounds.yaml', 'compounds'),
        'settings': ('data/settings/Settings.yaml', 'settings')
    }
    
    if domain not in domain_map:
        raise ValueError(f"Unknown domain: {domain}")
    
    yaml_path, items_key = domain_map[domain]
    yaml_file = project_root / yaml_path
    
    if not yaml_file.exists():
        raise FileNotFoundError(f"Data file not found: {yaml_file}")
    
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)
    
    return yaml_file, data, items_key


def save_domain_data(yaml_file: Path, data: Dict[str, Any], dry_run: bool = False):
    """
    Save updated data back to YAML file.
    
    Args:
        yaml_file: Path to YAML file
        data: Updated data dict
        dry_run: If True, don't actually write file
    """
    if dry_run:
        print(f"\n[DRY RUN] Would save to: {yaml_file}")
        return
    
    # Backup original file
    backup_file = yaml_file.with_suffix('.yaml.backup')
    if yaml_file.exists():
        import shutil
        shutil.copy2(yaml_file, backup_file)
        print(f"\n📋 Backup created: {backup_file}")
    
    # Write updated data
    with open(yaml_file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"✅ Saved: {yaml_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate computed fields in source YAML data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--domain',
        choices=['materials', 'contaminants', 'compounds', 'settings', 'all'],
        default='all',
        help='Domain to generate for (default: all)'
    )
    parser.add_argument(
        '--generators',
        help='Comma-separated list of generators to run (default: all)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be generated without modifying files'
    )
    parser.add_argument(
        '--incremental',
        action='store_true',
        help='Only process items missing fields'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate completeness, don\'t generate'
    )
    
    args = parser.parse_args()
    
    # Determine domains to process
    domains = ['materials', 'contaminants', 'compounds', 'settings'] if args.domain == 'all' else [args.domain]
    
    print("=" * 80)
    print("🚀 SOURCE DATA GENERATOR")
    print("=" * 80)
    print(f"\nDomains: {', '.join(domains)}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'WRITE'}")
    print(f"Incremental: {args.incremental}")
    
    # Process each domain
    for domain in domains:
        print(f"\n{'='*80}")
        print(f"📦 DOMAIN: {domain.upper()}")
        print(f"{'='*80}")
        
        try:
            # Load data
            yaml_file, data, items_key = load_domain_data(domain)
            items = data.get(items_key, {})
            print(f"\n📄 Loaded: {yaml_file}")
            print(f"   Items: {len(items)}")
            
            # Initialize coordinator
            config = {
                'domain': domain,
                'project_root': project_root,
                'dry_run': args.dry_run
            }
            coordinator = GeneratorCoordinator(domain, config)
            
            # Register generators
            coordinator.register_generator(SlugGenerator(config))
            coordinator.register_generator(URLGenerator(config))
            coordinator.register_generator(BreadcrumbGenerator(config))
            
            if args.validate_only:
                # Validate only
                print("\n🔍 Validating completeness...")
                validation = coordinator.validate_completeness(items)
                
                if validation['complete']:
                    print(f"✅ All {validation['total_items']} items have complete fields")
                else:
                    print(f"⚠️  {validation['items_with_missing_fields']} items missing fields:")
                    for item_id, missing in list(validation['missing_fields'].items())[:5]:
                        print(f"   • {item_id}: {', '.join(missing)}")
                    if len(validation['missing_fields']) > 5:
                        print(f"   ... and {len(validation['missing_fields']) - 5} more")
            else:
                # Generate fields
                updated_items = coordinator.generate_all(items, incremental=args.incremental)
                
                # Update data dict
                data[items_key] = updated_items
                
                # Save
                save_domain_data(yaml_file, data, dry_run=args.dry_run)
                
                # Validate
                validation = coordinator.validate_completeness(updated_items)
                if validation['complete']:
                    print(f"\n✅ Validation: All {validation['total_items']} items complete")
                else:
                    print(f"\n⚠️  Warning: {validation['items_with_missing_fields']} items still missing fields")
        
        except Exception as e:
            print(f"\n❌ Error processing {domain}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"\n{'='*80}")
    print("✅ Generation complete")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()
