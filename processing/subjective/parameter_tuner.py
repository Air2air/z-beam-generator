"""
Subjective Evaluation Parameter Tuner

Automatically adjusts generation parameters based on Grok AI subjective evaluation feedback.
Uses dimension scores to make granular, targeted parameter adjustments.

Author: System
Created: November 16, 2025
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ParameterAdjustment:
    """Represents a parameter adjustment recommendation"""
    parameter: str
    old_value: float
    new_value: float
    reason: str
    dimension: str
    dimension_score: float


class SubjectiveParameterTuner:
    """
    Tunes generation parameters based on subjective evaluation dimensions.
    
    Maps low dimension scores to specific parameter adjustments:
    - Clarity → Adjust temperature (complexity control)
    - Professionalism → Adjust presence_penalty (formality)
    - Technical Accuracy → Adjust technical_depth slider
    - Human-likeness → Adjust presence_penalty (naturalness)
    - Engagement → Adjust temperature + conversational_tone
    - Jargon-free → Adjust technical_depth (simplicity)
    """
    
    # Dimension score thresholds
    THRESHOLD_POOR = 5.0      # < 5.0 = poor, needs significant adjustment
    THRESHOLD_LOW = 7.0       # < 7.0 = below target, needs adjustment
    THRESHOLD_GOOD = 8.5      # >= 8.5 = excellent, no adjustment needed
    
    # Adjustment magnitudes
    ADJUSTMENT_LARGE = 0.10   # For scores < 5.0
    ADJUSTMENT_MEDIUM = 0.05  # For scores 5.0-7.0
    ADJUSTMENT_SMALL = 0.02   # For fine-tuning
    
    # Parameter bounds
    TEMPERATURE_BOUNDS = (0.5, 1.5)
    PENALTY_BOUNDS = (0.0, 2.0)
    SLIDER_BOUNDS = (0, 100)
    
    def __init__(self, feedback_db=None):
        """
        Initialize tuner with optional feedback database.
        
        Args:
            feedback_db: WinstonFeedbackDatabase instance for logging adjustments
        """
        self.feedback_db = feedback_db
    
    def analyze_and_adjust(
        self,
        subjective_eval: dict,
        current_params: dict,
        author_id: int | None = None
    ) -> tuple[dict, list]:
        """
        Analyze subjective evaluation and recommend parameter adjustments.
        
        Args:
            subjective_eval: dict with dimension scores from get_latest_subjective_evaluation()
            current_params: Current generation parameters
            author_id: Optional author ID for author-specific adjustments
            
        Returns:
            Tuple of (adjusted_params, list of ParameterAdjustment objects)
        """
        adjustments = []
        new_params = current_params.copy()
        
        # Extract dimension scores
        clarity = subjective_eval.get('clarity_score', 10.0)
        professionalism = subjective_eval.get('professionalism_score', 10.0)
        technical_accuracy = subjective_eval.get('technical_accuracy_score', 10.0)
        human_likeness = subjective_eval.get('human_likeness_score', 10.0)
        engagement = subjective_eval.get('engagement_score', 10.0)
        jargon_free = subjective_eval.get('jargon_free_score', 10.0)
        
        # 1. CLARITY → Temperature adjustment
        if clarity < self.THRESHOLD_LOW:
            adjustment = self._adjust_clarity(clarity, new_params)
            if adjustment:
                adjustments.append(adjustment)
                new_params = self._apply_adjustment(new_params, adjustment)
        
        # 2. PROFESSIONALISM → Presence penalty adjustment
        if professionalism < self.THRESHOLD_LOW:
            adjustment = self._adjust_professionalism(professionalism, new_params)
            if adjustment:
                adjustments.append(adjustment)
                new_params = self._apply_adjustment(new_params, adjustment)
        
        # 3. TECHNICAL ACCURACY → Technical depth slider
        if technical_accuracy < self.THRESHOLD_LOW:
            adjustment = self._adjust_technical_accuracy(technical_accuracy, new_params)
            if adjustment:
                adjustments.append(adjustment)
                new_params = self._apply_adjustment(new_params, adjustment)
        
        # 4. HUMAN-LIKENESS → Presence penalty adjustment
        if human_likeness < self.THRESHOLD_LOW:
            adjustment = self._adjust_human_likeness(human_likeness, new_params)
            if adjustment:
                adjustments.append(adjustment)
                new_params = self._apply_adjustment(new_params, adjustment)
        
        # 5. ENGAGEMENT → Temperature + conversational tone
        if engagement < self.THRESHOLD_LOW:
            adj_list = self._adjust_engagement(engagement, new_params)
            for adjustment in adj_list:
                adjustments.append(adjustment)
                new_params = self._apply_adjustment(new_params, adjustment)
        
        # 6. JARGON-FREE → Technical depth slider
        if jargon_free < self.THRESHOLD_LOW:
            adjustment = self._adjust_jargon_free(jargon_free, new_params)
            if adjustment:
                adjustments.append(adjustment)
                new_params = self._apply_adjustment(new_params, adjustment)
        
        # Log adjustments if database available
        if self.feedback_db and adjustments:
            self._log_adjustments(subjective_eval, adjustments, author_id)
        
        return new_params, adjustments
    
    def _adjust_clarity(self, score: float, params: dict) -> ParameterAdjustment | None:
        """
        Low clarity → Reduce temperature (simpler, clearer output)
        
        Rationale: High temperature increases randomness and complexity.
        Lowering it produces more focused, predictable, clearer text.
        """
        current_temp = params.get('api', {}).get('temperature', 1.0)
        
        if score < self.THRESHOLD_POOR:
            delta = -self.ADJUSTMENT_LARGE
        elif score < self.THRESHOLD_LOW:
            delta = -self.ADJUSTMENT_MEDIUM
        else:
            return None
        
        new_temp = max(self.TEMPERATURE_BOUNDS[0], min(self.TEMPERATURE_BOUNDS[1], current_temp + delta))
        
        if abs(new_temp - current_temp) < 0.01:  # No meaningful change
            return None
        
        return ParameterAdjustment(
            parameter='temperature',
            old_value=current_temp,
            new_value=new_temp,
            reason=f"Low clarity score ({score:.1f}/10) → reduce temperature for clearer output",
            dimension='clarity',
            dimension_score=score
        )
    
    def _adjust_professionalism(self, score: float, params: dict) -> ParameterAdjustment | None:
        """
        Low professionalism → Increase presence penalty (reduce casual repetition)
        
        Rationale: Presence penalty discourages repetitive patterns,
        leading to more varied, professional-sounding language.
        """
        current_penalty = params.get('api_penalties', {}).get('presence_penalty', 1.0)
        
        if score < self.THRESHOLD_POOR:
            delta = self.ADJUSTMENT_LARGE
        elif score < self.THRESHOLD_LOW:
            delta = self.ADJUSTMENT_MEDIUM
        else:
            return None
        
        new_penalty = max(self.PENALTY_BOUNDS[0], min(self.PENALTY_BOUNDS[1], current_penalty + delta))
        
        if abs(new_penalty - current_penalty) < 0.01:
            return None
        
        return ParameterAdjustment(
            parameter='presence_penalty',
            old_value=current_penalty,
            new_value=new_penalty,
            reason=f"Low professionalism ({score:.1f}/10) → increase presence penalty for more formal tone",
            dimension='professionalism',
            dimension_score=score
        )
    
    def _adjust_technical_accuracy(self, score: float, params: dict) -> ParameterAdjustment | None:
        """
        Low technical accuracy → Increase technical_depth slider
        
        Rationale: More technical depth means more specific technical details,
        improving accuracy of technical statements.
        """
        current_depth = params.get('voice', {}).get('technical_depth', 50)
        
        if score < self.THRESHOLD_POOR:
            delta = 15
        elif score < self.THRESHOLD_LOW:
            delta = 10
        else:
            return None
        
        new_depth = max(self.SLIDER_BOUNDS[0], min(self.SLIDER_BOUNDS[1], current_depth + delta))
        
        if abs(new_depth - current_depth) < 1:
            return None
        
        return ParameterAdjustment(
            parameter='technical_depth',
            old_value=current_depth,
            new_value=new_depth,
            reason=f"Low technical accuracy ({score:.1f}/10) → increase technical depth for more precise details",
            dimension='technical_accuracy',
            dimension_score=score
        )
    
    def _adjust_human_likeness(self, score: float, params: dict) -> ParameterAdjustment | None:
        """
        Low human-likeness → Reduce presence penalty (allow more natural patterns)
        
        Rationale: Too high presence penalty can make text feel stilted.
        Reducing it allows more natural, human-like language patterns.
        """
        current_penalty = params.get('api_penalties', {}).get('presence_penalty', 1.0)
        
        if score < self.THRESHOLD_POOR:
            delta = -self.ADJUSTMENT_LARGE
        elif score < self.THRESHOLD_LOW:
            delta = -self.ADJUSTMENT_MEDIUM
        else:
            return None
        
        new_penalty = max(self.PENALTY_BOUNDS[0], min(self.PENALTY_BOUNDS[1], current_penalty + delta))
        
        if abs(new_penalty - current_penalty) < 0.01:
            return None
        
        return ParameterAdjustment(
            parameter='presence_penalty',
            old_value=current_penalty,
            new_value=new_penalty,
            reason=f"Low human-likeness ({score:.1f}/10) → reduce presence penalty for more natural patterns",
            dimension='human_likeness',
            dimension_score=score
        )
    
    def _adjust_engagement(self, score: float, params: dict) -> list[ParameterAdjustment]:
        """
        Low engagement → Increase temperature + conversational_tone
        
        Rationale: Higher temperature adds variety and unpredictability.
        More conversational tone makes content more engaging.
        """
        adjustments = []
        
        # Adjust temperature
        current_temp = params.get('api', {}).get('temperature', 1.0)
        if score < self.THRESHOLD_POOR:
            temp_delta = self.ADJUSTMENT_LARGE
        elif score < self.THRESHOLD_LOW:
            temp_delta = self.ADJUSTMENT_MEDIUM
        else:
            temp_delta = 0
        
        if temp_delta > 0:
            new_temp = max(self.TEMPERATURE_BOUNDS[0], min(self.TEMPERATURE_BOUNDS[1], current_temp + temp_delta))
            if abs(new_temp - current_temp) >= 0.01:
                adjustments.append(ParameterAdjustment(
                    parameter='temperature',
                    old_value=current_temp,
                    new_value=new_temp,
                    reason=f"Low engagement ({score:.1f}/10) → increase temperature for more variety",
                    dimension='engagement',
                    dimension_score=score
                ))
        
        # Adjust conversational tone
        current_tone = params.get('voice', {}).get('conversational_tone', 50)
        if score < self.THRESHOLD_POOR:
            tone_delta = 15
        elif score < self.THRESHOLD_LOW:
            tone_delta = 10
        else:
            tone_delta = 0
        
        if tone_delta > 0:
            new_tone = max(self.SLIDER_BOUNDS[0], min(self.SLIDER_BOUNDS[1], current_tone + tone_delta))
            if abs(new_tone - current_tone) >= 1:
                adjustments.append(ParameterAdjustment(
                    parameter='conversational_tone',
                    old_value=current_tone,
                    new_value=new_tone,
                    reason=f"Low engagement ({score:.1f}/10) → increase conversational tone",
                    dimension='engagement',
                    dimension_score=score
                ))
        
        return adjustments
    
    def _adjust_jargon_free(self, score: float, params: dict) -> ParameterAdjustment | None:
        """
        Low jargon-free score → Reduce technical_depth slider
        
        Rationale: Lower technical depth means simpler, more accessible language
        with less jargon and technical terminology.
        """
        current_depth = params.get('voice', {}).get('technical_depth', 50)
        
        if score < self.THRESHOLD_POOR:
            delta = -15
        elif score < self.THRESHOLD_LOW:
            delta = -10
        else:
            return None
        
        new_depth = max(self.SLIDER_BOUNDS[0], min(self.SLIDER_BOUNDS[1], current_depth + delta))
        
        if abs(new_depth - current_depth) < 1:
            return None
        
        return ParameterAdjustment(
            parameter='technical_depth',
            old_value=current_depth,
            new_value=new_depth,
            reason=f"Low jargon-free score ({score:.1f}/10) → reduce technical depth for simpler language",
            dimension='jargon_free',
            dimension_score=score
        )
    
    def _apply_adjustment(self, params: dict, adjustment: ParameterAdjustment) -> dict:
        """Apply a parameter adjustment to the params dict"""
        new_params = params.copy()
        
        if adjustment.parameter == 'temperature':
            if 'api' not in new_params:
                new_params['api'] = {}
            new_params['api']['temperature'] = adjustment.new_value
        
        elif adjustment.parameter in ['frequency_penalty', 'presence_penalty']:
            if 'api_penalties' not in new_params:
                new_params['api_penalties'] = {}
            new_params['api_penalties'][adjustment.parameter] = adjustment.new_value
        
        elif adjustment.parameter in ['technical_depth', 'conversational_tone', 'imperfection_level']:
            if 'voice' not in new_params:
                new_params['voice'] = {}
            new_params['voice'][adjustment.parameter] = int(adjustment.new_value)
        
        return new_params
    
    def _log_adjustments(
        self,
        subjective_eval: dict,
        adjustments: list,
        author_id: int | None
    ):
        """Log parameter adjustments to database for tracking"""
        try:
            # Log to a new table (would need to be created)
            # For now, just log to console
            logger.info("🔧 [LEARNING] Parameter adjustments based on subjective evaluation:")
            for adj in adjustments:
                logger.info(
                    f"   {adj.parameter}: {adj.old_value:.3f} → {adj.new_value:.3f} "
                    f"(reason: {adj.dimension} score {adj.dimension_score:.1f}/10)"
                )
        except Exception as e:
            logger.warning(f"⚠️ [LEARNING] Failed to log adjustments: {e}")
    
    def should_adjust(self, overall_score: float) -> bool:
        """
        Determine if parameters should be adjusted based on overall score.
        
        Args:
            overall_score: Overall subjective evaluation score (0-10)
            
        Returns:
            True if score below threshold and adjustment recommended
        """
        return overall_score < self.THRESHOLD_LOW
