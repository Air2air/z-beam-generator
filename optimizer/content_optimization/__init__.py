"""
Content Optimization Package

Provides modular content optimization functionality previously contained
in a single monolithic file.
"""

from .timeout_utils import run_with_timeout, create_timeout_wrapper
from .content_analyzer import (
    update_content_with_ai_analysis,
    extract_author_info_from_content,
    extract_author_info_from_frontmatter_file,
    update_content_with_comprehensive_analysis
)
from .data_finder import find_material_data
from .sophisticated_optimizer import run_sophisticated_optimization

__all__ = [
    "run_with_timeout",
    "create_timeout_wrapper", 
    "update_content_with_ai_analysis",
    "extract_author_info_from_content",
    "extract_author_info_from_frontmatter_file",
    "update_content_with_comprehensive_analysis",
    "find_material_data",
    "run_sophisticated_optimization"
]
