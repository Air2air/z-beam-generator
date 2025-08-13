"""
Schema-Driven Validation Module

This module provides schema-driven validation functions.
All validation rules come from JSON schemas in the schemas/ directory.
"""

from .schema_driven_validator import validate_component, ComponentStatus, SchemaDrivenValidator

def parse_terminal_errors(terminal_output: str):
    """Parse terminal output for validation errors."""
    # This can be implemented based on specific terminal output patterns
    # For now, return empty list as placeholder
    return []

# Re-export important classes and functions
__all__ = ['validate_component', 'ComponentStatus', 'SchemaDrivenValidator', 'parse_terminal_errors']