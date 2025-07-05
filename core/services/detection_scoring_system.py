"""
Comprehensive scoring system for AI detection and Natural Voice assessment.
"""

from dataclasses import dataclass
from typing import Dict, Tuple, Optional
from enum import Enum


class ScoreCategory(Enum):
    """Categories for different score interpretations."""
    EXCELLENT = "excellent"
    GOOD = "good" 
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class ScoreInterpretation:
    """Interpretation of a detection score."""
    category: ScoreCategory
    description: str
    recommendation: str
    is_passing: bool
    color_code: str
    emoji: str


class DetectionScoringSystem:
    """
    Unified scoring system that clarifies the meaning of AI and Natural Voice scores.
    
    SCORING PHILOSOPHY:
    - AI Detection: Low scores (0-25%) = GOOD (minimal AI patterns)
    - Natural Voice: Mid-range scores (15-25%) = EXCELLENT (authentic professional voice)
    """

    def __init__(self):
        self.ai_thresholds = self._define_ai_thresholds()
        self.natural_voice_thresholds = self._define_natural_voice_thresholds()

    def _define_ai_thresholds(self) -> Dict[str, ScoreInterpretation]:
        """Define AI detection score thresholds and interpretations."""
        return {
            "0-10": ScoreInterpretation(
                category=ScoreCategory.EXCELLENT,
                description="Minimal AI patterns detected - excellent natural flow",
                recommendation="Content passes with flying colors",
                is_passing=True,
                color_code="🟢",
                emoji="🎯"
            ),
            "11-25": ScoreInterpretation(
                category=ScoreCategory.GOOD,
                description="Low AI patterns - good natural content",
                recommendation="Minor refinements for even better flow",
                is_passing=True,
                color_code="🟢",
                emoji="✅"
            ),
            "26-40": ScoreInterpretation(
                category=ScoreCategory.ACCEPTABLE,
                description="Some AI patterns detected - needs refinement",
                recommendation="Improve with Natural Voice enhancement",
                is_passing=False,
                color_code="🟠",
                emoji="⚠️"
            ),
            "41-60": ScoreInterpretation(
                category=ScoreCategory.POOR,
                description="Clear AI patterns - robotic language detected",
                recommendation="Requires significant creative improvement",
                is_passing=False,
                color_code="🔴",
                emoji="🤖"
            ),
            "61-100": ScoreInterpretation(
                category=ScoreCategory.CRITICAL,
                description="Heavy AI patterns - extremely robotic",
                recommendation="Complete rewrite with high creativity temperature",
                is_passing=False,
                color_code="🔴",
                emoji="🚨"
            )
        }

    def _define_natural_voice_thresholds(self) -> Dict[str, ScoreInterpretation]:
        """
        Define Natural Voice score thresholds and interpretations.
        
        CRITICAL PHILOSOPHY:
        - Low scores (0-14%): Too artificial, lacks authentic professional voice
        - Optimal scores (15-25%): AUTHENTIC professional expertise with natural flow
        - High scores (40-100%): FORCED HUMANIZATION - excessive casual language, trying too hard
        
        Natural Voice is NOT about sounding casual or colloquial.
        It's about authentic professional expertise expressed naturally.
        """
        return {
            "0-9": ScoreInterpretation(
                category=ScoreCategory.POOR,
                description="Too artificial - lacks authentic professional voice and expertise markers",
                recommendation="Add natural expertise indicators, industry-specific insights, and professional flow",
                is_passing=False,
                color_code="🔵",
                emoji="🎭"
            ),
            "10-14": ScoreInterpretation(
                category=ScoreCategory.ACCEPTABLE,
                description="Some professional authenticity but needs more natural expertise flow",
                recommendation="Enhance with genuine industry knowledge and natural technical language",
                is_passing=False,
                color_code="🟡",
                emoji="📝"
            ),
            "15-25": ScoreInterpretation(
                category=ScoreCategory.EXCELLENT,
                description="EXCELLENT - Authentic professional voice with natural expertise and credible flow",
                recommendation="Perfect balance of technical knowledge and natural expression",
                is_passing=True,
                color_code="🟢",
                emoji="🎯"
            ),
            "26-39": ScoreInterpretation(
                category=ScoreCategory.GOOD,
                description="Good professional authenticity with minor over-casualness",
                recommendation="Reduce excessive casual language while maintaining natural flow",
                is_passing=True,
                color_code="🟢",
                emoji="✅"
            ),
            "40-59": ScoreInterpretation(
                category=ScoreCategory.POOR,
                description="FORCED HUMANIZATION detected - excessive casual language, trying too hard",
                recommendation="Reduce exaggerated casual tone, maintain professional credibility",
                is_passing=False,
                color_code="🟠",
                emoji="⚠️"
            ),
            "60-100": ScoreInterpretation(
                category=ScoreCategory.CRITICAL,
                description="SEVERE over-humanization - sounds fake, forced, and unprofessional",
                recommendation="Complete rewrite with authentic professional voice, avoid humanization tricks",
                is_passing=False,
                color_code="🔴",
                emoji="🚨"
            )
        }

    def interpret_ai_score(self, score: int) -> ScoreInterpretation:
        """Interpret an AI detection score."""
        for range_key, interpretation in self.ai_thresholds.items():
            min_score, max_score = map(int, range_key.split('-'))
            if min_score <= score <= max_score:
                return interpretation
        
        # Fallback for edge cases
        return self.ai_thresholds["61-100"]

    def interpret_natural_voice_score(self, score: int) -> ScoreInterpretation:
        """Interpret a Natural Voice score."""
        for range_key, interpretation in self.natural_voice_thresholds.items():
            min_score, max_score = map(int, range_key.split('-'))
            if min_score <= score <= max_score:
                return interpretation
        
        # Fallback for edge cases
        return self.natural_voice_thresholds["60-100"]

    def get_comprehensive_assessment(
        self, ai_score: int, nv_score: int, ai_threshold: int, nv_threshold: int
    ) -> Dict[str, any]:
        """Get comprehensive assessment of both scores."""
        ai_interpretation = self.interpret_ai_score(ai_score)
        nv_interpretation = self.interpret_natural_voice_score(nv_score)
        
        # Determine overall status
        ai_passes = ai_score <= ai_threshold
        nv_passes = nv_score <= nv_threshold
        overall_pass = ai_passes and nv_passes
        
        # Generate combined recommendations
        recommendations = []
        if not ai_passes:
            recommendations.append(f"AI: {ai_interpretation.recommendation}")
        if not nv_passes:
            recommendations.append(f"NV: {nv_interpretation.recommendation}")
        
        # Specific combination insights
        if ai_score <= 25 and 15 <= nv_score <= 25:
            recommendations.append("EXCELLENT: Optimal balance of low AI patterns and authentic professional voice")
        elif ai_score <= 25 and nv_score > 40:
            recommendations.append("CAUTION: Good AI detection but over-humanized voice - reduce forced casualness")
        elif ai_score > 40 and 15 <= nv_score <= 25:
            recommendations.append("MIXED: Good natural voice but too many AI patterns - increase creativity")
        elif ai_score > 40 and nv_score > 40:
            recommendations.append("CRITICAL: Both AI patterns and forced humanization detected - complete rewrite needed")
        
        return {
            "ai_interpretation": ai_interpretation,
            "nv_interpretation": nv_interpretation,
            "ai_passes": ai_passes,
            "nv_passes": nv_passes,
            "overall_pass": overall_pass,
            "recommendations": recommendations,
            "quality_level": self._determine_quality_level(ai_score, nv_score),
        }

    def _determine_quality_level(self, ai_score: int, nv_score: int) -> str:
        """Determine overall quality level based on both scores."""
        if ai_score <= 15 and 15 <= nv_score <= 25:
            return "PREMIUM"
        elif ai_score <= 25 and 15 <= nv_score <= 30:
            return "EXCELLENT"
        elif ai_score <= 35 and 10 <= nv_score <= 35:
            return "GOOD"
        elif ai_score <= 50 and nv_score <= 50:
            return "ACCEPTABLE"
        else:
            return "NEEDS_IMPROVEMENT"

    def is_threshold_setting_useful(self, ai_threshold: int, nv_threshold: int) -> Dict[str, any]:
        """
        Analyze if the current threshold settings are useful and appropriately configured.
        
        Returns analysis of threshold effectiveness and recommendations.
        """
        analysis = {
            "ai_threshold_analysis": self._analyze_ai_threshold(ai_threshold),
            "nv_threshold_analysis": self._analyze_nv_threshold(nv_threshold),
            "threshold_compatibility": self._analyze_threshold_compatibility(ai_threshold, nv_threshold),
            "recommendations": []
        }
        
        # AI threshold analysis
        if ai_threshold > 40:
            analysis["recommendations"].append("AI threshold too high - allows too many robotic patterns")
        elif ai_threshold < 15:
            analysis["recommendations"].append("AI threshold very strict - may be difficult to achieve")
        
        # Natural Voice threshold analysis  
        if nv_threshold > 35:
            analysis["recommendations"].append("NV threshold too high - allows forced humanization")
        elif nv_threshold < 20:
            analysis["recommendations"].append("NV threshold may be too strict for natural professional voice")
        
        # Compatibility analysis
        if ai_threshold <= 25 and 20 <= nv_threshold <= 30:
            analysis["recommendations"].append("EXCELLENT threshold configuration for authentic professional content")
        
        return analysis

    def _analyze_ai_threshold(self, threshold: int) -> Dict[str, str]:
        """Analyze AI threshold setting."""
        if threshold <= 15:
            return {"level": "very_strict", "description": "Extremely strict AI detection"}
        elif threshold <= 25:
            return {"level": "strict", "description": "Strict AI detection - good for professional content"}
        elif threshold <= 35:
            return {"level": "moderate", "description": "Moderate AI detection tolerance"}
        elif threshold <= 50:
            return {"level": "lenient", "description": "Lenient AI detection - allows some robotic patterns"}
        else:
            return {"level": "very_lenient", "description": "Very lenient - may allow heavy AI patterns"}

    def _analyze_nv_threshold(self, threshold: int) -> Dict[str, str]:
        """Analyze Natural Voice threshold setting."""
        if threshold <= 20:
            return {"level": "strict", "description": "Strict natural voice requirements"}
        elif threshold <= 30:
            return {"level": "balanced", "description": "Balanced natural voice tolerance"}
        elif threshold <= 40:
            return {"level": "moderate", "description": "Moderate tolerance for casual elements"}
        else:
            return {"level": "lenient", "description": "Lenient - may allow forced humanization"}

    def _analyze_threshold_compatibility(self, ai_threshold: int, nv_threshold: int) -> Dict[str, str]:
        """Analyze how well the thresholds work together."""
        if ai_threshold <= 25 and 20 <= nv_threshold <= 30:
            return {"compatibility": "excellent", "description": "Optimal settings for professional content"}
        elif ai_threshold <= 35 and nv_threshold <= 35:
            return {"compatibility": "good", "description": "Good balance for most content types"}
        elif ai_threshold > 40 or nv_threshold > 40:
            return {"compatibility": "concerning", "description": "May allow low-quality content"}
        else:
            return {"compatibility": "acceptable", "description": "Workable but could be optimized"}
