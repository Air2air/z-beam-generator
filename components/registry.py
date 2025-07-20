"""
Component registry for dynamic component discovery and instantiation.

MODULE DIRECTIVES FOR AI ASSISTANTS:
1. DYNAMIC DISCOVERY: Component loading must be fully dynamic
2. NO HARDCODED MAPPINGS: Avoid hardcoded component class mappings
3. ROBUST IMPORTING: Handle import edge cases but don't use placeholder implementations
4. TYPE SAFETY: Ensure all loaded components inherit from BaseComponent
5. CONSISTENT NAMING: Follow component naming conventions for discovery
"""

import logging
import importlib
import inspect
import os
import sys
from typing import Dict, Any, Type, Optional
from pathlib import Path

# Ensure parent directory is in path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from components.base import BaseComponent

logger = logging.getLogger(__name__)

class ComponentRegistry:
    """
    Registry for component discovery and instantiation.
    """
    
    def __init__(self, debug_mode=False):
        """Initialize component registry."""
        self.components = {}
        self.debug_mode = debug_mode
        
        if self.debug_mode:
            logger.setLevel(logging.DEBUG)
        
        # Try using sys.path to help with imports
        self._ensure_paths_in_sys()
        
        self._load_default_components()
        self._discover_components()
        
        if self.debug_mode:
            logger.debug(f"Registered components: {self.list_components()}")
    
    def _ensure_paths_in_sys(self):
        """Ensure all necessary paths are in sys.path."""
        # Add project root to path
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
            logger.debug(f"Added project root to sys.path: {project_root}")
        
        # Add components directory to path
        components_dir = os.path.dirname(os.path.abspath(__file__))
        if components_dir not in sys.path:
            sys.path.insert(0, components_dir)
            logger.debug(f"Added components directory to sys.path: {components_dir}")
    
    def _load_default_components(self):
        """Load default components from the mapping."""
        logger.debug("Loading default components...")
        # No hardcoded mappings - this is just a placeholder to demonstrate the structure
        default_components = {
            "frontmatter": "components.frontmatter.generator.FrontmatterGenerator",
            "content": "components.content.generator.ContentGenerator",
            "table": "components.table.generator.TableGenerator",
            "tags": "components.tags.generator.TagsGenerator",
            "jsonld": "components.jsonld.generator.JsonLdGenerator",
            "bullets": "components.bullets.BulletsComponent",
        }
        
        for name, class_path in default_components.items():
            try:
                module_path, class_name = class_path.rsplit('.', 1)
                logger.debug(f"Attempting to load component '{name}' from {module_path}.{class_name}")
                
                # Special handling for frontmatter to avoid import issues
                if name == "frontmatter":
                    self._load_frontmatter_component()
                    continue
                
                component_class = self._load_component_class(module_path, class_name)
                if component_class:
                    self.register_component(name, component_class)
                    logger.debug(f"Successfully registered '{name}'")
                else:
                    logger.warning(f"Failed to load component '{name}': class not found or invalid")
            except Exception as e:
                logger.warning(f"Failed to load default component '{name}': {e}")
                if self.debug_mode:
                    import traceback
                    logger.debug(traceback.format_exc())
    
    def _load_frontmatter_component(self):
        """Special handling for loading the frontmatter component."""
        try:
            # Try direct import first (simpler approach without importlib.util)
            frontmatter_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontmatter')
            generator_path = os.path.join(frontmatter_dir, 'generator.py')
            
            if not os.path.exists(generator_path):
                logger.warning(f"Frontmatter generator file not found at {generator_path}")
                return
                
            logger.debug(f"Loading frontmatter component directly from {frontmatter_dir}")
            
            # Add frontmatter directory to path temporarily
            sys.path.insert(0, os.path.dirname(frontmatter_dir))
            
            try:
                # Try to import directly
                from components.frontmatter.generator import FrontmatterGenerator
                self.register_component('frontmatter', FrontmatterGenerator)
                logger.debug("Successfully registered 'frontmatter' using direct import")
            except ImportError as e:
                logger.debug(f"Direct import failed: {e}, trying alternative approach")
                
                # Fallback to manual module loading
                module_name = "frontmatter_generator"
                with open(generator_path, 'r') as file:
                    code = file.read()
                
                # Create module namespace
                module_namespace = {}
                
                # Execute the code in this namespace
                try:
                    exec(code, module_namespace)
                    if 'FrontmatterGenerator' in module_namespace:
                        component_class = module_namespace['FrontmatterGenerator']
                        # Check if it's a valid component class
                        if inspect.isclass(component_class) and issubclass(component_class, BaseComponent):
                            self.register_component('frontmatter', component_class)
                            logger.debug("Successfully registered 'frontmatter' using exec approach")
                        else:
                            logger.warning("FrontmatterGenerator is not a valid component class")
                    else:
                        logger.warning("FrontmatterGenerator class not found in module")
                except Exception as inner_e:
                    logger.warning(f"Failed to execute frontmatter module: {inner_e}")
            finally:
                # Remove the temporary path
                if frontmatter_dir in sys.path:
                    sys.path.remove(frontmatter_dir)
                
        except Exception as e:
            logger.warning(f"Failed to load frontmatter component: {e}")
            if self.debug_mode:
                import traceback
                logger.debug(traceback.format_exc())
    
    def _discover_components(self):
        """Discover components by scanning directories with improved import handling."""
        logger.debug("Discovering components...")
        # Get the components directory
        components_dir = Path(__file__).parent
        
        # Scan directories for component files
        for item in components_dir.iterdir():
            if item.is_dir() and not item.name.startswith('__'):
                logger.debug(f"Checking directory: {item.name}")
                
                # Check for generator.py
                generator_path = item / "generator.py"
                if generator_path.exists():
                    logger.debug(f"Found generator.py in {item.name}")
                    
                    # Skip frontmatter as it's handled separately
                    if item.name == 'frontmatter':
                        continue
                        
                    # Try to import the component with absolute path to avoid import issues
                    module_name = f"components.{item.name}.generator"
                    
                    # Handle special cases for class naming conventions
                    if item.name == 'jsonld':
                        class_name = "JsonLdGenerator"  # With capital 'L'
                    else:
                        class_name = f"{item.name.capitalize()}Generator"
                    
                    try:
                        # First try direct file loading if module import fails
                        component_class = None
                        try:
                            component_class = self._load_component_class(module_name, class_name)
                        except ImportError:
                            # Fall back to direct file loading
                            component_class = self._load_component_from_file(generator_path, class_name)
                        
                        if component_class and item.name not in self.components:
                            self.register_component(item.name, component_class)
                            logger.debug(f"Discovered and registered '{item.name}'")
                    except Exception as e:
                        logger.warning(f"Failed to load discovered component '{item.name}': {e}")
                        if self.debug_mode:
                            import traceback
                            logger.debug(traceback.format_exc())
    
    def _load_component_class(self, module_path: str, class_name: str) -> Optional[Type[BaseComponent]]:
        """
        Load a component class from a module path and class name.
        
        Args:
            module_path: Path to the module (e.g., "components.content.generator")
            class_name: Name of the class to load (e.g., "ContentGenerator")
            
        Returns:
            Component class or None if not found or not a BaseComponent
        """
        try:
            logger.debug(f"Importing module: {module_path}")
            module = importlib.import_module(module_path)
            logger.debug(f"Looking for class: {class_name}")
            
            if not hasattr(module, class_name):
                logger.warning(f"Class {class_name} not found in {module_path}")
                # List available classes in module
                if self.debug_mode:
                    classes = [name for name, obj in inspect.getmembers(module, inspect.isclass)]
                    logger.debug(f"Available classes in {module_path}: {classes}")
                return None
            
            component_class = getattr(module, class_name)
            
            # Verify it's a subclass of BaseComponent
            if not inspect.isclass(component_class):
                logger.warning(f"{class_name} in {module_path} is not a class")
                return None
                
            if not issubclass(component_class, BaseComponent):
                logger.warning(f"{class_name} in {module_path} is not a subclass of BaseComponent")
                return None
                
            logger.debug(f"Successfully loaded {class_name} from {module_path}")
            return component_class
            
        except ImportError as e:
            logger.warning(f"Could not import {module_path}: {e}")
            return None
        except AttributeError as e:
            logger.warning(f"Could not get {class_name} from {module_path}: {e}")
            return None
        except Exception as e:
            logger.warning(f"Unexpected error loading {class_name} from {module_path}: {e}")
            if self.debug_mode:
                import traceback
                logger.debug(traceback.format_exc())
            return None
    
    def _load_component_from_file(self, file_path, class_name):
        """Load a component class directly from a file path."""
        try:
            logger.debug(f"Loading component directly from {file_path}")
            
            # Try standard import first
            module_path = f"components.{os.path.basename(os.path.dirname(file_path))}.{os.path.basename(file_path).replace('.py', '')}"
            try:
                module = importlib.import_module(module_path)
            except ImportError:
                # If standard import fails, use exec approach (avoid importlib.util)
                with open(file_path, 'r') as file:
                    code = file.read()
                
                # Create module namespace
                module_namespace = {}
                
                # Execute the code in this namespace
                exec(code, module_namespace)
                
                # Create a simple module-like object
                class SimpleModule:
                    pass
                
                module = SimpleModule()
                
                # Transfer all items to the module
                for key, value in module_namespace.items():
                    setattr(module, key, value)
            
            # Get the component class
            if hasattr(module, class_name):
                component_class = getattr(module, class_name)
                if inspect.isclass(component_class) and issubclass(component_class, BaseComponent):
                    logger.debug(f"Successfully loaded {class_name} from file {file_path}")
                    return component_class
                else:
                    logger.warning(f"{class_name} in {file_path} is not a valid component class")
            else:
                logger.warning(f"{class_name} class not found in {file_path}")
                # List available classes
                if self.debug_mode:
                    if isinstance(module, SimpleModule):
                        classes = [name for name in dir(module) if inspect.isclass(getattr(module, name))]
                    else:
                        classes = [name for name, obj in inspect.getmembers(module, inspect.isclass)]
                    logger.debug(f"Available classes in {file_path}: {classes}")
            
            return None
        except Exception as e:
            logger.warning(f"Failed to load component from file {file_path}: {e}")
            if self.debug_mode:
                import traceback
                logger.debug(traceback.format_exc())
            return None
    
    def register_component(self, name: str, component_class: Type[BaseComponent]):
        """
        Register a component with the registry.
        
        Args:
            name: Name of the component
            component_class: Component class
        """
        self.components[name] = component_class
        logger.debug(f"Registered component '{name}': {component_class.__name__}")
    
    def get_component_class(self, name: str) -> Optional[Type[BaseComponent]]:
        """
        Get a component class by name.
        
        Args:
            name: Name of the component
            
        Returns:
            Component class or None if not found
        """
        component_class = self.components.get(name)
        if component_class is None:
            logger.warning(f"Component '{name}' not found in registry")
            if self.debug_mode:
                logger.debug(f"Available components: {list(self.components.keys())}")
        return component_class
    
    def list_components(self) -> Dict[str, str]:
        """
        List all registered components.
        
        Returns:
            Dictionary of component name to class name
        """
        return {name: component_class.__name__ for name, component_class in self.components.items()}