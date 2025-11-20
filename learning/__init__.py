"""
Dynamic Learning System for Winston Feedback

This module provides machine learning capabilities that adapt generation
strategies based on Winston AI detection feedback.

Active Components:
- PatternLearner: Learns which phrases/patterns consistently fail (used by orchestrator)
- PromptOptimizer: Dynamically adjusts prompts based on feedback (used by orchestrator)
- TemperatureAdvisor: Recommends optimal temperature settings (used by orchestrator)
- SuccessPredictor: Predicts success likelihood before generation (used by orchestrator)
- SweetSpotAnalyzer: Parameter range optimization from successful generations
- RealismOptimizer: Realism threshold learning
- SubjectivePatternLearner: Pattern learning from Grok evaluations
- WeightLearner: Winston/Realism weighting optimization

Note: For comprehensive quality scoring and parameter correlation analysis,
see the Scoring Module in processing.evaluation, which includes:
  - CompositeScorer (unified quality metrics)
  - SubjectiveEvaluator (human-like assessment)

Removed Modules (Nov 20, 2025):
- fix_strategies (no usage found)
- granular_correlator (test code only)
"""

from learning.pattern_learner import PatternLearner
from learning.prompt_optimizer import PromptOptimizer
from learning.temperature_advisor import TemperatureAdvisor
from learning.success_predictor import SuccessPredictor

__all__ = [
    'PatternLearner',
    'PromptOptimizer',
    'TemperatureAdvisor',
    'SuccessPredictor'
]
