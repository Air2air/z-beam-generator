#!/usr/bin/env python3
"""
Backup File Cleanup Script
Description: Safely removes old backup files while preserving recent ones
Usage: python3 scripts/maintenance/cleanup_backups.py [--dry-run] [--keep N]
Dependencies: pathlib, argparse
Last Updated: 2025-09-05
"""

import argparse
from pathlib import Path
from typing import List


def find_backup_files(directory: str = "config") -> List[Path]:
    """
    Find all backup files in the specified directory.

    Args:
        directory: Directory to search for backup files

    Returns:
        List of backup file paths
    """
    config_dir = Path(directory)
    if not config_dir.exists():
        print(f"❌ Directory {directory} not found")
        return []

    # Find all files with .backup_ in the name
    backup_files = list(config_dir.glob("*.backup_*"))
    return sorted(backup_files, key=lambda x: x.stat().st_mtime, reverse=True)


def cleanup_backups(directory: str = "config", keep_count: int = 3, dry_run: bool = True) -> dict:
    """
    Clean up old backup files while preserving the most recent ones.

    Args:
        directory: Directory containing backup files
        keep_count: Number of most recent backups to keep
        dry_run: If True, only show what would be deleted

    Returns:
        Dictionary with cleanup statistics
    """
    backup_files = find_backup_files(directory)

    if not backup_files:
        return {
            "files_found": 0,
            "files_to_remove": 0,
            "files_removed": 0,
            "message": f"No backup files found in {directory}"
        }

    files_to_remove = backup_files[keep_count:] if len(backup_files) > keep_count else []
    files_to_keep = backup_files[:keep_count] if len(backup_files) > keep_count else backup_files

    print(f"📁 Found {len(backup_files)} backup files in {directory}")
    print(f"✅ Keeping {len(files_to_keep)} most recent files:")
    for file in files_to_keep:
        print(f"   • {file.name}")

    if files_to_remove:
        print(f"\n🗑️  Would remove {len(files_to_remove)} old files:")
        for file in files_to_remove:
            print(f"   • {file.name}")

        if not dry_run:
            removed_count = 0
            for file in files_to_remove:
                try:
                    file.unlink()
                    removed_count += 1
                    print(f"   ✅ Removed: {file.name}")
                except Exception as e:
                    print(f"   ❌ Failed to remove {file.name}: {e}")

            return {
                "files_found": len(backup_files),
                "files_to_remove": len(files_to_remove),
                "files_removed": removed_count,
                "message": f"Successfully removed {removed_count} backup files"
            }
        else:
            return {
                "files_found": len(backup_files),
                "files_to_remove": len(files_to_remove),
                "files_removed": 0,
                "message": f"Dry run: Would remove {len(files_to_remove)} files"
            }
    else:
        return {
            "files_found": len(backup_files),
            "files_to_remove": 0,
            "files_removed": 0,
            "message": f"No cleanup needed - only {len(backup_files)} backup files (keeping {keep_count})"
        }


def main():
    """Main entry point for the backup cleanup script."""
    parser = argparse.ArgumentParser(
        description="Clean up old backup files while preserving recent ones",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  python3 scripts/maintenance/cleanup_backups.py --dry-run          # Preview cleanup
  python3 scripts/maintenance/cleanup_backups.py                    # Remove old backups (keep 3)
  python3 scripts/maintenance/cleanup_backups.py --keep 5           # Keep 5 most recent
  python3 scripts/maintenance/cleanup_backups.py --directory config # Specify directory
        """
    )

    parser.add_argument(
        "--directory", "-d",
        default="config",
        help="Directory to clean up (default: config)"
    )
    parser.add_argument(
        "--keep", "-k",
        type=int,
        default=3,
        help="Number of most recent backups to keep (default: 3)"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be deleted without actually deleting"
    )

    args = parser.parse_args()

    print("🧹 Backup File Cleanup")
    print("=" * 40)

    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be deleted")
    else:
        print("⚠️  LIVE MODE - Files will be permanently deleted")

    print(f"📁 Target directory: {args.directory}")
    print(f"📊 Keep count: {args.keep}")
    print()

    result = cleanup_backups(args.directory, args.keep, args.dry_run)

    print("\n📋 SUMMARY:")
    print(f"   • Files found: {result['files_found']}")
    print(f"   • Files to remove: {result['files_to_remove']}")
    print(f"   • Files removed: {result['files_removed']}")
    print(f"   • Message: {result['message']}")


if __name__ == "__main__":
    main()
