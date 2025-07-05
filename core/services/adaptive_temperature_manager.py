"""
Adaptive Temperature Management for optimized content generation and detection.
"""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple
from generator.core.domain.models import TemperatureConfig
from generator.modules.logger import get_logger

logger = get_logger("adaptive_temperature_manager")


@dataclass
class TemperatureStrategy:
    """Defines temperature strategy for different scenarios."""
    content_temp: float
    detection_temp: float
    improvement_temp: float
    reasoning: str


class AdaptiveTemperatureManager:
    """
    Manages dynamic temperature strategies based on:
    1. AI detection scores (high = too robotic, needs more creativity)
    2. Natural Voice scores (high = over-humanized, needs more control)
    3. Iteration patterns (stuck in loops, needs temperature adjustment)
    """

    def __init__(self, base_config: TemperatureConfig):
        self.base_config = base_config
        self.logger = get_logger("adaptive_temperature_manager")
        
        # Track performance patterns
        self.ai_score_history = []
        self.natural_voice_history = []
        self.iteration_patterns = {}
        
        # Define temperature strategies
        self.strategies = {
            "conservative": TemperatureStrategy(
                content_temp=0.5,
                detection_temp=0.2,
                improvement_temp=0.6,
                reasoning="Conservative approach for consistent, controlled output"
            ),
            "balanced": TemperatureStrategy(
                content_temp=0.6,
                detection_temp=0.3,
                improvement_temp=0.7,
                reasoning="Balanced approach for natural but controlled output"
            ),
            "creative": TemperatureStrategy(
                content_temp=0.8,
                detection_temp=0.3,
                improvement_temp=0.9,
                reasoning="Creative approach to break AI patterns"
            ),
            "refinement": TemperatureStrategy(
                content_temp=0.4,
                detection_temp=0.2,
                improvement_temp=0.5,
                reasoning="Low temperature for precise refinement"
            ),
            "breakthrough": TemperatureStrategy(
                content_temp=0.9,
                detection_temp=0.4,
                improvement_temp=1.0,
                reasoning="High creativity to overcome stuck patterns"
            )
        }

    def get_adaptive_temperature(
        self,
        section_name: str,
        iteration: int,
        ai_score: Optional[int] = None,
        natural_voice_score: Optional[int] = None,
        content_type: str = "content"
    ) -> Tuple[float, str]:
        """
        Get adaptive temperature based on current performance and patterns.
        
        Args:
            section_name: Name of the section being processed
            iteration: Current iteration number
            ai_score: Latest AI detection score (0-100, lower = better)
            natural_voice_score: Latest Natural Voice score (15-25 optimal)
            content_type: Type of generation ('content', 'detection', 'improvement')
            
        Returns:
            Tuple of (temperature, reasoning)
        """
        
        # Update score histories
        if ai_score is not None:
            self.ai_score_history.append(ai_score)
        if natural_voice_score is not None:
            self.natural_voice_history.append(natural_voice_score)
            
        # Analyze current situation
        strategy_name = self._analyze_situation(section_name, iteration, ai_score, natural_voice_score)
        strategy = self.strategies[strategy_name]
        
        # Get temperature based on content type
        if content_type == "content":
            temperature = strategy.content_temp
        elif content_type == "detection":
            temperature = strategy.detection_temp
        elif content_type == "improvement":
            temperature = strategy.improvement_temp
        else:
            temperature = self.base_config.content_temp
            
        reasoning = f"Strategy: {strategy_name} - {strategy.reasoning}"
        
        self.logger.info(f"🌡️ Adaptive Temperature: {temperature} for {content_type} ({reasoning})")
        
        return temperature, reasoning

    def _analyze_situation(
        self,
        section_name: str,
        iteration: int,
        ai_score: Optional[int],
        natural_voice_score: Optional[int]
    ) -> str:
        """Analyze current situation and determine best temperature strategy."""
        
        # Early iterations - be conservative
        if iteration <= 2:
            return "balanced"
            
        # High AI scores (robotic content) - need more creativity
        if ai_score is not None and ai_score > 50:
            self.logger.info(f"🤖 High AI score ({ai_score}%) detected - increasing creativity")
            return "creative"
            
        # Very high AI scores - breakthrough needed
        if ai_score is not None and ai_score > 75:
            self.logger.info(f"🚨 Very high AI score ({ai_score}%) - breakthrough strategy")
            return "breakthrough"
            
        # Natural Voice too low (artificial) - need more creativity
        if natural_voice_score is not None and natural_voice_score < 10:
            self.logger.info(f"🎭 Natural Voice too low ({natural_voice_score}%) - increasing creativity")
            return "creative"
            
        # Natural Voice too high (over-humanized) - need more control
        if natural_voice_score is not None and natural_voice_score > 40:
            self.logger.info(f"⚠️ Natural Voice too high ({natural_voice_score}%) - applying control")
            return "conservative"
            
        # Natural Voice in good range - use refinement
        if natural_voice_score is not None and 15 <= natural_voice_score <= 25:
            self.logger.info(f"✅ Natural Voice optimal ({natural_voice_score}%) - refining")
            return "refinement"
            
        # Stuck in pattern (many iterations without improvement)
        if iteration > 4:
            pattern_key = f"{section_name}_{iteration}"
            if self._is_stuck_pattern(section_name, iteration):
                self.logger.info(f"🔄 Stuck pattern detected - breakthrough strategy")
                return "breakthrough"
                
        # Late iterations but making progress
        if iteration > 3:
            return "refinement"
            
        # Default balanced approach
        return "balanced"

    def _is_stuck_pattern(self, section_name: str, iteration: int) -> bool:
        """Detect if we're stuck in a repetitive pattern."""
        # Check if scores haven't improved in last 2 iterations
        if len(self.ai_score_history) >= 3:
            recent_ai = self.ai_score_history[-3:]
            if max(recent_ai) - min(recent_ai) < 5:  # Less than 5% variation
                return True
                
        if len(self.natural_voice_history) >= 3:
            recent_nv = self.natural_voice_history[-3:]
            if max(recent_nv) - min(recent_nv) < 5:  # Less than 5% variation
                return True
                
        return False

    def create_adaptive_config(
        self,
        section_name: str,
        iteration: int,
        ai_score: Optional[int] = None,
        natural_voice_score: Optional[int] = None
    ) -> TemperatureConfig:
        """Create a TemperatureConfig with adaptive temperatures."""
        
        content_temp, content_reasoning = self.get_adaptive_temperature(
            section_name, iteration, ai_score, natural_voice_score, "content"
        )
        
        detection_temp, detection_reasoning = self.get_adaptive_temperature(
            section_name, iteration, ai_score, natural_voice_score, "detection"
        )
        
        improvement_temp, improvement_reasoning = self.get_adaptive_temperature(
            section_name, iteration, ai_score, natural_voice_score, "improvement"
        )
        
        # Log the adaptive strategy
        self.logger.info(f"🧠 Adaptive Config for {section_name} (iteration {iteration}):")
        self.logger.info(f"   Content: {content_temp} ({content_reasoning})")
        self.logger.info(f"   Detection: {detection_temp} ({detection_reasoning})")
        self.logger.info(f"   Improvement: {improvement_temp} ({improvement_reasoning})")
        
        return TemperatureConfig(
            content_temp=content_temp,
            detection_temp=detection_temp,
            improvement_temp=improvement_temp,
            summary_temp=self.base_config.summary_temp,
            metadata_temp=self.base_config.metadata_temp,
        )

    def reset_for_new_section(self, section_name: str):
        """Reset tracking for a new section."""
        self.ai_score_history = []
        self.natural_voice_history = []
        self.logger.info(f"🔄 Reset adaptive tracking for section: {section_name}")

    def get_performance_summary(self) -> Dict:
        """Get summary of adaptive performance."""
        return {
            "ai_score_trend": self.ai_score_history[-5:] if self.ai_score_history else [],
            "natural_voice_trend": self.natural_voice_history[-5:] if self.natural_voice_history else [],
            "total_ai_samples": len(self.ai_score_history),
            "total_nv_samples": len(self.natural_voice_history),
            "avg_ai_score": sum(self.ai_score_history) / len(self.ai_score_history) if self.ai_score_history else 0,
            "avg_nv_score": sum(self.natural_voice_history) / len(self.natural_voice_history) if self.natural_voice_history else 0,
        }

    def get_adaptive_strategy(
        self,
        ai_score: Optional[int] = None,
        natural_voice_score: Optional[int] = None,
        iteration: int = 1
    ) -> TemperatureStrategy:
        """
        Get adaptive temperature strategy based on detection scores.
        
        This method provides the strategy that the detection service expects.
        """
        strategy_name = self._analyze_situation("unknown", iteration, ai_score, natural_voice_score)
        return self.strategies[strategy_name]

    def get_detection_temperature(self, detection_type: str, iteration: int) -> float:
        """
        Get detection temperature for specific detection type.
        
        Args:
            detection_type: 'ai' or 'natural_voice'
            iteration: Current iteration number
        """
        if detection_type == "ai":
            # AI detection should be consistent and conservative
            return min(0.3, self.base_config.detection_temp)
        elif detection_type == "natural_voice":
            # Natural Voice detection needs slightly more flexibility
            return min(0.4, self.base_config.detection_temp + 0.1)
        else:
            return self.base_config.detection_temp

    def record_ai_score(self, score: float):
        """Record AI detection score for pattern analysis."""
        self.ai_score_history.append(score)
        # Keep only last 10 scores to avoid memory bloat
        if len(self.ai_score_history) > 10:
            self.ai_score_history = self.ai_score_history[-10:]

    def record_natural_voice_score(self, score: float):
        """Record Natural Voice score for pattern analysis."""
        self.natural_voice_history.append(score)
        # Keep only last 10 scores to avoid memory bloat
        if len(self.natural_voice_history) > 10:
            self.natural_voice_history = self.natural_voice_history[-10:]

    def update_base_config(self, new_config: TemperatureConfig):
        """Update the base configuration."""
        self.base_config = new_config

    def get_status_summary(self) -> Dict:
        """Get status summary for debugging."""
        return {
            "ai_scores": self.ai_score_history[-3:] if self.ai_score_history else [],
            "nv_scores": self.natural_voice_history[-3:] if self.natural_voice_history else [],
            "current_base_config": {
                "content_temp": self.base_config.content_temp,
                "detection_temp": self.base_config.detection_temp,
                "improvement_temp": self.base_config.improvement_temp,
            }
        }
