"""
Lightweight component validation for Z-Beam generator.
Simple validation without bloat.
"""

from .validator import validate_component, parse_terminal_errors

__all__ = ['validate_component', 'parse_terminal_errors']
