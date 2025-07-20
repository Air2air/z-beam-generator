"""
Configuration management utilities with standard approaches.
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ConfigManager:
    """Unified configuration management without caching."""
    
    DEFAULT_CONFIG = {
        "assembly": {
            "component_order": [
                "frontmatter", 
                "content", 
                "bullets", 
                "table", 
                "tags", 
                "jsonld"
            ]
        },
        "output": {
            "directory": "output"
        },
        "components": {}
    }
    
    @staticmethod
    def ensure_directories() -> None:
        """Ensure required directories exist."""
        directories = ['config', 'output', 'logs']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @staticmethod
    def load_config(config_name: str = "config") -> Dict[str, Any]:
        """Load configuration from file or create default.
        
        Args:
            config_name: Name of the configuration file (without extension)
            
        Returns:
            Configuration dictionary
        """
        config_path = os.path.join('config', f'{config_name}.yaml')
        
        # Create default config if it doesn't exist
        if not os.path.exists(config_path):
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w') as f:
                yaml.dump(ConfigManager.DEFAULT_CONFIG, f)
            
            logger.info(f"Created default configuration at {config_path}")
            return ConfigManager.DEFAULT_CONFIG.copy()
        
        # Load existing config
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f) or {}
                
            # Ensure required sections exist
            for key, value in ConfigManager.DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
                    
            return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return ConfigManager.DEFAULT_CONFIG.copy()
    
    @staticmethod
    def save_config(config: Dict[str, Any], config_name: str = "config") -> bool:
        """Save configuration to file.
        
        Args:
            config: Configuration dictionary
            config_name: Name of the configuration file (without extension)
            
        Returns:
            True if successful, False otherwise
        """
        config_path = os.path.join('config', f'{config_name}.yaml')
        
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w') as f:
                yaml.dump(config, f)
                
            logger.info(f"Saved configuration to {config_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False