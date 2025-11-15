"""
Dynamic Learning System for Winston Feedback

This module provides machine learning capabilities that adapt generation
strategies based on Winston AI detection feedback.

Components:
- PatternLearner: Learns which phrases/patterns consistently fail
- PromptOptimizer: Dynamically adjusts prompts based on feedback
- TemperatureAdvisor: Recommends optimal temperature settings
- SuccessPredictor: Predicts success likelihood before generation
"""

from processing.learning.pattern_learner import PatternLearner
from processing.learning.prompt_optimizer import PromptOptimizer
from processing.learning.temperature_advisor import TemperatureAdvisor
from processing.learning.success_predictor import SuccessPredictor

__all__ = [
    'PatternLearner',
    'PromptOptimizer',
    'TemperatureAdvisor',
    'SuccessPredictor'
]
