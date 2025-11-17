"""
Subjective Quality Assessment Module

Provides comprehensive subjective quality evaluation for generated content:
- Grok AI 6-dimension evaluation (clarity, professionalism, technical accuracy, etc.)
- Pattern validation (lightweight rule-based checks)
- Automated parameter tuning based on evaluation feedback

Components:
- evaluator.py: Grok AI multi-dimensional quality assessment
- validator.py: Pattern-based validation rules
- parameter_tuner.py: Dimension-based parameter adjustment

Author: System
Created: November 16, 2025
"""

from processing.subjective.evaluator import SubjectiveEvaluator
from processing.subjective.validator import SubjectiveValidator
from processing.subjective.parameter_tuner import (
    SubjectiveParameterTuner,
    ParameterAdjustment
)

__all__ = [
    'SubjectiveEvaluator',
    'SubjectiveValidator',
    'SubjectiveParameterTuner',
    'ParameterAdjustment'
]
