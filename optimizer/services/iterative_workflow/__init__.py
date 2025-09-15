"""
Iterative Workflow Service

Consolidated, optimized iterative workflow service for Z-Beam Generator.
Provides generic iterative improvement workflows with configurable strategies.

Features:
- Generic iteration management for any workflow
- Configurable iteration strategies (linear, exponential backoff, adaptive)
- Progress tracking and reporting
- Early exit conditions based on quality thresholds
- History management and rollback capabilities
- Status reporting and monitoring

This module consolidates previously duplicated implementations and provides
a single, optimized service for iterative workflows.
"""

# Import all classes from the consolidated service implementation
from .service import (
    IterativeWorkflowService,
    IterationStrategy,
    ExitCondition,
    IterationContext,
    IterationResult,
    WorkflowResult,
    WorkflowConfiguration,
    IterativeWorkflowError
)

# Export public API
__all__ = [
    "IterativeWorkflowService",
    "IterationStrategy", 
    "ExitCondition",
    "IterationContext",
    "IterationResult",
    "WorkflowResult",
    "WorkflowConfiguration",
    "IterativeWorkflowError"
]
