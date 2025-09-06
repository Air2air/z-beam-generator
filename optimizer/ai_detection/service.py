#!/usr/bin/env python3
"""
AI Detection Service - Root Level
Provides centralized AI detection capabilities for all components
"""

import logging
import time
from typing import Optional

from .providers.mock import MockProvider

# Import providers after importing types to avoid circular imports
from .providers.winston import WinstonProvider
from .types import AIDetectionConfig, AIDetectionError, AIDetectionResult


class AIDetectionService:
    """Main AI detection service class."""

    def __init__(self, config: Optional[AIDetectionConfig] = None):
        self.config = config or AIDetectionConfig()
        self.logger = logging.getLogger(__name__)

        # Initialize providers
        self.providers = {
            "winston": WinstonProvider(self.config),
            "mock": MockProvider(self.config),
        }

    def detect_ai_content(self, content: str) -> AIDetectionResult:
        """Detect AI-generated content using ONLY real APIs (no mocks in production)."""
        start_time = time.time()

        try:
            # PRODUCTION: Only use real Winston API - no mock fallback
            if self.config.provider == "winston":
                provider = self.providers.get("winston")
                if not provider:
                    raise AIDetectionError("Winston provider not available")
            else:
                raise AIDetectionError(f"Unknown provider: {self.config.provider}")

            result = provider.analyze_text(content)

            processing_time = time.time() - start_time

            return AIDetectionResult(
                score=result.score,
                confidence=result.confidence,
                classification=result.classification,
                provider=self.config.provider,
                processing_time=processing_time,
                details=result.details,
            )

        except Exception as e:
            self.logger.error(f"AI detection failed: {e}")
            processing_time = time.time() - start_time

            return AIDetectionResult(
                score=0.0,
                confidence=0.0,
                classification="error",
                provider=self.config.provider,
                processing_time=processing_time,
                details={"error": str(e)},
            )


# Global service instance for easy access
_ai_detection_service = None


def get_ai_detection_service() -> Optional[AIDetectionService]:
    """Get the global AI detection service instance"""
    return _ai_detection_service


def initialize_ai_detection_service(
    config: Optional[AIDetectionConfig] = None,
) -> AIDetectionService:
    """Initialize the global AI detection service"""
    global _ai_detection_service
    _ai_detection_service = AIDetectionService(config)
    return _ai_detection_service


class AIDetectionError(Exception):
    """Exception raised for AI detection errors"""

    pass
