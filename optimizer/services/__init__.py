"""
Consolidated Import Management for Z-Beam Optimizer

Centralizes all imports and provides a single entry point for common functionality.
"""

import logging
from typing import Any, Dict, Optional

# Core service imports
from .base import SimplifiedService, ServiceConfiguration
from .config_unified import (
    UnifiedConfig,
    get_config,
    get_ai_detection_service_config,
    get_workflow_service_config,
    get_optimization_defaults,
    is_test_environment,
)
from .errors import (
    OptimizerError,
    ConfigurationError,
    ServiceError,
    ValidationError,
    RetryableError,
    InitializationError,
    TimeoutError,
    ResourceError,
    ServiceConfigurationError,  # Legacy alias
)

# Service implementations
from .ai_detection_optimization.service import AIDetectionOptimizationService
from .iterative_workflow.service import (
    IterativeWorkflowService,
    IterativeWorkflowError,
    IterationStrategy,
    ExitCondition,
    WorkflowConfiguration,
    IterationContext,
    IterationResult,
    WorkflowResult,
)

# Common utilities
from ..utils.common import setup_logging, validate_config
from ..utils.async_utils import run_async, gather_with_exception_handling
from ..utils.cache_utils import LRUCache, CacheEntry

# Type hints and dataclasses
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

__all__ = [
    # Core services
    "SimplifiedService",
    "ServiceConfiguration",

    # Configuration
    "UnifiedConfig",
    "get_config",
    "get_ai_detection_service_config",
    "get_workflow_service_config",
    "get_optimization_defaults",
    "is_test_environment",

    # Errors
    "OptimizerError",
    "ConfigurationError",
    "ServiceError",
    "ValidationError",
    "RetryableError",
    "InitializationError",
    "TimeoutError",
    "ResourceError",
    "ServiceConfigurationError",

    # AI Detection Service
    "AIDetectionOptimizationService",

    # Iterative Workflow Service
    "IterativeWorkflowService",
    "IterativeWorkflowError",
    "IterationStrategy",
    "ExitCondition",
    "WorkflowConfiguration",
    "IterationContext",
    "IterationResult",
    "WorkflowResult",

    # Common utilities
    "setup_logging",
    "validate_config",
    "run_async",
    "gather_with_exception_handling",
    "LRUCache",
    "CacheEntry",

    # Standard library re-exports
    "dataclass",
    "field",
    "datetime",
    "timedelta",
    "Enum",
]


def create_service_registry() -> Dict[str, Any]:
    """
    Create a registry of all available services.

    Returns:
        Dict mapping service names to service classes
    """
    return {
        'ai_detection': AIDetectionOptimizationService,
        'iterative_workflow': IterativeWorkflowService,
    }


def initialize_all_services(config: Optional[UnifiedConfig] = None) -> Dict[str, SimplifiedService]:
    """
    Initialize all services with unified configuration.

    Args:
        config: Unified configuration instance

    Returns:
        Dict mapping service names to initialized service instances
    """
    if config is None:
        config = get_config()

    services = {}
    registry = create_service_registry()

    for service_name, service_class in registry.items():
        try:
            service_config = config.get_service_config(service_name)
            if service_config.enabled:
                service_instance = service_class(service_config)
                services[service_name] = service_instance
                logging.info(f"Initialized service: {service_name}")
        except Exception as e:
            logging.error(f"Failed to initialize service {service_name}: {e}")

    return services


async def initialize_services_async(services: Dict[str, SimplifiedService]) -> None:
    """
    Asynchronously initialize all service instances.

    Args:
        services: Dict of service instances to initialize
    """
    init_tasks = []
    for service_name, service in services.items():
        init_tasks.append(service.initialize())

    await gather_with_exception_handling(init_tasks)


def get_service_health_status(services: Dict[str, SimplifiedService]) -> Dict[str, Any]:
    """
    Get health status for all services.

    Args:
        services: Dict of service instances

    Returns:
        Dict with overall health and individual service status
    """
    overall_healthy = True
    service_status = {}

    for service_name, service in services.items():
        try:
            health = service.health_check()
            service_status[service_name] = health
            if not health.get('healthy', True):
                overall_healthy = False
        except Exception as e:
            service_status[service_name] = {
                'healthy': False,
                'error': str(e)
            }
            overall_healthy = False

    return {
        'overall_healthy': overall_healthy,
        'services': service_status,
        'timestamp': datetime.now().isoformat()
    }


# Convenience functions for quick access
def get_ai_service() -> AIDetectionOptimizationService:
    """Get initialized AI detection service."""
    config = get_ai_detection_service_config()
    return AIDetectionOptimizationService(config)


def get_workflow_service() -> IterativeWorkflowService:
    """Get initialized iterative workflow service."""
    config = get_workflow_service_config()
    return IterativeWorkflowService(config)
