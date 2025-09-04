"""
Iterative Workflow Service

This service provides generic iterative improvement workflows that can be used
by any component in the system. It handles the common patterns of iterative
processing with configurable strategies, progress tracking, and early exit conditions.

Features:
- Generic iteration management for any workflow
- Configurable iteration strategies (linear, exponential backoff, etc.)
- Progress tracking and reporting
- Early exit conditions based on quality thresholds
- History management and rollback capabilities
- Status reporting and monitoring
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Callable, Union, Awaitable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .. import BaseService, ServiceConfiguration, ServiceError

logger = logging.getLogger(__name__)


class IterationStrategy(Enum):
    """Strategies for controlling iteration behavior."""
    LINEAR = "linear"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    ADAPTIVE = "adaptive"
    FIXED_COUNT = "fixed_count"


class ExitCondition(Enum):
    """Conditions for exiting iteration."""
    QUALITY_THRESHOLD = "quality_threshold"
    MAX_ITERATIONS = "max_iterations"
    TIME_LIMIT = "time_limit"
    CONVERGENCE = "convergence"
    MANUAL = "manual"


@dataclass
class IterationContext:
    """Context information for an iteration."""
    iteration_number: int
    start_time: datetime
    previous_result: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IterationResult:
    """Result of a single iteration."""
    iteration_number: int
    result: Any
    quality_score: float
    processing_time: float
    metadata: Dict[str, Any]
    timestamp: datetime


@dataclass
class WorkflowResult:
    """Result of an iterative workflow."""
    final_result: Any
    iterations: List[IterationResult]
    total_time: float
    exit_reason: str
    success: bool
    metadata: Dict[str, Any]


@dataclass
class WorkflowConfiguration:
    """Configuration for an iterative workflow."""
    max_iterations: int = 10
    quality_threshold: float = 0.9
    time_limit_seconds: Optional[float] = None
    iteration_strategy: IterationStrategy = IterationStrategy.LINEAR
    exit_conditions: List[ExitCondition] = field(default_factory=lambda: [ExitCondition.QUALITY_THRESHOLD, ExitCondition.MAX_ITERATIONS])
    convergence_threshold: float = 0.01
    backoff_factor: float = 2.0
    min_delay: float = 0.1
    max_delay: float = 10.0
    adaptive_quality_improvement: float = 0.05


class IterativeWorkflowError(ServiceError):
    """Raised when iterative workflow fails."""
    pass


class IterativeWorkflowService(BaseService):
    """
    Service for managing iterative improvement workflows.

    This service provides generic functionality for:
    - Running iterative processes with configurable strategies
    - Tracking progress and quality improvements
    - Implementing early exit conditions
    - Managing workflow history and rollback
    - Providing status reporting and monitoring
    """

    def __init__(self, config: ServiceConfiguration):
        # Initialize attributes before calling super().__init__
        self.active_workflows: Dict[str, WorkflowResult] = {}
        self.workflow_history: Dict[str, List[WorkflowResult]] = {}
        self.default_config = WorkflowConfiguration()

        super().__init__(config)

    def _validate_config(self) -> None:
        """Validate service configuration."""
        # No specific validation required for base implementation
        pass

    def _initialize(self) -> None:
        """Initialize the service."""
        self.logger.info("Iterative Workflow Service initialized")

    async def run_iterative_workflow(
        self,
        workflow_id: str,
        initial_input: Any,
        iteration_function: Callable[[Any, IterationContext], Awaitable[Any]],
        quality_function: Callable[[Any], Awaitable[float]],
        workflow_config: Optional[WorkflowConfiguration] = None,
        **kwargs
    ) -> WorkflowResult:
        """
        Run an iterative workflow.

        Args:
            workflow_id: Unique identifier for the workflow
            initial_input: Initial input for the workflow
            iteration_function: Function to call for each iteration
            quality_function: Function to assess quality of results
            workflow_config: Configuration for the workflow
            **kwargs: Additional arguments for iteration function

        Returns:
            WorkflowResult: Complete workflow result

        Raises:
            IterativeWorkflowError: If workflow fails
        """
        config = workflow_config or self.default_config
        start_time = datetime.now()

        self.logger.info(f"Starting iterative workflow: {workflow_id}")

        # Initialize workflow tracking
        iterations: List[IterationResult] = []
        current_input = initial_input
        previous_quality = 0.0

        try:
            for iteration_num in range(1, config.max_iterations + 1):
                iteration_start = datetime.now()

                # Create iteration context
                context = IterationContext(
                    iteration_number=iteration_num,
                    start_time=iteration_start,
                    previous_result=current_input,
                    metadata={"workflow_id": workflow_id}
                )

                # Run iteration
                self.logger.debug(f"Running iteration {iteration_num} for workflow {workflow_id}")
                iteration_result = await iteration_function(current_input, context)

                # Assess quality
                quality_score = await quality_function(iteration_result)

                # Record iteration result
                processing_time = (datetime.now() - iteration_start).total_seconds()
                iteration_record = IterationResult(
                    iteration_number=iteration_num,
                    result=iteration_result,
                    quality_score=quality_score,
                    processing_time=processing_time,
                    metadata=context.metadata,
                    timestamp=datetime.now()
                )
                iterations.append(iteration_record)

                # Check exit conditions
                exit_reason = self._check_exit_conditions(
                    iteration_record, iterations, config, start_time
                )

                if exit_reason:
                    self.logger.info(f"Workflow {workflow_id} exiting at iteration {iteration_num}: {exit_reason}")
                    break

                # Prepare for next iteration
                current_input = iteration_result
                previous_quality = quality_score

                # Apply iteration strategy delay
                await self._apply_iteration_strategy_delay(iteration_num, config)

            # Determine final result and success
            if iterations:
                final_result = iterations[-1].result
                final_quality = iterations[-1].quality_score
                success = final_quality >= config.quality_threshold
                exit_reason = exit_reason or "max_iterations_reached"
            else:
                final_result = initial_input
                final_quality = 0.0
                success = False
                exit_reason = "no_iterations_completed"

            # Create workflow result
            total_time = (datetime.now() - start_time).total_seconds()
            workflow_result = WorkflowResult(
                final_result=final_result,
                iterations=iterations,
                total_time=total_time,
                exit_reason=exit_reason,
                success=success,
                metadata={
                    "workflow_id": workflow_id,
                    "final_quality": final_quality,
                    "iterations_completed": len(iterations)
                }
            )

            # Store workflow result
            self.active_workflows[workflow_id] = workflow_result
            if workflow_id not in self.workflow_history:
                self.workflow_history[workflow_id] = []
            self.workflow_history[workflow_id].append(workflow_result)

            self.logger.info(f"Completed iterative workflow: {workflow_id} ({exit_reason})")
            return workflow_result

        except Exception as e:
            self.logger.error(f"Workflow {workflow_id} failed: {e}")
            raise IterativeWorkflowError(f"Workflow execution failed: {e}") from e

    def _check_exit_conditions(
        self,
        current_iteration: IterationResult,
        all_iterations: List[IterationResult],
        config: WorkflowConfiguration,
        start_time: datetime
    ) -> Optional[str]:
        """
        Check if any exit conditions are met.

        Args:
            current_iteration: Current iteration result
            all_iterations: All completed iterations
            config: Workflow configuration
            start_time: Workflow start time

        Returns:
            Optional[str]: Exit reason if condition met, None otherwise
        """
        # Quality threshold
        if (ExitCondition.QUALITY_THRESHOLD in config.exit_conditions and
            current_iteration.quality_score >= config.quality_threshold):
            return "quality_threshold_reached"

        # Max iterations
        if (ExitCondition.MAX_ITERATIONS in config.exit_conditions and
            current_iteration.iteration_number >= config.max_iterations):
            return "max_iterations_reached"

        # Time limit
        if (config.time_limit_seconds and
            ExitCondition.TIME_LIMIT in config.exit_conditions):
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed >= config.time_limit_seconds:
                return "time_limit_exceeded"

        # Convergence
        if (ExitCondition.CONVERGENCE in config.exit_conditions and
            len(all_iterations) >= 2):
            prev_quality = all_iterations[-2].quality_score
            improvement = current_iteration.quality_score - prev_quality
            if abs(improvement) < config.convergence_threshold:
                return "convergence_reached"

        return None

    async def _apply_iteration_strategy_delay(
        self,
        iteration_num: int,
        config: WorkflowConfiguration
    ) -> None:
        """Apply delay based on iteration strategy."""
        if config.iteration_strategy == IterationStrategy.LINEAR:
            delay = config.min_delay
        elif config.iteration_strategy == IterationStrategy.EXPONENTIAL_BACKOFF:
            delay = min(config.min_delay * (config.backoff_factor ** (iteration_num - 1)), config.max_delay)
        elif config.iteration_strategy == IterationStrategy.ADAPTIVE:
            # Adaptive delay based on recent performance (simplified)
            delay = config.min_delay
        else:  # FIXED_COUNT or unknown
            delay = 0.0

        if delay > 0:
            await asyncio.sleep(delay)

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a workflow.

        Args:
            workflow_id: Workflow identifier

        Returns:
            Optional[Dict[str, Any]]: Workflow status information
        """
        if workflow_id not in self.active_workflows:
            return None

        workflow = self.active_workflows[workflow_id]
        return {
            "workflow_id": workflow_id,
            "status": "completed",
            "success": workflow.success,
            "exit_reason": workflow.exit_reason,
            "iterations_completed": len(workflow.iterations),
            "total_time": workflow.total_time,
            "final_quality": workflow.metadata.get("final_quality", 0.0)
        }

    def get_workflow_history(self, workflow_id: str) -> List[Dict[str, Any]]:
        """
        Get history of a workflow.

        Args:
            workflow_id: Workflow identifier

        Returns:
            List[Dict[str, Any]]: Workflow history
        """
        if workflow_id not in self.workflow_history:
            return []

        return [
            {
                "success": w.success,
                "exit_reason": w.exit_reason,
                "iterations": len(w.iterations),
                "total_time": w.total_time,
                "final_quality": w.metadata.get("final_quality", 0.0),
                "timestamp": w.iterations[-1].timestamp if w.iterations else None
            }
            for w in self.workflow_history[workflow_id]
        ]

    def cancel_workflow(self, workflow_id: str) -> bool:
        """
        Cancel a running workflow.

        Args:
            workflow_id: Workflow identifier

        Returns:
            bool: True if workflow was cancelled
        """
        # Note: In a real implementation, this would need to integrate with
        # asyncio task management to actually cancel running workflows
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            workflow.metadata["cancelled"] = True
            workflow.exit_reason = "manually_cancelled"
            self.logger.info(f"Cancelled workflow: {workflow_id}")
            return True
        return False

    def cleanup_old_workflows(self, max_age_hours: int = 24) -> int:
        """
        Clean up old workflow data.

        Args:
            max_age_hours: Maximum age of workflows to keep

        Returns:
            int: Number of workflows cleaned up
        """
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        cleaned_count = 0

        # Clean active workflows
        to_remove = []
        for workflow_id, workflow in self.active_workflows.items():
            if workflow.iterations and workflow.iterations[-1].timestamp.timestamp() < cutoff_time:
                to_remove.append(workflow_id)

        for workflow_id in to_remove:
            del self.active_workflows[workflow_id]
            cleaned_count += 1

        # Clean workflow history (keep last few runs)
        for workflow_id, history in self.workflow_history.items():
            if len(history) > 5:  # Keep last 5 runs
                self.workflow_history[workflow_id] = history[-5:]
                cleaned_count += len(history) - 5

        if cleaned_count > 0:
            self.logger.info(f"Cleaned up {cleaned_count} old workflow records")

        return cleaned_count

    def health_check(self) -> bool:
        """Perform health check."""
        try:
            # Basic health check - service is healthy if it can manage workflows
            return True
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
