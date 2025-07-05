"""
Enhanced Detection Service - Coordinator for AI and Natural Voice Detection
Refactored to use discrete, non-overlapping detection services with clear scoring logic.
"""

from config.global_config import get_config

from core.domain.models import AIScore, GenerationContext, TemperatureConfig
from core.interfaces.services import IAPIClient, IPromptRepository
from core.exceptions import DetectionError
from core.services.ai_detection_service import AIDetectionService
from core.services.natural_voice_detection_service import NaturalVoiceDetectionService
from core.services.detection_scoring_system import DetectionScoringSystem
from core.services.adaptive_temperature_manager import AdaptiveTemperatureManager
from modules.logger import get_logger
from typing import Optional, Dict, List
import time

logger = get_logger("detection_service")


class DetectionService:
    """
    Unified Detection Service Coordinator.
    
    Manages discrete AI and Natural Voice detection services to provide:
    1. Separate, non-overlapping detection paths
    2. Clear scoring interpretation (low AI = good, mid NV = excellent)
    3. Dynamic temperature adaptation based on detection patterns
    4. Unified improvement recommendations
    """

    def __init__(self, api_client: IAPIClient, prompt_repository: IPromptRepository):
        self._api_client = api_client
        self._prompt_repository = prompt_repository
        self.logger = get_logger("detection_service")

        # Initialize discrete detection services
        self.ai_detection_service = AIDetectionService(api_client, prompt_repository)
        self.natural_voice_service = NaturalVoiceDetectionService(api_client, prompt_repository)
        
        # Initialize scoring and temperature management
        self.scoring_system = DetectionScoringSystem()
        
        # Initialize with base temperature config (will be updated dynamically)
        base_temp_config = TemperatureConfig(
            content_temp=0.6,
            detection_temp=0.3,
            improvement_temp=0.7
        )
        self.temp_manager = AdaptiveTemperatureManager(base_temp_config)
        
        # Track detection patterns for adaptive management
        self.detection_history = []

    def detect_ai_patterns(
        self,
        content: str,
        context: GenerationContext,
        iteration: int = 1,
        temperature: float = None,
        timeout: int = None,
        temperature_config: Optional[TemperatureConfig] = None,
    ) -> AIScore:
        """
        Detect AI-generated patterns in content.
        
        SCORING: Low scores (0-25%) = GOOD (minimal AI patterns)
        """
        # Set defaults from config if not provided
        if temperature is None:
            from config.global_config import get_config
            temperature = get_config().get_detection_temperature()
        if timeout is None:
            from config.global_config import get_config
            timeout = get_config().get_api_timeout()
            
        self.logger.info(f"🧠 AI Detection - Starting analysis (iteration {iteration})")
        
        # Get adaptive temperature if available
        if temperature_config:
            self.temp_manager.update_base_config(temperature_config)
        
        adaptive_temp = self.temp_manager.get_detection_temperature("ai", iteration)
        
        try:
            ai_score = self.ai_detection_service.detect_ai_patterns(
                content, context, iteration, adaptive_temp, timeout, temperature_config
            )
            
            # Update temperature manager with results
            self.temp_manager.record_ai_score(ai_score.score)
            
            # Get score interpretation
            interpretation = self.scoring_system.interpret_ai_score(ai_score.score)
            
            self.logger.info(
                f"🧠 AI Detection Result: {ai_score.score}% "
                f"({interpretation.category.value.upper()}) - {interpretation.description}"
            )
            
            return ai_score
            
        except Exception as e:
            self.logger.error(f"AI detection failed: {e}")
            raise DetectionError(f"AI detection failed: {e}") from e

    def detect_natural_voice_authenticity(
        self,
        content: str,
        context: GenerationContext,
        iteration: int = 1,
        temperature: float = None,
        timeout: int = None,
        temperature_config: Optional[TemperatureConfig] = None,
    ) -> AIScore:
        """
        Detect Natural Voice authenticity in content.
        
        SCORING: Mid-range scores (15-25%) = EXCELLENT (authentic professional voice)
        """
        # Set defaults from config if not provided
        if temperature is None:
            from config.global_config import get_config
            temperature = get_config().get_detection_temperature()
        if timeout is None:
            from config.global_config import get_config
            timeout = get_config().get_api_timeout()
            
        self.logger.info(f"👤 Natural Voice - Starting analysis (iteration {iteration})")
        
        # Get adaptive temperature if available
        if temperature_config:
            self.temp_manager.update_base_config(temperature_config)
        
        adaptive_temp = self.temp_manager.get_detection_temperature("natural_voice", iteration)
        
        try:
            nv_score = self.natural_voice_service.detect_natural_voice_authenticity(
                content, context, iteration, adaptive_temp, timeout, temperature_config
            )
            
            # Update temperature manager with results
            self.temp_manager.record_natural_voice_score(nv_score.score)
            
            # Get score interpretation
            interpretation = self.scoring_system.interpret_natural_voice_score(nv_score.score)
            
            self.logger.info(
                f"👤 Natural Voice Result: {nv_score.score}% "
                f"({interpretation.category.value.upper()}) - {interpretation.description}"
            )
            
            return nv_score
            
        except Exception as e:
            self.logger.error(f"Natural Voice detection failed: {e}")
            raise DetectionError(f"Natural Voice detection failed: {e}") from e

    def run_comprehensive_detection(
        self,
        content: str,
        context: GenerationContext,
        ai_threshold: int,
        natural_voice_threshold: int,
        iteration: int = 1,
        temperature_config: Optional[TemperatureConfig] = None,
    ) -> Dict[str, any]:
        """
        Run both AI and Natural Voice detection with comprehensive analysis.
        
        Returns unified results with clear scoring interpretation and recommendations.
        """
        # Get timeout from config for internal method calls
        from config.global_config import get_config
        timeout = get_config().get_api_timeout()
        
        self.logger.info(f"🔍 Comprehensive Detection - Starting analysis (iteration {iteration})")
        
        results = {
            "iteration": iteration,
            "timestamp": time.time(),
            "ai_detection": None,
            "natural_voice_detection": None,
            "overall_status": None,
            "recommendations": [],
            "temperature_adjustments": None,
        }
        
        try:
            # Run AI Detection
            ai_score = self.detect_ai_patterns(
                content, context, iteration, timeout=timeout, temperature_config=temperature_config
            )
            ai_interpretation = self.scoring_system.interpret_ai_score(ai_score.score)
            ai_passes = ai_score.score <= ai_threshold
            
            results["ai_detection"] = {
                "score": ai_score.score,
                "threshold": ai_threshold,
                "passes": ai_passes,
                "interpretation": ai_interpretation,
                "raw_result": ai_score,
            }
            
            # Run Natural Voice Detection  
            nv_score = self.detect_natural_voice_authenticity(
                content, context, iteration, timeout=timeout, temperature_config=temperature_config
            )
            nv_interpretation = self.scoring_system.interpret_natural_voice_score(nv_score.score)
            nv_passes = nv_score.score <= natural_voice_threshold
            
            results["natural_voice_detection"] = {
                "score": nv_score.score,
                "threshold": natural_voice_threshold,
                "passes": nv_passes,
                "interpretation": nv_interpretation,
                "raw_result": nv_score,
            }
            
            # Determine overall status
            both_pass = ai_passes and nv_passes
            results["overall_status"] = "PASS" if both_pass else "FAIL"
            
            # Generate improvement recommendations
            recommendations = self._generate_improvement_recommendations(
                ai_score.score, nv_score.score, ai_threshold, natural_voice_threshold
            )
            results["recommendations"] = recommendations
            
            # Get adaptive temperature recommendations
            temp_strategy = self.temp_manager.get_adaptive_strategy(
                ai_score.score, nv_score.score, iteration
            )
            results["temperature_adjustments"] = {
                "strategy": temp_strategy.reasoning,
                "content_temp": temp_strategy.content_temp,
                "detection_temp": temp_strategy.detection_temp,
                "improvement_temp": temp_strategy.improvement_temp,
            }
            
            # Log comprehensive results
            self._log_comprehensive_results(results)
            
            # Track detection history for pattern analysis
            self.detection_history.append({
                "iteration": iteration,
                "ai_score": ai_score.score,
                "nv_score": nv_score.score,
                "ai_passes": ai_passes,
                "nv_passes": nv_passes,
            })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Comprehensive detection failed: {e}")
            results["error"] = str(e)
            results["overall_status"] = "ERROR"
            return results

    def _generate_improvement_recommendations(
        self, ai_score: float, nv_score: float, ai_threshold: int, nv_threshold: int
    ) -> List[str]:
        """Generate specific improvement recommendations based on detection results."""
        recommendations = []
        thresholds = get_config().get_content_scoring_thresholds()
        
        # AI-specific recommendations
        if ai_score > ai_threshold:
            if ai_score > thresholds["high_ai"]:
                recommendations.append("HIGH AI DETECTED: Add more natural variations, conversational elements")
            elif ai_score > thresholds["low_quality"]:
                recommendations.append("MODERATE AI: Incorporate industry-specific terminology and examples")
            else:
                recommendations.append("MILD AI: Minor adjustments to sentence structure needed")
        
        # Natural Voice specific recommendations  
        if nv_score > nv_threshold:
            if nv_score > thresholds["high_ai"]:
                recommendations.append("OVER-HUMANIZED: Reduce excessive casual language, maintain professionalism")
            elif nv_score > thresholds["low_quality"]:
                recommendations.append("VOICE IMBALANCE: Balance technical expertise with conversational tone")
            else:
                recommendations.append("MINOR VOICE ADJUSTMENT: Fine-tune professional authenticity")
        
        # Get thresholds from config instead of hardcoding
        thresholds = get_config().get_score_balance_thresholds()
        
        # Scoring-specific guidance
        if ai_score <= thresholds["excellent_ai"] and thresholds["low_nv"] <= nv_score <= thresholds["high_nv"]:
            recommendations.append("EXCELLENT: Content achieves optimal AI/Natural Voice balance")
        elif ai_score <= thresholds["excellent_ai"] and nv_score < thresholds["low_nv"]:
            recommendations.append("GOOD AI, LOW NV: Add more authentic professional voice elements")
        elif ai_score > thresholds["excellent_ai"] and thresholds["low_nv"] <= nv_score <= thresholds["high_nv"]:
            recommendations.append("GOOD NV, HIGH AI: Reduce robotic patterns while preserving voice")
        
        return recommendations

    def _log_comprehensive_results(self, results: Dict[str, any]) -> None:
        """Log comprehensive detection results with clear formatting."""
        iteration = results["iteration"]
        ai_result = results["ai_detection"]
        nv_result = results["natural_voice_detection"]
        status = results["overall_status"]
        
        self.logger.info(f"🔍 Comprehensive Detection Results (Iteration {iteration}):")
        
        # AI Detection Results
        ai_emoji = ai_result["interpretation"].emoji
        ai_status = "✅ PASS" if ai_result["passes"] else "❌ FAIL"
        self.logger.info(
            f"   🧠 AI Detection: {ai_result['score']}% {ai_emoji} ({ai_status}) "
            f"[Threshold: ≤{ai_result['threshold']}%]"
        )
        self.logger.info(f"      {ai_result['interpretation'].description}")
        
        # Natural Voice Results
        nv_emoji = nv_result["interpretation"].emoji
        nv_status = "✅ PASS" if nv_result["passes"] else "❌ FAIL"
        self.logger.info(
            f"   👤 Natural Voice: {nv_result['score']}% {nv_emoji} ({nv_status}) "
            f"[Threshold: ≤{nv_result['threshold']}%]"
        )
        self.logger.info(f"      {nv_result['interpretation'].description}")
        
        # Overall Status
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        self.logger.info(f"   🏁 Overall: {status_emoji} {status}")
        
        # Recommendations
        if results["recommendations"]:
            self.logger.info("   💡 Recommendations:")
            for rec in results["recommendations"]:
                self.logger.info(f"      • {rec}")
        
        # Temperature Strategy
        temp_adj = results.get("temperature_adjustments")
        if temp_adj:
            self.logger.info(f"   🌡️ Temperature Strategy: {temp_adj['strategy']}")

    def get_detection_patterns(self) -> Dict[str, any]:
        """Get analysis of detection patterns for debugging and optimization."""
        if not self.detection_history:
            return {"status": "no_data", "message": "No detection history available"}
        
        recent_history = self.detection_history[-5:]  # Last 5 iterations
        
        return {
            "total_iterations": len(self.detection_history),
            "recent_ai_scores": [h["ai_score"] for h in recent_history],
            "recent_nv_scores": [h["nv_score"] for h in recent_history],
            "ai_trend": self._calculate_trend([h["ai_score"] for h in recent_history]),
            "nv_trend": self._calculate_trend([h["nv_score"] for h in recent_history]),
            "pass_rate": {
                "ai": sum(1 for h in recent_history if h["ai_passes"]) / len(recent_history),
                "nv": sum(1 for h in recent_history if h["nv_passes"]) / len(recent_history),
            },
            "temperature_manager_status": self.temp_manager.get_status_summary(),
        }

    def _calculate_trend(self, scores: List[float]) -> str:
        """Calculate trend direction for scores."""
        if len(scores) < 2:
            return "insufficient_data"
        
        if scores[-1] > scores[0]:
            return "increasing"
        elif scores[-1] < scores[0]:
            return "decreasing"
        else:
            return "stable"

    # Legacy compatibility methods (deprecated but maintained for backward compatibility)
    
    def detect_ai_content(self, *args, **kwargs) -> AIScore:
        """Legacy method - redirects to detect_ai_patterns."""
        self.logger.warning("Using deprecated detect_ai_content method. Use detect_ai_patterns instead.")
        return self.detect_ai_patterns(*args, **kwargs)
    
    def detect_human_content(self, *args, **kwargs) -> AIScore:
        """Legacy method - redirects to detect_natural_voice_authenticity.""" 
        self.logger.warning("Using deprecated detect_human_content method. Use detect_natural_voice_authenticity instead.")
        return self.detect_natural_voice_authenticity(*args, **kwargs)
