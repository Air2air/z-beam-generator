"""
Realism Evaluation Integration Facade

Mirrors the successful WinstonIntegration architecture to provide:
- Centralized realism evaluation logic
- Adaptive threshold management
- Database logging and feedback analysis
- Parameter adjustment suggestions
- Clear error handling and fail-fast behavior

This facade replaces scattered realism checks with a single, testable interface.

Architecture inspired by: processing/detection/winston_integration.py
Author: System
Created: November 18, 2025
"""

import logging
from typing import Dict, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class RealismIntegration:
    """
    Unified facade for realism evaluation and feedback.
    
    Responsibilities:
    - Manage adaptive realism thresholds (4.0 → 5.5 → 6.5 → 7.0)
    - Coordinate realism evaluation with SubjectiveEvaluator
    - Log evaluation results to feedback database
    - Provide parameter adjustment suggestions
    - Track improvement trends
    
    Benefits:
    - Single source of truth for realism behavior
    - Easy to mock for testing
    - Clear threshold progression logic
    - Centralized feedback collection
    """
    
    def __init__(
        self,
        api_client=None,
        feedback_db=None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Realism integration.
        
        Args:
            api_client: Grok API client (REQUIRED - fail-fast)
            feedback_db: WinstonFeedbackDatabase instance (optional)
            config: Configuration dict with realism settings
            
        Raises:
            ValueError: If api_client is None (fail-fast architecture)
        """
        if api_client is None:
            raise ValueError(
                "RealismIntegration requires api_client. "
                "Cannot operate without Grok API per fail-fast architecture."
            )
        
        self.api_client = api_client
        self.feedback_db = feedback_db
        self.config = config or {}
        
        # Initialize evaluator (lazy to avoid circular imports)
        self._evaluator = None
        
        # Initialize optimizer (lazy)
        self._optimizer = None
        
        # Track evaluation history for trend analysis
        self.evaluation_history = []
        
        logger.info("RealismIntegration initialized with adaptive thresholds")
    
    @property
    def evaluator(self):
        """Lazy-load SubjectiveEvaluator to avoid circular imports"""
        if self._evaluator is None:
            from processing.subjective import SubjectiveEvaluator
            self._evaluator = SubjectiveEvaluator(
                api_client=self.api_client,
                quality_threshold=7.0,  # Max threshold (not enforced here)
                verbose=False
            )
        return self._evaluator
    
    @property
    def optimizer(self):
        """Lazy-load RealismOptimizer for parameter suggestions"""
        if self._optimizer is None:
            try:
                from processing.learning.realism_optimizer import RealismOptimizer
                self._optimizer = RealismOptimizer()
            except Exception as e:
                logger.warning(f"RealismOptimizer unavailable: {e}")
        return self._optimizer
    
    def get_adaptive_threshold(self, attempt: int) -> float:
        """
        Get adaptive realism threshold for current attempt.
        
        Progressive thresholds allow early iterations to pass while
        maintaining quality standards on final attempts.
        
        Args:
            attempt: Current attempt number (1-based)
            
        Returns:
            float: Threshold value (0-10 scale)
                - Attempt 1: 4.0 (lenient - accept reasonable content)
                - Attempt 2: 5.5 (moderate quality)
                - Attempt 3: 6.5 (good quality)
                - Attempt 4+: 7.0 (high quality bar)
        """
        if attempt == 1:
            return 4.0
        elif attempt == 2:
            return 5.5
        elif attempt == 3:
            return 6.5
        else:
            return 7.0
    
    def evaluate_and_log(
        self,
        text: str,
        material: str,
        component_type: str,
        attempt: int,
        current_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate content realism and log results.
        
        This is the primary method for all realism evaluation operations.
        Mirrors WinstonIntegration.detect_and_log() architecture.
        
        Args:
            text: Generated text to evaluate
            material: Material name
            component_type: Component type
            attempt: Current attempt number
            current_params: Current generation parameters
            
        Returns:
            Dict with:
            - realism_score: float (0-10)
            - threshold: float (adaptive threshold for this attempt)
            - passes_gate: bool (score >= threshold)
            - evaluation_result: SubjectiveEvaluationResult object
            - ai_tendencies: Dict (detected AI patterns)
            - suggested_adjustments: Dict (parameter recommendations)
            - voice_authenticity: float (0-10, if available)
            - tonal_consistency: float (0-10, if available)
        """
        # Get adaptive threshold for this attempt
        threshold = self.get_adaptive_threshold(attempt)
        
        # Run realism evaluation
        try:
            evaluation_result = self.evaluator.evaluate(
                content=text,
                material_name=material,
                component_type=component_type
            )
        except Exception as e:
            logger.error(f"❌ Realism evaluation failed: {e}")
            # Fail gracefully - return neutral result
            return {
                'realism_score': 5.0,
                'threshold': threshold,
                'passes_gate': False,
                'evaluation_result': None,
                'ai_tendencies': {},
                'suggested_adjustments': None,
                'error': str(e)
            }
        
        realism_score = evaluation_result.overall_score
        passes_gate = realism_score >= threshold
        
        # Extract dimension scores
        voice_authenticity = None
        tonal_consistency = None
        ai_tendencies = {}
        
        for dim_score in evaluation_result.dimension_scores:
            if dim_score.dimension.value == 'voice_authenticity':
                voice_authenticity = dim_score.score
            elif dim_score.dimension.value == 'tonal_consistency':
                tonal_consistency = dim_score.score
        
        # Calculate AI tendencies from dimension scores
        for dim_score in evaluation_result.dimension_scores:
            dim = dim_score.dimension.value
            # Lower score = stronger AI tendency
            tendency_strength = max(0, 7.0 - dim_score.score) / 7.0
            
            if dim == 'voice_authenticity':
                ai_tendencies['generic_language'] = tendency_strength
            elif dim == 'tonal_consistency':
                ai_tendencies['unnatural_transitions'] = tendency_strength
            elif dim == 'human_likeness':
                ai_tendencies['ai_patterns'] = tendency_strength
        
        # Get parameter adjustment suggestions if score is low
        suggested_adjustments = None
        if not passes_gate and self.optimizer and ai_tendencies:
            try:
                suggested_adjustments = self.optimizer.suggest_parameters(
                    ai_tendencies=ai_tendencies,
                    current_params=current_params
                )
            except Exception as e:
                logger.warning(f"Failed to get realism adjustments: {e}")
        
        # Log to database if available
        if self.feedback_db and realism_score is not None:
            try:
                self.feedback_db.log_realism_learning(
                    topic=material,
                    component_type=component_type,
                    ai_tendencies=ai_tendencies,
                    suggested_params=suggested_adjustments or {},
                    realism_score=realism_score,
                    success=passes_gate
                )
            except Exception as e:
                logger.warning(f"Failed to log realism result: {e}")
        
        # Track in history for trend analysis
        self.evaluation_history.append({
            'attempt': attempt,
            'score': realism_score,
            'threshold': threshold,
            'passed': passes_gate
        })
        
        # Log result
        if passes_gate:
            logger.info(
                f"✅ Realism passed: {realism_score:.1f}/10 >= {threshold}/10 (attempt {attempt})"
            )
        else:
            logger.warning(
                f"❌ Realism score below threshold: {realism_score:.1f}/10 < {threshold}/10 (attempt {attempt})"
            )
        
        return {
            'realism_score': realism_score,
            'threshold': threshold,
            'passes_gate': passes_gate,
            'evaluation_result': evaluation_result,
            'ai_tendencies': ai_tendencies,
            'suggested_adjustments': suggested_adjustments,
            'voice_authenticity': voice_authenticity,
            'tonal_consistency': tonal_consistency
        }
    
    def get_improvement_trend(self) -> Dict[str, Any]:
        """
        Analyze improvement trend across attempts.
        
        Returns:
            Dict with:
            - improving: bool (scores trending up)
            - stuck: bool (no improvement over 2+ attempts)
            - avg_score: float (average across attempts)
            - score_delta: float (change from first to last)
        """
        if len(self.evaluation_history) < 2:
            return {
                'improving': False,
                'stuck': False,
                'avg_score': self.evaluation_history[0]['score'] if self.evaluation_history else 0.0,
                'score_delta': 0.0
            }
        
        scores = [h['score'] for h in self.evaluation_history]
        
        # Check if improving (last score > first score)
        improving = scores[-1] > scores[0]
        
        # Check if stuck (last 2 scores within 0.5 points)
        stuck = False
        if len(scores) >= 2:
            stuck = abs(scores[-1] - scores[-2]) < 0.5
        
        return {
            'improving': improving,
            'stuck': stuck,
            'avg_score': sum(scores) / len(scores),
            'score_delta': scores[-1] - scores[0]
        }
    
    def should_trigger_fresh_regeneration(self) -> bool:
        """
        Determine if fresh regeneration should be triggered.
        
        Mirrors Winston stuck pattern detection but for realism scores.
        
        Returns:
            True if scores are stuck and not improving
        """
        if len(self.evaluation_history) < 3:
            return False
        
        trend = self.get_improvement_trend()
        return trend['stuck'] and not trend['improving']
