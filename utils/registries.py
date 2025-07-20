"""
MODULE DIRECTIVES FOR AI ASSISTANTS:
1. NO CACHING: Registries must not cache any data between calls
2. FRESH LOADING: Always load fresh data on each access
3. SPECIFIC IMPLEMENTATIONS: Each registry implements get/list methods for its type
4. BASE REUSE: Use the Registry base class for common functionality
"""

import os
import importlib.util
import inspect
import sys
import logging
from typing import Dict, Any, List, Optional, Type

from utils.registry import Registry

logger = logging.getLogger(__name__)

# Import BaseComponent conditionally to avoid circular imports
try:
    from components.base import BaseComponent
except ImportError:
    # Create a placeholder for testing
    class BaseComponent:
        """Placeholder BaseComponent for testing."""
        pass

class SchemaRegistry(Registry):
    """Registry for schema definitions without caching."""
    
    def __init__(self, schema_dir: Optional[str] = None):
        """Initialize schema registry.
        
        Args:
            schema_dir: Directory containing schema files
        """
        if schema_dir is None:
            # Default to schemas/definitions in project
            import os.path
            root_dir = os.path.dirname(os.path.dirname(__file__))
            schema_dir = os.path.join(root_dir, "schemas", "definitions")
            
        super().__init__(
            resource_dir=schema_dir,
            resource_type="schema",
            extensions=['.yaml', '.yml', '.json']
        )
    
    def get_schema(self, article_type: str) -> Dict[str, Any]:
        """Get schema for a specific article type.
        
        Args:
            article_type: Type of article (material, region, etc.)
            
        Returns:
            Schema definition or empty dict
        """
        schema = self.get_resource(article_type)
        return schema or {}
    
    def list_schemas(self) -> List[str]:
        """List all available schemas."""
        return self.list_resources()

class ComponentRegistry(Registry):
    """Registry for components without caching."""
    
    def __init__(self, component_dir: Optional[str] = None):
        """Initialize component registry.
        
        Args:
            component_dir: Directory containing component files
        """
        if component_dir is None:
            # Default to components in project
            import os.path
            root_dir = os.path.dirname(os.path.dirname(__file__))
            component_dir = os.path.join(root_dir, "components")
            
        super().__init__(
            resource_dir=component_dir,
            resource_type="component",
            extensions=['.py'],
            loader=self._load_component_class
        )
    
    def _load_component_class(self, path: str) -> Optional[Type[BaseComponent]]:
        """Load a component class from a file.
        
        Args:
            path: Path to component file
            
        Returns:
            Component class or None if not found
        """
        try:
            # Create a unique module name to avoid caching
            unique_id = os.urandom(4).hex()
            module_name = f"component_{unique_id}"
            
            # Import the module
            spec = importlib.util.spec_from_file_location(module_name, path)
            if not spec or not spec.loader:
                return None
                
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Find component class
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BaseComponent) and 
                    obj is not BaseComponent):
                    return obj
                    
            # Clean up sys.modules
            del sys.modules[module_name]
            return None
            
        except Exception as e:
            logger.error(f"Error loading component from {path}: {e}")
            return None
    
    def get_component(self, name: str) -> Optional[Type[BaseComponent]]:
        """Get component class by name.
        
        Args:
            name: Component name
            
        Returns:
            Component class or None if not found
        """
        return self.get_resource(name)
    
    def list_components(self) -> List[str]:
        """List all available components."""
        return self.list_resources()

class PromptRegistry(Registry):
    """Registry for prompt templates without caching."""
    
    def __init__(self, component_dir: Optional[str] = None):
        """Initialize prompt registry.
        
        Args:
            component_dir: Directory containing component directories
        """
        if component_dir is None:
            # Default to components in project
            import os.path
            root_dir = os.path.dirname(os.path.dirname(__file__))
            component_dir = os.path.join(root_dir, "components")
            
        super().__init__(
            resource_dir=component_dir,
            resource_type="prompt",
            extensions=['.yaml', '.yml']
        )
    
    def _get_resource_paths(self) -> Dict[str, str]:
        """Get mapping of component names to prompt file paths.
        
        Returns:
            Dictionary mapping component names to prompt paths
        """
        prompts = {}
        
        if not os.path.exists(self.resource_dir):
            return prompts
            
        for item in os.listdir(self.resource_dir):
            component_path = os.path.join(self.resource_dir, item)
            
            if os.path.isdir(component_path) and not item.startswith('.'):
                prompt_path = os.path.join(component_path, "prompt.yaml")
                
                if os.path.exists(prompt_path):
                    prompts[item] = prompt_path
                    
        return prompts
    
    def get_prompt(self, component_name: str) -> Dict[str, Any]:
        """Get prompt template for a component.
        
        Args:
            component_name: Name of the component
            
        Returns:
            Prompt configuration or empty dict
        """
        prompt = self.get_resource(component_name)
        return prompt or {}
    
    def list_prompts(self) -> List[str]:
        """List all available prompt templates."""
        return self.list_resources()

class ConfigRegistry(Registry):
    """Registry for configuration files without caching."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize config registry.
        
        Args:
            config_dir: Directory containing configuration files
        """
        if config_dir is None:
            # Default to config in project
            import os.path
            root_dir = os.path.dirname(os.path.dirname(__file__))
            config_dir = os.path.join(root_dir, "config")
            
        super().__init__(
            resource_dir=config_dir,
            resource_type="config",
            extensions=['.yaml', '.yml', '.json']
        )
    
    def get_config(self, name: str) -> Dict[str, Any]:
        """Get configuration by name.
        
        Args:
            name: Name of the configuration
            
        Returns:
            Configuration data or empty dict
        """
        config = self.get_resource(name)
        return config or {}
    
    def list_configs(self) -> List[str]:
        """List all available configurations."""
        return self.list_resources()