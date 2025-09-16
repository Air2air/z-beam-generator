"""
Consolidated Import Management for Z-Beam Optimizer

Provides clean, focused imports for core optimizer functionality.
"""

import logging
from typing import Any, Dict, Optional

# Core service infrastructure
from .base import SimplifiedService, ServiceConfiguration
from .config_unified import (
    UnifiedConfig,
    get_config,
    get_ai_detection_service_config,
    get_workflow_service_config,
)
from .errors import (
    OptimizerError,
    ConfigurationError,
    ServiceError,
    ValidationError,
)

# Primary services (consolidated from 6 to 3)
from .ai_detection_optimization.service import AIDetectionOptimizationService
from .iterative_workflow.service import IterativeWorkflowService

# Essential utilities
from ..utils.async_utils import run_async
from ..utils.cache_utils import LRUCache

# Main exports
__all__ = [
    # Core infrastructure
    "SimplifiedService",
    "ServiceConfiguration", 
    "UnifiedConfig",
    "get_config",
    
    # Primary services
    "AIDetectionOptimizationService",
    "IterativeWorkflowService",
    
    # Error handling
    "OptimizerError",
    "ConfigurationError",
    "ServiceError",
    
    # Utilities
    "run_async",
    "LRUCache",
]