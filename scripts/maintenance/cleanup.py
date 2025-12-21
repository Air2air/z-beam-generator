#!/usr/bin/env python3
"""
Automated Cleanup Script

Cleans temporary files, caches, and old logs to reduce repository bloat.
Safe to run regularly - only removes expendable files.

Features:
- Removes Python cache files (__pycache__, *.pyc, *.pyo)
- Archives old log files (>30 days)
- Cleans pytest cache
- Removes temporary files (.tmp, .bak, .old)
- Reports disk space saved

Usage:
    # Dry run (show what would be deleted)
    python3 scripts/maintenance/cleanup.py --dry-run
    
    # Full cleanup
    python3 scripts/maintenance/cleanup.py
    
    # Aggressive cleanup (includes output files)
    python3 scripts/maintenance/cleanup.py --aggressive
"""

import argparse
import os
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple


def get_dir_size(path: Path) -> int:
    """Calculate total size of directory in bytes."""
    total = 0
    try:
        for entry in path.rglob('*'):
            if entry.is_file():
                total += entry.stat().st_size
    except (PermissionError, FileNotFoundError):
        pass
    return total


def format_size(bytes: int) -> str:
    """Format bytes as human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.1f} TB"


def clean_python_cache(root_dir: Path, dry_run: bool = False) -> Tuple[int, List[str]]:
    """
    Remove Python cache files.
    
    Returns:
        Tuple of (bytes_freed, files_removed)
    """
    removed = []
    bytes_freed = 0
    
    # Find __pycache__ directories
    for cache_dir in root_dir.rglob('__pycache__'):
        if cache_dir.is_dir():
            size = get_dir_size(cache_dir)
            bytes_freed += size
            removed.append(str(cache_dir.relative_to(root_dir)))
            
            if not dry_run:
                shutil.rmtree(cache_dir, ignore_errors=True)
    
    # Find .pyc and .pyo files
    for pattern in ['**/*.pyc', '**/*.pyo']:
        for pyc_file in root_dir.rglob(pattern.split('/')[-1]):
            if pyc_file.is_file() and pattern.split('/')[-1].endswith(pyc_file.suffix):
                size = pyc_file.stat().st_size
                bytes_freed += size
                removed.append(str(pyc_file.relative_to(root_dir)))
                
                if not dry_run:
                    pyc_file.unlink()
    
    return bytes_freed, removed


def clean_pytest_cache(root_dir: Path, dry_run: bool = False) -> Tuple[int, List[str]]:
    """Remove pytest cache directory."""
    removed = []
    bytes_freed = 0
    
    pytest_cache = root_dir / '.pytest_cache'
    if pytest_cache.exists():
        size = get_dir_size(pytest_cache)
        bytes_freed += size
        removed.append('.pytest_cache/')
        
        if not dry_run:
            shutil.rmtree(pytest_cache, ignore_errors=True)
    
    return bytes_freed, removed


def archive_old_logs(root_dir: Path, days: int = 30, dry_run: bool = False) -> Tuple[int, List[str]]:
    """
    Archive log files older than specified days.
    
    Moves to logs/archive/ instead of deleting.
    """
    archived = []
    bytes_freed = 0
    cutoff_date = datetime.now() - timedelta(days=days)
    
    logs_dir = root_dir / 'logs'
    archive_dir = logs_dir / 'archive'
    
    if not logs_dir.exists():
        return 0, []
    
    # Create archive directory
    if not dry_run and not archive_dir.exists():
        archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Find old log files
    for log_file in logs_dir.glob('*.log'):
        if log_file.is_file():
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            
            if mtime < cutoff_date:
                size = log_file.stat().st_size
                bytes_freed += size
                archived.append(str(log_file.relative_to(root_dir)))
                
                if not dry_run:
                    archive_path = archive_dir / log_file.name
                    shutil.move(str(log_file), str(archive_path))
    
    return bytes_freed, archived


def clean_temp_files(root_dir: Path, dry_run: bool = False) -> Tuple[int, List[str]]:
    """Remove temporary files (.tmp, .bak, .old)."""
    removed = []
    bytes_freed = 0
    
    patterns = ['*.tmp', '*.bak', '*.old']
    
    for pattern in patterns:
        for temp_file in root_dir.rglob(pattern):
            if temp_file.is_file():
                # Skip .git directory
                if '.git' in temp_file.parts:
                    continue
                
                size = temp_file.stat().st_size
                bytes_freed += size
                removed.append(str(temp_file.relative_to(root_dir)))
                
                if not dry_run:
                    temp_file.unlink()
    
    return bytes_freed, removed


def clean_output_files(root_dir: Path, dry_run: bool = False) -> Tuple[int, List[str]]:
    """Remove files in output/ directory (aggressive mode only)."""
    removed = []
    bytes_freed = 0
    
    output_dir = root_dir / 'output'
    if not output_dir.exists():
        return 0, []
    
    for file in output_dir.iterdir():
        if file.is_file():
            size = file.stat().st_size
            bytes_freed += size
            removed.append(str(file.relative_to(root_dir)))
            
            if not dry_run:
                file.unlink()
    
    return bytes_freed, removed


def main():
    """Main cleanup function."""
    parser = argparse.ArgumentParser(
        description='Clean temporary files and caches from Z-Beam Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (see what would be deleted)
  python3 scripts/maintenance/cleanup.py --dry-run
  
  # Standard cleanup
  python3 scripts/maintenance/cleanup.py
  
  # Aggressive cleanup (includes output files)
  python3 scripts/maintenance/cleanup.py --aggressive
        """
    )
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be deleted without deleting')
    parser.add_argument('--aggressive', action='store_true',
                       help='Also clean output/ directory')
    parser.add_argument('--days', type=int, default=30,
                       help='Archive logs older than N days (default: 30)')
    
    args = parser.parse_args()
    
    # Get root directory
    root_dir = Path(__file__).parent.parent.parent
    
    print("=" * 80)
    print("Z-BEAM GENERATOR CLEANUP")
    print("=" * 80)
    print()
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be deleted")
        print()
    
    total_bytes = 0
    total_items = 0
    
    # 1. Clean Python cache
    print("📦 Cleaning Python cache files...")
    bytes_freed, removed = clean_python_cache(root_dir, args.dry_run)
    total_bytes += bytes_freed
    total_items += len(removed)
    print(f"   {'Would remove' if args.dry_run else 'Removed'}: {len(removed)} items ({format_size(bytes_freed)})")
    
    # 2. Clean pytest cache
    print("🧪 Cleaning pytest cache...")
    bytes_freed, removed = clean_pytest_cache(root_dir, args.dry_run)
    total_bytes += bytes_freed
    total_items += len(removed)
    print(f"   {'Would remove' if args.dry_run else 'Removed'}: {len(removed)} items ({format_size(bytes_freed)})")
    
    # 3. Archive old logs
    print(f"📋 Archiving logs older than {args.days} days...")
    bytes_freed, archived = archive_old_logs(root_dir, args.days, args.dry_run)
    total_bytes += bytes_freed
    total_items += len(archived)
    print(f"   {'Would archive' if args.dry_run else 'Archived'}: {len(archived)} files ({format_size(bytes_freed)})")
    
    # 4. Clean temp files
    print("🗑️  Cleaning temporary files (.tmp, .bak, .old)...")
    bytes_freed, removed = clean_temp_files(root_dir, args.dry_run)
    total_bytes += bytes_freed
    total_items += len(removed)
    print(f"   {'Would remove' if args.dry_run else 'Removed'}: {len(removed)} items ({format_size(bytes_freed)})")
    
    # 5. Clean output (aggressive only)
    if args.aggressive:
        print("💣 Cleaning output/ directory (aggressive mode)...")
        bytes_freed, removed = clean_output_files(root_dir, args.dry_run)
        total_bytes += bytes_freed
        total_items += len(removed)
        print(f"   {'Would remove' if args.dry_run else 'Removed'}: {len(removed)} items ({format_size(bytes_freed)})")
    
    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total items: {total_items}")
    print(f"Disk space {'that would be freed' if args.dry_run else 'freed'}: {format_size(total_bytes)}")
    print()
    
    if args.dry_run:
        print("💡 Run without --dry-run to actually perform cleanup")
    else:
        print("✅ Cleanup complete!")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
