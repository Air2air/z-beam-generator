"""
Debug utility to help troubleshoot component loading issues.
"""

import logging
import importlib
import inspect
from typing import Dict, Any, Type

from components.base import BaseComponent

logger = logging.getLogger(__name__)

def debug_component_loading(component_type: str, args=None, kwargs=None) -> Dict[str, Any]:
    """Debug the component loading process.
    
    This function attempts to load a component and provides detailed logging
    about what's happening during the process.
    
    Args:
        component_type: Type of component to load (e.g., 'tags', 'content')
        args: Arguments to pass to the component constructor
        kwargs: Keyword arguments to pass to the component constructor
        
    Returns:
        Dictionary with debug information
    """
    args = args or []
    kwargs = kwargs or {}
    
    logger.info(f"DEBUG: Attempting to load component type: {component_type}")
    
    # Track debug info
    debug_info = {
        "component_type": component_type,
        "args": args,
        "kwargs": kwargs,
        "errors": [],
        "loaded_class": None,
        "instance": None,
        "component_file": None
    }
    
    try:
        # Standard component path convention
        module_name = f"components.{component_type}.generator"
        class_name = f"{component_type.capitalize()}Generator"
        
        logger.info(f"DEBUG: Trying to import {module_name} and load {class_name}")
        
        try:
            # Try importing the module
            module = importlib.import_module(module_name)
            debug_info["component_file"] = inspect.getfile(module)
            logger.info(f"DEBUG: Successfully imported module from {debug_info['component_file']}")
            
            # Try getting the class
            if hasattr(module, class_name):
                component_class = getattr(module, class_name)
                debug_info["loaded_class"] = component_class.__name__
                logger.info(f"DEBUG: Found component class: {debug_info['loaded_class']}")
                
                # Check if it's a subclass of BaseComponent
                if not issubclass(component_class, BaseComponent):
                    error_msg = f"Component class {class_name} is not a subclass of BaseComponent"
                    debug_info["errors"].append(error_msg)
                    logger.error(f"DEBUG: {error_msg}")
                
                # Try instantiating the component
                try:
                    instance = component_class(*args, **kwargs)
                    debug_info["instance"] = instance.__class__.__name__
                    logger.info(f"DEBUG: Successfully instantiated {debug_info['instance']}")
                    
                    # Check for abstract methods
                    abstract_methods = []
                    for name, method in inspect.getmembers(instance.__class__):
                        if getattr(method, "__isabstractmethod__", False):
                            abstract_methods.append(name)
                    
                    if abstract_methods:
                        error_msg = f"Component class {class_name} has abstract methods: {abstract_methods}"
                        debug_info["errors"].append(error_msg)
                        logger.error(f"DEBUG: {error_msg}")
                        
                except Exception as e:
                    error_msg = f"Error instantiating component: {str(e)}"
                    debug_info["errors"].append(error_msg)
                    logger.error(f"DEBUG: {error_msg}")
            else:
                error_msg = f"Component class {class_name} not found in module {module_name}"
                debug_info["errors"].append(error_msg)
                logger.error(f"DEBUG: {error_msg}")
                
        except ImportError as e:
            error_msg = f"Error importing module {module_name}: {str(e)}"
            debug_info["errors"].append(error_msg)
            logger.error(f"DEBUG: {error_msg}")
            
    except Exception as e:
        error_msg = f"Unexpected error during component loading: {str(e)}"
        debug_info["errors"].append(error_msg)
        logger.error(f"DEBUG: {error_msg}", exc_info=True)
        
    return debug_info