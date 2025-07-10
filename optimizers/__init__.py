"""
Optimizers package - Simplified
"""

# Remove the base_optimizer import and just import the simple functions
from .simple_optimizers import apply_writing_style, add_technical_depth, humanize_content

__all__ = [
    'apply_writing_style',
    'add_technical_depth', 
    'humanize_content'
]