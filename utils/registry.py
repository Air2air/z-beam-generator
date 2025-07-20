"""
MODULE DIRECTIVES FOR AI ASSISTANTS:
1. NO CACHING: Registries must not cache any data between calls
2. FRESH LOADING: Always load fresh data on each access
3. UNIFIED INTERFACE: All registries should follow the same interface pattern
4. RESOURCE TYPES: Support component, schema, prompt, and config resources
5. ERROR HANDLING: Provide clear error messages for missing resources
"""

import os
import yaml
import json
import importlib.util
import inspect
import sys
import logging
from typing import Dict, Any, List, Optional, Callable, Type

logger = logging.getLogger(__name__)

class Registry:
    """Base registry for all resource types with no caching."""
    
    def __init__(self, 
                 resource_dir: str,
                 resource_type: str,
                 extensions: List[str] = None,
                 loader: Optional[Callable] = None):
        """Initialize a registry.
        
        Args:
            resource_dir: Directory containing resources
            resource_type: Type of resources (schema, component, etc.)
            extensions: List of file extensions to consider
            loader: Custom loader function
        """
        self.resource_dir = resource_dir
        self.resource_type = resource_type
        self.extensions = extensions or ['.yaml', '.yml', '.json', '.py']
        self.loader = loader or self._default_loader
        
        # Create resource directory if it doesn't exist
        if not os.path.exists(resource_dir) and resource_type != 'component':
            os.makedirs(resource_dir)
            logger.info(f"Created {resource_type} directory: {resource_dir}")
    
    def _default_loader(self, path: str) -> Any:
        """Default loader that handles YAML and JSON files.
        
        Args:
            path: Path to resource file
            
        Returns:
            Loaded resource
        """
        try:
            if not os.path.exists(path):
                logger.warning(f"Resource not found: {path}")
                return None
                
            with open(path, 'r') as file:
                if path.endswith(('.yaml', '.yml')):
                    return yaml.safe_load(file)
                elif path.endswith('.json'):
                    return json.load(file)
                else:
                    # Try YAML as default
                    return yaml.safe_load(file)
        except Exception as e:
            logger.error(f"Error loading {path}: {e}")
            return None
    
    def _get_resource_paths(self) -> Dict[str, str]:
        """Get mapping of resource names to file paths.
        
        Returns:
            Dictionary mapping resource names to paths
        """
        resources = {}
        
        if not os.path.exists(self.resource_dir):
            return resources
            
        for item in os.listdir(self.resource_dir):
            item_path = os.path.join(self.resource_dir, item)
            
            # Skip hidden files and directories
            if item.startswith('.'):
                continue
                
            # Handle files
            if os.path.isfile(item_path) and any(item.endswith(ext) for ext in self.extensions):
                resource_name = os.path.splitext(item)[0]
                resources[resource_name] = item_path
                
            # Handle directories with generators
            elif os.path.isdir(item_path):
                generator_path = os.path.join(item_path, 'generator.py')
                prompt_path = os.path.join(item_path, 'prompt.yaml')
                
                if os.path.exists(generator_path) and self.resource_type == 'component':
                    resources[item] = generator_path
                elif os.path.exists(prompt_path) and self.resource_type == 'prompt':
                    resources[item] = prompt_path
                    
        return resources
    
    def get_resource(self, name: str) -> Any:
        """Get a specific resource by name.
        
        Args:
            name: Name of the resource
            
        Returns:
            Resource data or None if not found
        """
        paths = self._get_resource_paths()
        
        if name not in paths:
            logger.debug(f"{self.resource_type.capitalize()} not found: {name}")
            return None
            
        path = paths[name]
        return self.loader(path)
    
    def list_resources(self) -> List[str]:
        """List all available resources.
        
        Returns:
            List of resource names
        """
        return list(self._get_resource_paths().keys())