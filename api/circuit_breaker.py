#!/usr/bin/env python3
"""
API Circuit Breaker and Fallback System

Implements circuit breaker pattern and intelligent fallback mechanisms
to improve API connectivity robustness and prevent cascading failures.
"""

import time
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import threading

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"         # Circuit is open, failing fast
    HALF_OPEN = "half_open"  # Testing if service recovered

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior"""
    failure_threshold: int = 5  # Failures before opening circuit
    recovery_timeout: int = 60  # Seconds before attempting recovery
    expected_exception: tuple = (Exception,)  # Exceptions that count as failures
    success_threshold: int = 3  # Successes needed to close circuit in half-open state

@dataclass
class ProviderHealth:
    """Health status of an API provider"""
    name: str
    state: CircuitState
    failure_count: int
    last_failure_time: Optional[float]
    success_count: int
    total_requests: int
    avg_response_time: float

class CircuitBreaker:
    """Circuit breaker implementation for API providers"""

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self._lock = threading.RLock()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.success_count = 0

    def should_attempt_call(self) -> bool:
        """Check if call should be attempted based on circuit state"""
        with self._lock:
            if self.state == CircuitState.CLOSED:
                return True
            elif self.state == CircuitState.OPEN:
                if self._should_attempt_recovery():
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                    return True
                return False
            elif self.state == CircuitState.HALF_OPEN:
                return True
            return False

    def _should_attempt_recovery(self) -> bool:
        """Check if enough time has passed to attempt recovery"""
        if self.last_failure_time is None:
            return True
        return (time.time() - self.last_failure_time) >= self.config.recovery_timeout

    def record_success(self):
        """Record a successful call"""
        with self._lock:
            self.failure_count = 0
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    logger.info(f"Circuit breaker closed - service recovered")

    def record_failure(self, exception: Exception):
        """Record a failed call"""
        with self._lock:
            if isinstance(exception, self.config.expected_exception):
                self.failure_count += 1
                self.last_failure_time = time.time()

                if self.state == CircuitState.HALF_OPEN:
                    self.state = CircuitState.OPEN
                    logger.warning(f"Circuit breaker opened during recovery test")
                elif (self.state == CircuitState.CLOSED and
                      self.failure_count >= self.config.failure_threshold):
                    self.state = CircuitState.OPEN
                    logger.warning(f"Circuit breaker opened after {self.failure_count} failures")

class ProviderFallbackManager:
    """Manages fallback logic for API providers"""

    def __init__(self):
        self.providers: Dict[str, ProviderHealth] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.fallback_order: List[str] = []

    def register_provider(self, name: str, circuit_config: Optional[CircuitBreakerConfig] = None):
        """Register an API provider with circuit breaker"""
        if circuit_config is None:
            circuit_config = CircuitBreakerConfig()

        self.providers[name] = ProviderHealth(
            name=name,
            state=CircuitState.CLOSED,
            failure_count=0,
            last_failure_time=None,
            success_count=0,
            total_requests=0,
            avg_response_time=0.0
        )

        self.circuit_breakers[name] = CircuitBreaker(circuit_config)

        if name not in self.fallback_order:
            self.fallback_order.append(name)

    def set_fallback_order(self, order: List[str]):
        """Set the order in which providers should be tried"""
        self.fallback_order = order

    def execute_with_fallback(self, operation: Callable, *args, **kwargs):
        """
        Execute operation with automatic fallback to alternative providers

        Args:
            operation: Function that takes provider_name as first arg
            *args, **kwargs: Additional arguments for operation

        Returns:
            Result from first successful provider

        Raises:
            AllProvidersFailedError: If all providers fail
        """
        errors = []

        for provider_name in self.fallback_order:
            if provider_name not in self.providers:
                continue

            provider = self.providers[provider_name]
            circuit_breaker = self.circuit_breakers[provider_name]

            # Check if we should attempt this provider
            if not circuit_breaker.should_attempt_call():
                logger.warning(f"Skipping {provider_name} - circuit breaker is OPEN")
                continue

            try:
                logger.info(f"Attempting operation with {provider_name}")
                start_time = time.time()

                # Execute the operation
                result = operation(provider_name, *args, **kwargs)

                response_time = time.time() - start_time

                # Record success
                circuit_breaker.record_success()
                self._update_provider_stats(provider_name, success=True, response_time=response_time)

                logger.info(f"✅ Operation succeeded with {provider_name} ({response_time:.2f}s)")
                return result

            except Exception as e:
                error_msg = f"{provider_name}: {str(e)}"
                errors.append(error_msg)
                logger.warning(f"❌ Operation failed with {provider_name}: {e}")

                # Record failure
                circuit_breaker.record_failure(e)
                self._update_provider_stats(provider_name, success=False)

                continue

        # All providers failed
        error_summary = "; ".join(errors)
        raise AllProvidersFailedError(f"All providers failed: {error_summary}")

    def _update_provider_stats(self, provider_name: str, success: bool, response_time: Optional[float] = None):
        """Update provider statistics"""
        if provider_name not in self.providers:
            return

        provider = self.providers[provider_name]
        provider.total_requests += 1

        if success and response_time is not None:
            provider.success_count += 1
            # Update rolling average response time
            if provider.avg_response_time == 0:
                provider.avg_response_time = response_time
            else:
                provider.avg_response_time = (provider.avg_response_time + response_time) / 2

    def get_health_status(self) -> Dict[str, Dict[str, Any]]:
        """Get health status of all providers"""
        status = {}
        for name, provider in self.providers.items():
            circuit_breaker = self.circuit_breakers[name]
            status[name] = {
                "state": provider.state.value,
                "circuit_state": circuit_breaker.state.value,
                "failure_count": provider.failure_count,
                "success_count": provider.success_count,
                "total_requests": provider.total_requests,
                "avg_response_time": provider.avg_response_time,
                "last_failure_time": provider.last_failure_time,
            }
        return status

    def reset_provider(self, provider_name: str):
        """Reset a provider's circuit breaker and statistics"""
        if provider_name in self.circuit_breakers:
            self.circuit_breakers[provider_name] = CircuitBreaker(CircuitBreakerConfig())
            logger.info(f"Reset circuit breaker for {provider_name}")

class AllProvidersFailedError(Exception):
    """Raised when all providers in fallback chain have failed"""
    pass

# Global instance for easy access
fallback_manager = ProviderFallbackManager()

def initialize_api_fallback_system():
    """Initialize the API fallback system with current providers"""
    try:
        from run import API_PROVIDERS

        # Register all available providers
        for provider_name in API_PROVIDERS.keys():
            fallback_manager.register_provider(provider_name)

        # Set fallback order (fastest first based on typical performance)
        fallback_order = ["grok", "deepseek"]  # Grok is typically faster
        fallback_manager.set_fallback_order(fallback_order)

        logger.info(f"✅ API fallback system initialized with providers: {list(API_PROVIDERS.keys())}")

    except ImportError:
        logger.warning("Could not initialize API fallback system - run.py not available")

if __name__ == "__main__":
    # Example usage
    initialize_api_fallback_system()

    # Print current status
    status = fallback_manager.get_health_status()
    print("🔍 API Provider Health Status:")
    for provider, stats in status.items():
        print(f"  {provider}: {stats['circuit_state']} ({stats['total_requests']} requests)")
