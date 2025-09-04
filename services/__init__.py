"""
Base service classes for the Z-Beam Generator service architecture.

This module provides the foundation for all services in the system, including:
- BaseService: Abstract base class for all services
- ServiceRegistry: Central registry for service discovery and dependency injection
- ServiceConfiguration: Configuration management for services
"""

import abc
import logging
from typing import Any, Dict, Optional, Type, TypeVar
from dataclasses import dataclass
from contextlib import contextmanager

logger = logging.getLogger(__name__)

T = TypeVar('T', bound='BaseService')


class ServiceError(Exception):
    """Base exception for service-related errors."""
    pass


class ServiceConfigurationError(ServiceError):
    """Raised when service configuration is invalid or missing."""
    pass


class ServiceInitializationError(ServiceError):
    """Raised when service initialization fails."""
    pass


@dataclass
class ServiceConfiguration:
    """Configuration container for services."""
    name: str
    version: str = "1.0.0"
    enabled: bool = True
    settings: Dict[str, Any] = None

    def __post_init__(self):
        if self.settings is None:
            self.settings = {}


class BaseService(abc.ABC):
    """
    Abstract base class for all services in the Z-Beam Generator.

    Provides common functionality for:
    - Configuration management
    - Logging
    - Health checks
    - Lifecycle management
    - Error handling
    """

    def __init__(self, config: ServiceConfiguration):
        """
        Initialize the service with configuration.

        Args:
            config: Service configuration object

        Raises:
            ServiceConfigurationError: If configuration is invalid
            ServiceInitializationError: If initialization fails
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._initialized = False
        self._healthy = False

        # Validate configuration
        self._validate_config()

        # Initialize service
        try:
            self._initialize()
            self._initialized = True
            self._healthy = True
            self.logger.info(f"Service {config.name} initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize service {config.name}: {e}")
            raise ServiceInitializationError(f"Service initialization failed: {e}") from e

    @abc.abstractmethod
    def _validate_config(self) -> None:
        """
        Validate the service configuration.

        Raises:
            ServiceConfigurationError: If configuration is invalid
        """
        pass

    @abc.abstractmethod
    def _initialize(self) -> None:
        """
        Initialize the service.

        This method should contain service-specific initialization logic.
        """
        pass

    @abc.abstractmethod
    def health_check(self) -> bool:
        """
        Perform a health check on the service.

        Returns:
            bool: True if service is healthy, False otherwise
        """
        pass

    def is_initialized(self) -> bool:
        """Check if the service is initialized."""
        return self._initialized

    def is_healthy(self) -> bool:
        """Check if the service is healthy."""
        return self._healthy

    def get_service_info(self) -> Dict[str, Any]:
        """Get information about the service."""
        return {
            "name": self.config.name,
            "version": self.config.version,
            "enabled": self.config.enabled,
            "initialized": self._initialized,
            "healthy": self._healthy,
            "class": self.__class__.__name__
        }


class ServiceRegistry:
    """
    Central registry for service discovery and dependency injection.

    Provides:
    - Service registration and discovery
    - Dependency injection
    - Service lifecycle management
    - Configuration management
    """

    _instance = None
    _services: Dict[str, BaseService] = {}
    _configurations: Dict[str, ServiceConfiguration] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'logger'):
            self.logger = logging.getLogger(f"{__name__}.ServiceRegistry")

    @classmethod
    def get_instance(cls) -> 'ServiceRegistry':
        """Get the singleton instance of the service registry."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_service(self, service: BaseService) -> None:
        """
        Register a service in the registry.

        Args:
            service: The service instance to register
        """
        service_name = service.config.name
        if service_name in self._services:
            self.logger.warning(f"Service {service_name} already registered, replacing")

        self._services[service_name] = service
        self.logger.info(f"Registered service: {service_name}")

    def get_service(self, service_name: str) -> BaseService:
        """
        Get a service by name.

        Args:
            service_name: Name of the service to retrieve

        Returns:
            BaseService: The requested service instance

        Raises:
            ServiceError: If service is not found
        """
        if service_name not in self._services:
            raise ServiceError(f"Service not found: {service_name}")

        service = self._services[service_name]
        if not service.is_healthy():
            self.logger.warning(f"Service {service_name} is not healthy")

        return service

    def get_service_typed(self, service_name: str, service_type: Type[T]) -> T:
        """
        Get a service by name with type checking.

        Args:
            service_name: Name of the service to retrieve
            service_type: Expected type of the service

        Returns:
            T: The requested service instance

        Raises:
            ServiceError: If service is not found or type doesn't match
        """
        service = self.get_service(service_name)
        if not isinstance(service, service_type):
            raise ServiceError(f"Service {service_name} is not of type {service_type.__name__}")
        return service

    def unregister_service(self, service_name: str) -> None:
        """
        Unregister a service from the registry.

        Args:
            service_name: Name of the service to unregister
        """
        if service_name in self._services:
            del self._services[service_name]
            self.logger.info(f"Unregistered service: {service_name}")
        else:
            self.logger.warning(f"Service {service_name} not found for unregistration")

    def list_services(self) -> Dict[str, Dict[str, Any]]:
        """
        List all registered services with their information.

        Returns:
            Dict[str, Dict[str, Any]]: Service information
        """
        return {
            name: service.get_service_info()
            for name, service in self._services.items()
        }

    def health_check_all(self) -> Dict[str, bool]:
        """
        Perform health checks on all registered services.

        Returns:
            Dict[str, bool]: Health status of all services
        """
        results = {}
        for name, service in self._services.items():
            try:
                results[name] = service.health_check()
            except Exception as e:
                self.logger.error(f"Health check failed for service {name}: {e}")
                results[name] = False
        return results

    @contextmanager
    def service_context(self, service_name: str):
        """
        Context manager for service usage.

        Args:
            service_name: Name of the service to use

        Yields:
            BaseService: The service instance
        """
        service = self.get_service(service_name)
        try:
            yield service
        except Exception as e:
            self.logger.error(f"Error using service {service_name}: {e}")
            raise
        finally:
            # Any cleanup logic can go here
            pass


# Global service registry instance
service_registry = ServiceRegistry.get_instance()
