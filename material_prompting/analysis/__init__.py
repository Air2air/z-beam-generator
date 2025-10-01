"""
Material Analysis Module

Comprehensive value analysis and validation system for material properties.

This module ensures that every value for each material is fully analyzed, 
checked and highly accurate through multi-stage validation processes.

Components:
- ValueAnalyzer: Main analysis engine
- PropertyAnalysis: Individual property analysis results
- MaterialAnalysisReport: Complete material analysis reports
- ValidationSource: Reference source tracking
- AccuracyClass: Accuracy classification system
"""

from .analyzer import (
    ValueAnalyzer,
    PropertyAnalysis,
    MaterialAnalysisReport,
    ValidationSource,
    ValidationLevel,
    AccuracyClass
)

__all__ = [
    'ValueAnalyzer',
    'PropertyAnalysis', 
    'MaterialAnalysisReport',
    'ValidationSource',
    'ValidationLevel',
    'AccuracyClass'
]