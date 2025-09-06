"""
Z-Beam Cleanup System

This package contains all cleanup-related functionality for the Z-Beam project,
including file cleanup tests, orphaned file detection, and project maintenance tools.

Two interfaces available:
1. CleanupManager (from test_cleanup) - Test-integrated cleanup
2. CleanupManager (from cleanup_manager) - Standalone cleanup system
"""

from .cleanup_manager import CleanupManager

# Import both cleanup interfaces
from .test_cleanup import CleanupManager as TestCleanupManager

# Default to standalone manager for safety and simplicity
__all__ = ["CleanupManager", "TestCleanupManager"]
