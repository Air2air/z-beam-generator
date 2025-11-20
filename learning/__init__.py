"""
Dynamic Learning System for Winston Feedback

This module provides machine learning capabilities that adapt generation
strategies based on Winston AI detection feedback.

Active Components (4 core modules):
- SweetSpotAnalyzer: Parameter range optimization from successful generations
- SubjectivePatternLearner: Pattern learning from Grok evaluations
- RealismOptimizer: Realism threshold learning
- WeightLearner: Winston/Realism weighting optimization

Note: For comprehensive quality scoring and parameter correlation analysis,
see the Scoring Module in postprocessing.evaluation, which includes:
  - CompositeScorer (unified quality metrics)
  - SubjectiveEvaluator (human-like assessment)

Archived Modules (Nov 20, 2025 - Phase 2):
Phase 1 Removals:
- fix_strategies (no usage found)
- granular_correlator (test code only)

Phase 2 Archival (orchestrator-only modules):
- pattern_learner (used only by --validate-content)
- temperature_advisor (used only by --validate-content)
- prompt_optimizer (used only by --validate-content)
- success_predictor (used only by --validate-content)
- fix_strategy_manager (used only by --validate-content)

Total Reduction: 12 → 4 modules (67% reduction)
"""

# Core active learning modules are imported directly where needed:
# - sweet_spot_analyzer (used in shared/commands/generation.py)
# - subjective_pattern_learner (used in postprocessing/evaluation/subjective_evaluator.py)
# - realism_optimizer (used in shared/commands/global_evaluation.py)
# - weight_learner (used in postprocessing/evaluation/composite_scorer.py)

__all__ = []  # No public exports - modules imported directly where needed
