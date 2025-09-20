#!/usr/bin/env python3
"""
Simplified Service Architecture for Z-Beam Optimizer

Consolidated service pattern that reduces complexity while maintaining functionality.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from .config_unified import get_config, UnifiedConfig, ServiceConfiguration
from .errors import ConfigurationError

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Status of a service."""
    INITIALIZED = "initialized"
    HEALTHY = "healthy"
    PROCESSING = "processing"
    ERROR = "error"
    DISABLED = "disabled"
    UNKNOWN = "unknown"

    def __str__(self):
        return self.value


@dataclass
class ServiceResult:
    """Result from a service operation."""
    success: bool = False
    message: str = ""
    status: ServiceStatus = ServiceStatus.UNKNOWN
    data: Optional[Dict[str, Any]] = None
    error: Optional[Exception] = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}


class SimplifiedService(ABC):
    """
    Simplified service base class that consolidates functionality.

    This replaces the complex 3-layer service architecture with a clean 2-layer approach.
    """

    def __init__(self, config: Optional[ServiceConfiguration] = None):
        if config is None:
            raise ConfigurationError("Service configuration is required")
        self.config = config
        if not self.config.enabled:
            self.status = ServiceStatus.DISABLED
        else:
            self.status = ServiceStatus.INITIALIZED
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._initialized = False

    def _get_default_config(self) -> ServiceConfiguration:
        """Get default configuration for this service."""
        return ServiceConfiguration(
            name=self.__class__.__name__,
            version="1.0.0",
            enabled=True,
            settings={}
        )

    async def initialize(self) -> None:
        """Initialize the service."""
        if self._initialized:
            return

        try:
            await self._initialize_service()
            self._initialized = True
            self.logger.info(f"Service {self.config.name} initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize service {self.config.name}: {e}")
            raise

    @abstractmethod
    async def _initialize_service(self) -> None:
        """Service-specific initialization logic."""
        pass

    def health_check(self) -> ServiceResult:
        """Perform health check."""
        if not self.config.enabled:
            return ServiceResult(
                success=False,
                message="Service is disabled",
                status=ServiceStatus.DISABLED,
                data={'healthy': False}
            )

        try:
            # For testing purposes, we'll make this synchronous
            # In a real implementation, this would be async
            import asyncio
            if asyncio.iscoroutinefunction(self._check_health):
                # If _check_health is async, we need to handle it
                async def run_check():
                    result = await self._check_health()
                    return result
                result = asyncio.run(run_check())
            else:
                result = self._check_health()

            status = ServiceStatus.HEALTHY if result.get('healthy', True) else ServiceStatus.ERROR
            return ServiceResult(
                success=result.get('healthy', True),
                message=result.get('status', 'Health check completed'),
                status=status,
                data=result
            )
        except Exception as e:
            self.logger.error(f"Health check failed for {self.config.name}: {e}")
            return ServiceResult(
                success=False,
                message=f"Health check failed: {str(e)}",
                status=ServiceStatus.ERROR,
                data={'error': str(e), 'healthy': False}
            )

    @abstractmethod
    def _check_health(self) -> Dict[str, Any]:
        """Service-specific health check logic."""
        pass

    def is_enabled(self) -> bool:
        """Check if service is enabled."""
        return self.config.enabled

    def get_setting(self, key: str, default=None) -> Any:
        """Get a configuration setting."""
        return self.config.get_setting(key, default)

    def set_setting(self, key: str, value: Any) -> None:
        """Set a configuration setting."""
        self.config.set_setting(key, value)
