#!/usr/bin/env python3
"""
Unified Error Handling for Z-Beam Optimizer

Consolidates all error types into a single, consistent system.
"""

from typing import Any, Dict, Optional


class OptimizerError(Exception):
    """
    Base exception for all optimizer-related errors.

    Provides consistent error handling across all services.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self):
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


class ConfigurationError(OptimizerError):
    """Raised when configuration is invalid or missing."""

    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(message, {"config_key": config_key} if config_key else None)


class ServiceError(OptimizerError):
    """Raised when a service operation fails."""

    def __init__(self, message: str, service_name: Optional[str] = None):
        super().__init__(message, {"service_name": service_name} if service_name else None)


class ValidationError(OptimizerError):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
        super().__init__(message, details if details else None)


class RetryableError(OptimizerError):
    """Raised for errors that could be retried."""

    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message, {"retry_after": retry_after} if retry_after else None)


class InitializationError(OptimizerError):
    """Raised when service initialization fails."""

    def __init__(self, message: str, service_name: str):
        super().__init__(message, {"service_name": service_name})


class TimeoutError(OptimizerError):
    """Raised when operations timeout."""

    def __init__(self, message: str, timeout_seconds: Optional[int] = None):
        super().__init__(message, {"timeout_seconds": timeout_seconds} if timeout_seconds else None)


class ResourceError(OptimizerError):
    """Raised when resources are unavailable."""

    def __init__(self, message: str, resource_type: Optional[str] = None):
        super().__init__(message, {"resource_type": resource_type} if resource_type else None)


# Legacy error classes for backward compatibility
ServiceConfigurationError = ConfigurationError
AIDetectionProviderError = ServiceError
