"""
Dynamic Evolution Service

This service provides dynamic prompt/content evolution capabilities that can be used
by any component in the system. It handles the evolution of prompts and content
based on performance data, user feedback, and quality metrics.

Features:
- Template-based prompt evolution
- Gradual improvement application
- Evolution history tracking
- Performance analytics
- A/B testing capabilities
- Version control for prompts
"""

import asyncio
import json
import logging
import hashlib
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from copy import deepcopy

from .. import BaseService, ServiceConfiguration, ServiceError

logger = logging.getLogger(__name__)


class EvolutionStrategy(Enum):
    """Strategies for evolving prompts/content."""
    GRADUAL = "gradual"
    RADICAL = "radical"
    CONSERVATIVE = "conservative"
    ADAPTIVE = "adaptive"


class EvolutionTrigger(Enum):
    """Triggers for initiating evolution."""
    PERFORMANCE_DROP = "performance_drop"
    QUALITY_THRESHOLD = "quality_threshold"
    TIME_BASED = "time_based"
    MANUAL = "manual"
    FEEDBACK_BASED = "feedback_based"


@dataclass
class EvolutionTemplate:
    """Template for prompt/content evolution."""
    template_id: str
    base_prompt: str
    evolution_rules: Dict[str, Any]
    variables: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"


@dataclass
class EvolutionResult:
    """Result of an evolution operation."""
    original_content: str
    evolved_content: str
    evolution_strategy: EvolutionStrategy
    quality_improvement: float
    performance_metrics: Dict[str, float]
    metadata: Dict[str, Any]
    timestamp: datetime


@dataclass
class EvolutionHistory:
    """History of evolution operations."""
    template_id: str
    evolution_results: List[EvolutionResult] = field(default_factory=list)
    performance_trends: Dict[str, List[float]] = field(default_factory=dict)
    last_evolution: Optional[datetime] = None
    total_evolutions: int = 0


@dataclass
class ABTestVariant:
    """A/B test variant for evolution testing."""
    variant_id: str
    content: str
    performance_score: float = 0.0
    sample_size: int = 0
    confidence_interval: Tuple[float, float] = (0.0, 0.0)
    is_winner: bool = False


@dataclass
class ABTest:
    """A/B test configuration and results."""
    test_id: str
    variants: List[ABTestVariant]
    control_variant: str
    test_duration_days: int
    start_date: datetime
    end_date: Optional[datetime] = None
    winner_variant: Optional[str] = None
    status: str = "running"


class DynamicEvolutionError(ServiceError):
    """Raised when dynamic evolution fails."""
    pass


class DynamicEvolutionService(BaseService):
    """
    Service for dynamic prompt/content evolution.

    This service provides:
    - Template-based evolution of prompts and content
    - Gradual improvement application with rollback capabilities
    - Evolution history tracking and analytics
    - A/B testing for evolution validation
    - Performance-driven evolution triggers
    """

    def __init__(self, config: ServiceConfiguration):
        # Initialize attributes before calling super().__init__
        self.templates: Dict[str, EvolutionTemplate] = {}
        self.evolution_history: Dict[str, EvolutionHistory] = {}
        self.active_ab_tests: Dict[str, ABTest] = {}
        self.performance_cache: Dict[str, Dict[str, Any]] = {}

        super().__init__(config)

    def _validate_config(self) -> None:
        """Validate service configuration."""
        # No specific validation required for base implementation
        pass

    def _initialize(self) -> None:
        """Initialize the service."""
        self.logger.info("Dynamic Evolution Service initialized")

    def register_template(
        self,
        template_id: str,
        base_prompt: str,
        evolution_rules: Dict[str, Any],
        variables: Optional[Dict[str, Any]] = None,
        constraints: Optional[Dict[str, Any]] = None
    ) -> EvolutionTemplate:
        """
        Register an evolution template.

        Args:
            template_id: Unique identifier for the template
            base_prompt: Base prompt template
            evolution_rules: Rules for evolution
            variables: Template variables
            constraints: Evolution constraints

        Returns:
            EvolutionTemplate: The registered template
        """
        if template_id in self.templates:
            self.logger.warning(f"Template {template_id} already exists, updating")

        template = EvolutionTemplate(
            template_id=template_id,
            base_prompt=base_prompt,
            evolution_rules=evolution_rules,
            variables=variables or {},
            constraints=constraints or {}
        )

        self.templates[template_id] = template
        self.evolution_history[template_id] = EvolutionHistory(template_id=template_id)

        self.logger.info(f"Registered evolution template: {template_id}")
        return template

    async def evolve_content(
        self,
        template_id: str,
        current_content: str,
        performance_data: Dict[str, Any],
        evolution_strategy: EvolutionStrategy = EvolutionStrategy.GRADUAL,
        **kwargs
    ) -> EvolutionResult:
        """
        Evolve content based on performance data.

        Args:
            template_id: Template to use for evolution
            current_content: Current content to evolve
            performance_data: Performance metrics and data
            evolution_strategy: Strategy for evolution
            **kwargs: Additional evolution parameters

        Returns:
            EvolutionResult: Evolution result

        Raises:
            DynamicEvolutionError: If evolution fails
        """
        if template_id not in self.templates:
            raise DynamicEvolutionError(f"Template not found: {template_id}")

        template = self.templates[template_id]
        start_time = datetime.now()

        try:
            # Apply evolution strategy
            evolved_content = await self._apply_evolution_strategy(
                template, current_content, performance_data, evolution_strategy, **kwargs
            )

            # Calculate quality improvement
            quality_improvement = self._calculate_quality_improvement(
                current_content, evolved_content, performance_data
            )

            # Create evolution result
            result = EvolutionResult(
                original_content=current_content,
                evolved_content=evolved_content,
                evolution_strategy=evolution_strategy,
                quality_improvement=quality_improvement,
                performance_metrics=performance_data,
                metadata={
                    "template_id": template_id,
                    "strategy": evolution_strategy.value,
                    "processing_time": (datetime.now() - start_time).total_seconds()
                },
                timestamp=datetime.now()
            )

            # Update evolution history
            history = self.evolution_history[template_id]
            history.evolution_results.append(result)
            history.last_evolution = result.timestamp
            history.total_evolutions += 1

            # Update performance trends
            self._update_performance_trends(history, result)

            self.logger.info(f"Evolved content for template {template_id}: "
                           f"improvement={quality_improvement:.3f}")

            return result

        except Exception as e:
            self.logger.error(f"Evolution failed for template {template_id}: {e}")
            raise DynamicEvolutionError(f"Evolution failed: {e}") from e

    async def _apply_evolution_strategy(
        self,
        template: EvolutionTemplate,
        content: str,
        performance_data: Dict[str, Any],
        strategy: EvolutionStrategy,
        **kwargs
    ) -> str:
        """Apply the specified evolution strategy."""
        if strategy == EvolutionStrategy.GRADUAL:
            return await self._apply_gradual_evolution(template, content, performance_data, **kwargs)
        elif strategy == EvolutionStrategy.RADICAL:
            return await self._apply_radical_evolution(template, content, performance_data, **kwargs)
        elif strategy == EvolutionStrategy.CONSERVATIVE:
            return await self._apply_conservative_evolution(template, content, performance_data, **kwargs)
        elif strategy == EvolutionStrategy.ADAPTIVE:
            return await self._apply_adaptive_evolution(template, content, performance_data, **kwargs)
        else:
            raise DynamicEvolutionError(f"Unknown evolution strategy: {strategy}")

    async def _apply_gradual_evolution(
        self,
        template: EvolutionTemplate,
        content: str,
        performance_data: Dict[str, Any],
        **kwargs
    ) -> str:
        """Apply gradual evolution strategy."""
        # Simple gradual improvement based on performance
        quality_score = performance_data.get("quality_score", 0.5)

        if quality_score < 0.7:
            # Add more specific instructions
            evolved = content + " Please ensure the response is detailed and comprehensive."
        elif quality_score < 0.9:
            # Add quality emphasis
            evolved = content + " Focus on providing high-quality, accurate information."
        else:
            # Minor refinement
            evolved = content + " Maintain the current high quality standards."

        return evolved

    async def _apply_radical_evolution(
        self,
        template: EvolutionTemplate,
        content: str,
        performance_data: Dict[str, Any],
        **kwargs
    ) -> str:
        """Apply radical evolution strategy."""
        # More aggressive changes
        base_prompt = template.base_prompt

        # Replace sections based on performance issues
        if performance_data.get("quality_score", 0.5) < 0.6:
            evolved = base_prompt.replace(
                "Create content",
                "Create comprehensive, high-quality content with detailed analysis"
            )
        else:
            evolved = base_prompt

        return evolved

    async def _apply_conservative_evolution(
        self,
        template: EvolutionTemplate,
        content: str,
        performance_data: Dict[str, Any],
        **kwargs
    ) -> str:
        """Apply conservative evolution strategy."""
        # Minimal changes to preserve working content
        quality_score = performance_data.get("quality_score", 0.5)

        if quality_score < 0.8:
            evolved = content + " (refined)"
        else:
            evolved = content

        return evolved

    async def _apply_adaptive_evolution(
        self,
        template: EvolutionTemplate,
        content: str,
        performance_data: Dict[str, Any],
        **kwargs
    ) -> str:
        """Apply adaptive evolution strategy based on history."""
        template_id = template.template_id
        history = self.evolution_history.get(template_id)

        if not history or not history.evolution_results:
            # No history, use gradual approach
            return await self._apply_gradual_evolution(template, content, performance_data, **kwargs)

        # Analyze recent performance trends
        recent_results = history.evolution_results[-5:]  # Last 5 evolutions
        avg_improvement = sum(r.quality_improvement for r in recent_results) / len(recent_results)

        if avg_improvement > 0.1:
            # Good improvement trend, continue gradual
            return await self._apply_gradual_evolution(template, content, performance_data, **kwargs)
        elif avg_improvement < 0:
            # Declining performance, be more conservative
            return await self._apply_conservative_evolution(template, content, performance_data, **kwargs)
        else:
            # Stagnant, try radical approach
            return await self._apply_radical_evolution(template, content, performance_data, **kwargs)

    def _calculate_quality_improvement(
        self,
        original: str,
        evolved: str,
        performance_data: Dict[str, Any]
    ) -> float:
        """Calculate the quality improvement from evolution."""
        # Simple heuristic based on content length and performance
        original_length = len(original)
        evolved_length = len(evolved)
        length_ratio = evolved_length / original_length if original_length > 0 else 1.0

        # Quality score from performance data
        quality_score = performance_data.get("quality_score", 0.5)

        # Improvement calculation (simplified)
        improvement = (length_ratio - 1.0) * 0.1 + (quality_score - 0.5) * 0.2
        return max(-1.0, min(1.0, improvement))  # Clamp between -1 and 1

    def _update_performance_trends(
        self,
        history: EvolutionHistory,
        result: EvolutionResult
    ) -> None:
        """Update performance trends in history."""
        # Track quality improvements over time
        if "quality_improvements" not in history.performance_trends:
            history.performance_trends["quality_improvements"] = []

        history.performance_trends["quality_improvements"].append(result.quality_improvement)

        # Keep only last 20 data points
        if len(history.performance_trends["quality_improvements"]) > 20:
            history.performance_trends["quality_improvements"] = history.performance_trends["quality_improvements"][-20:]

    def should_evolve(
        self,
        template_id: str,
        trigger: EvolutionTrigger,
        performance_data: Dict[str, Any],
        **kwargs
    ) -> Tuple[bool, str]:
        """
        Determine if evolution should be triggered.

        Args:
            template_id: Template identifier
            trigger: Evolution trigger type
            performance_data: Current performance data
            **kwargs: Additional trigger parameters

        Returns:
            Tuple[bool, str]: (should_evolve, reason)
        """
        if template_id not in self.templates:
            return False, f"Template {template_id} not found"

        if trigger == EvolutionTrigger.PERFORMANCE_DROP:
            threshold = kwargs.get("performance_threshold", 0.7)
            current_performance = performance_data.get("quality_score", 1.0)
            if current_performance < threshold:
                return True, f"Performance dropped below threshold: {current_performance} < {threshold}"

        elif trigger == EvolutionTrigger.QUALITY_THRESHOLD:
            threshold = kwargs.get("quality_threshold", 0.8)
            current_quality = performance_data.get("quality_score", 0.0)
            if current_quality < threshold:
                return True, f"Quality below threshold: {current_quality} < {threshold}"

        elif trigger == EvolutionTrigger.TIME_BASED:
            hours_since_last = kwargs.get("hours_threshold", 24)
            history = self.evolution_history.get(template_id)
            if history and history.last_evolution:
                hours_elapsed = (datetime.now() - history.last_evolution).total_seconds() / 3600
                if hours_elapsed >= hours_since_last:
                    return True, f"Time threshold exceeded: {hours_elapsed:.1f} hours"

        elif trigger == EvolutionTrigger.MANUAL:
            return True, "Manual trigger"

        return False, "No evolution trigger conditions met"

    def create_ab_test(
        self,
        test_id: str,
        template_id: str,
        variants: List[str],
        control_variant: str,
        duration_days: int = 7
    ) -> ABTest:
        """
        Create an A/B test for evolution validation.

        Args:
            test_id: Unique test identifier
            template_id: Template being tested
            variants: List of variant content
            control_variant: Control variant content
            duration_days: Test duration in days

        Returns:
            ABTest: Created A/B test
        """
        if test_id in self.active_ab_tests:
            raise DynamicEvolutionError(f"A/B test {test_id} already exists")

        # Create test variants
        test_variants = []
        for i, content in enumerate(variants):
            variant = ABTestVariant(
                variant_id=f"{test_id}_variant_{i}",
                content=content
            )
            test_variants.append(variant)

        # Add control variant
        control = ABTestVariant(
            variant_id=f"{test_id}_control",
            content=control_variant
        )
        test_variants.insert(0, control)

        ab_test = ABTest(
            test_id=test_id,
            variants=test_variants,
            control_variant=control_variant,
            test_duration_days=duration_days,
            start_date=datetime.now()
        )

        self.active_ab_tests[test_id] = ab_test
        self.logger.info(f"Created A/B test: {test_id} with {len(test_variants)} variants")

        return ab_test

    def update_ab_test_performance(
        self,
        test_id: str,
        variant_id: str,
        performance_score: float
    ) -> None:
        """
        Update performance data for an A/B test variant.

        Args:
            test_id: Test identifier
            variant_id: Variant identifier
            performance_score: Performance score for the variant
        """
        if test_id not in self.active_ab_tests:
            raise DynamicEvolutionError(f"A/B test {test_id} not found")

        ab_test = self.active_ab_tests[test_id]
        variant = next((v for v in ab_test.variants if v.variant_id == variant_id), None)

        if not variant:
            raise DynamicEvolutionError(f"Variant {variant_id} not found in test {test_id}")

        # Update variant performance (simple moving average)
        variant.sample_size += 1
        variant.performance_score = (
            (variant.performance_score * (variant.sample_size - 1)) + performance_score
        ) / variant.sample_size

    def get_ab_test_results(self, test_id: str) -> Optional[Dict[str, Any]]:
        """
        Get results of an A/B test.

        Args:
            test_id: Test identifier

        Returns:
            Optional[Dict[str, Any]]: Test results
        """
        if test_id not in self.active_ab_tests:
            return None

        ab_test = self.active_ab_tests[test_id]

        # Find best performing variant
        best_variant = max(ab_test.variants, key=lambda v: v.performance_score)

        return {
            "test_id": test_id,
            "status": ab_test.status,
            "best_variant": best_variant.variant_id,
            "best_score": best_variant.performance_score,
            "variants": [
                {
                    "id": v.variant_id,
                    "score": v.performance_score,
                    "sample_size": v.sample_size
                }
                for v in ab_test.variants
            ],
            "days_running": (datetime.now() - ab_test.start_date).days
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
            return {"error": f"No evolution history for template {template_id}"}

        history = self.evolution_history[template_id]

        if not history.evolution_results:
            return {"total_evolutions": 0, "avg_improvement": 0.0}

        improvements = [r.quality_improvement for r in history.evolution_results]
        avg_improvement = sum(improvements) / len(improvements)

        return {
            "total_evolutions": history.total_evolutions,
            "avg_improvement": avg_improvement,
            "last_evolution": history.last_evolution.isoformat() if history.last_evolution else None,
            "improvement_trend": improvements[-10:],  # Last 10 improvements
            "performance_trends": history.performance_trends
        }

    def rollback_evolution(self, template_id: str, steps: int = 1) -> bool:
        """
        Rollback evolution by specified number of steps.

        Args:
            template_id: Template identifier
            steps: Number of steps to rollback

        Returns:
            bool: True if rollback successful
        """
        if template_id not in self.evolution_history:
            return False

        history = self.evolution_history[template_id]

        if len(history.evolution_results) < steps:
            return False

        # Remove last N evolution results
        history.evolution_results = history.evolution_results[:-steps]
        history.total_evolutions -= steps

        # Update last evolution timestamp
        if history.evolution_results:
            history.last_evolution = history.evolution_results[-1].timestamp
        else:
            history.last_evolution = None

        self.logger.info(f"Rolled back evolution for template {template_id} by {steps} steps")
        return True

    def health_check(self) -> bool:
        """Perform health check."""
        try:
            # Basic health check - service is healthy if it can manage templates
            return True
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
