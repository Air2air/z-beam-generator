"""
Material Generation Recovery and Validation System

This package provides comprehensive tools for validating generated content,
detecting failures, and recovering from component generation issues.

Main modules:
- validator: Content validation and quality scoring
- recovery_runner: Direct component recovery system  
- recovery_system: Main recovery coordination system
- cli: Command-line interfaces for validation and recovery

Usage:
    from recovery import MaterialRecoverySystem, DirectRecoveryRunner
    from recovery.cli import validate_material, recover_components
"""

from .recovery_system import MaterialRecoverySystem, MaterialValidationReport, ComponentResult, ComponentStatus
from .recovery_runner import DirectRecoveryRunner
from .validator import ContentValidator

__version__ = "1.0.0"
__all__ = [
    "MaterialRecoverySystem", 
    "MaterialValidationReport", 
    "ComponentResult", 
    "ComponentStatus",
    "DirectRecoveryRunner",
    "ContentValidator"
]
