"""
Dynamic Evolution Service for Z-Beam Generator.

This module provides dynamic content evolution capabilities for content generation,
including A/B testing, template evolution, and performance-based optimization.
"""

import asyncio
import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from services import BaseService, ServiceConfiguration, ServiceError

logger = logging.getLogger(__name__)


class DynamicEvolutionError(ServiceError):
    """Raised when dynamic evolution operations fail."""

    pass


class EvolutionStrategy(Enum):
    """Strategies for content evolution."""

    GRADUAL = "gradual"
    RADICAL = "radical"
    CONSERVATIVE = "conservative"
    ADAPTIVE = "adaptive"


class EvolutionTrigger(Enum):
    """Triggers for evolution."""

    PERFORMANCE_DROP = "performance_drop"
    QUALITY_THRESHOLD = "quality_threshold"
    TIME_BASED = "time_based"
    MANUAL = "manual"


@dataclass
class EvolutionTemplate:
    """Template for content evolution."""

    template_id: str
    base_prompt: str
    evolution_rules: Dict[str, Any] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now()


@dataclass
class EvolutionResult:
    """Result of a content evolution."""

    original_content: str
    evolved_content: str
    evolution_strategy: EvolutionStrategy
    quality_improvement: float
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EvolutionHistory:
    """History of evolutions for a template."""

    template_id: str
    evolution_results: List[EvolutionResult] = field(default_factory=list)
    performance_trends: Dict[str, List[float]] = field(default_factory=dict)
    last_evolution: Optional[datetime] = None
    total_evolutions: int = 0

    def add_result(self, result: EvolutionResult) -> None:
        """Add an evolution result to history."""
        self.evolution_results.append(result)
        self.total_evolutions += 1
        self.last_evolution = result.timestamp

        # Keep only last 20 results
        if len(self.evolution_results) > 20:
            self.evolution_results = self.evolution_results[-20:]


@dataclass
class ABTestVariant:
    """Variant in an A/B test."""

    variant_id: str
    content: str
    performance_score: float = 0.0
    sample_size: int = 0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ABTest:
    """A/B test configuration and results."""

    test_id: str
    template_id: str
    variants: List[ABTestVariant] = field(default_factory=list)
    control_variant: str = ""
    test_duration_days: int = 7
    status: str = "running"
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None

    @property
    def is_active(self) -> bool:
        """Check if test is still active."""
        if self.status != "running":
            return False
        if self.end_date:
            return datetime.now() < self.end_date
        return True


class DynamicEvolutionService(BaseService):
    """
    Service for dynamic content evolution with A/B testing and performance optimization.

    Provides:
    - Template-based content evolution
    - Multiple evolution strategies
    - A/B testing framework
    - Performance tracking and analytics
    - Evolution history and rollback
    """

    def __init__(self, config: ServiceConfiguration):
        super().__init__(config)
        self.templates: Dict[str, EvolutionTemplate] = {}
        self.evolution_history: Dict[str, EvolutionHistory] = {}
        self.active_ab_tests: Dict[str, ABTest] = {}
        self.performance_cache: Dict[str, Dict[str, Any]] = {}

    def _validate_config(self) -> None:
        """Validate service configuration."""
        required_settings = ["max_templates", "evolution_history_size"]
        for setting in required_settings:
            if setting not in self.config.settings:
                if setting == "max_templates":
                    self.config.settings[setting] = 10
                elif setting == "evolution_history_size":
                    self.config.settings[setting] = 50

    def _initialize(self) -> None:
        """Initialize the service."""
        logger.info("Initializing DynamicEvolutionService")

    def health_check(self) -> bool:
        """Perform health check."""
        return True

    def register_template(
        self,
        template_id: str,
        base_prompt: str,
        evolution_rules: Optional[Dict[str, Any]] = None,
        variables: Optional[Dict[str, Any]] = None,
        constraints: Optional[Dict[str, Any]] = None,
    ) -> EvolutionTemplate:
        """
        Register or update an evolution template.

        Args:
            template_id: Unique identifier for the template
            base_prompt: Base prompt for content generation
            evolution_rules: Rules for evolution
            variables: Template variables
            constraints: Content constraints

        Returns:
            EvolutionTemplate: The registered template
        """
        if evolution_rules is None:
            evolution_rules = {}
        if variables is None:
            variables = {}
        if constraints is None:
            constraints = {}

        template = EvolutionTemplate(
            template_id=template_id,
            base_prompt=base_prompt,
            evolution_rules=evolution_rules,
            variables=variables,
            constraints=constraints,
        )

        self.templates[template_id] = template

        # Initialize evolution history if not exists
        if template_id not in self.evolution_history:
            self.evolution_history[template_id] = EvolutionHistory(
                template_id=template_id
            )

        logger.info(f"Registered template: {template_id}")
        return template

    async def evolve_content(
        self,
        template_id: str,
        current_content: str,
        performance_data: Dict[str, Any],
        evolution_strategy: Optional[EvolutionStrategy] = None,
    ) -> Optional[EvolutionResult]:
        """
        Evolve content based on performance data.

        Args:
            template_id: Template to use for evolution
            current_content: Current content to evolve
            performance_data: Performance metrics
            evolution_strategy: Evolution strategy to use

        Returns:
            Optional[EvolutionResult]: Evolution result or None if template not found
        """
        if template_id not in self.templates:
            raise DynamicEvolutionError(f"Template not found: {template_id}")

        template = self.templates[template_id]
        history = self.evolution_history[template_id]

        # Determine strategy
        if evolution_strategy is None:
            evolution_strategy = self._select_adaptive_strategy(history)

        # Apply evolution
        evolved_content = await self._apply_evolution_strategy(
            template, current_content, performance_data, evolution_strategy
        )

        # Calculate quality improvement
        original_quality = performance_data.get("quality_score", 0.5)
        # Simulate quality assessment (in real implementation, this would use actual quality metrics)
        evolved_quality = min(1.0, original_quality + 0.1)
        quality_improvement = evolved_quality - original_quality

        # Create evolution result
        result = EvolutionResult(
            original_content=current_content,
            evolved_content=evolved_content,
            evolution_strategy=evolution_strategy,
            quality_improvement=quality_improvement,
            performance_metrics=performance_data.copy(),
            metadata={"template_id": template_id},
        )

        # Update history
        history.add_result(result)
        self._update_performance_trends(history, result)

        logger.info(
            f"Evolved content for template {template_id} using {evolution_strategy.value} strategy"
        )
        return result

    def _select_adaptive_strategy(self, history: EvolutionHistory) -> EvolutionStrategy:
        """Select evolution strategy based on history."""
        if len(history.evolution_results) < 2:
            return EvolutionStrategy.GRADUAL

        # Analyze recent performance
        recent_results = history.evolution_results[-3:]
        avg_improvement = sum(r.quality_improvement for r in recent_results) / len(
            recent_results
        )

        if avg_improvement > 0.1:
            return EvolutionStrategy.RADICAL
        elif avg_improvement > 0.05:
            return EvolutionStrategy.GRADUAL
        else:
            return EvolutionStrategy.CONSERVATIVE

    async def _apply_evolution_strategy(
        self,
        template: EvolutionTemplate,
        content: str,
        performance_data: Dict[str, Any],
        strategy: EvolutionStrategy,
    ) -> str:
        """Apply the specified evolution strategy."""
        if strategy == EvolutionStrategy.GRADUAL:
            # Small, incremental changes
            return f"{content} [gradually improved]"
        elif strategy == EvolutionStrategy.RADICAL:
            # Significant changes
            return f"{content} [radically evolved]"
        elif strategy == EvolutionStrategy.CONSERVATIVE:
            # Minimal changes
            return f"{content} [conservatively refined]"
        elif strategy == EvolutionStrategy.ADAPTIVE:
            # Adaptive based on performance
            return f"{content} [adaptively optimized]"
        else:
            return content

    def should_evolve(
        self,
        template_id: str,
        trigger: EvolutionTrigger,
        performance_data: Dict[str, Any],
        **kwargs,
    ) -> tuple[bool, str]:
        """
        Check if content should be evolved based on trigger conditions.

        Args:
            template_id: Template identifier
            trigger: Evolution trigger type
            performance_data: Current performance data
            **kwargs: Additional parameters for trigger

        Returns:
            tuple[bool, str]: (should_evolve, reason)
        """
        if template_id not in self.templates:
            return False, f"Template '{template_id}' not found"

        template = self.templates[template_id]
        history = self.evolution_history.get(template_id)

        if trigger == EvolutionTrigger.PERFORMANCE_DROP:
            threshold = kwargs.get("performance_threshold", 0.7)
            current_perf = performance_data.get("quality_score", 0.0)
            if current_perf < threshold:
                return (
                    True,
                    f"Performance dropped below threshold ({current_perf:.2f} < {threshold})",
                )
            return (
                False,
                f"Performance above threshold ({current_perf:.2f} >= {threshold})",
            )

        elif trigger == EvolutionTrigger.QUALITY_THRESHOLD:
            threshold = kwargs.get("quality_threshold", 0.8)
            current_quality = performance_data.get("quality_score", 0.0)
            if current_quality < threshold:
                return (
                    True,
                    f"Quality below threshold ({current_quality:.2f} < {threshold})",
                )
            return (
                False,
                f"Quality above threshold ({current_quality:.2f} >= {threshold})",
            )

        elif trigger == EvolutionTrigger.TIME_BASED:
            if not history or not history.last_evolution:
                return True, "No previous evolution found"

            threshold_hours = kwargs.get("hours_threshold", 24)
            time_since_last = datetime.now() - history.last_evolution
            if time_since_last.total_seconds() > (threshold_hours * 3600):
                return (
                    True,
                    f"Time threshold exceeded ({time_since_last.total_seconds()/3600:.1f} hours > {threshold_hours})",
                )
            return (
                False,
                f"Time threshold not exceeded ({time_since_last.total_seconds()/3600:.1f} hours <= {threshold_hours})",
            )

        elif trigger == EvolutionTrigger.MANUAL:
            return True, "Manual trigger"

        return False, "No evolution trigger conditions met"

    def create_ab_test(
        self,
        test_id: str,
        template_id: str,
        variants: List[str],
        control_variant: str,
        duration_days: int = 7,
    ) -> ABTest:
        """
        Create an A/B test.

        Args:
            test_id: Unique test identifier
            template_id: Template to test
            variants: List of variant content
            control_variant: Control variant content
            duration_days: Test duration in days

        Returns:
            ABTest: Created A/B test
        """
        if test_id in self.active_ab_tests:
            raise DynamicEvolutionError(f"A/B test '{test_id}' already exists")

        if template_id not in self.templates:
            raise DynamicEvolutionError(f"Template '{template_id}' not found")

        # Create control variant
        control = ABTestVariant(
            variant_id=f"{test_id}_control", content=control_variant
        )

        # Create test variants
        test_variants = []
        for i, content in enumerate(variants):
            variant = ABTestVariant(
                variant_id=f"{test_id}_variant_{i}", content=content
            )
            test_variants.append(variant)

        ab_test = ABTest(
            test_id=test_id,
            template_id=template_id,
            variants=[control] + test_variants,
            control_variant=control_variant,
            test_duration_days=duration_days,
            end_date=datetime.now() + timedelta(days=duration_days),
        )

        self.active_ab_tests[test_id] = ab_test
        logger.info(f"Created A/B test: {test_id} with {len(test_variants)} variants")
        return ab_test

    def update_ab_test_performance(
        self, test_id: str, variant_id: str, performance_score: float
    ) -> None:
        """
        Update performance for an A/B test variant.

        Args:
            test_id: Test identifier
            variant_id: Variant identifier
            performance_score: New performance score
        """
        if test_id not in self.active_ab_tests:
            raise DynamicEvolutionError(f"A/B test '{test_id}' not found")

        ab_test = self.active_ab_tests[test_id]
        variant = next(
            (v for v in ab_test.variants if v.variant_id == variant_id), None
        )

        if not variant:
            raise DynamicEvolutionError(
                f"Variant '{variant_id}' not found in test '{test_id}'"
            )

        # Update performance (simple average)
        total_score = variant.performance_score * variant.sample_size
        variant.sample_size += 1
        variant.performance_score = (
            total_score + performance_score
        ) / variant.sample_size

    def get_ab_test_results(self, test_id: str) -> Optional[Dict[str, Any]]:
        """
        Get results for an A/B test.

        Args:
            test_id: Test identifier

        Returns:
            Optional[Dict[str, Any]]: Test results or None if not found
        """
        if test_id not in self.active_ab_tests:
            return None

        ab_test = self.active_ab_tests[test_id]

        # Find best performing variant
        if not ab_test.variants:
            return {"error": "No variants found"}

        best_variant = max(ab_test.variants, key=lambda v: v.performance_score)
        control_variant = next(
            (v for v in ab_test.variants if v.variant_id.endswith("_control")), None
        )

        return {
            "test_id": test_id,
            "status": ab_test.status,
            "best_variant": best_variant.variant_id,
            "best_score": best_variant.performance_score,
            "control_score": control_variant.performance_score
            if control_variant
            else 0.0,
            "variants": [
                {
                    "id": v.variant_id,
                    "score": v.performance_score,
                    "sample_size": v.sample_size,
                }
                for v in ab_test.variants
            ],
        }

    def get_evolution_analytics(self, template_id: str) -> Dict[str, Any]:
        """
        Get evolution analytics for a template.

        Args:
            template_id: Template identifier

        Returns:
            Dict[str, Any]: Evolution analytics
        """
        if template_id not in self.evolution_history:
            return {"error": f"Template '{template_id}' not found"}

        history = self.evolution_history[template_id]

        if not history.evolution_results:
            return {
                "total_evolutions": 0,
                "avg_improvement": 0.0,
                "best_improvement": 0.0,
                "worst_improvement": 0.0,
            }

        improvements = [r.quality_improvement for r in history.evolution_results]

        return {
            "total_evolutions": history.total_evolutions,
            "avg_improvement": sum(improvements) / len(improvements),
            "best_improvement": max(improvements),
            "worst_improvement": min(improvements),
            "improvement_trend": improvements[-10:],  # Last 10 improvements
            "recent_optimizations": len(
                [r for r in history.evolution_results[-5:] if r.quality_improvement > 0]
            ),  # Recent positive improvements
        }

    def rollback_evolution(self, template_id: str, steps: int = 1) -> bool:
        """
        Rollback evolution history.

        Args:
            template_id: Template identifier
            steps: Number of steps to rollback

        Returns:
            bool: True if rollback successful
        """
        if template_id not in self.evolution_history:
            return False

        history = self.evolution_history[template_id]

        if len(history.evolution_results) <= steps:
            return False

        # Remove last N results
        history.evolution_results = history.evolution_results[:-steps]
        history.total_evolutions -= steps

        # Update last evolution timestamp
        if history.evolution_results:
            history.last_evolution = history.evolution_results[-1].timestamp
        else:
            history.last_evolution = None

        logger.info(f"Rolled back {steps} evolution steps for template {template_id}")
        return True

    def _update_performance_trends(
        self, history: EvolutionHistory, result: EvolutionResult
    ) -> None:
        """Update performance trends in history."""
        if "quality_improvements" not in history.performance_trends:
            history.performance_trends["quality_improvements"] = []

        history.performance_trends["quality_improvements"].append(
            result.quality_improvement
        )

        # Keep only last 20 trend points
        if len(history.performance_trends["quality_improvements"]) > 20:
            history.performance_trends[
                "quality_improvements"
            ] = history.performance_trends["quality_improvements"][-20:]
