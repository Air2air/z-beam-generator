"""
Service Registry for Z-Beam Optimizer

This module provides a centralized service registry for managing
all optimizer services and their dependencies.
"""

import logging
from typing import Any, Dict, Optional, Type

logger = logging.getLogger(__name__)


class ServiceRegistry:
    """Centralized service registry for managing optimizer services."""

    _instance = None

    def __init__(self):
        self._services: Dict[str, Any] = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_service(self, service: Any) -> None:
        """Register a service instance."""
        service_name = getattr(service.config, "name", service.__class__.__name__)
        self._services[service_name] = service
        logger.debug(f"Registered service: {service_name}")

    def get_service(self, name: str) -> Optional[Any]:
        """Get a service by name."""
        return self._services.get(name)

    def get_service_typed(self, name: str, service_type: Type) -> Optional[Any]:
        """Get a service by name and type."""
        service = self._services.get(name)
        if service and isinstance(service, service_type):
            return service
        return None

    def list_services(self) -> Dict[str, str]:
        """List all registered services."""
        return {
            name: service.__class__.__name__ for name, service in self._services.items()
        }

    def clear(self) -> None:
        """Clear all registered services."""
        self._services.clear()
        logger.debug("Cleared all services from registry")


# Global service registry instance
service_registry = ServiceRegistry.get_instance()
