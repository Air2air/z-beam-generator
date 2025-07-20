import os
import yaml
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SchemaRegistry:
    """Registry for managing and retrieving article schemas."""
    
    def __init__(self, schemas_dir: str = None):
        """Initialize the schema registry.
        
        Args:
            schemas_dir: Directory containing schema YAML files
        """
        if schemas_dir is None:
            # Default to schemas directory in same directory as this file
            schemas_dir = os.path.join(os.path.dirname(__file__), "definitions")
        
        self.schemas_dir = schemas_dir
        self.schemas = self._load_schemas()
        
    def _load_schemas(self) -> Dict[str, Any]:
        """Load all schema definitions from YAML files."""
        schemas = {}
        
        if not os.path.exists(self.schemas_dir):
            logger.warning(f"Schemas directory not found: {self.schemas_dir}")
            return schemas
        
        for filename in os.listdir(self.schemas_dir):
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                schema_path = os.path.join(self.schemas_dir, filename)
                schema_type = os.path.splitext(filename)[0]
                
                try:
                    with open(schema_path, 'r') as file:
                        schema_def = yaml.safe_load(file)
                        schemas[schema_type] = schema_def
                        logger.debug(f"Loaded schema: {schema_type}")
                except Exception as e:
                    logger.error(f"Error loading schema {schema_path}: {e}")
        
        return schemas
    
    def get_schema(self, article_type: str) -> Dict[str, Any]:
        """Get schema definition for an article type.
        
        Args:
            article_type: Type of article (material, region, etc.)
            
        Returns:
            Schema definition or empty dict if not found
        """
        return self.schemas.get(article_type, {})
    
    def list_available_schemas(self) -> list:
        """List all available schema types."""
        return list(self.schemas.keys())