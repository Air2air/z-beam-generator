"""
Composite Quality Scorer

Combines multiple evaluation dimensions into unified quality metric.

WEIGHT LEARNING ARCHITECTURE:
Weights are dynamically learned from historical correlation data by WeightLearner.
The learning system analyzes which metric combinations best predict actual success,
then optimizes weights per material/component context.

Static config weights (config.yaml) are ONLY fallback defaults when insufficient
data exists. System learns optimal weights as generations accumulate.

Example learned weights:
- Winston: 0.65 (micros), 0.50 (FAQs) - varies by component
- Subjective: 0.25 (Steel), 0.35 (Aluminum) - varies by material
- Readability: 0.10 global baseline

This enables context-specific optimization instead of one-size-fits-all weighting.
"""

from typing import Dict, Any, Optional
import logging
from generation.config.config_loader import get_config
from learning.weight_learner import WeightLearner

logger = logging.getLogger(__name__)


class CompositeScorer:
    """
    Calculate composite quality score from multiple evaluation dimensions.
    
    Combines:
    - Winston human_score (0-100): AI detection resistance
    - Subjective overall_score (0-10): Human quality assessment  
    - Readability score (0-100): Comprehension ease
    
    DYNAMIC WEIGHT LEARNING:
    Uses WeightLearner to get optimal weights from historical correlation data.
    Weights adapt per material/component context for maximum prediction accuracy.
    
    Static config weights (config.yaml) are ONLY fallback defaults when
    insufficient historical data exists (< 50 generations).
    
    Missing scores handled by redistributing weight to available dimensions,
    always prioritizing Winston as the primary metric.
    """
    
    def __init__(
        self,
        weight_learner: Optional[WeightLearner] = None,
        winston_weight: Optional[float] = None,
        subjective_weight: Optional[float] = None,
        readability_weight: Optional[float] = None
    ):
        """
        Initialize composite scorer with dynamic weight learning.
        
        Args:
            weight_learner: WeightLearner instance for dynamic optimization (recommended)
            winston_weight: Manual weight override for Winston (not recommended)
            subjective_weight: Manual weight override for subjective (not recommended)
            readability_weight: Manual weight override for readability (not recommended)
            
        Note: Manual weight overrides disable learning. Only use for testing.
        
        Raises:
            ValueError: If manual weights don't sum to 1.0
        """
        # Initialize weight learner (or use provided instance)
        self.weight_learner = weight_learner or WeightLearner()
        
        # Manual overrides (for testing only - disables learning)
        self.manual_winston = winston_weight
        self.manual_subjective = subjective_weight
        self.manual_readability = readability_weight
        
        # If manual overrides provided, validate they sum to 1.0
        if all(w is not None for w in [winston_weight, subjective_weight, readability_weight]):
            total = winston_weight + subjective_weight + readability_weight
            if not 0.99 <= total <= 1.01:
                raise ValueError(
                    f"Manual weights must sum to 1.0, got {total} "
                    f"({winston_weight} + {subjective_weight} + {readability_weight})"
                )
            logger.warning(
                "⚠️  Manual weight overrides active - LEARNING DISABLED. "
                f"winston={winston_weight:.1%}, "
                f"subjective={subjective_weight:.1%}, "
                f"readability={readability_weight:.1%}"
            )
        else:
            logger.info("CompositeScorer initialized with dynamic weight learning")
    
    def calculate(
        self,
        winston_human_score: float,
        subjective_overall_score: Optional[float] = None,
        readability_score: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate composite quality score using learned or manual weights.
        
        Weights are UNIVERSAL (not context-specific). Quality is quality
        regardless of material or component - the system learns ONE optimal
        weight set that maximizes prediction accuracy across all generations.
        
        ALL scores on 0-1.0 normalized scale for consistency.
        
        Args:
            winston_human_score: Winston human score (0-1.0 normalized, NOT 0-100)
            subjective_overall_score: Subjective evaluation (0-10 scale, will be normalized)
            readability_score: Flesch reading ease (0-100 scale, will be normalized)
            
        Returns:
            Dict with:
            - composite_score: Final weighted score (0-1.0 normalized)
            - winston_contribution: Points from Winston (0-1.0)
            - subjective_contribution: Points from subjective (0-1.0)
            - readability_contribution: Points from readability (0-1.0)
            - weights_used: Actual weights after redistribution
            - weights_source: "manual" or "learned:global" or "default"
            - all_dimensions_present: Boolean flag
            
        Raises:
            ValueError: If scores out of expected range
        """
        # Validate Winston score (required) - now expects 0-1.0 normalized
        if not 0.0 <= winston_human_score <= 1.0:
            raise ValueError(
                f"winston_human_score must be 0-1.0 normalized, got {winston_human_score}"
            )
        
        # Validate and normalize optional scores
        if subjective_overall_score is not None:
            if not 0.0 <= subjective_overall_score <= 10.0:
                raise ValueError(
                    f"subjective_overall_score must be 0-10, got {subjective_overall_score}"
                )
            # Normalize to 0-1.0 (divide by 10)
            subjective_normalized = subjective_overall_score / 10.0
        else:
            subjective_normalized = None
        
        if readability_score is not None:
            if not 0.0 <= readability_score <= 100.0:
                raise ValueError(
                    f"readability_score must be 0-100, got {readability_score}"
                )
            # Normalize to 0-1.0 (divide by 100)
            readability_normalized = readability_score / 100.0
        else:
            readability_normalized = None
        
        # Get weights (manual overrides or learned from data)
        if all(w is not None for w in [self.manual_winston, self.manual_subjective, self.manual_readability]):
            # Use manual overrides (testing only)
            winston_weight = self.manual_winston
            subjective_weight = self.manual_subjective
            readability_weight = self.manual_readability
            weights_source = "manual"
        else:
            # Use learned weights from WeightLearner (universal, not context-specific)
            winston_weight, subjective_weight, readability_weight = \
                self.weight_learner.get_optimal_weights()
            
            # Determine if learned or default
            # (WeightLearner falls back to defaults if < 50 samples)
            weights_source = "learned:global"  # Could be default fallback internally
        
        # Handle missing scores by redistributing weights
        # Priority: Always redistribute to Winston (primary metric)
        available_weights = {
            'winston': winston_weight,
            'subjective': subjective_weight if subjective_normalized is not None else 0.0,
            'readability': readability_weight if readability_normalized is not None else 0.0
        }
        
        # Calculate missing weight and add to Winston
        total_available = sum(available_weights.values())
        if total_available < 1.0:
            missing_weight = 1.0 - total_available
            available_weights['winston'] += missing_weight
            logger.debug(
                f"Redistributed {missing_weight:.1%} missing weight to Winston "
                f"(subjective={'present' if subjective_normalized else 'missing'}, "
                f"readability={'present' if readability_normalized else 'missing'})"
            )
        
        # Calculate contributions (each dimension * weight) - ALL on 0-1.0 scale now
        winston_contrib = winston_human_score * available_weights['winston']
        
        subjective_contrib = (
            subjective_normalized * available_weights['subjective']
            if subjective_normalized is not None
            else 0.0
        )
        
        readability_contrib = (
            readability_normalized * available_weights['readability']
            if readability_normalized is not None
            else 0.0
        )
        
        # Sum for composite score
        composite = winston_contrib + subjective_contrib + readability_contrib
        
        # Check if all dimensions present
        all_present = (
            subjective_normalized is not None and 
            readability_score is not None
        )
        
        result = {
            'composite_score': round(composite, 2),
            'winston_contribution': round(winston_contrib, 2),
            'subjective_contribution': round(subjective_contrib, 2),
            'readability_contribution': round(readability_contrib, 2),
            'weights_used': {
                'winston': round(available_weights['winston'], 3),
                'subjective': round(available_weights['subjective'], 3),
                'readability': round(available_weights['readability'], 3)
            },
            'weights_source': weights_source,
            'all_dimensions_present': all_present,
            'dimensions_available': {
                'winston': True,  # Always available (required)
                'subjective': subjective_normalized is not None,
                'readability': readability_score is not None
            }
        }
        
        logger.debug(
            f"Composite score: {result['composite_score']:.2f} "
            f"(winston={winston_contrib:.1f}, "
            f"subjective={subjective_contrib:.1f}, "
            f"readability={readability_contrib:.1f}) "
            f"[{weights_source}]"
        )
        
        return result
    
    def calculate_from_detection_result(
        self,
        detection_result: Dict[str, Any],
        subjective_evaluation: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Convenience method to calculate from database result objects.
        
        Args:
            detection_result: Dict from detection_results table with keys:
                - human_score: Winston human score
                - readability_score: Flesch reading ease (optional)
            subjective_evaluation: Dict from subjective_evaluations table with keys:
                - overall_score: Subjective quality score (optional)
                
        Returns:
            Composite score result dict (same as calculate())
        """
        winston_score = detection_result['human_score']
        readability_score = detection_result.get('readability_score')
        subjective_score = (
            subjective_evaluation['overall_score']
            if subjective_evaluation
            else None
        )
        
        return self.calculate(
            winston_human_score=winston_score,
            subjective_overall_score=subjective_score,
            readability_score=readability_score
        )
    
    def interpret_score(self, composite_score: float) -> Dict[str, str]:
        """
        Interpret composite quality score with human-readable assessment.
        
        Args:
            composite_score: Composite quality score (0-100)
            
        Returns:
            Dict with:
            - level: 'excellent', 'good', 'acceptable', 'poor', 'failing'
            - description: Human-readable interpretation
            - recommendation: Actionable next step
        """
        if composite_score >= 85:
            return {
                'level': 'excellent',
                'description': 'Exceptional quality across all dimensions',
                'recommendation': 'Deploy immediately - this is top-tier content'
            }
        elif composite_score >= 75:
            return {
                'level': 'good',
                'description': 'High quality with minor improvement opportunities',
                'recommendation': 'Acceptable for deployment - consider minor refinements'
            }
        elif composite_score >= 65:
            return {
                'level': 'acceptable',
                'description': 'Meets minimum standards but has clear weaknesses',
                'recommendation': 'Review individual dimensions - improve lowest scoring area'
            }
        elif composite_score >= 50:
            return {
                'level': 'poor',
                'description': 'Below acceptable standards - significant issues present',
                'recommendation': 'Retry generation with adjusted parameters'
            }
        else:
            return {
                'level': 'failing',
                'description': 'Unacceptable quality - fundamental problems detected',
                'recommendation': 'Review prompt and parameters - major changes needed'
            }
