"""
Dynamic Learning System for Winston Feedback

This module provides machine learning capabilities that adapt generation
strategies based on Winston AI detection feedback.

Components:
- PatternLearner: Learns which phrases/patterns consistently fail
- PromptOptimizer: Dynamically adjusts prompts based on feedback
- TemperatureAdvisor: Recommends optimal temperature settings
- SuccessPredictor: Predicts success likelihood before generation
- GranularParameterCorrelator: Fine-grained parameter correlation analysis

Note: For comprehensive quality scoring and parameter correlation analysis,
see the Scoring Module in processing.evaluation, which includes:
  - CompositeScorer (unified quality metrics)
  - GranularParameterCorrelator (parameter-quality relationships)
  - SubjectiveEvaluator (human-like assessment)
"""

from learning.pattern_learner import PatternLearner
from learning.prompt_optimizer import PromptOptimizer
from learning.temperature_advisor import TemperatureAdvisor
from learning.success_predictor import SuccessPredictor
from learning.granular_correlator import (
    GranularParameterCorrelator,
    ParameterCorrelation,
    ParameterInteraction
)

__all__ = [
    'PatternLearner',
    'PromptOptimizer',
    'TemperatureAdvisor',
    'SuccessPredictor',
    'GranularParameterCorrelator',
    'ParameterCorrelation',
    'ParameterInteraction'
]
