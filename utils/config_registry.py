import os
import logging
from typing import Dict, Any

from utils.base_registry import BaseRegistry

logger = logging.getLogger(__name__)

class ConfigRegistry(BaseRegistry):
    """Registry for managing configuration files without caching."""
    
    def __init__(self, config_dir: str = None):
        """Initialize the configuration registry.
        
        Args:
            config_dir: Directory containing configuration files
        """
        if config_dir is None:
            # Default to config directory in project root
            root_dir = os.path.dirname(os.path.dirname(__file__))
            config_dir = os.path.join(root_dir, "config")
            
            # Create config directory if it doesn't exist
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
                logger.info(f"Created configuration directory: {config_dir}")
        
        super().__init__(
            resource_dir=config_dir,
            resource_type="configuration",
            file_extensions=['.yaml', '.yml', '.json']
        )
    
    def get_config(self, name: str) -> Dict[str, Any]:
        """Get configuration by name, always freshly loaded from disk.
        
        Args:
            name: Name of the configuration
            
        Returns:
            Configuration data or empty dict if not found
        """
        return self.get(name)