#!/usr/bin/env python3
"""
Frontmatter Structure Normalizer - Schema 5.0.0

PURPOSE: Migrate all frontmatter files from 4.0.0 to 5.0.0 structure
CHANGES:
  1. Flatten relationships (move to top level)
  2. Remove duplicate 'name' field (keep 'title')
  3. Reorder fields according to specification
  4. Update schema_version to 5.0.0

USAGE:
    # Dry run (preview changes)
    python3 scripts/normalize_frontmatter_structure.py --dry-run
    
    # Apply to all frontmatter
    python3 scripts/normalize_frontmatter_structure.py
    
    # Apply to specific directory
    python3 scripts/normalize_frontmatter_structure.py --path frontmatter/contaminants/
"""

import argparse
from pathlib import Path
from collections import OrderedDict
from typing import Dict, Any, List
import logging

# Use shared YAML utilities
from shared.utils.file_io import read_yaml_file, write_yaml_file

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


# ============================================================================
# FIELD ORDER SPECIFICATION (Schema 5.0.0)
# ============================================================================

FIELD_ORDER = [
    # IDENTITY
    'id',
    'title',
    'slug',
    'category',
    'subcategory',
    'schema_version',
    'content_type',
    
    # DATES & METADATA
    'datePublished',
    'dateModified',
    
    # AUTHOR
    'author',
    
    # CONTENT (type-specific)
    'contamination_description',
    'description',
    'compound_description',
    'settings_description',
    'micro',
    
    # TECHNICAL DATA (type-specific)
    'laser_properties',
    'physical_properties',
    'chemical_properties',
    'mechanical_properties',
    'laser_parameters',
    'process_parameters',
    
    # Additional content
    'context_notes',
    
    # DOMAIN LINKAGES (FLATTENED - now top level)
    'produces_compounds',
    'removes_contaminants',
    'found_in_materials',
    'effective_against',
    'related_materials',
    'related_contaminants',
    'related_compounds',
    'related_settings',
    
    # SEO & NAVIGATION
    'breadcrumb',
    'images',
    'valid_materials',
    'valid_contaminants',
    'compatible_materials',
    'appearance',
    'commonality_score',
    'eeat',
    
    # INTERNAL
    '_metadata',
]


def flatten_relationships(data: Dict) -> Dict:
    """
    Flatten relationships structure to top level.
    
    BEFORE (4.0.0):
        relationships:
            produces_compounds: [...]
            related_materials: [...]
    
    AFTER (5.0.0):
        produces_compounds: [...]
        related_materials: [...]
    """
    if 'relationships' not in data:
        return data
    
    linkages = data.pop('relationships')
    
    # Move each linkage type to top level
    linkage_types = [
        'produces_compounds',
        'removes_contaminants',
        'found_in_materials',
        'effective_against',
        'related_materials',
        'related_contaminants',
        'related_compounds',
        'related_settings',
    ]
    
    for linkage_type in linkage_types:
        if linkage_type in linkages:
            data[linkage_type] = linkages[linkage_type]
    
    return data


def remove_duplicate_fields(data: Dict) -> Dict:
    """
    Remove duplicate 'name' field (keep 'title').
    
    BEFORE: id, name, slug, title
    AFTER: id, title, slug
    """
    if 'name' in data:
        # Only remove if title exists
        if 'title' in data:
            del data['name']
            logger.debug(f"   Removed duplicate 'name' field")
    
    return data


def reorder_fields(data: Dict) -> OrderedDict:
    """
    Reorder fields according to specification.
    
    Uses FIELD_ORDER list to ensure consistent ordering.
    Fields not in FIELD_ORDER are appended at the end.
    """
    ordered = OrderedDict()
    
    # Add fields in specified order
    for field in FIELD_ORDER:
        if field in data:
            ordered[field] = data[field]
    
    # Add any remaining fields not in FIELD_ORDER
    for field in data:
        if field not in ordered:
            ordered[field] = data[field]
            logger.debug(f"   ⚠️  Unexpected field '{field}' (not in specification)")
    
    return ordered


def update_schema_version(data: Dict) -> Dict:
    """Update schema_version to 5.0.0."""
    data['schema_version'] = '5.0.0'
    return data


def normalize_file(file_path: Path, dry_run: bool = False) -> Dict[str, Any]:
    """
    Normalize a single frontmatter file.
    
    Returns:
        Dict with 'changes' (list of change descriptions) and 'success' (bool)
    """
    changes = []
    
    try:
        # Load file
        data = load_yaml(file_path)
        
        # Track changes
        original_keys = set(data.keys())
        had_relationships = 'relationships' in data
        had_name_field = 'name' in data
        original_schema = data.get('schema_version', 'unknown')
        
        # Apply transformations
        data = flatten_relationships(data)
        data = remove_duplicate_fields(data)
        data = update_schema_version(data)
        data = reorder_fields(data)
        
        # Record changes
        if had_relationships:
            changes.append('Flattened relationships')
        
        if had_name_field and 'name' not in data:
            changes.append('Removed duplicate name field')
        
        if original_schema != '5.0.0':
            changes.append(f'Updated schema {original_schema} → 5.0.0')
        
        new_keys = set(data.keys())
        if original_keys != new_keys:
            changes.append(f'Reordered fields ({len(data)} total)')
        
        # Save if not dry run
        if not dry_run and changes:
            write_yaml_file(file_path, data, sort_keys=False)
        
        return {
            'success': True,
            'changes': changes,
            'file': file_path.name
        }
        
    except Exception as e:
        logger.error(f"   ❌ Error processing {file_path.name}: {e}")
        return {
            'success': False,
            'changes': [],
            'error': str(e),
            'file': file_path.name
        }


def normalize_directory(directory: Path, dry_run: bool = False) -> Dict[str, Any]:
    """
    Normalize all YAML files in a directory.
    
    Returns:
        Dict with summary statistics
    """
    yaml_files = list(directory.glob('*.yaml'))
    
    if not yaml_files:
        logger.warning(f"⚠️  No YAML files found in {directory}")
        return {
            'total': 0,
            'success': 0,
            'failed': 0,
            'unchanged': 0
        }
    
    logger.info(f"\n{'=' * 80}")
    logger.info(f"NORMALIZING: {directory}")
    logger.info(f"{'=' * 80}")
    logger.info(f"Found {len(yaml_files)} YAML files")
    logger.info("")
    
    results = {
        'total': len(yaml_files),
        'success': 0,
        'failed': 0,
        'unchanged': 0,
        'details': []
    }
    
    for yaml_file in sorted(yaml_files):
        result = normalize_file(yaml_file, dry_run=dry_run)
        results['details'].append(result)
        
        if result['success']:
            if result['changes']:
                results['success'] += 1
                status = '✅' if not dry_run else '🔍'
                logger.info(f"{status} {result['file']}")
                for change in result['changes']:
                    logger.info(f"   • {change}")
            else:
                results['unchanged'] += 1
                logger.debug(f"   ⏭️  {result['file']} (no changes needed)")
        else:
            results['failed'] += 1
            logger.error(f"❌ {result['file']}: {result.get('error', 'Unknown error')}")
    
    return results


def print_summary(all_results: List[Dict], dry_run: bool = False) -> None:
    """Print summary of all normalization operations."""
    total_files = sum(r['total'] for r in all_results)
    total_success = sum(r['success'] for r in all_results)
    total_unchanged = sum(r['unchanged'] for r in all_results)
    total_failed = sum(r['failed'] for r in all_results)
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("NORMALIZATION SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total files processed: {total_files}")
    logger.info(f"Successfully normalized: {total_success}")
    logger.info(f"No changes needed: {total_unchanged}")
    logger.info(f"Failed: {total_failed}")
    logger.info("")
    
    if dry_run:
        logger.info("⚠️  DRY RUN MODE - No files were modified")
        logger.info("   Run without --dry-run to apply changes")
    else:
        logger.info("✅ Files have been normalized to Schema 5.0.0")
    
    logger.info("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description='Normalize frontmatter structure to Schema 5.0.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Dry run (preview changes)
    python3 scripts/normalize_frontmatter_structure.py --dry-run
    
    # Apply to all frontmatter
    python3 scripts/normalize_frontmatter_structure.py
    
    # Apply to contaminants only
    python3 scripts/normalize_frontmatter_structure.py --path frontmatter/contaminants/
    
    # Verbose output
    python3 scripts/normalize_frontmatter_structure.py --verbose
        """
    )
    
    parser.add_argument(
        '--path',
        type=str,
        default='frontmatter',
        help='Path to frontmatter directory (default: frontmatter/)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Resolve path
    base_path = Path(__file__).resolve().parents[1]
    target_path = base_path / args.path
    
    if not target_path.exists():
        logger.error(f"❌ Path does not exist: {target_path}")
        return 1
    
    logger.info("=" * 80)
    logger.info("FRONTMATTER STRUCTURE NORMALIZER - Schema 5.0.0")
    logger.info("=" * 80)
    logger.info("")
    logger.info("CHANGES:")
    logger.info("  1. Flatten relationships (move to top level)")
    logger.info("  2. Remove duplicate 'name' field (keep 'title')")
    logger.info("  3. Reorder fields according to specification")
    logger.info("  4. Update schema_version to 5.0.0")
    logger.info("")
    
    if args.dry_run:
        logger.info("⚠️  DRY RUN MODE - No files will be modified")
        logger.info("")
    
    # Process directories
    all_results = []
    
    if target_path.is_dir():
        # Check if this is the top-level frontmatter directory
        subdirs = [d for d in target_path.iterdir() if d.is_dir()]
        
        if subdirs and any(d.name in ['contaminants', 'materials', 'compounds', 'settings'] for d in subdirs):
            # Process each subdirectory
            for subdir in sorted(subdirs):
                if subdir.name.startswith('.'):
                    continue
                results = normalize_directory(subdir, dry_run=args.dry_run)
                all_results.append(results)
        else:
            # Process this directory directly
            results = normalize_directory(target_path, dry_run=args.dry_run)
            all_results.append(results)
    else:
        logger.error(f"❌ Path is not a directory: {target_path}")
        return 1
    
    # Print summary
    print_summary(all_results, dry_run=args.dry_run)
    
    return 0


if __name__ == "__main__":
    exit(main())
