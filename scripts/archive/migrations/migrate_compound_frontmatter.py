#!/usr/bin/env python3
"""
Compound Frontmatter Migration Script

Migrates all 20 compound frontmatter files from flat structure to grouped relationships structure.
Implements specification in docs/COMPOUND_FRONTMATTER_RESTRUCTURE_SPEC.md.

Usage:
    python3 scripts/migration/migrate_compound_frontmatter.py [--dry-run] [--verbose]
    
    --dry-run: Show what would be changed without writing files
    --verbose: Show detailed progress

Created: December 18, 2025
Part of: Compound Frontmatter Restructure
"""

import sys
import argparse
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from export.core.universal_exporter import FrontmatterExporter
from export.config.loader import load_domain_config

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s'
    )


def migrate_compounds(dry_run: bool = False, verbose: bool = False) -> dict:
    """
    Migrate all compound frontmatter files.
    
    Args:
        dry_run: If True, don't write files
        verbose: If True, show detailed progress
        
    Returns:
        Dict with migration statistics
    """
    setup_logging(verbose)
    
    logger.info("=" * 80)
    logger.info("COMPOUND FRONTMATTER MIGRATION")
    logger.info("=" * 80)
    logger.info(f"Mode: {'DRY RUN' if dry_run else 'LIVE MIGRATION'}")
    logger.info("")
    
    # Load compounds configuration
    logger.info("Loading domain configuration...")
    config = load_domain_config('compounds')
    
    # Create exporter
    exporter = FrontmatterExporter(config)
    
    # Count files before
    existing_files = list(exporter.output_path.glob("*.yaml"))
    logger.info(f"Found {len(existing_files)} existing compound frontmatter files")
    logger.info("")
    
    if dry_run:
        logger.info("DRY RUN: No files will be modified")
        logger.info("This would regenerate all compound frontmatter with new structure")
        logger.info("")
        
        # Show what would be changed
        data = exporter._load_domain_data()
        compounds = data[exporter.items_key]
        
        logger.info(f"Would process {len(compounds)} compounds:")
        for idx, compound_id in enumerate(compounds.keys(), 1):
            logger.info(f"  {idx}. {compound_id}")
        
        stats = {
            'total': len(compounds),
            'processed': 0,
            'succeeded': 0,
            'failed': 0,
            'dry_run': True
        }
    else:
        # Execute migration
        logger.info("Starting migration...")
        logger.info("")
        
        results = exporter.export_all(force=True)
        
        succeeded = sum(1 for v in results.values() if v)
        failed = len(results) - succeeded
        
        stats = {
            'total': len(results),
            'processed': len(results),
            'succeeded': succeeded,
            'failed': failed,
            'dry_run': False
        }
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("MIGRATION COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Total compounds: {stats['total']}")
        logger.info(f"Successfully migrated: {stats['succeeded']}")
        logger.info(f"Failed: {stats['failed']}")
        logger.info(f"Success rate: {stats['succeeded']/stats['total']*100:.1f}%")
        
        if stats['failed'] > 0:
            logger.warning("")
            logger.warning("Some compounds failed to migrate. Check logs above for details.")
    
    return stats


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Migrate compound frontmatter files to new grouped structure'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without writing files'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed progress'
    )
    
    args = parser.parse_args()
    
    try:
        stats = migrate_compounds(dry_run=args.dry_run, verbose=args.verbose)
        
        # Exit code based on results
        if stats['dry_run']:
            sys.exit(0)
        elif stats['failed'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Migration failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
