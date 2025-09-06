#!/usr/bin/env python3
"""
AI Detection Service Package
"""

from .config import (
    AI_DETECTION_CONFIG,
    create_dynamic_ai_detection_config,
    get_default_ai_detection_config,
)
from .service import (
    AIDetectionError,
    AIDetectionResult,
    AIDetectionService,
    get_ai_detection_service,
    initialize_ai_detection_service,
)
from .types import AIDetectionConfig

__all__ = [
    "AIDetectionService",
    "AIDetectionConfig",
    "AIDetectionResult",
    "AIDetectionError",
    "get_ai_detection_service",
    "initialize_ai_detection_service",
    "create_dynamic_ai_detection_config",
    "get_default_ai_detection_config",
    "AI_DETECTION_CONFIG",
]
