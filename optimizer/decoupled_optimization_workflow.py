"""
Decoupled Optimization Workflow

This module provides the simplified optimization workflow that uses the
standalone optimization orchestrator instead of the complex embedded logic.
"""

import asyncio
import logging
from typing import Dict, Any

from optimization_orchestrator import ContentOptimizationOrchestrator, OptimizationConfig

logger = logging.getLogger(__name__)


def run_decoupled_optimization_workflow(material: str, component_type: str, existing_content: str,
                                       current_score: float, target_score: float, ai_service,
                                       dynamic_config: dict) -> bool:
    """
    Run the decoupled optimization workflow using the standalone optimization system.

    Args:
        material: Material name
        component_type: Component type
        existing_content: Existing content to optimize
        current_score: Current AI detection score
        target_score: Target score to achieve
        ai_service: AI detection service
        dynamic_config: Dynamic configuration

    Returns:
        bool: True if optimization successful
    """
    try:
        max_iterations = dynamic_config.get("max_iterations", 5)
        improvement_threshold = dynamic_config.get("improvement_threshold", 3.0)

        print(f"🔄 Decoupled optimization parameters:")
        print(f"   📊 Current score: {current_score}")
        print(f"   🎯 Target score: {target_score}")
        print(f"   🔄 Max iterations: {max_iterations}")
        print(f"   📈 Improvement threshold: {improvement_threshold}")

        # Create optimization configuration
        config = OptimizationConfig(
            target_score=target_score,
            max_iterations=max_iterations,
            improvement_threshold=improvement_threshold
        )

        # Initialize the decoupled optimization orchestrator
        orchestrator = ContentOptimizationOrchestrator(ai_service=ai_service)

        # Run optimization using the decoupled system
        result = asyncio.run(orchestrator.optimize_content(
            content=existing_content,
            material_name=material,
            config=config
        ))

        # Save the optimized content if it was improved
        if result.success and result.improvement > 0:
            from utils.file_operations import save_component_to_file_original
            save_component_to_file_original(material, component_type, result.optimized_content)
            print(f"   💾 Saved optimized content to file")

        return result.success

    except Exception as e:
        print(f"❌ Decoupled optimization workflow failed: {e}")
        return False
