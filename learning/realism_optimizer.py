"""
RealismOptimizer - Parameter optimization based on realism feedback.

This module analyzes AI tendencies detected in generated content and suggests
parameter adjustments to improve realism while maintaining AI detection scores.
"""

from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RealismAdjustment:
    """Represents a parameter adjustment to fix realism issues."""
    parameter: str
    current_value: float
    suggested_value: float
    change_amount: float
    rationale: str


class RealismOptimizer:
    """
    Optimizes generation parameters to improve content realism.
    
    Maps detected AI tendencies to specific parameter adjustments based on
    learned patterns and theoretical understanding of how parameters affect output.
    """
    
    # Mapping of AI tendencies to parameter adjustments
    # Format: tendency -> [(parameter, adjustment_direction, magnitude, rationale)]
    TENDENCY_MAPPINGS = {
        'formulaic_phrasing': [
            ('temperature', 'increase', 0.05, "Higher temperature increases lexical variety"),
            ('structural_predictability', 'decrease', 0.1, "Reduce rigid structural patterns"),
        ],
        'unnatural_transitions': [
            ('sentence_rhythm_variation', 'increase', 0.1, "Add natural flow variation"),
            ('structural_predictability', 'decrease', 0.1, "Less predictable structure"),
        ],
        'excessive_enthusiasm': [
            ('emotional_tone', 'decrease', 0.15, "Tone down enthusiasm level"),
            ('opinion_rate', 'decrease', 0.1, "Reduce opinionated statements"),
        ],
        'rigid_structure': [
            ('structural_predictability', 'decrease', 0.15, "Break rigid patterns"),
            ('sentence_rhythm_variation', 'increase', 0.1, "Vary sentence structure"),
            ('imperfection_tolerance', 'increase', 0.1, "Allow structural imperfections"),
        ],
        'overly_polished': [
            ('imperfection_tolerance', 'increase', 0.15, "Allow natural imperfections"),
            ('frequency_penalty', 'decrease', 0.05, "Reduce excessive polish"),
        ],
        'mechanical_tone': [
            ('temperature', 'increase', 0.05, "Add spontaneity"),
            ('trait_frequency', 'increase', 0.1, "More personality traits"),
            ('colloquialism_frequency', 'increase', 0.1, "More casual language"),
        ],
        'repetitive_patterns': [
            ('frequency_penalty', 'increase', 0.1, "Penalize repetition"),
            ('sentence_rhythm_variation', 'increase', 0.1, "Vary patterns"),
        ],
        'forced_transitions': [
            ('structural_predictability', 'decrease', 0.1, "Less forced connections"),
            ('sentence_rhythm_variation', 'increase', 0.1, "Natural flow"),
        ],
        'artificial_symmetry': [
            ('imperfection_tolerance', 'increase', 0.15, "Allow asymmetry"),
            ('structural_predictability', 'decrease', 0.1, "Break symmetrical patterns"),
        ],
        'generic_language': [
            ('temperature', 'increase', 0.05, "More specific word choices"),
            ('technical_intensity', 'increase', 1, "Add specificity (1-3 scale)"),
        ],
    }
    
    def __init__(self):
        """Initialize the RealismOptimizer."""
        self.adjustment_history: List[Dict] = []
    
    def analyze_ai_tendencies(
        self,
        tendencies: List[str],
        current_params: Dict[str, float]
    ) -> List[RealismAdjustment]:
        """
        Analyze detected AI tendencies and suggest parameter adjustments.
        
        Args:
            tendencies: List of AI tendency identifiers
            current_params: Current generation parameters
            
        Returns:
            List of RealismAdjustment objects with suggested changes
        """
        if not tendencies:
            logger.info("No AI tendencies detected - no adjustments needed")
            return []
        
        logger.info(f"Analyzing {len(tendencies)} AI tendencies: {', '.join(tendencies)}")

        required_params = {
            param
            for tendency in tendencies
            if tendency in self.TENDENCY_MAPPINGS
            for param, _, _, _ in self.TENDENCY_MAPPINGS[tendency]
        }
        missing_params = sorted([param for param in required_params if param not in current_params])
        if missing_params:
            raise KeyError(
                f"Current parameters missing required keys for AI tendency analysis: {', '.join(missing_params)}"
            )
        
        # Aggregate adjustments (may have multiple tendencies affecting same parameter)
        param_adjustments: Dict[str, Dict] = {}
        
        for tendency in tendencies:
            if tendency not in self.TENDENCY_MAPPINGS:
                logger.warning(f"Unknown AI tendency: {tendency}")
                continue
            
            mappings = self.TENDENCY_MAPPINGS[tendency]
            for param, direction, magnitude, rationale in mappings:
                if param not in param_adjustments:
                    param_adjustments[param] = {
                        'direction': direction,
                        'magnitude': 0.0,
                        'rationales': []
                    }
                
                # Accumulate magnitude if same direction, otherwise take max
                if param_adjustments[param]['direction'] == direction:
                    param_adjustments[param]['magnitude'] += magnitude
                else:
                    param_adjustments[param]['magnitude'] = max(
                        param_adjustments[param]['magnitude'],
                        magnitude
                    )
                
                param_adjustments[param]['rationales'].append(f"{tendency}: {rationale}")
        
        # Convert to RealismAdjustment objects
        adjustments = []
        for param, adjustment_info in param_adjustments.items():
            current_value = current_params[param]
            
            # Calculate suggested value
            if adjustment_info['direction'] == 'increase':
                suggested_value = min(1.0, current_value + adjustment_info['magnitude'])
            else:  # decrease
                suggested_value = max(0.0, current_value - adjustment_info['magnitude'])
            
            # Special handling for integer parameters (technical_intensity, context_detail_level)
            if param in ['technical_intensity', 'context_detail_level']:
                suggested_value = max(1, min(3, round(suggested_value)))
            
            change_amount = suggested_value - current_value
            
            adjustments.append(RealismAdjustment(
                parameter=param,
                current_value=current_value,
                suggested_value=suggested_value,
                change_amount=change_amount,
                rationale=' | '.join(adjustment_info['rationales'])
            ))
        
        logger.info(f"Generated {len(adjustments)} parameter adjustments")
        return adjustments
    
    def suggest_parameters(
        self,
        current_params: Dict[str, float],
        ai_tendencies: List[str],
        realism_score: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Generate adjusted parameters to improve realism.
        
        Args:
            current_params: Current generation parameters
            ai_tendencies: List of detected AI tendencies
            realism_score: Current realism score (0-10)
            
        Returns:
            Dictionary of adjusted parameters
        """
        adjustments = self.analyze_ai_tendencies(ai_tendencies, current_params)
        
        if not adjustments:
            logger.info("No adjustments needed - returning original parameters")
            return current_params.copy()
        
        # Apply adjustments
        adjusted_params = current_params.copy()
        for adjustment in adjustments:
            adjusted_params[adjustment.parameter] = adjustment.suggested_value
            logger.info(
                f"  {adjustment.parameter}: {adjustment.current_value:.3f} → "
                f"{adjustment.suggested_value:.3f} (Δ{adjustment.change_amount:+.3f})"
            )
        
        # Record adjustment for learning
        self.adjustment_history.append({
            'ai_tendencies': ai_tendencies,
            'realism_score': realism_score,
            'adjustments': adjustments,
            'adjusted_params': adjusted_params.copy()
        })
        
        return adjusted_params
    
    def calculate_combined_score(
        self,
        winston_score: float,
        realism_score: float,
        winston_weight: float = 0.4,
        realism_weight: float = 0.6
    ) -> float:
        """
        Calculate combined optimization score.
        
        Args:
            winston_score: Winston AI detection score (0-100)
            realism_score: Realism score (0-10)
            winston_weight: Weight for Winston score (default 0.4)
            realism_weight: Weight for realism score (default 0.6)
            
        Returns:
            Combined score normalized to 0-100 scale
        """
        # Normalize realism to 0-100 scale
        realism_normalized = realism_score * 10
        
        # Weighted combination
        combined = (winston_score * winston_weight) + (realism_normalized * realism_weight)
        
        return combined
    
    def should_retry(
        self,
        winston_score: float,
        realism_score: float,
        combined_threshold: float = 70.0
    ) -> Tuple[bool, str]:
        """
        Determine if generation should be retried based on scores.
        
        Args:
            winston_score: Winston AI detection score
            realism_score: Realism score (required)
            combined_threshold: Minimum acceptable combined score
            
        Returns:
            (should_retry, reason)
        """
        if realism_score is None:
            raise ValueError("realism_score is required for retry decision")
        
        combined = self.calculate_combined_score(winston_score, realism_score)
        
        if combined < combined_threshold:
            return True, (
                f"Combined score {combined:.1f} below threshold {combined_threshold:.1f} "
                f"(Winston: {winston_score:.1f}, Realism: {realism_score:.1f}/10)"
            )
        
        return False, f"Combined score {combined:.1f} acceptable"
    
    def get_adjustment_summary(self) -> str:
        """Get human-readable summary of recent adjustments."""
        if not self.adjustment_history:
            return "No adjustments made yet"
        
        latest = self.adjustment_history[-1]
        latest_realism_score = latest['realism_score']
        realism_display = (
            f"{latest_realism_score:.1f}/10"
            if latest_realism_score is not None
            else "N/A"
        )
        lines = [
            f"Latest Adjustment (for realism score {realism_display}):",
            f"  AI Tendencies: {', '.join(latest['ai_tendencies'])}",
            "  Parameter Changes:"
        ]
        
        for adj in latest['adjustments']:
            lines.append(
                f"    - {adj.parameter}: {adj.current_value:.3f} → "
                f"{adj.suggested_value:.3f} ({adj.rationale})"
            )
        
        return '\n'.join(lines)
