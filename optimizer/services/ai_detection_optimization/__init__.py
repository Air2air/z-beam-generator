"""
AI Detection Optimization Service

This service provides centralized AI detection analysis and optimization capabilities
that can be used by any component in the system.

Features:
- Unified AI detection interface across multiple providers
- Caching for performance optimization
- Batch processing capabilities
- Quality assessment integration
- Configurable detection thresholds
"""

import abc
import asyncio
import hashlib
import json
import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

from services import BaseService, ServiceConfiguration, ServiceConfigurationError, ServiceError

logger = logging.getLogger(__name__)


@dataclass
class AIDetectionResult:
    """Result of AI detection analysis."""
    content: str
    score: float
    provider: str
    confidence: float
    detected: bool
    metadata: Dict[str, Any]
    timestamp: datetime


@dataclass
class BatchDetectionRequest:
    """Request for batch AI detection analysis."""
    contents: List[str]
    providers: Optional[List[str]] = None
    options: Optional[Dict[str, Any]] = None


@dataclass
class BatchDetectionResult:
    """Result of batch AI detection analysis."""
    results: List[AIDetectionResult]
    summary: Dict[str, Any]
    processing_time: float


class AIDetectionProviderError(ServiceError):
    """Raised when an AI detection provider fails."""
    pass


class AIDetectionProvider:
    """
    Base class for AI detection providers.

    This abstract class defines the interface that all AI detection providers
    must implement.
    """

    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize the provider.

        Args:
            name: Provider name
            config: Provider-specific configuration
        """
        self.name = name
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abc.abstractmethod
    async def detect_ai_content(self, content: str, **kwargs) -> AIDetectionResult:
        """
        Detect AI-generated content.

        Args:
            content: The content to analyze
            **kwargs: Additional provider-specific options

        Returns:
            AIDetectionResult: Detection result
        """
        pass

    @abc.abstractmethod
    def is_available(self) -> bool:
        """
        Check if the provider is available.

        Returns:
            bool: True if provider is available
        """
        pass

    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the provider."""
        return {
            "name": self.name,
            "available": self.is_available(),
            "config": {k: "***" if "key" in k.lower() else v for k, v in self.config.items()}
        }


class MockAIDetectionProvider(AIDetectionProvider):
    """
    Mock AI detection provider for testing.

    This provider simulates AI detection with configurable behavior.
    """

    def __init__(self, name: str = "mock", config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config or {})
        self.mock_score = self.config.get("mock_score", 0.5)
        self.mock_detected = self.config.get("mock_detected", False)

    async def detect_ai_content(self, content: str, **kwargs) -> AIDetectionResult:
        """Mock AI detection implementation."""
        # Simulate some processing time
        await asyncio.sleep(0.1)

        # Simple mock logic based on content length
        score = min(len(content) / 1000.0, 1.0) if len(content) > 100 else 0.1
        detected = score > 0.5

        return AIDetectionResult(
            content=content,
            score=score,
            provider=self.name,
            confidence=0.8,
            detected=detected,
            metadata={"mock": True, "content_length": len(content)},
            timestamp=datetime.now()
        )

    def is_available(self) -> bool:
        return True


class AIDetectionOptimizationService(BaseService):
    """
    Service for AI detection analysis and optimization.

    This service provides:
    - Unified interface for multiple AI detection providers
    - Caching for performance optimization
    - Batch processing capabilities
    - Quality assessment integration
    - Configurable detection thresholds
    """

    def __init__(self, config: ServiceConfiguration):
        # Initialize attributes before calling super().__init__
        self.providers: Dict[str, AIDetectionProvider] = {}
        self.cache: Dict[str, AIDetectionResult] = {}
        self.cache_ttl = timedelta(hours=config.settings.get("cache_ttl_hours", 1))
        self.executor = ThreadPoolExecutor(max_workers=config.settings.get("max_workers", 4))
        self.detection_threshold = config.settings.get("detection_threshold", 0.7)
        self.confidence_threshold = config.settings.get("confidence_threshold", 0.8)

        super().__init__(config)

        # Store original config for service registry compatibility
        self._service_config = config

        # Create a config object with attributes for backward compatibility
        # Keep the original config for BaseService compatibility
        self.ai_config = type('Config', (), {})()
        self.ai_config.target_score = config.settings.get("target_score", 65.0)
        self.ai_config.max_iterations = config.settings.get("max_iterations", 5)
        self.ai_config.improvement_threshold = config.settings.get("improvement_threshold", 3.0)
        self.ai_config.human_threshold = config.settings.get("human_threshold", 75.0)
        self.ai_config.min_text_length_winston = config.settings.get("min_text_length_winston", 300)
        self.ai_config.short_content_threshold = config.settings.get("short_content_threshold", 400)
        self.ai_config.min_content_length = config.settings.get("min_content_length", 150)
        self.ai_config.fallback_score_first_iteration = config.settings.get("fallback_score_first_iteration", 60.0)
        self.ai_config.fallback_score_short_content = config.settings.get("fallback_score_short_content", 55.0)
        self.ai_config.fallback_score_very_short = config.settings.get("fallback_score_very_short", 40.0)
        self.ai_config.fallback_score_error = config.settings.get("fallback_score_error", 50.0)
        self.status_update_interval = config.settings.get("status_update_interval", 10)
        self.iteration_status_frequency = config.settings.get("iteration_status_frequency", 5)
        self.ai_config.word_count_tolerance = config.settings.get("word_count_tolerance", 1.5)
        self.ai_config.winston_timeout_cap = config.settings.get("winston_timeout_cap", 15)
        self.ai_config.max_tokens = config.settings.get("max_tokens", 3000)
        self.ai_config.retry_delay = config.settings.get("retry_delay", 0.5)
        self.ai_config.winston_human_range = config.settings.get("winston_human_range", (70, 100))
        self.ai_config.winston_unclear_range = config.settings.get("winston_unclear_range", (30, 70))
        self.ai_config.winston_ai_range = config.settings.get("winston_ai_range", (0, 30))
        self.ai_config.min_iterations_before_exit = config.settings.get("min_iterations_before_exit", 3)
        self.ai_config.early_exit_score_threshold = config.settings.get("early_exit_score_threshold", 10)
        self.ai_config.deepseek_optimization_enabled = config.settings.get("deepseek_optimization_enabled", True)
        self.ai_config.config_backup_enabled = config.settings.get("config_backup_enabled", True)
        self.ai_config.enable_detailed_logging = config.settings.get("enable_detailed_logging", True)
        self.ai_config.max_sentence_details = config.settings.get("max_sentence_details", 5)

        # Add settings attribute for compatibility
        self.ai_config.settings = config.settings

    def get_service_info(self) -> Dict[str, Any]:
        """Get information about the service."""
        return {
            "name": self._service_config.name,
            "version": self._service_config.version,
            "enabled": self._service_config.enabled,
            "initialized": self._initialized,
            "healthy": self._healthy,
            "class": self.__class__.__name__
        }

    def _validate_config(self) -> None:
        """Validate service configuration."""
        required_settings = ["providers"]
        for setting in required_settings:
            if setting not in self.config.settings:
                raise ServiceConfigurationError(f"Missing required setting: {setting}")

        providers_config = self.config.settings["providers"]
        if not isinstance(providers_config, dict):
            raise ServiceConfigurationError("providers setting must be a dictionary")

    def _initialize(self) -> None:
        """Initialize the service."""
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        """Initialize AI detection providers."""
        providers_config = self.config.settings["providers"]

        for provider_name, provider_config in providers_config.items():
            provider_type = provider_config.get("type", "mock")

            if provider_type == "mock":
                provider = MockAIDetectionProvider(provider_name, provider_config)
            else:
                # Here you would initialize real providers like OpenAI, etc.
                self.logger.warning(f"Unknown provider type: {provider_type}, using mock")
                provider = MockAIDetectionProvider(provider_name, provider_config)

            self.providers[provider_name] = provider
            self.logger.info(f"Initialized provider: {provider_name}")

    async def detect_ai_content(
        self,
        content: str,
        providers: Optional[List[str]] = None,
        use_cache: bool = True,
        **kwargs
    ) -> AIDetectionResult:
        """
        Detect AI-generated content using available providers.

        Args:
            content: The content to analyze
            providers: List of provider names to use (None for all)
            use_cache: Whether to use cached results
            **kwargs: Additional options

        Returns:
            AIDetectionResult: Detection result

        Raises:
            AIDetectionProviderError: If all providers fail
        """
        # Check cache first
        if use_cache:
            cache_key = self._get_cache_key(content, providers or list(self.providers.keys()))
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                self.logger.debug("Returning cached AI detection result")
                return cached_result

        # Determine which providers to use
        target_providers = providers or list(self.providers.keys())
        available_providers = [p for p in target_providers if p in self.providers and self.providers[p].is_available()]

        if not available_providers:
            raise AIDetectionProviderError("No available AI detection providers")

        # Try providers in order
        last_error = None
        for provider_name in available_providers:
            provider = self.providers[provider_name]
            try:
                self.logger.debug(f"Using provider: {provider_name}")
                result = await provider.detect_ai_content(content, **kwargs)

                # Cache the result
                if use_cache:
                    self._cache_result(cache_key, result)

                return result

            except Exception as e:
                self.logger.warning(f"Provider {provider_name} failed: {e}")
                last_error = e
                continue

        # All providers failed
        raise AIDetectionProviderError(f"All AI detection providers failed. Last error: {last_error}")

    async def batch_detect_ai_content(
        self,
        request: BatchDetectionRequest
    ) -> BatchDetectionResult:
        """
        Perform batch AI detection analysis.

        Args:
            request: Batch detection request

        Returns:
            BatchDetectionResult: Batch detection results
        """
        start_time = datetime.now()

        # Process contents concurrently
        tasks = []
        for content in request.contents:
            task = self.detect_ai_content(
                content=content,
                providers=request.providers,
                **(request.options or {})
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        successful_results = []
        errors = []

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                errors.append(f"Content {i}: {result}")
                # Create a fallback result
                successful_results.append(AIDetectionResult(
                    content=request.contents[i],
                    score=0.0,
                    provider="error",
                    confidence=0.0,
                    detected=False,
                    metadata={"error": str(result)},
                    timestamp=datetime.now()
                ))
            else:
                successful_results.append(result)

        # Calculate summary
        processing_time = (datetime.now() - start_time).total_seconds()
        avg_score = sum(r.score for r in successful_results) / len(successful_results) if successful_results else 0
        detected_count = sum(1 for r in successful_results if r.detected)

        summary = {
            "total_contents": len(request.contents),
            "successful_detections": len(successful_results),
            "errors": len(errors),
            "average_score": avg_score,
            "detected_count": detected_count,
            "detection_rate": detected_count / len(successful_results) if successful_results else 0,
            "error_details": errors
        }

        return BatchDetectionResult(
            results=successful_results,
            summary=summary,
            processing_time=processing_time
        )

    def is_available(self) -> bool:
        """
        Check if the AI detection optimization service is available.

        Returns:
            bool: True if service is available and healthy
        """
        return self.health_check()

    def optimize_detection_thresholds(
        self,
        historical_results: List[AIDetectionResult],
        target_accuracy: float = 0.9
    ) -> Dict[str, float]:
        """
        Optimize detection thresholds based on historical results.

        Args:
            historical_results: Historical detection results
            target_accuracy: Target accuracy level

        Returns:
            Dict[str, float]: Optimized thresholds
        """
        if not historical_results:
            return {
                "detection_threshold": self.detection_threshold,
                "confidence_threshold": self.confidence_threshold
            }

        # Simple optimization logic (can be enhanced with ML)
        scores = [r.score for r in historical_results]
        confidences = [r.confidence for r in historical_results]

        # Calculate optimal thresholds
        optimal_detection_threshold = sorted(scores)[int(len(scores) * (1 - target_accuracy))]
        optimal_confidence_threshold = sorted(confidences)[int(len(confidences) * (1 - target_accuracy))]

        return {
            "detection_threshold": optimal_detection_threshold,
            "confidence_threshold": optimal_confidence_threshold
        }

    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all providers.

        Returns:
            Dict[str, Dict[str, Any]]: Provider status information
        """
        return {
            name: provider.get_provider_info()
            for name, provider in self.providers.items()
        }

    def health_check(self) -> bool:
        """
        Perform health check for the AI detection optimization service.

        Returns:
            bool: True if service is healthy and has available providers
        """
        try:
            # Check if at least one provider is available
            available_providers = [p for p in self.providers.values() if p.is_available()]
            return len(available_providers) > 0
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False

    def _get_cache_key(self, content: str, providers: List[str]) -> str:
        """Generate cache key for content and providers."""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        providers_str = json.dumps(sorted(providers), sort_keys=True)
        return f"{content_hash}:{providers_str}"

    def _get_cached_result(self, cache_key: str) -> Optional[AIDetectionResult]:
        """Get cached result if available and not expired."""
        if cache_key not in self.cache:
            return None

        result = self.cache[cache_key]
        if datetime.now() - result.timestamp > self.cache_ttl:
            del self.cache[cache_key]
            return None

        return result

    def _cache_result(self, cache_key: str, result: AIDetectionResult) -> None:
        """Cache a detection result."""
        self.cache[cache_key] = result

        # Clean up old cache entries (simple LRU-like behavior)
        if len(self.cache) > self.config.settings.get("max_cache_size", 1000):
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k].timestamp)
            del self.cache[oldest_key]
