#!/usr/bin/env python3
"""
AI Detection Service - Root Level
Provides centralized AI detection capabilities for all components
"""

import time
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class AIDetectionResult:
    """AI detection analysis result"""
    score: float  # AI detection score (0-100, higher = more AI-like)
    confidence: float  # Confidence level (0-1)
    classification: str  # "human", "ai", or "unclear"
    details: Dict[str, Any]  # Additional analysis details
    processing_time: float
    provider: str  # Which provider was used

@dataclass
class AIDetectionConfig:
    """Configuration for AI detection service"""
    provider: str = "gptzero"
    enabled: bool = True
    target_score: float = 30.0
    max_iterations: int = 3
    improvement_threshold: float = 5.0
    timeout: int = 30
    retry_attempts: int = 3

class AIDetectionService:
    """
    Main AI detection service that provides centralized access to AI detection capabilities.
    This service can be injected into any component that needs AI detection.
    """

    def __init__(self, config: Optional[AIDetectionConfig] = None):
        """
        Initialize AI detection service

        Args:
            config: Service configuration. If None, loads from default config file.
        """
        self.config = config or self._load_default_config()
        self.provider = None
        self._initialized = False

        if self.config.enabled:
            self._initialize_provider()

    def analyze_text(self, text: str, options: Optional[Dict] = None) -> AIDetectionResult:
        """
        Analyze text for AI detection

        Args:
            text: Text to analyze
            options: Additional options for analysis

        Returns:
            AIDetectionResult with analysis results

        Raises:
            AIDetectionError: If analysis fails
        """
        if not self.is_available():
            raise AIDetectionError("AI detection service is not available")

        start_time = time.time()

        try:
            result = self.provider.analyze_text(text, options or {})
            result.provider = self.config.provider
            result.processing_time = time.time() - start_time
            return result
        except Exception as e:
            logger.error(f"AI detection analysis failed: {e}")
            raise AIDetectionError(f"Analysis failed: {e}")

    def is_available(self) -> bool:
        """Check if AI detection service is available and working"""
        return self._initialized and self.provider and self.provider.is_available()

    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current provider"""
        if not self.is_available():
            return {"status": "unavailable"}

        return {
            "status": "available",
            "provider": self.config.provider,
            "config": {
                "target_score": self.config.target_score,
                "max_iterations": self.config.max_iterations,
                "timeout": self.config.timeout
            }
        }

    def _initialize_provider(self):
        """Initialize the AI detection provider"""
        try:
            if self.config.provider == "gptzero":
                from .providers.gptzero import GPTZeroProvider
                self.provider = GPTZeroProvider(self.config)
            elif self.config.provider == "phrasly":
                from .providers.phrasly import PhraslyProvider
                self.provider = PhraslyProvider(self.config)
            elif self.config.provider == "winston":
                from .providers.winston import WinstonProvider
                self.provider = WinstonProvider(self.config)
            elif self.config.provider == "mock":
                from .providers.mock import MockProvider
                self.provider = MockProvider(self.config)
            else:
                raise ValueError(f"Unknown AI detection provider: {self.config.provider}")

            self._initialized = True
            logger.info(f"✅ AI detection service initialized with {self.config.provider} provider")

        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize AI detection provider: {e}")
            self._initialized = False

    def _load_default_config(self) -> AIDetectionConfig:
        """Load default configuration from config file"""
        config_path = Path("config/ai_detection.yaml")

        if not config_path.exists():
            # Fallback to legacy config
            legacy_config = Path("config/gptzero_config.yaml")
            if legacy_config.exists():
                return self._load_legacy_config(legacy_config)
            else:
                logger.warning("No AI detection config found, using defaults")
                return AIDetectionConfig()

        try:
            import yaml
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f)

            return AIDetectionConfig(
                provider=data.get('provider', 'gptzero'),
                enabled=data.get('enabled', True),
                target_score=data.get('target_score', 30.0),
                max_iterations=data.get('max_iterations', 3),
                improvement_threshold=data.get('improvement_threshold', 5.0),
                timeout=data.get('timeout', 30),
                retry_attempts=data.get('retry_attempts', 3)
            )
        except Exception as e:
            logger.warning(f"Failed to load AI detection config: {e}")
            return AIDetectionConfig()

    def _load_legacy_config(self, config_path: Path) -> AIDetectionConfig:
        """Load configuration from legacy GPTZero config file"""
        try:
            import yaml
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f)

            return AIDetectionConfig(
                provider="gptzero",
                enabled=True,
                target_score=data.get('GPTZERO_TARGET_SCORE', 30.0),
                max_iterations=data.get('GPTZERO_MAX_ITERATIONS', 3),
                improvement_threshold=data.get('GPTZERO_IMPROVEMENT_THRESHOLD', 5.0)
            )
        except Exception as e:
            logger.warning(f"Failed to load legacy config: {e}")
            return AIDetectionConfig()

# Global service instance for easy access
_ai_detection_service = None

def get_ai_detection_service() -> Optional[AIDetectionService]:
    """Get the global AI detection service instance"""
    return _ai_detection_service

def initialize_ai_detection_service(config: Optional[AIDetectionConfig] = None) -> AIDetectionService:
    """Initialize the global AI detection service"""
    global _ai_detection_service
    _ai_detection_service = AIDetectionService(config)
    return _ai_detection_service

class AIDetectionError(Exception):
    """Exception raised for AI detection errors"""
    pass
