"""
Component registry for dynamic component discovery and instantiation.

MODULE DIRECTIVES FOR AI ASSISTANTS:
1. NO CACHING: This registry must not cache component classes
2. FRESH LOADING: Always load components fresh on each access
3. DYNAMIC DISCOVERY: Use dynamic discovery of components rather than fixed lists
4. MODULE ISOLATION: Load each component in isolation to prevent cross-contamination
5. ERROR HANDLING: Provide clear error messages for component loading issues
6. TYPE ANNOTATIONS: Maintain proper type annotations on all methods
"""

import os
import sys
import importlib.util
import inspect
import logging
from typing import Dict, Any, Type, List, Optional

logger = logging.getLogger(__name__)

# Import base component class in a way that doesn't fail tests when run in isolation
try:
    from components.base import BaseComponent
except ImportError:
    # Create a placeholder for testing
    class BaseComponent:
        """Placeholder BaseComponent for testing."""
        pass

class ComponentRegistry:
    """Registry for managing and retrieving components without caching."""
    
    def __init__(self, components_dir: str = None):
        """Initialize the component registry.
        
        Args:
            components_dir: Directory containing component modules
        """
        if components_dir is None:
            # Default to components directory
            components_dir = os.path.dirname(__file__)
        
        self.components_dir = components_dir
        logger.debug(f"Initialized ComponentRegistry in {components_dir}")
    
    def _discover_component_paths(self) -> Dict[str, str]:
        """Discover component module paths by scanning directory.
        
        Returns:
            Dictionary mapping component names to their file paths
        """
        component_paths = {}
        
        # Always scan directory for fresh list of components
        if not os.path.exists(self.components_dir):
            logger.warning(f"Components directory not found: {self.components_dir}")
            return component_paths
            
        # Get all Python files and directories in the components directory
        for item in os.listdir(self.components_dir):
            component_path = os.path.join(self.components_dir, item)
            
            # Skip special files and directories
            if item.startswith('__') or item == 'base.py' or item == 'registry.py':
                continue
                
            if item.endswith('.py'):
                # Python file component
                module_name = item[:-3]  # Remove .py
                component_paths[module_name] = component_path
            
            elif os.path.isdir(component_path):
                # Directory component
                init_path = os.path.join(component_path, '__init__.py')
                generator_path = os.path.join(component_path, 'generator.py')
                
                # Try generator.py first, then __init__.py
                if os.path.exists(generator_path):
                    component_paths[item] = generator_path
                elif os.path.exists(init_path):
                    component_paths[item] = init_path
        
        return component_paths
    
    def _load_component(self, component_name: str, file_path: str) -> Optional[Type[BaseComponent]]:
        """Load a component class from file without caching.
        
        Args:
            component_name: Name of the component
            file_path: Path to the component file
            
        Returns:
            Component class or None if not found
        """
        try:
            # Use a unique module name to avoid Python's module cache
            unique_id = os.urandom(8).hex()
            module_name = f"{component_name}_{unique_id}"
            
            # Import the module using importlib.util to avoid caching
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if not spec or not spec.loader:
                logger.warning(f"Could not load spec for {component_name} from {file_path}")
                return None
                
            module = importlib.util.module_from_spec(spec)
            # Add module to sys.modules temporarily for imports within the module to work
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Find the component class in the module
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BaseComponent) and 
                    obj is not BaseComponent):
                    return obj
            
            # Clean up sys.modules to avoid memory leaks
            del sys.modules[module_name]
            
            logger.warning(f"No component class found in {component_name} at {file_path}")
            return None
            
        except Exception as e:
            logger.error(f"Error importing component {component_name} from {file_path}: {e}")
            return None
    
    def get_component(self, component_name: str) -> Optional[Type[BaseComponent]]:
        """Get a component class by name, freshly loaded from disk.
        
        Args:
            component_name: Name of the component
            
        Returns:
            Component class or None if not found
        """
        # Always scan for components to get fresh paths
        component_paths = self._discover_component_paths()
        
        if component_name not in component_paths:
            logger.warning(f"Component not found: {component_name}")
            return None
        
        file_path = component_paths[component_name]
        logger.debug(f"Loading component {component_name} from {file_path}")
        
        # Load the component fresh from disk
        return self._load_component(component_name, file_path)
    
    def list_available_components(self) -> List[str]:
        """List all available components by scanning directory.
        
        Returns:
            List of component names
        """
        # Always scan directory for fresh list
        return list(self._discover_component_paths().keys())