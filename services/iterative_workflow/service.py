"""
Iterative Workflow Service for Z-Beam Generator.

This module provides iterative workflow capabilities for content generation,
including various iteration strategies, exit conditions, and workflow management.
"""

import asyncio
import time
import logging
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from services import BaseService, ServiceConfiguration, ServiceError


logger = logging.getLogger(__name__)


class IterativeWorkflowError(ServiceError):
    """Raised when iterative workflow operations fail."""
    pass


class IterationStrategy(Enum):
    """Strategies for controlling iteration timing and behavior."""
    LINEAR = "linear"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    ADAPTIVE = "adaptive"


class ExitCondition(Enum):
    """Conditions that can cause workflow termination."""
    QUALITY_THRESHOLD = "quality_threshold"
    MAX_ITERATIONS = "max_iterations"
    TIME_LIMIT = "time_limit"
    CONVERGENCE = "convergence"
    MANUAL = "manual"


@dataclass
class IterationContext:
    """Context information passed to iteration functions."""
    iteration_number: int
    previous_result: Any
    workflow_id: str
    start_time: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def elapsed_time(self) -> float:
        """Time elapsed since workflow start in seconds."""
        return (datetime.now() - self.start_time).total_seconds()


@dataclass
class WorkflowConfiguration:
    """Configuration for iterative workflows."""
    max_iterations: int = 10
    quality_threshold: float = 0.9
    time_limit_seconds: Optional[float] = None
    iteration_strategy: IterationStrategy = IterationStrategy.LINEAR
    exit_conditions: List[ExitCondition] = field(default_factory=lambda: [
        ExitCondition.QUALITY_THRESHOLD,
        ExitCondition.MAX_ITERATIONS
    ])
    convergence_threshold: float = 0.01
    backoff_factor: float = 2.0
    min_delay: float = 0.1
    max_delay: float = 10.0


@dataclass
class IterationResult:
    """Result of a single iteration."""
    iteration_number: int
    input_content: Any
    output_content: Any
    quality_score: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowResult:
    """Result of an iterative workflow."""
    workflow_id: str
    success: bool
    iterations: List[IterationResult] = field(default_factory=list)
    final_result: Any = None
    exit_reason: str = ""
    total_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class IterativeWorkflowService(BaseService):
    """
    Service for managing iterative workflows with various strategies and exit conditions.

    Provides:
    - Multiple iteration strategies (linear, exponential backoff, adaptive)
    - Flexible exit conditions (quality, time, iterations, convergence)
    - Workflow tracking and history
    - Cancellation support
    - Performance monitoring
    """

    def __init__(self, config: ServiceConfiguration):
        super().__init__(config)
        self.active_workflows: Dict[str, WorkflowResult] = {}
        self.workflow_history: Dict[str, List[WorkflowResult]] = {}
        self.default_config = WorkflowConfiguration()

    def _validate_config(self) -> None:
        """Validate service configuration."""
        required_settings = ["max_iterations", "quality_threshold", "time_limit_seconds"]
        for setting in required_settings:
            if setting not in self.config.settings:
                self.config.settings[setting] = getattr(self.default_config, setting)

    def _initialize(self) -> None:
        """Initialize the service."""
        logger.info("Initializing IterativeWorkflowService")

    def health_check(self) -> bool:
        """Perform health check."""
        return True

    async def run_iterative_workflow(
        self,
        workflow_id: str,
        initial_input: Any,
        iteration_function: Callable[[Any, IterationContext], Any],
        quality_function: Callable[[Any], float],
        workflow_config: Optional[WorkflowConfiguration] = None
    ) -> WorkflowResult:
        """
        Run an iterative workflow.

        Args:
            workflow_id: Unique identifier for the workflow
            initial_input: Initial input for the workflow
            iteration_function: Async function to perform iteration
            quality_function: Function to assess quality of results
            workflow_config: Workflow configuration

        Returns:
            WorkflowResult: Complete workflow result
        """
        if workflow_config is None:
            workflow_config = self.default_config

        start_time = datetime.now()
        result = WorkflowResult(workflow_id=workflow_id, success=False)
        current_content = initial_input
        context = IterationContext(
            iteration_number=0,
            previous_result=initial_input,
            workflow_id=workflow_id,
            start_time=start_time
        )

        try:
            for iteration_num in range(1, workflow_config.max_iterations + 1):
                # Check time limit
                if (workflow_config.time_limit_seconds and
                    context.elapsed_time >= workflow_config.time_limit_seconds):
                    result.exit_reason = "time_limit_exceeded"
                    break

                # Apply iteration strategy delay
                await self._apply_iteration_delay(iteration_num, workflow_config)

                # Update context
                context.iteration_number = iteration_num
                context.previous_result = current_content

                # Perform iteration
                try:
                    new_content = await iteration_function(current_content, context)
                except Exception as e:
                    logger.error(f"Iteration {iteration_num} failed: {e}")
                    raise IterativeWorkflowError(f"Iteration {iteration_num} failed: {e}") from e

                # Assess quality
                try:
                    quality_score = quality_function(new_content)
                except Exception as e:
                    logger.error(f"Quality assessment failed for iteration {iteration_num}: {e}")
                    quality_score = 0.0

                # Record iteration
                iteration_result = IterationResult(
                    iteration_number=iteration_num,
                    input_content=current_content,
                    output_content=new_content,
                    quality_score=quality_score,
                    timestamp=datetime.now(),
                    metadata=context.metadata.copy()
                )
                result.iterations.append(iteration_result)

                # Check exit conditions
                if self._should_exit(iteration_result, workflow_config, result.iterations):
                    result.success = True
                    result.final_result = new_content
                    break

                current_content = new_content

            # Set final result and exit reason
            if not result.final_result:
                result.final_result = current_content
                if not result.exit_reason:
                    result.exit_reason = "max_iterations_reached"

        except Exception as e:
            logger.error(f"Workflow {workflow_id} failed: {e}")
            result.exit_reason = f"error: {str(e)}"
        finally:
            result.total_time = (datetime.now() - start_time).total_seconds()
            self._record_workflow_result(result)

        return result

    async def _apply_iteration_delay(self, iteration_num: int, config: WorkflowConfiguration) -> None:
        """Apply delay based on iteration strategy."""
        if iteration_num == 1:
            return  # No delay for first iteration

        if config.iteration_strategy == IterationStrategy.LINEAR:
            delay = config.min_delay
        elif config.iteration_strategy == IterationStrategy.EXPONENTIAL_BACKOFF:
            delay = min(config.min_delay * (config.backoff_factor ** (iteration_num - 2)), config.max_delay)
        elif config.iteration_strategy == IterationStrategy.ADAPTIVE:
            # Adaptive strategy - could be based on previous iteration performance
            delay = config.min_delay
        else:
            delay = config.min_delay

        await asyncio.sleep(delay)

    def _should_exit(self, current_iteration: IterationResult, config: WorkflowConfiguration,
                    all_iterations: List[IterationResult]) -> bool:
        """Check if workflow should exit based on conditions."""
        # Quality threshold
        if (ExitCondition.QUALITY_THRESHOLD in config.exit_conditions and
            current_iteration.quality_score >= config.quality_threshold):
            return True

        # Convergence check
        if (ExitCondition.CONVERGENCE in config.exit_conditions and
            len(all_iterations) >= 2):
            prev_score = all_iterations[-2].quality_score
            current_score = current_iteration.quality_score
            improvement = current_score - prev_score
            if abs(improvement) < config.convergence_threshold:
                return True

        return False

    def _record_workflow_result(self, result: WorkflowResult) -> None:
        """Record workflow result in history."""
        if result.workflow_id not in self.workflow_history:
            self.workflow_history[result.workflow_id] = []

        self.workflow_history[result.workflow_id].append(result)
        self.active_workflows[result.workflow_id] = result

        # Keep only recent history (last 10 results per workflow)
        if len(self.workflow_history[result.workflow_id]) > 10:
            self.workflow_history[result.workflow_id] = self.workflow_history[result.workflow_id][-10:]

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a workflow."""
        if workflow_id not in self.active_workflows:
            return None

        result = self.active_workflows[workflow_id]
        return {
            "workflow_id": workflow_id,
            "success": result.success,
            "iterations_completed": len(result.iterations),
            "total_time": result.total_time,
            "exit_reason": result.exit_reason,
            "last_updated": result.iterations[-1].timestamp if result.iterations else None
        }

    def get_workflow_history(self, workflow_id: str) -> List[Dict[str, Any]]:
        """Get history of a workflow."""
        if workflow_id not in self.workflow_history:
            return []

        return [
            {
                "iterations": len(result.iterations),
                "success": result.success,
                "total_time": result.total_time,
                "exit_reason": result.exit_reason,
                "timestamp": result.iterations[-1].timestamp if result.iterations else None
            }
            for result in self.workflow_history[workflow_id]
        ]

    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow."""
        if workflow_id not in self.active_workflows:
            return False

        result = self.active_workflows[workflow_id]
        result.metadata["cancelled"] = True
        result.exit_reason = "cancelled"
        return True

    def cleanup_old_workflows(self, max_age_hours: int = 24) -> int:
        """Clean up old workflow data."""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        cleaned_count = 0

        # Clean active workflows
        to_remove = []
        for workflow_id, result in self.active_workflows.items():
            if result.iterations and result.iterations[-1].timestamp < cutoff_time:
                to_remove.append(workflow_id)

        for workflow_id in to_remove:
            del self.active_workflows[workflow_id]
            cleaned_count += 1

        # Clean history (keep at least one entry per workflow)
        for workflow_id, results in self.workflow_history.items():
            if len(results) > 1:
                old_results = [r for r in results[:-1]
                             if r.iterations and r.iterations[-1].timestamp < cutoff_time]
                for old_result in old_results:
                    results.remove(old_result)
                    cleaned_count += 1

        logger.info(f"Cleaned up {cleaned_count} old workflow entries")
        return cleaned_count
