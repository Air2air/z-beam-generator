"""
Standalone AI Detection Optimization System

This module provides a decoupled optimization system that can work with any content,
independent of component generation. It uses the existing service architecture for
AI detection, iterative workflows, and configuration optimization.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, Optional

from optimizer.service_initializer import initialize_optimizer_services
from optimizer.services import ServiceConfiguration
from optimizer.services.ai_detection_optimization import AIDetectionOptimizationService
from optimizer.services.iterative_workflow.service import (
    IterativeWorkflowService,
    WorkflowConfiguration,
)
from optimizer.services.service_registry import service_registry

logger = logging.getLogger(__name__)


@dataclass
class OptimizationConfig:
    """Configuration for content optimization."""

    target_score: float = 75.0
    max_iterations: int = 5
    improvement_threshold: float = 3.0
    time_limit_seconds: Optional[float] = None
    convergence_threshold: float = 0.01


@dataclass
class OptimizationResult:
    """Result of content optimization."""

    original_content: str
    optimized_content: str
    original_score: float
    final_score: float
    iterations_performed: int
    total_time: float
    success: bool
    improvement: float
    metadata: Dict[str, Any]


class ContentOptimizationOrchestrator:
    """
    Orchestrator for standalone content optimization.

    This system decouples complex optimization logic from component generation,
    allowing any content to be optimized using the same sophisticated iterative
    workflow that was previously embedded in TextComponentGenerator.
    """

    def __init__(
        self,
        ai_service: Optional[AIDetectionOptimizationService] = None,
        workflow_service: Optional[IterativeWorkflowService] = None,
    ):
        """
        Initialize the optimization orchestrator.

        Args:
            ai_service: AI detection service (will be retrieved from registry if None)
            workflow_service: Workflow service (will be retrieved from registry if None)
        """
        # Initialize services if not provided
        if ai_service is None or workflow_service is None:
            logger.info("🔧 Initializing optimizer services...")
            init_result = initialize_optimizer_services()
            if not init_result["success"]:
                raise ValueError(
                    f"Failed to initialize services: {init_result['errors']}"
                )

        # Try to get services from registry, create if not available
        if ai_service:
            self.ai_service = ai_service
        else:
            self.ai_service = service_registry.get_service_typed(
                "ai_detection_service", AIDetectionOptimizationService
            )
            if not self.ai_service:
                raise ValueError(
                    "AI detection service not found in registry and not provided"
                )

        if workflow_service:
            self.workflow_service = workflow_service
        else:
            self.workflow_service = service_registry.get_service_typed(
                "iterative_workflow_service", IterativeWorkflowService
            )
            if not self.workflow_service:
                raise ValueError(
                    "Iterative workflow service not found in registry and not provided"
                )

        if not self.ai_service:
            raise ValueError("AI detection service not available")
        if not self.workflow_service:
            raise ValueError("Iterative workflow service not available")

        logger.info("✅ Content optimization orchestrator initialized")

    async def optimize_content(
        self,
        content: str,
        material_name: str,
        config: Optional[OptimizationConfig] = None,
        iteration_function: Optional[Callable] = None,
        **kwargs,
    ) -> OptimizationResult:
        """
        Optimize content using the decoupled optimization system.

        Args:
            content: Content to optimize
            material_name: Name of the material for context
            config: Optimization configuration
            iteration_function: Custom iteration function (optional)
            **kwargs: Additional parameters for iteration function

        Returns:
            OptimizationResult: Optimization results
        """
        if config is None:
            config = OptimizationConfig()

        start_time = datetime.now()
        workflow_id = f"optimization_{material_name}_{int(start_time.timestamp())}"

        # Get initial score
        try:
            initial_result = await self.ai_service.detect_ai_content(content)
            initial_score = (
                initial_result.score if hasattr(initial_result, "score") else 50.0
            )
        except Exception as e:
            logger.warning(f"Could not get initial AI score: {e}")
            initial_score = 50.0

        logger.info(f"🚀 Starting optimization for {material_name}")
        logger.info(f"   📊 Initial score: {initial_score:.1f}")
        logger.info(f"   🎯 Target score: {config.target_score}")
        logger.info(f"   🔄 Max iterations: {config.max_iterations}")

        # Use default iteration function if none provided
        if iteration_function is None:
            iteration_function = self._default_iteration_function

        # Create workflow configuration
        workflow_config = WorkflowConfiguration(
            max_iterations=config.max_iterations,
            quality_threshold=config.target_score / 100.0,  # Convert to 0-1 scale
            time_limit_seconds=config.time_limit_seconds,
            convergence_threshold=config.convergence_threshold,
        )

        # Prepare iteration context
        iteration_context = {
            "material_name": material_name,
            "ai_service": self.ai_service,
            "config": config,
            "kwargs": kwargs,
        }

        # Run iterative workflow
        workflow_result = await self.workflow_service.run_iterative_workflow(
            workflow_id=workflow_id,
            initial_input=content,
            iteration_function=lambda content, ctx: iteration_function(
                content, iteration_context
            ),
            quality_function=self._quality_assessment_function,
            workflow_config=workflow_config,
        )

        # Calculate final results
        final_score = (
            workflow_result.iterations[-1].quality_score
            if workflow_result.iterations
            else initial_score
        )
        improvement = final_score - initial_score
        total_time = (datetime.now() - start_time).total_seconds()

        success = final_score >= config.target_score

        result = OptimizationResult(
            original_content=content,
            optimized_content=workflow_result.final_result or content,
            original_score=initial_score,
            final_score=final_score,
            iterations_performed=len(workflow_result.iterations),
            total_time=total_time,
            success=success,
            improvement=improvement,
            metadata={
                "workflow_id": workflow_id,
                "exit_reason": workflow_result.exit_reason,
                "iterations": [
                    {
                        "number": it.iteration_number,
                        "score": it.quality_score,
                        "timestamp": it.timestamp.isoformat(),
                    }
                    for it in workflow_result.iterations
                ],
            },
        )

        logger.info(f"🏁 Optimization completed for {material_name}")
        logger.info(
            f"   📊 Final score: {final_score:.1f} (improvement: {improvement:+.1f})"
        )
        logger.info(f"   ⏱️ Total time: {total_time:.1f}s")
        logger.info(f"   ✅ Success: {success}")

        return result

    async def _default_iteration_function(
        self, content: str, context: Dict[str, Any]
    ) -> str:
        """
        Default iteration function for content optimization.

        This is a simplified version that focuses on basic improvements
        without the complex logic from TextComponentGenerator.
        """
        material_name = context["material_name"]
        ai_service = context["ai_service"]

        # Simple prompt for content improvement
        improvement_prompt = f"""
        Improve the following content for {material_name} laser cleaning.
        Make it more natural and human-like while maintaining technical accuracy.
        Focus on:
        - Natural language flow
        - Professional tone
        - Clear explanations
        - Technical precision

        Original content:
        {content}

        Improved content:
        """

        # Here you would call your API to generate improved content
        # For now, return the original content (this would be replaced with actual API call)
        logger.info(f"   🔄 Iteration for {material_name} - applying basic improvements")

        # In a real implementation, you would:
        # 1. Call an API with the improvement prompt
        # 2. Get the improved content back
        # 3. Return the improved content

        return content  # Placeholder

    async def _quality_assessment_function(self, content: str) -> float:
        """
        Assess the quality of content using AI detection.

        Returns:
            float: Quality score (0-100 scale)

        Raises:
            Exception: If quality assessment fails
        """
        result = await self.ai_service.detect_ai_content(content)
        # Convert to 0-100 scale and invert (lower AI score = higher quality)
        quality_score = (1.0 - result.score) * 100
        return quality_score

    async def batch_optimize(
        self, content_items: Dict[str, str], config: Optional[OptimizationConfig] = None
    ) -> Dict[str, OptimizationResult]:
        """
        Optimize multiple content items in batch.

        Args:
            content_items: Dict of material_name -> content
            config: Optimization configuration

        Returns:
            Dict[str, OptimizationResult]: Optimization results for each item
        """
        if config is None:
            config = OptimizationConfig()

        logger.info(f"🚀 Starting batch optimization for {len(content_items)} items")

        # Process items concurrently
        tasks = [
            self.optimize_content(content, material_name, config)
            for material_name, content in content_items.items()
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        batch_results = {}
        for i, (material_name, _) in enumerate(content_items.items()):
            if isinstance(results[i], Exception):
                logger.error(
                    f"Batch optimization failed for {material_name}: {results[i]}"
                )
                # Create a failure result
                batch_results[material_name] = OptimizationResult(
                    original_content=content_items[material_name],
                    optimized_content=content_items[material_name],
                    original_score=0.0,
                    final_score=0.0,
                    iterations_performed=0,
                    total_time=0.0,
                    success=False,
                    improvement=0.0,
                    metadata={"error": str(results[i])},
                )
            else:
                batch_results[material_name] = results[i]

        successful_optimizations = sum(1 for r in batch_results.values() if r.success)
        logger.info(
            f"🏁 Batch optimization completed: {successful_optimizations}/{len(content_items)} successful"
        )

        return batch_results


# Convenience functions for easy usage
async def optimize_content_simple(
    content: str,
    material_name: str,
    target_score: float = 75.0,
    max_iterations: int = 5,
) -> OptimizationResult:
    """
    Simple function to optimize content with default settings.

    Args:
        content: Content to optimize
        material_name: Material name for context
        target_score: Target AI detection score
        max_iterations: Maximum iterations

    Returns:
        OptimizationResult: Optimization results
    """
    config = OptimizationConfig(
        target_score=target_score, max_iterations=max_iterations
    )

    orchestrator = ContentOptimizationOrchestrator()
    return await orchestrator.optimize_content(content, material_name, config)


async def batch_optimize_materials(
    materials_content: Dict[str, str],
    target_score: float = 75.0,
    max_iterations: int = 5,
) -> Dict[str, OptimizationResult]:
    """
    Optimize multiple materials in batch.

    Args:
        materials_content: Dict of material_name -> content
        target_score: Target AI detection score
        max_iterations: Maximum iterations

    Returns:
        Dict[str, OptimizationResult]: Results for each material
    """
    config = OptimizationConfig(
        target_score=target_score, max_iterations=max_iterations
    )

    orchestrator = ContentOptimizationOrchestrator()
    return await orchestrator.batch_optimize(materials_content, config)
