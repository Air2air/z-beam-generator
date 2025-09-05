"""
Optimizer Services Package

This package contains all the service modules for optimization:
- ai_detection_optimization: AI detection optimization service
- iterative_workflow: Iterative workflow management service
- dynamic_evolution: Dynamic prompt/content evolution service
- quality_assessment: Quality assessment and benchmarking service
- configuration_optimizer: Configuration optimization service
"""

from .ai_detection_optimization import AIDetectionOptimizationService
from .iterative_workflow import IterativeWorkflowService, WorkflowConfiguration
from .dynamic_evolution import DynamicEvolutionService
from .quality_assessment import QualityAssessmentService
from .configuration_optimizer import ConfigurationOptimizationService

__all__ = [
    'AIDetectionOptimizationService',
    'IterativeWorkflowService',
    'WorkflowConfiguration',
    'DynamicEvolutionService',
    'QualityAssessmentService',
    'ConfigurationOptimizationService'
]
