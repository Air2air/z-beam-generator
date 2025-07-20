"""
MODULE DIRECTIVES FOR AI ASSISTANTS:
1. NO CACHING: This registry must not cache any resources
2. FRESH LOADING: Always load fresh data from disk on each access
3. DYNAMIC DISCOVERY: Use dynamic discovery of files rather than fixed lists
4. ERROR HANDLING: Provide clear error messages for missing resources
5. TYPE ANNOTATIONS: Maintain proper type annotations on all methods
6. EXTENSIBILITY: Registry must be extensible for different resource types
7. PATH RESOLUTION: Use relative paths when possible, absolute paths when necessary
8. NO HARDCODING: Avoid hardcoded paths or configuration values
"""

import os
import yaml
import json
import logging
from typing import Dict, Any, Optional, List, Callable

logger = logging.getLogger(__name__)

class BaseRegistry:
    """Base registry for managing resources loaded from files without caching."""
    
    def __init__(self, 
                 resource_dir: Optional[str] = None,
                 resource_type: str = "resource",
                 loader_function: Optional[Callable] = None,
                 file_extensions: List[str] = None):
        """Initialize the base registry.
        
        Args:
            resource_dir: Directory containing resource files
            resource_type: Type of resources being managed (for logging)
            loader_function: Custom function to load resources (defaults to YAML/JSON loader)
            file_extensions: List of file extensions to consider (defaults to ['.yaml', '.yml', '.json'])
        """
        self.resource_dir = resource_dir
        self.resource_type = resource_type
        self.loader_function = loader_function or self._default_loader
        self.file_extensions = file_extensions or ['.yaml', '.yml', '.json']
        
        logger.debug(f"Initialized {resource_type} registry in {resource_dir}")
    
    def _default_loader(self, file_path: str) -> Any:
        """Default loader that handles YAML and JSON files.
        
        Args:
            file_path: Path to the file to load
            
        Returns:
            Loaded resource data
        """
        try:
            with open(file_path, 'r') as file:
                if file_path.endswith(('.yaml', '.yml')):
                    return yaml.safe_load(file)
                elif file_path.endswith('.json'):
                    return json.load(file)
                else:
                    # Attempt YAML by default
                    return yaml.safe_load(file)
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}")
            return None
    
    def _get_resource_files(self) -> Dict[str, str]:
        """Get all resource files in the directory - scanned fresh each time.
        
        Returns:
            Dictionary mapping resource names to file paths
        """
        resource_files = {}
        
        if not self.resource_dir or not os.path.exists(self.resource_dir):
            logger.warning(f"{self.resource_type} directory not found: {self.resource_dir}")
            return resource_files
        
        # Always scan directory contents to get fresh list of files
        for filename in os.listdir(self.resource_dir):
            if any(filename.endswith(ext) for ext in self.file_extensions):
                file_path = os.path.join(self.resource_dir, filename)
                resource_name = os.path.splitext(filename)[0]
                resource_files[resource_name] = file_path
                
        return resource_files
    
    def list_available(self) -> List[str]:
        """List all available resources by scanning directory.
        
        Returns:
            List of resource names
        """
        # Always get fresh list of files
        return list(self._get_resource_files().keys())
    
    def get(self, name: str) -> Any:
        """Get a resource by name, loading it fresh from disk every time.
        
        Args:
            name: Name of the resource to retrieve
            
        Returns:
            Resource data or empty dict if not found
        """
        # Get fresh mapping of resources to files
        resource_files = self._get_resource_files()
        
        if name not in resource_files:
            logger.debug(f"{self.resource_type.capitalize()} not found: {name}")
            return {}
        
        file_path = resource_files[name]
        logger.debug(f"Loading {self.resource_type} from {file_path}")
        
        # Always load fresh from disk
        resource_data = self.loader_function(file_path)
        
        if resource_data is None:
            logger.warning(f"Failed to load {self.resource_type}: {name}")
            return {}
            
        return resource_data