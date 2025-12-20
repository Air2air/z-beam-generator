"""
Centralized Timestamp Generation Utilities

Provides consistent timestamp formatting across the codebase.
Eliminates duplicate datetime.now() calls with various formats.

Usage:
    from shared.utils.timestamp import get_iso_timestamp, get_backup_timestamp, get_readable_timestamp
    
    # ISO 8601 format (for database storage, API responses)
    iso = get_iso_timestamp()  # "2025-12-19T15:30:45.123456"
    
    # Backup filename format (for file naming)
    backup = get_backup_timestamp()  # "20251219_153045"
    
    # Human-readable format (for reports, logs)
    readable = get_readable_timestamp()  # "December 19, 2025 at 03:30 PM"
    short = get_readable_timestamp(short=True)  # "2025-12-19 15:30:45"
"""

from datetime import datetime
from typing import Optional


def get_iso_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Get ISO 8601 formatted timestamp.
    
    Format: 2025-12-19T15:30:45.123456
    Used for: Database storage, API responses, structured data
    
    Args:
        dt: Specific datetime to format (default: now)
        
    Returns:
        ISO 8601 formatted timestamp string
        
    Example:
        >>> get_iso_timestamp()
        '2025-12-19T15:30:45.123456'
    """
    if dt is None:
        dt = datetime.now()
    return dt.isoformat()


def get_backup_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Get backup filename-safe timestamp.
    
    Format: 20251219_153045
    Used for: Backup file naming, temporary files
    
    Args:
        dt: Specific datetime to format (default: now)
        
    Returns:
        Filename-safe timestamp string
        
    Example:
        >>> get_backup_timestamp()
        '20251219_153045'
        >>> f"Materials.backup_{get_backup_timestamp()}.yaml"
        'Materials.backup_20251219_153045.yaml'
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime('%Y%m%d_%H%M%S')


def get_readable_timestamp(dt: Optional[datetime] = None, short: bool = False) -> str:
    """
    Get human-readable timestamp.
    
    Formats:
        short=False: "December 19, 2025 at 03:30 PM"
        short=True: "2025-12-19 15:30:45"
    
    Used for: Reports, user-facing messages, documentation
    
    Args:
        dt: Specific datetime to format (default: now)
        short: Use short format (default: False)
        
    Returns:
        Human-readable timestamp string
        
    Example:
        >>> get_readable_timestamp()
        'December 19, 2025 at 03:30 PM'
        >>> get_readable_timestamp(short=True)
        '2025-12-19 15:30:45'
    """
    if dt is None:
        dt = datetime.now()
    
    if short:
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return dt.strftime('%B %d, %Y at %I:%M %p')


def get_timestamp(format_type: str = 'iso', dt: Optional[datetime] = None) -> str:
    """
    Get timestamp in specified format (convenience function).
    
    Args:
        format_type: 'iso', 'backup', or 'readable' (default: 'iso')
        dt: Specific datetime to format (default: now)
        
    Returns:
        Formatted timestamp string
        
    Example:
        >>> get_timestamp('iso')
        '2025-12-19T15:30:45.123456'
        >>> get_timestamp('backup')
        '20251219_153045'
        >>> get_timestamp('readable')
        'December 19, 2025 at 03:30 PM'
    """
    if format_type == 'iso':
        return get_iso_timestamp(dt)
    elif format_type == 'backup':
        return get_backup_timestamp(dt)
    elif format_type == 'readable':
        return get_readable_timestamp(dt)
    else:
        raise ValueError(f"Unknown format_type: {format_type}. Use 'iso', 'backup', or 'readable'")
