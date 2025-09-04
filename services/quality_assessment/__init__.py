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
import statistics
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import Counter

from .. import BaseService, ServiceConfiguration, ServiceError

logger = logging.getLogger(__name__)


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
    """Individual quality dimension score."""
    dimension: QualityDimension
    score: float  # 0.0 to 1.0
    weight: float = 1.0
    feedback: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityAssessment:
    """Complete quality assessment result."""
    content_id: str
    overall_score: float
    dimension_scores: List[QualityScore]
    weighted_score: float
    grade: str  # A, B, C, D, F
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
    """Quality trend analysis."""
    content_type: str
    time_period: str
    average_score: float
    score_trend: List[float]
    dimension_trends: Dict[QualityDimension, List[float]]
    improvement_rate: float
    consistency_score: float


class QualityAssessmentError(ServiceError):
    """Raised when quality assessment fails."""
    pass


class QualityAssessmentService(BaseService):
    """
    Service for comprehensive quality assessment and scoring.

    This service provides:
    - Multi-dimensional quality evaluation
    - Readability and structure analysis
    - Technical accuracy assessment
    - Consistency and completeness checking
    - Quality benchmarking and trends
    - Detailed feedback and recommendations
    """

    def __init__(self, config: ServiceConfiguration):
        # Initialize attributes before calling super().__init__
        self.assessment_history: Dict[str, List[QualityAssessment]] = {}
        self.quality_benchmarks: Dict[str, QualityBenchmark] = {}
        self.dimension_weights: Dict[QualityDimension, float] = {}
        self.quality_trends: Dict[str, QualityTrend] = {}

        super().__init__(config)

    def _validate_config(self) -> None:
        """Validate service configuration."""
        # No specific validation required for base implementation
        pass

    def _initialize(self) -> None:
        """Initialize the service with default configurations."""
        # Set default dimension weights
        self.dimension_weights = {
            QualityDimension.READABILITY: 0.15,
            QualityDimension.STRUCTURE: 0.20,
            QualityDimension.ACCURACY: 0.25,
            QualityDimension.CONSISTENCY: 0.15,
            QualityDimension.COMPLETENESS: 0.15,
            QualityDimension.ENGAGEMENT: 0.05,
            QualityDimension.TECHNICAL_DEPTH: 0.05
        }

        # Initialize default benchmarks
        self._initialize_default_benchmarks()

        self.logger.info("Quality Assessment Service initialized")

    def _initialize_default_benchmarks(self) -> None:
        """Initialize default quality benchmarks."""
        # High quality benchmark
        high_quality = QualityBenchmark(
            benchmark_id="high_quality",
            name="High Quality Standard",
            dimension_thresholds={
                QualityDimension.READABILITY: 0.85,
                QualityDimension.STRUCTURE: 0.90,
                QualityDimension.ACCURACY: 0.95,
                QualityDimension.CONSISTENCY: 0.85,
                QualityDimension.COMPLETENESS: 0.90,
                QualityDimension.ENGAGEMENT: 0.80,
                QualityDimension.TECHNICAL_DEPTH: 0.85
            },
            overall_threshold=0.88,
            description="High quality content standards"
        )

        # Standard quality benchmark
        standard_quality = QualityBenchmark(
            benchmark_id="standard_quality",
            name="Standard Quality",
            dimension_thresholds={
                QualityDimension.READABILITY: 0.70,
                QualityDimension.STRUCTURE: 0.75,
                QualityDimension.ACCURACY: 0.80,
                QualityDimension.CONSISTENCY: 0.70,
                QualityDimension.COMPLETENESS: 0.75,
                QualityDimension.ENGAGEMENT: 0.65,
                QualityDimension.TECHNICAL_DEPTH: 0.70
            },
            overall_threshold=0.73,
            description="Standard quality expectations"
        )

        self.quality_benchmarks["high_quality"] = high_quality
        self.quality_benchmarks["standard_quality"] = standard_quality

    async def assess_quality(
        self,
        content: str,
        content_id: Optional[str] = None,
        content_type: str = "general",
        benchmark_id: Optional[str] = None,
        **kwargs
    ) -> QualityAssessment:
        """
        Perform comprehensive quality assessment.

        Args:
            content: Content to assess
            content_id: Unique identifier for the content
            content_type: Type of content (article, blog, technical, etc.)
            benchmark_id: Benchmark to compare against
            **kwargs: Additional assessment parameters

        Returns:
            QualityAssessment: Complete quality assessment
        """
        if not content_id:
            content_id = self._generate_content_id(content)

        start_time = datetime.now()

        try:
            # Assess each quality dimension
            dimension_scores = []
            for dimension in QualityDimension:
                score = await self._assess_dimension(content, dimension, content_type, **kwargs)
                dimension_scores.append(score)

            # Calculate overall scores
            overall_score = sum(s.score for s in dimension_scores) / len(dimension_scores)
            weighted_score = sum(s.score * s.weight for s in dimension_scores)

            # Determine grade
            grade = self._calculate_grade(overall_score)

            # Generate feedback
            strengths, weaknesses, recommendations = self._generate_feedback(
                dimension_scores, content_type
            )

            # Create assessment result
            assessment = QualityAssessment(
                content_id=content_id,
                overall_score=overall_score,
                dimension_scores=dimension_scores,
                weighted_score=weighted_score,
                grade=grade,
                strengths=strengths,
                weaknesses=weaknesses,
                recommendations=recommendations,
                metadata={
                    "content_type": content_type,
                    "benchmark_id": benchmark_id,
                    "word_count": len(content.split()),
                    "character_count": len(content),
                    "processing_time": (datetime.now() - start_time).total_seconds()
                },
                timestamp=datetime.now()
            )

            # Store assessment history
            if content_id not in self.assessment_history:
                self.assessment_history[content_id] = []
            self.assessment_history[content_id].append(assessment)

            # Update quality trends
            self._update_quality_trends(content_type, assessment)

            self.logger.info(f"Quality assessment completed for {content_id}: "
                           f"score={overall_score:.3f}, grade={grade}")

            return assessment

        except Exception as e:
            self.logger.error(f"Quality assessment failed for {content_id}: {e}")
            raise QualityAssessmentError(f"Assessment failed: {e}") from e

    async def _assess_dimension(
        self,
        content: str,
        dimension: QualityDimension,
        content_type: str,
        **kwargs
    ) -> QualityScore:
        """Assess a specific quality dimension."""
        if dimension == QualityDimension.READABILITY:
            return await self._assess_readability(content, **kwargs)
        elif dimension == QualityDimension.STRUCTURE:
            return await self._assess_structure(content, content_type, **kwargs)
        elif dimension == QualityDimension.ACCURACY:
            return await self._assess_accuracy(content, content_type, **kwargs)
        elif dimension == QualityDimension.CONSISTENCY:
            return await self._assess_consistency(content, **kwargs)
        elif dimension == QualityDimension.COMPLETENESS:
            return await self._assess_completeness(content, content_type, **kwargs)
        elif dimension == QualityDimension.ENGAGEMENT:
            return await self._assess_engagement(content, **kwargs)
        elif dimension == QualityDimension.TECHNICAL_DEPTH:
            return await self._assess_technical_depth(content, content_type, **kwargs)
        else:
            raise QualityAssessmentError(f"Unknown quality dimension: {dimension}")

    async def _assess_readability(self, content: str, **kwargs) -> QualityScore:
        """Assess content readability."""
        words = content.split()
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not words or not sentences:
            return QualityScore(
                dimension=QualityDimension.READABILITY,
                score=0.0,
                feedback="Content is too short or malformed"
            )

        # Average words per sentence
        avg_words_per_sentence = len(words) / len(sentences)

        # Average syllables per word (simplified)
        avg_syllables_per_word = sum(self._count_syllables(word) for word in words) / len(words)

        # Flesch Reading Ease score (simplified)
        flesch_score = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)

        # Normalize to 0-1 scale
        readability_score = max(0.0, min(1.0, flesch_score / 100.0))

        feedback = self._get_readability_feedback(readability_score, avg_words_per_sentence)

        return QualityScore(
            dimension=QualityDimension.READABILITY,
            score=readability_score,
            feedback=feedback,
            metadata={
                "avg_words_per_sentence": avg_words_per_sentence,
                "avg_syllables_per_word": avg_syllables_per_word,
                "flesch_score": flesch_score
            }
        )

    async def _assess_structure(self, content: str, content_type: str, **kwargs) -> QualityScore:
        """Assess content structure."""
        # Check for structural elements
        has_title = bool(re.search(r'^#{1,6}\s+', content, re.MULTILINE))
        has_paragraphs = len(re.findall(r'\n\s*\n', content)) > 0
        has_lists = bool(re.search(r'^[\s]*[-*+]\s+', content, re.MULTILINE))
        has_headings = len(re.findall(r'^#{1,6}\s+', content, re.MULTILINE)) > 1

        structure_score = 0.0
        feedback_parts = []

        if has_title:
            structure_score += 0.2
            feedback_parts.append("Has clear title")
        else:
            feedback_parts.append("Missing clear title")

        if has_paragraphs:
            structure_score += 0.3
            feedback_parts.append("Well-organized paragraphs")
        else:
            feedback_parts.append("Could benefit from paragraph breaks")

        if has_lists:
            structure_score += 0.2
            feedback_parts.append("Uses lists effectively")
        else:
            feedback_parts.append("Could use lists for better organization")

        if has_headings:
            structure_score += 0.3
            feedback_parts.append("Good use of headings")
        else:
            feedback_parts.append("Could benefit from section headings")

        return QualityScore(
            dimension=QualityDimension.STRUCTURE,
            score=structure_score,
            feedback="; ".join(feedback_parts),
            metadata={
                "has_title": has_title,
                "has_paragraphs": has_paragraphs,
                "has_lists": has_lists,
                "has_headings": has_headings
            }
        )

    async def _assess_accuracy(self, content: str, content_type: str, **kwargs) -> QualityScore:
        """Assess content accuracy."""
        # This is a simplified accuracy assessment
        # In a real implementation, this would use fact-checking APIs or domain expertise

        # Check for factual indicators
        has_sources = bool(re.search(r'\b(source|reference|cite|according to)\b', content, re.IGNORECASE))
        has_data = bool(re.search(r'\b(\d+%|\d+\.\d+|statistics|data|research)\b', content, re.IGNORECASE))
        has_qualifiers = bool(re.search(r'\b(may|might|could|approximately|estimated)\b', content, re.IGNORECASE))

        accuracy_score = 0.5  # Base score

        if has_sources:
            accuracy_score += 0.2
        if has_data:
            accuracy_score += 0.2
        if has_qualifiers:
            accuracy_score += 0.1  # Appropriate use of uncertainty qualifiers

        feedback = "Accuracy assessment based on content indicators"
        if has_sources:
            feedback += "; Includes source references"
        if has_data:
            feedback += "; Contains supporting data"
        if has_qualifiers:
            feedback += "; Uses appropriate uncertainty qualifiers"

        return QualityScore(
            dimension=QualityDimension.ACCURACY,
            score=min(1.0, accuracy_score),
            feedback=feedback,
            metadata={
                "has_sources": has_sources,
                "has_data": has_data,
                "has_qualifiers": has_qualifiers
            }
        )

    async def _assess_consistency(self, content: str, **kwargs) -> QualityScore:
        """Assess content consistency."""
        # Check for consistency in terminology, tone, and style
        words = re.findall(r'\b\w+\b', content.lower())

        if len(words) < 10:
            return QualityScore(
                dimension=QualityDimension.CONSISTENCY,
                score=0.5,
                feedback="Content too short for consistency assessment"
            )

        # Check for repeated technical terms (consistency indicator)
        word_freq = Counter(words)
        technical_terms = [word for word, freq in word_freq.items() if freq > 2 and len(word) > 4]

        # Check for consistent tense usage
        past_tense = len(re.findall(r'\b\w+ed\b', content))
        present_tense = len(re.findall(r'\b\w+s\b|\bam\b|\bis\b|\bare\b', content))

        consistency_score = 0.6  # Base score

        if technical_terms:
            consistency_score += 0.2  # Consistent use of technical terminology

        # Balance between past and present tense
        total_verbs = past_tense + present_tense
        if total_verbs > 0:
            tense_balance = min(past_tense, present_tense) / max(past_tense, present_tense)
            consistency_score += tense_balance * 0.2

        feedback = f"Found {len(technical_terms)} consistently used technical terms"

        return QualityScore(
            dimension=QualityDimension.CONSISTENCY,
            score=min(1.0, consistency_score),
            feedback=feedback,
            metadata={
                "technical_terms_count": len(technical_terms),
                "tense_balance": tense_balance if 'tense_balance' in locals() else 0.0
            }
        )

    async def _assess_completeness(self, content: str, content_type: str, **kwargs) -> QualityScore:
        """Assess content completeness."""
        word_count = len(content.split())

        # Base completeness on content length and structure
        completeness_score = 0.0

        if word_count > 500:
            completeness_score = 0.9
        elif word_count > 200:
            completeness_score = 0.7
        elif word_count > 100:
            completeness_score = 0.5
        else:
            completeness_score = 0.3

        # Check for comprehensive coverage indicators
        has_introduction = bool(re.search(r'\b(intro|overview|summary|purpose)\b', content, re.IGNORECASE))
        has_conclusion = bool(re.search(r'\b(conclusion|summary|finally|in conclusion)\b', content, re.IGNORECASE))

        if has_introduction:
            completeness_score += 0.05
        if has_conclusion:
            completeness_score += 0.05

        feedback = f"Content length: {word_count} words"
        if has_introduction and has_conclusion:
            feedback += "; Has clear introduction and conclusion"
        elif has_introduction:
            feedback += "; Has introduction but could use conclusion"
        elif has_conclusion:
            feedback += "; Has conclusion but could use introduction"

        return QualityScore(
            dimension=QualityDimension.COMPLETENESS,
            score=min(1.0, completeness_score),
            feedback=feedback,
            metadata={
                "word_count": word_count,
                "has_introduction": has_introduction,
                "has_conclusion": has_conclusion
            }
        )

    async def _assess_engagement(self, content: str, **kwargs) -> QualityScore:
        """Assess content engagement."""
        # Check for engagement indicators
        has_questions = bool(re.search(r'\?', content))
        has_exclamations = bool(re.search(r'!', content))
        has_quotes = bool(re.search(r'"[^"]*"', content) or re.search(r"'[^']*'", content))
        has_calls_to_action = bool(re.search(r'\b(learn more|find out|discover|see|check out)\b', content, re.IGNORECASE))

        engagement_score = 0.0

        if has_questions:
            engagement_score += 0.3
        if has_exclamations:
            engagement_score += 0.2
        if has_quotes:
            engagement_score += 0.2
        if has_calls_to_action:
            engagement_score += 0.3

        feedback_parts = []
        if has_questions:
            feedback_parts.append("Uses questions to engage readers")
        if has_exclamations:
            feedback_parts.append("Uses exclamations for emphasis")
        if has_quotes:
            feedback_parts.append("Includes quotes for credibility")
        if has_calls_to_action:
            feedback_parts.append("Contains calls to action")

        return QualityScore(
            dimension=QualityDimension.ENGAGEMENT,
            score=min(1.0, engagement_score),
            feedback="; ".join(feedback_parts) if feedback_parts else "Could benefit from more engaging elements",
            metadata={
                "has_questions": has_questions,
                "has_exclamations": has_exclamations,
                "has_quotes": has_quotes,
                "has_calls_to_action": has_calls_to_action
            }
        )

    async def _assess_technical_depth(self, content: str, content_type: str, **kwargs) -> QualityScore:
        """Assess technical depth."""
        if content_type not in ["technical", "tutorial", "documentation"]:
            return QualityScore(
                dimension=QualityDimension.TECHNICAL_DEPTH,
                score=0.5,
                feedback="Not applicable for non-technical content"
            )

        # Check for technical indicators
        has_code = bool(re.search(r'`.*?`', content))  # Inline code
        has_code_blocks = bool(re.search(r'```.*?```', content, re.DOTALL))  # Code blocks
        has_technical_terms = bool(re.search(r'\b(API|function|class|method|algorithm|database)\b', content, re.IGNORECASE))
        has_examples = bool(re.search(r'\b(example|for instance|such as|like this)\b', content, re.IGNORECASE))

        technical_score = 0.0

        if has_code:
            technical_score += 0.3
        if has_code_blocks:
            technical_score += 0.3
        if has_technical_terms:
            technical_score += 0.2
        if has_examples:
            technical_score += 0.2

        feedback_parts = []
        if has_code or has_code_blocks:
            feedback_parts.append("Includes code examples")
        if has_technical_terms:
            feedback_parts.append("Uses appropriate technical terminology")
        if has_examples:
            feedback_parts.append("Provides practical examples")

        return QualityScore(
            dimension=QualityDimension.TECHNICAL_DEPTH,
            score=min(1.0, technical_score),
            feedback="; ".join(feedback_parts) if feedback_parts else "Could benefit from more technical depth",
            metadata={
                "has_code": has_code,
                "has_code_blocks": has_code_blocks,
                "has_technical_terms": has_technical_terms,
                "has_examples": has_examples
            }
        )

    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)."""
        word = word.lower()
        count = 0
        vowels = "aeiouy"
        if word[0] in vowels:
            count += 1
        for i in range(1, len(word)):
            if word[i] in vowels and word[i - 1] not in vowels:
                count += 1
        if word.endswith("e"):
            count -= 1
        return max(1, count)

    def _get_readability_feedback(self, score: float, avg_words_per_sentence: float) -> str:
        """Generate readability feedback."""
        if score > 0.8:
            return "Excellent readability"
        elif score > 0.6:
            feedback = "Good readability"
            if avg_words_per_sentence > 20:
                feedback += "; Consider shorter sentences"
            return feedback
        elif score > 0.4:
            return "Moderate readability; could be improved"
        else:
            return "Poor readability; needs significant improvement"

    def _calculate_grade(self, overall_score: float) -> str:
        """Calculate letter grade from score."""
        if overall_score >= 0.9:
            return "A"
        elif overall_score >= 0.8:
            return "B"
        elif overall_score >= 0.7:
            return "C"
        elif overall_score >= 0.6:
            return "D"
        else:
            return "F"

    def _generate_feedback(
        self,
        dimension_scores: List[QualityScore],
        content_type: str
    ) -> Tuple[List[str], List[str], List[str]]:
        """Generate comprehensive feedback."""
        strengths = []
        weaknesses = []
        recommendations = []

        for score in dimension_scores:
            if score.score > 0.8:
                strengths.append(f"Strong {score.dimension.value}: {score.feedback}")
            elif score.score < 0.6:
                weaknesses.append(f"Weak {score.dimension.value}: {score.feedback}")
                recommendations.append(f"Improve {score.dimension.value}: {score.feedback}")

        return strengths, weaknesses, recommendations

    def _generate_content_id(self, content: str) -> str:
        """Generate a unique content ID."""
        import hashlib
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"content_{content_hash}"

    def _update_quality_trends(self, content_type: str, assessment: QualityAssessment) -> None:
        """Update quality trends for content type."""
        if content_type not in self.quality_trends:
            self.quality_trends[content_type] = QualityTrend(
                content_type=content_type,
                time_period="daily",
                average_score=0.0,
                score_trend=[],
                dimension_trends={dim: [] for dim in QualityDimension},
                improvement_rate=0.0,
                consistency_score=0.0
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
                trend.dimension_trends[score.dimension] = trend.dimension_trends[score.dimension][-50:]

        # Update average score
        trend.average_score = statistics.mean(trend.score_trend) if trend.score_trend else 0.0

        # Calculate improvement rate (simplified)
        if len(trend.score_trend) >= 2:
            recent_scores = trend.score_trend[-10:] if len(trend.score_trend) >= 10 else trend.score_trend
            if len(recent_scores) >= 2:
                trend.improvement_rate = (recent_scores[-1] - recent_scores[0]) / len(recent_scores)

        # Calculate consistency score
        if len(trend.score_trend) >= 2:
            trend.consistency_score = 1.0 - (statistics.stdev(trend.score_trend) if len(trend.score_trend) > 1 else 0.0)

    def compare_to_benchmark(
        self,
        assessment: QualityAssessment,
        benchmark_id: str
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
            "overall_comparison": "above" if assessment.overall_score >= benchmark.overall_threshold else "below",
            "overall_difference": assessment.overall_score - benchmark.overall_threshold,
            "dimension_comparison": {}
        }

        for score in assessment.dimension_scores:
            threshold = benchmark.dimension_thresholds.get(score.dimension, 0.5)
            comparison["dimension_comparison"][score.dimension.value] = {
                "score": score.score,
                "threshold": threshold,
                "status": "above" if score.score >= threshold else "below",
                "difference": score.score - threshold
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
            }
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
                "recommendations": assessment.recommendations
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
