"""
AI Detection Configuration Optimization Module

Provides comprehensive optimization of AI detection settings using DeepSeek analysis
of Winston AI results to improve content generation quality.

Module Components:
- config_optimizer: Main optimization class and workflow
- prompt_optimizer: DeepSeek prompt generation and interaction
- validation: Configuration validation and backup/restore
- utils: Analysis utilities and data processing functions
"""

from .config_optimizer import AIDetectionConfigOptimizer
from .validation import ConfigValidator
from .utils import AnalysisUtils

__all__ = [
    "AIDetectionConfigOptimizer",
    "ConfigValidator", 
    "AnalysisUtils"
]
