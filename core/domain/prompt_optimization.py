"""
Domain models for prompt optimization.
Contains value objects and entities for the prompt optimization domain.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from enum import Enum


class PromptPerformanceLevel(Enum):
    """Performance level classification for prompts."""

    EXCELLENT = "excellent"  # >80% success rate
    GOOD = "good"  # 60-80% success rate
    AVERAGE = "average"  # 40-60% success rate
    POOR = "poor"  # <40% success rate
    INSUFFICIENT_DATA = "insufficient_data"  # <10 samples


class TrendDirection(Enum):
    """Trend direction for prompt performance over time."""

    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class PromptMetrics:
    """Immutable performance metrics for a prompt."""

    success_rate: float
    average_score: float
    usage_count: int
    confidence_interval: Optional[Tuple[float, float]] = None
    trend_direction: TrendDirection = TrendDirection.UNKNOWN
    last_10_scores: List[int] = field(default_factory=list)

    @property
    def performance_level(self) -> PromptPerformanceLevel:
        """Classify performance level based on success rate and sample size."""
        if self.usage_count < 10:
            return PromptPerformanceLevel.INSUFFICIENT_DATA

        if self.success_rate >= 0.8:
            return PromptPerformanceLevel.EXCELLENT
        elif self.success_rate >= 0.6:
            return PromptPerformanceLevel.GOOD
        elif self.success_rate >= 0.4:
            return PromptPerformanceLevel.AVERAGE
        else:
            return PromptPerformanceLevel.POOR

    @property
    def is_statistically_significant(self) -> bool:
        """Check if sample size is sufficient for statistical significance."""
        return self.usage_count >= 10

    @property
    def reliability_score(self) -> float:
        """
        Calculate reliability score (0-1) based on consistency and sample size.
        Higher scores indicate more reliable performance data.
        """
        if self.usage_count == 0:
            return 0.0

        # Base reliability on sample size (logarithmic scale)
        sample_reliability = min(1.0, self.usage_count / 50.0)

        # Factor in score consistency (lower variance = higher reliability)
        if len(self.last_10_scores) >= 3:
            scores_std = np.std(self.last_10_scores) if self.last_10_scores else 0
            consistency_factor = max(0.1, 1.0 - (scores_std / 100.0))
        else:
            consistency_factor = 0.5  # Medium reliability for small samples

        return sample_reliability * consistency_factor


@dataclass(frozen=True)
class PromptUsage:
    """Single usage record for a prompt."""

    prompt_name: str
    detection_type: str
    score: int
    success: bool
    iteration: int
    section_name: str
    content_type: str
    material_type: Optional[str]
    timestamp: datetime
    context_hash: Optional[str] = None
    response_time_ms: Optional[int] = None

    def __post_init__(self):
        """Validate usage data."""
        if not 0 <= self.score <= 100:
            raise ValueError(f"Score must be 0-100, got {self.score}")
        if self.iteration < 1:
            raise ValueError(f"Iteration must be >= 1, got {self.iteration}")


@dataclass
class PromptPerformanceProfile:
    """Complete performance profile for a prompt."""

    prompt_name: str
    detection_type: str
    metrics: PromptMetrics
    usage_history: List[PromptUsage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

    def add_usage(self, usage: PromptUsage) -> "PromptPerformanceProfile":
        """Add new usage and recalculate metrics (returns new instance)."""
        if usage.prompt_name != self.prompt_name:
            raise ValueError("Usage prompt name doesn't match profile")
        if usage.detection_type != self.detection_type:
            raise ValueError("Usage detection type doesn't match profile")

        # Create new usage history (keep last 100 entries for performance)
        new_history = (self.usage_history + [usage])[-100:]

        # Recalculate metrics
        new_metrics = self._calculate_metrics(new_history)

        return PromptPerformanceProfile(
            prompt_name=self.prompt_name,
            detection_type=self.detection_type,
            metrics=new_metrics,
            usage_history=new_history,
            created_at=self.created_at,
            last_updated=datetime.now(),
        )

    def _calculate_metrics(self, usage_history: List[PromptUsage]) -> PromptMetrics:
        """Calculate metrics from usage history."""
        if not usage_history:
            return PromptMetrics(success_rate=0.0, average_score=0.0, usage_count=0)

        # Basic metrics
        total_uses = len(usage_history)
        successes = sum(1 for usage in usage_history if usage.success)
        success_rate = successes / total_uses
        average_score = sum(usage.score for usage in usage_history) / total_uses

        # Recent scores for trend analysis
        recent_scores = [usage.score for usage in usage_history[-10:]]

        # Calculate trend direction
        trend = self._calculate_trend(usage_history)

        # Calculate confidence interval (Wilson score)
        confidence_interval = self._calculate_confidence_interval(successes, total_uses)

        return PromptMetrics(
            success_rate=success_rate,
            average_score=average_score,
            usage_count=total_uses,
            confidence_interval=confidence_interval,
            trend_direction=trend,
            last_10_scores=recent_scores,
        )

    def _calculate_trend(self, usage_history: List[PromptUsage]) -> TrendDirection:
        """Calculate performance trend from recent usage."""
        if len(usage_history) < 6:
            return TrendDirection.UNKNOWN

        # Split into first and second half for comparison
        mid_point = len(usage_history) // 2
        first_half_scores = [u.score for u in usage_history[:mid_point]]
        second_half_scores = [u.score for u in usage_history[mid_point:]]

        first_avg = sum(first_half_scores) / len(first_half_scores)
        second_avg = sum(second_half_scores) / len(second_half_scores)

        # For AI detection, lower scores are better
        score_diff = first_avg - second_avg

        if abs(score_diff) < 5:  # Within 5 points is stable
            return TrendDirection.STABLE
        elif score_diff > 0:  # Scores decreased (improved)
            return TrendDirection.IMPROVING
        else:  # Scores increased (declined)
            return TrendDirection.DECLINING

    def _calculate_confidence_interval(
        self, successes: int, total: int, confidence_level: float = 0.95
    ) -> Tuple[float, float]:
        """Calculate Wilson score confidence interval."""
        if total == 0:
            return (0.0, 0.0)

        # For small samples, use wider intervals
        if total < 10:
            return (0.0, 1.0)

        from scipy import stats
        import math

        z = stats.norm.ppf(1 - (1 - confidence_level) / 2)
        p = successes / total

        # Wilson score interval (more accurate than normal approximation)
        denominator = 1 + z**2 / total
        centre = (p + z**2 / (2 * total)) / denominator
        margin = (
            z * math.sqrt(p * (1 - p) / total + z**2 / (4 * total**2)) / denominator
        )

        return (max(0, centre - margin), min(1, centre + margin))


@dataclass(frozen=True)
class SelectionContext:
    """Context for prompt selection decisions."""

    detection_type: str
    iteration: int
    section_name: str
    content_type: str
    material_type: Optional[str] = None
    content_length: Optional[int] = None
    previous_scores: List[int] = field(default_factory=list)

    def to_hash(self) -> str:
        """Generate hash for caching selection decisions."""
        import hashlib

        content = f"{self.detection_type}:{self.iteration}:{self.section_name}:{self.content_type}:{self.material_type}"
        return hashlib.md5(content.encode()).hexdigest()


@dataclass(frozen=True)
class SelectionResult:
    """Result of prompt selection with reasoning."""

    selected_prompt: str
    selection_strategy: str
    confidence: float
    reasoning: str
    alternatives_considered: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        return f"Selected '{self.selected_prompt}' (strategy: {self.selection_strategy}, confidence: {self.confidence:.2f})"


@dataclass(frozen=True)
class OptimizationInsight:
    """Insight from prompt performance analysis."""

    insight_type: str  # "pattern", "recommendation", "warning"
    title: str
    description: str
    confidence: float
    actionable: bool
    supporting_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationReport:
    """Comprehensive optimization report."""

    detection_type: str
    generated_at: datetime
    total_prompts_analyzed: int
    total_usage_records: int
    top_performers: List[PromptPerformanceProfile]
    insights: List[OptimizationInsight]
    recommendations: List[str]

    def add_insight(self, insight: OptimizationInsight) -> None:
        """Add insight to the report."""
        self.insights.append(insight)

    def add_recommendation(self, recommendation: str) -> None:
        """Add recommendation to the report."""
        self.recommendations.append(recommendation)


# Import numpy for calculations if available, fallback to basic math
try:
    import numpy as np
except ImportError:
    # Fallback implementation for std calculation
    class np:
        @staticmethod
        def std(values):
            if not values:
                return 0
            mean = sum(values) / len(values)
            variance = sum((x - mean) ** 2 for x in values) / len(values)
            return variance**0.5
