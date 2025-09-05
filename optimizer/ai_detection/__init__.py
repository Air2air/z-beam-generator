#!/usr/bin/env python3
"""
AI Detection Service Package
"""

from .service import (
    AIDetectionService,
    AIDetectionConfig,
    AIDetectionResult,
    AIDetectionError,
    get_ai_detection_service,
    initialize_ai_detection_service
)
from .config import (
    create_dynamic_ai_detection_config,
    get_default_ai_detection_config,
    AI_DETECTION_CONFIG
)

__all__ = [
    'AIDetectionService',
    'AIDetectionConfig',
    'AIDetectionResult',
    'AIDetectionError',
    'get_ai_detection_service',
    'initialize_ai_detection_service',
    'create_dynamic_ai_detection_config',
    'get_default_ai_detection_config',
    'AI_DETECTION_CONFIG'
]
