#!/usr/bin/env python3
"""
AI Detection Types - Shared data classes and exceptions
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class AIDetectionConfig:
    """Configuration for AI detection service."""

    provider: str = "winston"
    enabled: bool = True
    target_score: float = 70.0
    max_iterations: int = 3
    improvement_threshold: float = 5.0
    timeout: int = 30
    retry_attempts: int = 3


@dataclass
class AIDetectionResult:
    """Result from AI detection analysis."""

    score: float
    confidence: float
    classification: str
    provider: str
    processing_time: float
    details: Optional[Dict[str, Any]] = None


class AIDetectionError(Exception):
    """Exception raised for AI detection errors"""

    pass
