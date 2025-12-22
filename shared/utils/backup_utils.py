"""
Backup Utilities - Centralized file backup operations

Consolidates 69+ backup creation patterns across the codebase into
standardized, reusable functions.

Created: December 21, 2025
Purpose: Code consolidation and DRY compliance
"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional


def create_backup(
    source_path: Path,
    backup_dir: Optional[Path] = None,
    timestamp: bool = True,
    suffix: str = ".backup"
) -> Path:
    """
    Create backup copy of a file with timestamp.
    
    Args:
        source_path: File to backup
        backup_dir: Directory for backup (default: same as source)
        timestamp: Add timestamp to backup filename (default: True)
        suffix: Backup file suffix (default: .backup)
    
    Returns:
        Path to created backup file
    
    Raises:
        FileNotFoundError: If source file doesn't exist
        OSError: If backup creation fails
    
    Examples:
        >>> # Simple backup: Materials.yaml → Materials.backup.yaml
        >>> backup_path = create_backup(Path('data/Materials.yaml'))
        
        >>> # Timestamped backup: Materials.yaml → Materials_20251221_143022.backup.yaml
        >>> backup_path = create_backup(Path('data/Materials.yaml'), timestamp=True)
        
        >>> # Custom location: Materials.yaml → backups/Materials_20251221.yaml
        >>> backup_path = create_backup(
        ...     Path('data/Materials.yaml'),
        ...     backup_dir=Path('backups'),
        ...     suffix=''
        ... )
    """
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source_path}")
    
    # Determine backup directory
    if backup_dir is None:
        backup_dir = source_path.parent
    else:
        backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Build backup filename
    stem = source_path.stem
    ext = source_path.suffix
    
    if timestamp:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{stem}_{ts}{suffix}{ext}"
    else:
        backup_name = f"{stem}{suffix}{ext}"
    
    backup_path = backup_dir / backup_name
    
    # Copy with metadata preservation
    shutil.copy2(source_path, backup_path)
    
    return backup_path


def create_backup_simple(source_path: Path, suffix: str = ".bak") -> Path:
    """
    Create simple backup in same directory without timestamp.
    
    Args:
        source_path: File to backup
        suffix: Backup suffix (default: .bak)
    
    Returns:
        Path to backup file
    
    Example:
        >>> # Materials.yaml → Materials.yaml.bak
        >>> backup = create_backup_simple(Path('data/Materials.yaml'))
    """
    return create_backup(source_path, timestamp=False, suffix=suffix)


def create_timestamped_backup(source_path: Path, backup_dir: Optional[Path] = None) -> Path:
    """
    Create timestamped backup with standard naming.
    
    Args:
        source_path: File to backup
        backup_dir: Optional backup directory
    
    Returns:
        Path to backup file
    
    Example:
        >>> # Materials.yaml → Materials_backup_20251221_143022.yaml
        >>> backup = create_timestamped_backup(Path('data/Materials.yaml'))
    """
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source_path}")
    
    if backup_dir is None:
        backup_dir = source_path.parent
    else:
        backup_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"{source_path.stem}_backup_{timestamp}{source_path.suffix}"
    backup_path = backup_dir / backup_name
    
    shutil.copy2(source_path, backup_path)
    
    return backup_path


def restore_backup(backup_path: Path, target_path: Optional[Path] = None) -> Path:
    """
    Restore file from backup.
    
    Args:
        backup_path: Backup file to restore
        target_path: Target location (auto-detected if None)
    
    Returns:
        Path to restored file
    
    Raises:
        FileNotFoundError: If backup doesn't exist
        ValueError: If target path can't be determined
    
    Example:
        >>> # Restore Materials_backup_20251221.yaml → Materials.yaml
        >>> restored = restore_backup(Path('data/Materials_backup_20251221.yaml'))
    """
    if not backup_path.exists():
        raise FileNotFoundError(f"Backup file not found: {backup_path}")
    
    if target_path is None:
        # Try to auto-detect original filename
        name = backup_path.name
        if '_backup_' in name:
            # Remove timestamp: Materials_backup_20251221_143022.yaml → Materials.yaml
            original_name = name.split('_backup_')[0] + backup_path.suffix
        elif name.endswith('.bak'):
            # Remove .bak: Materials.yaml.bak → Materials.yaml
            original_name = name[:-4]
        elif name.endswith('.backup'):
            # Remove .backup: Materials.backup.yaml → Materials.yaml
            original_name = name.replace('.backup', '')
        else:
            raise ValueError(f"Cannot auto-detect target path from: {backup_path}")
        
        target_path = backup_path.parent / original_name
    
    shutil.copy2(backup_path, target_path)
    
    return target_path


def list_backups(file_path: Path, backup_dir: Optional[Path] = None) -> list[Path]:
    """
    List all backups for a given file.
    
    Args:
        file_path: Original file
        backup_dir: Backup directory (default: same as file)
    
    Returns:
        List of backup file paths, sorted by modification time (newest first)
    
    Example:
        >>> backups = list_backups(Path('data/Materials.yaml'))
        >>> if backups:
        ...     latest = backups[0]
        ...     print(f"Latest backup: {latest}")
    """
    if backup_dir is None:
        backup_dir = file_path.parent
    
    if not backup_dir.exists():
        return []
    
    stem = file_path.stem
    pattern = f"{stem}_backup_*{file_path.suffix}"
    
    backups = sorted(
        backup_dir.glob(pattern),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    # Also check for simple .bak and .backup files
    simple_backups = [
        backup_dir / f"{stem}.bak",
        backup_dir / f"{stem}.backup{file_path.suffix}",
        backup_dir / f"{file_path.name}.bak"
    ]
    
    backups.extend([p for p in simple_backups if p.exists()])
    
    return backups


def cleanup_old_backups(file_path: Path, keep_count: int = 5, backup_dir: Optional[Path] = None) -> int:
    """
    Remove old backups, keeping only the most recent ones.
    
    Args:
        file_path: Original file
        keep_count: Number of backups to keep (default: 5)
        backup_dir: Backup directory (default: same as file)
    
    Returns:
        Number of backups deleted
    
    Example:
        >>> # Keep only 3 most recent backups
        >>> deleted = cleanup_old_backups(Path('data/Materials.yaml'), keep_count=3)
        >>> print(f"Deleted {deleted} old backups")
    """
    backups = list_backups(file_path, backup_dir)
    
    if len(backups) <= keep_count:
        return 0
    
    to_delete = backups[keep_count:]
    deleted_count = 0
    
    for backup in to_delete:
        try:
            backup.unlink()
            deleted_count += 1
        except OSError:
            pass
    
    return deleted_count
