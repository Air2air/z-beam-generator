"""
AI Detection Optimization Service

This service provides centralized AI detection analysis and optimization capabilities
that can be used by any component in the system.
"""

from optimizer.services.base import ServiceConfiguration
from optimizer.services.errors import AIDetectionProviderError
from optimizer.ai_detection.types import AIDetectionResult

from .service import AIDetectionOptimizationService

# Define missing batch classes for now (can be expanded later)
from dataclasses import dataclass
from typing import List


@dataclass
class BatchDetectionRequest:
    """Request for batch AI detection analysis."""
    contents: List[str]
    provider: str = "winston"


@dataclass
class BatchDetectionResult:
    """Result from batch AI detection analysis."""
    results: List[AIDetectionResult]
    total_processing_time: float
    success_count: int
    error_count: int


__all__ = [
    "AIDetectionOptimizationService",
    "AIDetectionProviderError",
    "AIDetectionResult",
    "BatchDetectionRequest",
    "BatchDetectionResult",
    "ServiceConfiguration",
]
