"""
Enhanced dependency injection container for the Z-Beam system.
Provides proper lifecycle management, service registration, and resolution.
"""

from typing import Dict, Any, Type, TypeVar, Callable, Optional, Protocol
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import inspect
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ServiceLifetime(Enum):
    """Enumeration of service lifetimes."""
    TRANSIENT = "transient"      # New instance every time
    SINGLETON = "singleton"      # Single instance for the application
    SCOPED = "scoped"           # Single instance per scope


class ServiceStatus(Enum):
    """Enumeration of service statuses."""
    REGISTERED = "registered"
    RESOLVED = "resolved"
    DISPOSED = "disposed"
    ERROR = "error"


@dataclass
class ServiceDescriptor:
    """Describes how a service should be created and managed."""
    interface: Type
    implementation: Optional[Type] = None
    factory: Optional[Callable] = None
    lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT
    instance: Optional[Any] = None
    dependencies: list = field(default_factory=list)
    status: ServiceStatus = ServiceStatus.REGISTERED
    created_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None
    access_count: int = 0


class IServiceScope(Protocol):
    """Protocol for service scopes."""
    
    async def resolve(self, interface: Type[T]) -> T:
        """Resolve a service within this scope."""
        ...
    
    async def dispose(self) -> None:
        """Dispose of all scoped services."""
        ...


class ContainerError(Exception):
    """Base exception for container errors."""
    pass


class ServiceNotRegisteredException(ContainerError):
    """Raised when a service is not registered."""
    pass


class CircularDependencyException(ContainerError):
    """Raised when a circular dependency is detected."""
    pass


class ServiceScope:
    """Manages scoped service instances."""
    
    def __init__(self, container: 'ModernServiceContainer'):
        self._container = container
        self._scoped_instances: Dict[Type, Any] = {}
        self._disposed = False
    
    async def resolve(self, interface: Type[T]) -> T:
        """Resolve a service within this scope."""
        if self._disposed:
            raise ContainerError("Cannot resolve services from disposed scope")
        
        descriptor = self._container._get_descriptor(interface)
        
        if descriptor.lifetime == ServiceLifetime.SCOPED:
            if interface not in self._scoped_instances:
                instance = await self._container._create_instance(descriptor)
                self._scoped_instances[interface] = instance
            return self._scoped_instances[interface]
        
        return await self._container.resolve(interface)
    
    async def dispose(self) -> None:
        """Dispose of all scoped services."""
        if self._disposed:
            return
        
        for instance in self._scoped_instances.values():
            if hasattr(instance, 'dispose') and callable(instance.dispose):
                try:
                    if asyncio.iscoroutinefunction(instance.dispose):
                        await instance.dispose()
                    else:
                        instance.dispose()
                except Exception as e:
                    logger.warning(f"Error disposing service {type(instance).__name__}: {e}")
        
        self._scoped_instances.clear()
        self._disposed = True


class ModernServiceContainer:
    """
    Enhanced dependency injection container with lifecycle management.
    Supports transient, singleton, and scoped service lifetimes.
    """
    
    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._singleton_instances: Dict[Type, Any] = {}
        self._resolution_stack: list = []  # For circular dependency detection
        self._disposed = False
    
    def register_transient(
        self, 
        interface: Type[T], 
        implementation: Type[T] = None,
        factory: Callable[[], T] = None
    ) -> 'ModernServiceContainer':
        """Register a transient service (new instance each time)."""
        return self._register_service(interface, implementation, factory, ServiceLifetime.TRANSIENT)
    
    def register_singleton(
        self, 
        interface: Type[T], 
        implementation: Type[T] = None,
        factory: Callable[[], T] = None
    ) -> 'ModernServiceContainer':
        """Register a singleton service (single instance)."""
        return self._register_service(interface, implementation, factory, ServiceLifetime.SINGLETON)
    
    def register_scoped(
        self, 
        interface: Type[T], 
        implementation: Type[T] = None,
        factory: Callable[[], T] = None
    ) -> 'ModernServiceContainer':
        """Register a scoped service (single instance per scope)."""
        return self._register_service(interface, implementation, factory, ServiceLifetime.SCOPED)
    
    def register_instance(self, interface: Type[T], instance: T) -> 'ModernServiceContainer':
        """Register a specific instance as a singleton."""
        descriptor = ServiceDescriptor(
            interface=interface,
            instance=instance,
            lifetime=ServiceLifetime.SINGLETON,
            status=ServiceStatus.RESOLVED,
            created_at=datetime.now()
        )
        self._services[interface] = descriptor
        self._singleton_instances[interface] = instance
        return self
    
    def _register_service(
        self,
        interface: Type[T],
        implementation: Type[T] = None,
        factory: Callable[[], T] = None,
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT
    ) -> 'ModernServiceContainer':
        """Internal method to register a service."""
        if self._disposed:
            raise ContainerError("Cannot register services on disposed container")
        
        if implementation is None and factory is None:
            implementation = interface  # Self-registration
        
        if implementation and not self._is_compatible(interface, implementation):
            raise ContainerError(
                f"Implementation {implementation.__name__} is not compatible with interface {interface.__name__}"
            )
        
        # Analyze dependencies if using implementation
        dependencies = []
        if implementation and hasattr(implementation, '__init__'):
            signature = inspect.signature(implementation.__init__)
            dependencies = [
                param.annotation for name, param in signature.parameters.items()
                if name != 'self' and param.annotation != inspect.Parameter.empty
            ]
        
        descriptor = ServiceDescriptor(
            interface=interface,
            implementation=implementation,
            factory=factory,
            lifetime=lifetime,
            dependencies=dependencies
        )
        
        self._services[interface] = descriptor
        
        logger.debug(f"Registered {lifetime.value} service: {interface.__name__}")
        return self
    
    async def resolve(self, interface: Type[T]) -> T:
        """Resolve a service instance."""
        if self._disposed:
            raise ContainerError("Cannot resolve services from disposed container")
        
        descriptor = self._get_descriptor(interface)
        
        # Check for circular dependencies
        if interface in self._resolution_stack:
            raise CircularDependencyException(
                f"Circular dependency detected: {' -> '.join(cls.__name__ for cls in self._resolution_stack)} -> {interface.__name__}"
            )
        
        # Handle singleton instances
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            if interface in self._singleton_instances:
                descriptor.last_accessed = datetime.now()
                descriptor.access_count += 1
                return self._singleton_instances[interface]
        
        # Create new instance
        self._resolution_stack.append(interface)
        try:
            instance = await self._create_instance(descriptor)
            
            if descriptor.lifetime == ServiceLifetime.SINGLETON:
                self._singleton_instances[interface] = instance
                descriptor.instance = instance
                descriptor.status = ServiceStatus.RESOLVED
                descriptor.created_at = datetime.now()
            
            descriptor.last_accessed = datetime.now()
            descriptor.access_count += 1
            
            return instance
        finally:
            self._resolution_stack.pop()
    
    async def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """Create a new instance based on the service descriptor."""
        try:
            if descriptor.factory:
                # Use factory function
                if asyncio.iscoroutinefunction(descriptor.factory):
                    return await descriptor.factory()
                else:
                    return descriptor.factory()
            
            elif descriptor.implementation:
                # Use implementation class with dependency injection
                if not descriptor.dependencies:
                    # No dependencies, simple instantiation
                    return descriptor.implementation()
                
                # Resolve dependencies
                resolved_deps = []
                for dep_type in descriptor.dependencies:
                    dep_instance = await self.resolve(dep_type)
                    resolved_deps.append(dep_instance)
                
                return descriptor.implementation(*resolved_deps)
            
            else:
                raise ContainerError(f"No implementation or factory registered for {descriptor.interface.__name__}")
        
        except Exception as e:
            descriptor.status = ServiceStatus.ERROR
            logger.error(f"Error creating instance of {descriptor.interface.__name__}: {e}")
            raise ContainerError(f"Failed to create instance of {descriptor.interface.__name__}: {e}") from e
    
    def _get_descriptor(self, interface: Type) -> ServiceDescriptor:
        """Get the service descriptor for an interface."""
        if interface not in self._services:
            raise ServiceNotRegisteredException(f"No service registered for {interface.__name__}")
        return self._services[interface]
    
    def _is_compatible(self, interface: Type, implementation: Type) -> bool:
        """Check if an implementation is compatible with an interface."""
        if interface == implementation:
            return True
        
        # Check if implementation is a subclass of interface
        try:
            return issubclass(implementation, interface)
        except TypeError:
            # Handle cases where interface might be a Protocol
            # For now, assume compatibility for Protocol types
            return hasattr(interface, '_is_protocol') or True
    
    @asynccontextmanager
    async def create_scope(self):
        """Create a new service scope."""
        scope = ServiceScope(self)
        try:
            yield scope
        finally:
            await scope.dispose()
    
    def is_registered(self, interface: Type) -> bool:
        """Check if a service is registered."""
        return interface in self._services
    
    def get_service_info(self, interface: Type) -> Optional[Dict[str, Any]]:
        """Get information about a registered service."""
        if not self.is_registered(interface):
            return None
        
        descriptor = self._services[interface]
        return {
            'interface': descriptor.interface.__name__,
            'implementation': descriptor.implementation.__name__ if descriptor.implementation else None,
            'lifetime': descriptor.lifetime.value,
            'status': descriptor.status.value,
            'created_at': descriptor.created_at,
            'last_accessed': descriptor.last_accessed,
            'access_count': descriptor.access_count,
            'dependencies': [dep.__name__ for dep in descriptor.dependencies],
            'is_singleton': descriptor.lifetime == ServiceLifetime.SINGLETON,
            'has_instance': descriptor.instance is not None,
        }
    
    def get_all_services(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all registered services."""
        return {
            interface.__name__: self.get_service_info(interface)
            for interface in self._services.keys()
        }
    
    def validate_registrations(self) -> list:
        """Validate all service registrations and return any issues."""
        issues = []
        
        for interface, descriptor in self._services.items():
            # Check for missing dependencies
            for dep_type in descriptor.dependencies:
                if not self.is_registered(dep_type):
                    issues.append(f"Service {interface.__name__} depends on unregistered service {dep_type.__name__}")
        
        return issues
    
    async def dispose(self) -> None:
        """Dispose of the container and all singleton instances."""
        if self._disposed:
            return
        
        # Dispose singleton instances that support disposal
        for instance in self._singleton_instances.values():
            if hasattr(instance, 'dispose') and callable(instance.dispose):
                try:
                    if asyncio.iscoroutinefunction(instance.dispose):
                        await instance.dispose()
                    else:
                        instance.dispose()
                except Exception as e:
                    logger.warning(f"Error disposing service {type(instance).__name__}: {e}")
        
        self._services.clear()
        self._singleton_instances.clear()
        self._resolution_stack.clear()
        self._disposed = True
        
        logger.info("Service container disposed")


# Global container instance
_container: Optional[ModernServiceContainer] = None


def get_container() -> ModernServiceContainer:
    """Get the global service container."""
    global _container
    if _container is None:
        _container = ModernServiceContainer()
    return _container


def reset_container() -> None:
    """Reset the global container (useful for testing)."""
    global _container
    if _container:
        asyncio.create_task(_container.dispose())
    _container = None


async def configure_container() -> ModernServiceContainer:
    """Configure the container with default services."""
    container = get_container()
    
    # Register basic services here
    # This will be expanded in the next phases
    
    # Validate all registrations
    issues = container.validate_registrations()
    if issues:
        logger.warning(f"Container validation issues: {issues}")
    
    return container
