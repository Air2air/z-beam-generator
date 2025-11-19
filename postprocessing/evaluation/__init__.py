"""
Scoring Module - Comprehensive Quality Assessment and Parameter Correlation

This unified scoring module provides:

1. Quality Scoring:
   - CompositeScorer: Combines Winston (60%) + Subjective (30%) + Readability (10%)
   - SubjectiveEvaluator: Human-like quality assessment
   
2. Parameter Analysis:
   - GranularParameterCorrelator: Fine-grained correlation analysis
   - Per-parameter sensitivity tracking
   - Optimal range identification
   - Statistical significance testing
   
3. Relationship Discovery:
   - Non-linear relationship detection (polynomial, logarithmic)
   - 2-way and 3-way parameter interactions
   - Synergistic effect identification
   
4. Adjustment Recommendations:
   - Precise parameter tuning (0.01 increments)
   - Expected impact calculations
   - Confidence-weighted suggestions

Key Features:
- Highly granular scoring enables precise parameter adjustments
- Statistical rigor ensures reliable correlations
- Interaction detection reveals synergistic effects
- Automated recommendation engine for optimization
"""

from .subjective_evaluator import SubjectiveEvaluator, evaluate_content, SubjectiveEvaluationResult
from .composite_scorer import CompositeScorer

__all__ = [
    'SubjectiveEvaluator',
    'evaluate_content',
    'SubjectiveEvaluationResult',
    'CompositeScorer'
]
