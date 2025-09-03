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

__all__ = [
    'AIDetectionService',
    'AIDetectionConfig',
    'AIDetectionResult',
    'AIDetectionError',
    'get_ai_detection_service',
    'initialize_ai_detection_service'
]
