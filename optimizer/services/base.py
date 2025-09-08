#!/usr/bin/env python3
"""
Base Service Classes for Optimizer Services
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ServiceConfiguration:
    """Configuration for a service."""

    name: str
    version: str = "1.0.0"
    enabled: bool = True
    settings: Optional[Dict[str, Any]] = None


class ServiceError(Exception):
    """Base exception for service errors."""

    pass


class ServiceConfigurationError(ServiceError):
    """Raised when service configuration is invalid."""

    pass


class BaseService(ABC):
    """Base class for all services."""

    def __init__(self, config: ServiceConfiguration):
        self.config = config
        self._initialized = False
        self._healthy = False
        self.logger = None

    def initialize(self) -> None:
        """Initialize the service."""
        if not self._initialized:
            self._validate_config()
            self._initialize()
            self._healthy = self.health_check()
            self._initialized = True

    @abstractmethod
    def _validate_config(self) -> None:
        """Validate service configuration."""
        pass

    @abstractmethod
    def _initialize(self) -> None:
        """Initialize the service implementation."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check if the service is healthy."""
        pass

    def is_initialized(self) -> bool:
        """Check if the service is initialized."""
        return self._initialized

    def is_healthy(self) -> bool:
        """Check if the service is healthy."""
        return self._healthy
