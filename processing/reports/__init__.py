"""
Generation Report System
========================

This module provides comprehensive reporting for content generation operations,
including batch tests, quality analysis, and parameter correlation studies.

Available Report Types:
- GenerationReport: Single material generation with full metrics
- BatchReport: Multiple materials with comparative analysis
- QualityReport: Quality scoring breakdown and interpretation
- ParameterReport: Parameter correlation and optimization insights
"""

from .generation_report import GenerationReport, BatchReport
from .quality_report import QualityReport
from .parameter_report import ParameterReport

__all__ = [
    'GenerationReport',
    'BatchReport',
    'QualityReport',
    'ParameterReport',
]
