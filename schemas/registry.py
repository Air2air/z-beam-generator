"""
MODULE DIRECTIVES FOR AI ASSISTANTS:
1. NO CACHING: This registry must not cache schema data
2. FRESH LOADING: Always load schemas fresh from disk on each access
3. SCHEMA VALIDATION: Do not perform schema validation in this registry
4. EXTENSIBILITY: Support multiple schema formats (.yaml, .yml, .json)
5. ERROR HANDLING: Provide clear error messages for schema issues
6. TYPE ANNOTATIONS: Maintain proper type annotations on all methods
"""

import os
import logging
from typing import Dict, Any

from utils.base_registry import BaseRegistry

logger = logging.getLogger(__name__)

class SchemaRegistry(BaseRegistry):
    """Registry for managing and retrieving article schemas without caching."""
    
    def __init__(self, schemas_dir: str = None):
        """Initialize the schema registry.
        
        Args:
            schemas_dir: Directory containing schema YAML files
        """
        if schemas_dir is None:
            # Default to schemas directory in same directory as this file
            schemas_dir = os.path.join(os.path.dirname(__file__), "definitions")
        
        # Initialize the base registry with schema-specific settings
        super().__init__(
            resource_dir=schemas_dir,
            resource_type="schema",
            file_extensions=['.yaml', '.yml', '.json']
        )
    
    def get_schema(self, article_type: str) -> Dict[str, Any]:
        """Get schema definition for an article type, loading fresh from disk.
        
        Args:
            article_type: Type of article (material, region, etc.)
            
        Returns:
            Schema definition or empty dict if not found
        """
        # Always get fresh data from disk
        return self.get(article_type)
    
    def list_available_schemas(self) -> list:
        """List all available schema types by scanning directory contents."""
        # Always scan directory for fresh list
        return self.list_available()