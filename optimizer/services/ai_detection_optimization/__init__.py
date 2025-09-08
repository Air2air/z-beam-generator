"""
AI Detection Optimization Service

This service provides centralized AI detection analysis and optimization capabilities
that can be used by any component in the system.
"""

from optimizer.services.base import ServiceConfiguration

from .service import (
    AIDetectionOptimizationService,
    AIDetectionProviderError,
    AIDetectionResult,
    BatchDetectionRequest,
    BatchDetectionResult,
)

__all__ = [
    "AIDetectionOptimizationService",
    "AIDetectionProviderError",
    "AIDetectionResult",
    "BatchDetectionRequest",
    "BatchDetectionResult",
    "ServiceConfiguration",
]
