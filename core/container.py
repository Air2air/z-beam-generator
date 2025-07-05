"""
Dependency injection container for the Z-Beam generator.
Manages service registration and resolution.
"""

from typing import Dict, Any, Type, TypeVar, Callable, Optional
from generator.core.exceptions import ConfigurationError, ErrorContext

T = TypeVar("T")


class ServiceContainer:
    """Simple dependency injection container."""

    def __init__(self):
        self._services: Dict[str, Type] = {}
        self._singletons: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}

    def register_singleton(self, interface: Type[T], implementation: Type[T]) -> None:
        """Register a singleton service implementation."""
        if not issubclass(implementation, interface):
            raise ConfigurationError(
                f"Implementation {implementation.__name__} does not implement {interface.__name__}",
                ErrorContext("service_registration", "container"),
            )
        self._services[interface.__name__] = implementation

    def register_factory(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """Register a factory function for a service."""
        self._factories[interface.__name__] = factory

    def get(self, interface: Type[T]) -> T:
        """Get a service instance."""
        interface_name = interface.__name__

        # Check if already instantiated as singleton
        if interface_name in self._singletons:
            return self._singletons[interface_name]

        # Check for factory
        if interface_name in self._factories:
            instance = self._factories[interface_name]()
            self._singletons[interface_name] = instance
            return instance

        # Check for registered class
        if interface_name in self._services:
            impl_class = self._services[interface_name]
            instance = impl_class()
            self._singletons[interface_name] = instance
            return instance

        raise ConfigurationError(
            f"No implementation registered for {interface_name}",
            ErrorContext("service_resolution", "container"),
        )

    def clear(self) -> None:
        """Clear all services (useful for testing)."""
        self._services.clear()
        self._singletons.clear()
        self._factories.clear()

    def is_registered(self, interface: Type) -> bool:
        """Check if a service is registered."""
        interface_name = interface.__name__
        return interface_name in self._services or interface_name in self._factories


# Global container instance
_container: Optional[ServiceContainer] = None


def get_container() -> ServiceContainer:
    """Get the global service container."""
    global _container
    if _container is None:
        _container = ServiceContainer()
    return _container


def configure_services(container: ServiceContainer) -> None:
    """Configure all services in the container."""
    # This will be called during application startup
    # Services will be registered here
    pass
