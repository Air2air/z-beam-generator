#!/usr/bin/env python3
"""
Common Utilities for Z-Beam Optimizer

Shared utility functions used across the optimizer system.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional


def setup_logging(level: str = "INFO", format_string: Optional[str] = None) -> None:
    """
    Set up logging configuration for the optimizer.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string for log messages
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("optimizer.log", mode='a')
        ]
    )


def validate_config(config: Dict[str, Any], required_keys: list) -> Dict[str, Any]:
    """
    Validate configuration dictionary for required keys.

    Args:
        config: Configuration dictionary to validate
        required_keys: List of required configuration keys

    Returns:
        Dict with validation results
    """
    missing_keys = []
    invalid_keys = []

    for key in required_keys:
        if key not in config:
            missing_keys.append(key)
        elif config[key] is None:
            invalid_keys.append(key)

    return {
        'valid': len(missing_keys) == 0 and len(invalid_keys) == 0,
        'missing_keys': missing_keys,
        'invalid_keys': invalid_keys,
        'errors': [f"Missing key: {k}" for k in missing_keys] +
                 [f"Invalid key: {k}" for k in invalid_keys]
    }


def get_project_root() -> Path:
    """Get the project root directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / "requirements.txt").exists() or (current / "pyproject.toml").exists():
            return current
        current = current.parent
    return Path.cwd()


def ensure_directory(path: Path) -> None:
    """Ensure a directory exists, creating it if necessary."""
    path.mkdir(parents=True, exist_ok=True)


def safe_get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Safely get environment variable."""
    return os.getenv(key, default)


def parse_bool_env(key: str, default: bool = False) -> bool:
    """Parse boolean environment variable."""
    value = safe_get_env(key)
    if value is None:
        return default
    return value.lower() in ('true', '1', 'yes', 'on')


def parse_int_env(key: str, default: int = 0) -> int:
    """Parse integer environment variable."""
    value = safe_get_env(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def parse_float_env(key: str, default: float = 0.0) -> float:
    """Parse float environment variable."""
    value = safe_get_env(key)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default
