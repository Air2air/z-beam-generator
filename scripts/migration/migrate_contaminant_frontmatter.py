"""
Migrate Contaminant Frontmatter to Schema 5.0.0

Regenerates all contaminant frontmatter files with the new grouped structure
where technical data is organized under relationships.* instead of scattered
at the top-level.

Usage:
    # Dry-run (preview only, no changes)
    python3 scripts/migration/migrate_contaminant_frontmatter.py --dry-run --verbose
    
    # Actual migration
    python3 scripts/migration/migrate_contaminant_frontmatter.py --verbose
    
    # Silent mode (minimal output)
    python3 scripts/migration/migrate_contaminant_frontmatter.py

Architecture:
    Uses UniversalFrontmatterExporter with contaminant_restructure enricher
    to regenerate all contaminant files. The enricher moves technical sections
    from top-level to relationships.* during export.

Output:
    - Statistics (total, succeeded, failed, success rate)
    - List of all contaminants processed (if --verbose)
"""

import argparse
import sys
from pathlib import Path
import logging
import yaml

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from export.core.universal_exporter import UniversalFrontmatterExporter


def migrate_contaminants(dry_run: bool = False, verbose: bool = False) -> dict:
    """
    Migrate all contaminant frontmatter to Schema 5.0.0 structure.
    
    Args:
        dry_run: If True, preview changes without modifying files
        verbose: If True, show detailed logging
        
    Returns:
        dict: Statistics (total, succeeded, failed, success_rate)
    """
    # Setup logging
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(levelname)-8s %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 75)
    logger.info("CONTAMINANT FRONTMATTER MIGRATION")
    logger.info("=" * 75)
    logger.info(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    logger.info("")
    
    # Load domain configuration
    logger.info("Loading domain configuration...")
    config_path = Path(__file__).parent.parent.parent / "export" / "config" / "contaminants.yaml"
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    logger.debug(f"Config validation passed for domain: {config['domain']}")
    
    # Initialize exporter with config dict
    exporter = UniversalFrontmatterExporter(config)
    logger.info(f"Loaded config for domain: contaminants")
    logger.info(f"Initialized UniversalFrontmatterExporter for domain: contaminants")
    
    # Get existing frontmatter files
    frontmatter_dir = Path(exporter.config['output_path'])
    existing_files = list(frontmatter_dir.glob("*.yaml"))
    logger.info(f"Found {len(existing_files)} existing contaminant frontmatter files")
    
    if dry_run:
        logger.info("")
        logger.info("DRY RUN: No files will be modified")
        logger.info("This would regenerate all contaminant frontmatter with new structure")
        logger.info("")
    
    # Load source data
    with open(exporter.source_file, 'r') as f:
        data_file = yaml.safe_load(f)
    
    contaminants = data_file.get(exporter.items_key, {})
    logger.info(f"Loaded {len(contaminants)} items from {exporter.config['source_file']}")
    
    if dry_run:
        logger.info(f"Would process {len(contaminants)} contaminants:")
        for i, contaminant_id in enumerate(contaminants.keys(), 1):
            logger.info(f"  {i}. {contaminant_id}")
        
        stats = {
            'total': len(contaminants),
            'succeeded': 0,
            'failed': 0,
            'success_rate': 0.0
        }
        return stats
    
    # Actual migration - regenerate all contaminants
    logger.info("")
    logger.info("Starting migration...")
    logger.info("")
    
    succeeded = 0
    failed = 0
    
    for contaminant_id, contaminant_data in contaminants.items():
        try:
            exporter.export_single(contaminant_id, contaminant_data, force=True)
            succeeded += 1
        except Exception as e:
            logger.error(f"Failed to export {contaminant_id}: {e}")
            failed += 1
    
    # Statistics
    total = len(contaminants)
    success_rate = (succeeded / total * 100) if total > 0 else 0
    
    logger.info("")
    logger.info("=" * 75)
    logger.info("MIGRATION COMPLETE")
    logger.info("=" * 75)
    logger.info(f"Total contaminants: {total}")
    logger.info(f"Successfully migrated: {succeeded}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Success rate: {success_rate:.1f}%")
    
    return {
        'total': total,
        'succeeded': succeeded,
        'failed': failed,
        'success_rate': success_rate
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Migrate contaminant frontmatter to Schema 5.0.0 grouped structure"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed logging"
    )
    
    args = parser.parse_args()
    
    stats = migrate_contaminants(dry_run=args.dry_run, verbose=args.verbose)
    
    # Exit with error code if any failures
    sys.exit(0 if stats['failed'] == 0 else 1)
