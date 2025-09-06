#!/usr/bin/env python3
"""
File Cleanup Script for Z-Beam Generator

Renames all content files with parentheses in their names to use clean slug naming.
This ensures consistent, clean paths without parentheses for all generated content.
"""

import argparse
import logging
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from utils.slug_utils import create_filename_slug, get_clean_material_mapping

    parser = argparse.ArgumentParser(
        description="Clean up Z-Beam file paths by removing parentheses"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show what would be done without making changes (default)",
    )
    parser.add_argument(
        "--execute", action="store_true", help="Actually perform the rename operations"
    )
    parser.add_argument(
        "--content-only",
        action="store_true",
        help="Only process content files, skip materials.yaml",
    )

    args = parser.parse_args()

    # Determine if this is a dry run
    dry_run = not args.execute

    if dry_run:
        logger.info("🔍 DRY RUN MODE - No files will be modified")
    else:
        logger.info("🚀 EXECUTION MODE - Files will be renamed")

    logger.info("=" * 60)

    # Find all files with parentheses in content directory
    content_dir = Path("content")
    files_with_parens = find_files_with_parentheses(content_dir)

    if not files_with_parens:
        logger.info("✅ No files with parentheses found in content directory")
    else:
        logger.info(f"📂 Found {len(files_with_parens)} files with parentheses")

        # Create rename plan
        rename_plan = create_rename_plan(files_with_parens)

        if not rename_plan:
            logger.info("✅ All files already have clean names")
        else:
            logger.info(f"📋 Created rename plan for {len(rename_plan)} files")

            # Show rename plan
            logger.info("\n📝 Rename Plan:")
            logger.info("-" * 40)
            for old_path, new_path in rename_plan:
                logger.info(f"  {old_path.name}")
                logger.info(f"  → {new_path.name}")
                logger.info("")

            # Execute rename plan
            results = execute_rename_plan(rename_plan, dry_run)

            logger.info("\n📊 Results:")
            logger.info(f"  ✅ Successful: {results['success']}")
            logger.info(f"  ❌ Failed: {results['failed']}")
            logger.info(f"  ⏭️  Skipped: {results['skipped']}")

    # Update materials.yaml unless content-only flag is set
    if not args.content_only:
        logger.info("\n📄 Updating materials.yaml...")
        logger.info("-" * 40)
        materials_updated = update_materials_yaml(dry_run)

        if materials_updated:
            logger.info("✅ Materials.yaml update plan created")
        else:
            logger.info("✅ Materials.yaml already clean or no changes needed")

    logger.info("\n" + "=" * 60)
    if dry_run:
        logger.info("🔍 DRY RUN COMPLETE - Use --execute to apply changes")
    else:
        logger.info("🚀 CLEANUP COMPLETE - All file paths are now clean!")

    logger.info("\n💡 Future generations will automatically use clean paths")
    logger.info("   All new content will be generated with clean slugs")


if __name__ == "__main__":
    main()
