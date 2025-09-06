"""
Quality Assessment Service

This service provides comprehensive quality assessment and scoring capabilities
that can be used by any component in the system. It evaluates content quality
across multiple dimensions and provides detailed scoring and feedback.

Features:
- Multi-dimensional quality scoring
- Readability analysis
- Content structure analysis
- Technical accuracy assessment
- Consistency checking
- Quality trend analysis
- Benchmarking against standards
"""

import asyncio
import logging
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
import hashlib

import statistics
from ..base import BaseService, ServiceConfiguration, ServiceError, ServiceConfigurationError


class QualityDimension(Enum):
    """Quality dimensions for assessment."""
    READABILITY = "readability"
    STRUCTURE = "structure"
    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"
    COMPLETENESS = "completeness"
    ENGAGEMENT = "engagement"
    TECHNICAL_DEPTH = "technical_depth"


@dataclass
class QualityScore:
    """Individual quality score for a dimension."""
    dimension: QualityDimension
    score: float
    weight: float
    feedback: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityAssessment:
    """Complete quality assessment result."""
    content_id: str
    overall_score: float
    dimension_scores: List[QualityScore]
    weighted_score: float
    grade: str
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    metadata: Dict[str, Any]
    timestamp: datetime


@dataclass
class QualityBenchmark:
    """Quality benchmark for comparison."""
    benchmark_id: str
    name: str
    dimension_thresholds: Dict[QualityDimension, float]
    overall_threshold: float
    description: str = ""


@dataclass
class QualityTrend:
    """Quality trend data for content types."""
    content_type: str
    time_period: str
    average_score: float
    score_trend: List[float]
    dimension_trends: Dict[QualityDimension, List[float]]
    improvement_rate: float
    consistency_score: float


class QualityAssessmentService(BaseService):
    """
    Service for comprehensive quality assessment and scoring.

    This service evaluates content across multiple quality dimensions and provides
    detailed feedback, trend analysis, and benchmarking capabilities.
    """

    def __init__(self, config: ServiceConfiguration):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)

        # Initialize data structures
        self.assessment_history: Dict[str, List[QualityAssessment]] = {}
        self.quality_trends: Dict[str, QualityTrend] = {}
        self.quality_benchmarks: Dict[str, QualityBenchmark] = {}

        # Default dimension weights
        self.dimension_weights = {
            QualityDimension.READABILITY: 0.15,
            QualityDimension.STRUCTURE: 0.20,
            QualityDimension.ACCURACY: 0.25,
            QualityDimension.CONSISTENCY: 0.15,
            QualityDimension.COMPLETENESS: 0.15,
            QualityDimension.ENGAGEMENT: 0.05,
            QualityDimension.TECHNICAL_DEPTH: 0.05,
        }

        # Initialize default benchmarks
        self._initialize_default_benchmarks()

    def _validate_config(self) -> None:
        """Validate service configuration."""
        if not self.config.name:
            raise ServiceConfigurationError("Service name is required")

    def _initialize(self) -> None:
        """Initialize the service."""
        self.logger.info(f"Initializing Quality Assessment Service: {self.config.name}")
        self._healthy = True

    def _initialize_default_benchmarks(self) -> None:
        """Initialize default quality benchmarks."""
        # High quality benchmark
        self.quality_benchmarks["high_quality"] = QualityBenchmark(
            benchmark_id="high_quality",
            name="High Quality Standard",
            dimension_thresholds={
                QualityDimension.READABILITY: 0.85,
                QualityDimension.STRUCTURE: 0.88,
                QualityDimension.ACCURACY: 0.90,
                QualityDimension.CONSISTENCY: 0.85,
                QualityDimension.COMPLETENESS: 0.88,
                QualityDimension.ENGAGEMENT: 0.80,
                QualityDimension.TECHNICAL_DEPTH: 0.85,
            },
            overall_threshold=0.88,
            description="High quality standards for premium content"
        )

        # Standard quality benchmark
        self.quality_benchmarks["standard_quality"] = QualityBenchmark(
            benchmark_id="standard_quality",
            name="Standard Quality",
            dimension_thresholds={
                QualityDimension.READABILITY: 0.70,
                QualityDimension.STRUCTURE: 0.75,
                QualityDimension.ACCURACY: 0.80,
                QualityDimension.CONSISTENCY: 0.70,
                QualityDimension.COMPLETENESS: 0.75,
                QualityDimension.ENGAGEMENT: 0.65,
                QualityDimension.TECHNICAL_DEPTH: 0.70,
            },
            overall_threshold=0.73,
            description="Standard quality requirements"
        )

    def _generate_content_id(self, content: str) -> str:
        """Generate a unique content ID from content hash."""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"content_{content_hash}"

    async def assess_quality(
        self,
        content: str,
        content_type: str = "general",
        content_id: Optional[str] = None,
        benchmark_id: str = "standard_quality"
    ) -> QualityAssessment:
        """
        Perform comprehensive quality assessment.

        Args:
            content: Content to assess
            content_type: Type of content (general, technical, creative, etc.)
            content_id: Optional content identifier
            benchmark_id: Benchmark to use for assessment

        Returns:
            QualityAssessment: Complete assessment result
        """
        if not content_id:
            content_id = self._generate_content_id(content)

        # Assess each dimension
        dimension_scores = []

        # Readability assessment
        readability_score = await self._assess_readability(content)
        dimension_scores.append(readability_score)

        # Structure assessment
        structure_score = await self._assess_structure(content, content_type)
        dimension_scores.append(structure_score)

        # Technical depth assessment
        technical_score = await self._assess_technical_depth(content, content_type)
        dimension_scores.append(technical_score)

        # Engagement assessment
        engagement_score = await self._assess_engagement(content)
        dimension_scores.append(engagement_score)

        # Calculate overall scores
        overall_score = sum(score.score * score.weight for score in dimension_scores)
        weighted_score = overall_score  # For now, same as overall

        # Determine grade
        grade = self._calculate_grade(overall_score)

        # Generate feedback
        strengths, weaknesses, recommendations = self._generate_feedback(
            dimension_scores, content_type
        )

        # Create assessment
        assessment = QualityAssessment(
            content_id=content_id,
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            weighted_score=weighted_score,
            grade=grade,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            metadata={"content_type": content_type, "benchmark_id": benchmark_id},
            timestamp=datetime.now()
        )

        # Store in history
        if content_id not in self.assessment_history:
            self.assessment_history[content_id] = []
        self.assessment_history[content_id].append(assessment)

        # Update trends
        self._update_quality_trends(content_type, assessment)

        return assessment

    async def _assess_readability(self, content: str) -> QualityScore:
        """Assess content readability."""
        if not content.strip():
            return QualityScore(
                dimension=QualityDimension.READABILITY,
                score=0.0,
                weight=self.dimension_weights[QualityDimension.READABILITY],
                feedback="Empty content"
            )

        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return QualityScore(
                dimension=QualityDimension.READABILITY,
                score=0.0,
                weight=self.dimension_weights[QualityDimension.READABILITY],
                feedback="No sentences found"
            )

        words = content.split()
        avg_words_per_sentence = len(words) / len(sentences)

        # Simple readability score based on sentence length
        if avg_words_per_sentence < 15:
            score = 0.9
            feedback = "Good readability with concise sentences"
        elif avg_words_per_sentence < 25:
            score = 0.7
            feedback = "Moderate readability"
        else:
            score = 0.4
            feedback = "Complex sentences may reduce readability"

        return QualityScore(
            dimension=QualityDimension.READABILITY,
            score=score,
            weight=self.dimension_weights[QualityDimension.READABILITY],
            feedback=feedback,
            metadata={
                "sentence_count": len(sentences),
                "word_count": len(words),
                "avg_words_per_sentence": avg_words_per_sentence
            }
        )

    async def _assess_structure(self, content: str, content_type: str) -> QualityScore:
        """Assess content structure."""
        # Check for headings
        heading_pattern = r'^#{1,6}\s+'
        headings = len(re.findall(heading_pattern, content, re.MULTILINE))

        # Check for paragraphs
        paragraphs = len(re.split(r'\n\s*\n', content.strip()))

        # Check for lists
        list_items = len(re.findall(r'^[\s]*[-*+]\s+', content, re.MULTILINE))

        # Calculate structure score
        structure_score = min(1.0, (headings * 0.3 + paragraphs * 0.1 + list_items * 0.05))

        if structure_score > 0.8:
            feedback = "Excellent structure with clear organization"
        elif structure_score > 0.6:
            feedback = "Good structure"
        elif structure_score > 0.3:
            feedback = "Basic structure present"
        else:
            feedback = "Poor structure - consider adding headings and paragraphs"

        return QualityScore(
            dimension=QualityDimension.STRUCTURE,
            score=structure_score,
            weight=self.dimension_weights[QualityDimension.STRUCTURE],
            feedback=feedback,
            metadata={
                "headings": headings,
                "paragraphs": paragraphs,
                "list_items": list_items
            }
        )

    async def _assess_technical_depth(self, content: str, content_type: str) -> QualityScore:
        """Assess technical depth."""
        if content_type != "technical":
            return QualityScore(
                dimension=QualityDimension.TECHNICAL_DEPTH,
                score=0.5,
                weight=self.dimension_weights[QualityDimension.TECHNICAL_DEPTH],
                feedback="Not applicable for non-technical content"
            )

        # Look for technical indicators
        technical_terms = [
            r'\bO\([^)]+\)',  # Big O notation
            r'\bcomplexity\b',
            r'\balgorithm\b',
            r'\bfunction\b',
            r'\bclass\b',
            r'\bmethod\b',
            r'\bAPI\b',
            r'\bdatabase\b',
            r'\bserver\b',
            r'\bclient\b'
        ]

        technical_score = 0.0
        found_terms = []

        for term in technical_terms:
            matches = len(re.findall(term, content, re.IGNORECASE))
            if matches > 0:
                technical_score += 0.1
                found_terms.append(term)

        technical_score = min(1.0, technical_score)

        if technical_score > 0.7:
            feedback = "Strong technical depth"
        elif technical_score > 0.4:
            feedback = "Moderate technical content"
        else:
            feedback = "Limited technical depth"

        return QualityScore(
            dimension=QualityDimension.TECHNICAL_DEPTH,
            score=technical_score,
            weight=self.dimension_weights[QualityDimension.TECHNICAL_DEPTH],
            feedback=feedback,
            metadata={"technical_terms_found": len(found_terms)}
        )

    async def _assess_engagement(self, content: str) -> QualityScore:
        """Assess content engagement."""
        # Look for engagement indicators
        engagement_indicators = [
            r'\b(you|your|we|us|our)\b',
            r'[?!]{2,}',
            r'\b(amazing|exciting|incredible|wonderful)\b',
            r'\b(imagine|think|consider|wonder)\b',
            r'\b(discover|learn|explore|find)\b'
        ]

        engagement_score = 0.0

        for indicator in engagement_indicators:
            matches = len(re.findall(indicator, content, re.IGNORECASE))
            if matches > 0:
                engagement_score += 0.2

        engagement_score = min(1.0, engagement_score)

        if engagement_score > 0.6:
            feedback = "Highly engaging content"
        elif engagement_score > 0.3:
            feedback = "Moderately engaging"
        else:
            feedback = "Low engagement - consider adding more interactive elements"

        return QualityScore(
            dimension=QualityDimension.ENGAGEMENT,
            score=engagement_score,
            weight=self.dimension_weights[QualityDimension.ENGAGEMENT],
            feedback=feedback
        )

    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from score."""
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"

    def _generate_feedback(
        self,
        dimension_scores: List[QualityScore],
        content_type: str
    ) -> Tuple[List[str], List[str], List[str]]:
        """Generate feedback from dimension scores."""
        strengths = []
        weaknesses = []
        recommendations = []

        for score_obj in dimension_scores:
            if score_obj.score >= 0.7:
                strengths.append(f"Good {score_obj.dimension.value}: {score_obj.feedback}")
            elif score_obj.score >= 0.4:
                weaknesses.append(f"Average {score_obj.dimension.value}: {score_obj.feedback}")
            else:
                weaknesses.append(f"Poor {score_obj.dimension.value}: {score_obj.feedback}")
                recommendations.append(f"Improve {score_obj.dimension.value}: {score_obj.feedback}")

        return strengths, weaknesses, recommendations

    def _update_quality_trends(
        self, content_type: str, assessment: QualityAssessment
    ) -> None:
        """Update quality trends for content type."""
        if content_type not in self.quality_trends:
            self.quality_trends[content_type] = QualityTrend(
                content_type=content_type,
                time_period="daily",
                average_score=0.0,
                score_trend=[],
                dimension_trends={dim: [] for dim in QualityDimension},
                improvement_rate=0.0,
                consistency_score=0.0,
            )

        trend = self.quality_trends[content_type]

        # Update score trend
        trend.score_trend.append(assessment.overall_score)
        if len(trend.score_trend) > 50:  # Keep last 50 assessments
            trend.score_trend = trend.score_trend[-50:]

        # Update dimension trends
        for score in assessment.dimension_scores:
            trend.dimension_trends[score.dimension].append(score.score)
            if len(trend.dimension_trends[score.dimension]) > 50:
                trend.dimension_trends[score.dimension] = trend.dimension_trends[
                    score.dimension
                ][-50:]

        # Update average score
        trend.average_score = (
            statistics.mean(trend.score_trend) if trend.score_trend else 0.0
        )

        # Calculate improvement rate (simplified)
        if len(trend.score_trend) >= 2:
            recent_scores = (
                trend.score_trend[-10:]
                if len(trend.score_trend) >= 10
                else trend.score_trend
            )
            if len(recent_scores) >= 2:
                trend.improvement_rate = (recent_scores[-1] - recent_scores[0]) / len(
                    recent_scores
                )

        # Calculate consistency score
        if len(trend.score_trend) >= 2:
            trend.consistency_score = 1.0 - (
                statistics.stdev(trend.score_trend)
                if len(trend.score_trend) > 1
                else 0.0
            )

    def compare_to_benchmark(
        self, assessment: QualityAssessment, benchmark_id: str
    ) -> Dict[str, Any]:
        """
        Compare assessment to a quality benchmark.

        Args:
            assessment: Quality assessment to compare
            benchmark_id: Benchmark identifier

        Returns:
            Dict[str, Any]: Comparison results
        """
        if benchmark_id not in self.quality_benchmarks:
            return {"error": f"Benchmark {benchmark_id} not found"}

        benchmark = self.quality_benchmarks[benchmark_id]

        comparison = {
            "benchmark_name": benchmark.name,
            "overall_comparison": "above"
            if assessment.overall_score >= benchmark.overall_threshold
            else "below",
            "overall_difference": assessment.overall_score
            - benchmark.overall_threshold,
            "dimension_comparison": {},
        }

        for score in assessment.dimension_scores:
            threshold = benchmark.dimension_thresholds.get(score.dimension, 0.5)
            comparison["dimension_comparison"][score.dimension.value] = {
                "score": score.score,
                "threshold": threshold,
                "status": "above" if score.score >= threshold else "below",
                "difference": score.score - threshold,
            }

        return comparison

    def get_quality_trends(self, content_type: str) -> Optional[Dict[str, Any]]:
        """
        Get quality trends for a content type.

        Args:
            content_type: Type of content

        Returns:
            Optional[Dict[str, Any]]: Quality trends data
        """
        if content_type not in self.quality_trends:
            return None

        trend = self.quality_trends[content_type]

        return {
            "content_type": content_type,
            "average_score": trend.average_score,
            "total_assessments": len(trend.score_trend),
            "improvement_rate": trend.improvement_rate,
            "consistency_score": trend.consistency_score,
            "recent_scores": trend.score_trend[-10:] if trend.score_trend else [],
            "dimension_averages": {
                dim.value: statistics.mean(scores) if scores else 0.0
                for dim, scores in trend.dimension_trends.items()
            },
        }

    def get_assessment_history(self, content_id: str) -> List[Dict[str, Any]]:
        """
        Get assessment history for content.

        Args:
            content_id: Content identifier

        Returns:
            List[Dict[str, Any]]: Assessment history
        """
        if content_id not in self.assessment_history:
            return []

        return [
            {
                "timestamp": assessment.timestamp.isoformat(),
                "overall_score": assessment.overall_score,
                "grade": assessment.grade,
                "strengths": assessment.strengths,
                "weaknesses": assessment.weaknesses,
                "recommendations": assessment.recommendations,
            }
            for assessment in self.assessment_history[content_id]
        ]

    def health_check(self) -> bool:
        """Perform health check."""
        try:
            # Basic health check - service is healthy if it can perform assessments
            return True
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
