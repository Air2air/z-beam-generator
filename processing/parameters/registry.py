"""
Parameter Registry

Auto-discovers and manages all parameter modules.
Provides factory pattern for parameter creation.
"""

import importlib
import inspect
import logging
from pathlib import Path
from typing import Dict, Type, Optional, List

from processing.parameters.base import BaseParameter, ParameterCategory

logger = logging.getLogger(__name__)


class ParameterRegistry:
    """
    Central registry for all parameter modules.
    
    Auto-discovers parameters in processing/parameters/
    Provides factory methods to create parameter instances.
    """
    
    def __init__(self):
        self._parameters: Dict[str, Type[BaseParameter]] = {}
        self._discover_parameters()
    
    def _discover_parameters(self):
        """
        Auto-discover all parameter modules by scanning directories.
        """
        base_path = Path(__file__).parent
        
        # Scan subdirectories: voice/, technical/, variation/, ai_detection/
        for category_dir in ['voice', 'technical', 'variation', 'ai_detection']:
            category_path = base_path / category_dir
            if not category_path.exists():
                logger.debug(f"Category directory not found: {category_path}")
                continue
            
            # Find all .py files except __init__.py
            for py_file in category_path.glob('*.py'):
                if py_file.name == '__init__.py':
                    continue
                
                # Import module
                module_name = f'processing.parameters.{category_dir}.{py_file.stem}'
                try:
                    module = importlib.import_module(module_name)
                    
                    # Find BaseParameter subclasses
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if (issubclass(obj, BaseParameter) and 
                            obj != BaseParameter and
                            obj.__module__ == module_name):  # Only classes defined in this module
                            
                            # Register by metadata name
                            try:
                                instance = obj(5)  # Dummy instance to get metadata
                                param_name = instance.get_metadata()['name']
                                self._parameters[param_name] = obj
                                logger.debug(f"Registered parameter: {param_name} ({obj.__name__})")
                            except Exception as e:
                                logger.warning(f"Could not register {obj.__name__}: {e}")
                                
                except ImportError as e:
                    logger.warning(f"Could not import {module_name}: {e}")
                except Exception as e:
                    logger.warning(f"Error processing {module_name}: {e}")
        
        logger.info(f"Parameter registry initialized with {len(self._parameters)} parameters")
    
    def create_parameter(self, name: str, config_value: int) -> BaseParameter:
        """
        Create parameter instance by name.
        
        Args:
            name: Parameter name (e.g., 'sentence_rhythm_variation')
            config_value: Value from config.yaml
            
        Returns:
            Parameter instance
            
        Raises:
            KeyError: If parameter name not found
        """
        if name not in self._parameters:
            raise KeyError(
                f"Parameter '{name}' not registered. "
                f"Available: {list(self._parameters.keys())}"
            )
        
        return self._parameters[name](config_value)
    
    def create_all_parameters(self, config: Dict[str, int]) -> Dict[str, BaseParameter]:
        """
        Create all parameters from config dict.
        
        Args:
            config: Dict mapping parameter names to values
            
        Returns:
            Dict mapping parameter names to instances
        """
        params = {}
        for name, value in config.items():
            if name in self._parameters:
                try:
                    params[name] = self.create_parameter(name, value)
                except Exception as e:
                    logger.warning(f"Could not create parameter '{name}': {e}")
        
        return params
    
    def get_by_category(self, category: ParameterCategory) -> List[str]:
        """
        Get all parameter names in a category.
        
        Args:
            category: ParameterCategory enum
            
        Returns:
            List of parameter names
        """
        names = []
        for name, param_class in self._parameters.items():
            try:
                instance = param_class(5)  # Dummy instance
                if instance.get_metadata()['category'] == category:
                    names.append(name)
            except Exception:
                pass
        return names
    
    def get_all_names(self) -> List[str]:
        """Get all registered parameter names"""
        return list(self._parameters.keys())
    
    def validate_config(self, config: Dict[str, int]) -> Dict[str, List[str]]:
        """
        Validate config has all required parameters.
        
        Args:
            config: Config dict to validate
            
        Returns:
            Dict with 'missing' and 'extra' keys containing lists of parameter names
        """
        registered = set(self._parameters.keys())
        provided = set(config.keys())
        
        return {
            'missing': list(registered - provided),
            'extra': list(provided - registered)
        }
    
    def get_parameter_count(self) -> int:
        """Get total number of registered parameters"""
        return len(self._parameters)


# Global registry instance (singleton)
_registry = None


def get_registry() -> ParameterRegistry:
    """
    Get global parameter registry (singleton).
    
    Returns:
        ParameterRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = ParameterRegistry()
    return _registry
