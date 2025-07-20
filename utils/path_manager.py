"""
Path management utilities for consistent file access.
"""

import os
from typing import Dict, Optional

class PathManager:
    """Unified path management for the application."""
    
    # Define path constants
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SCHEMAS_DIR = os.path.join(ROOT_DIR, "schemas", "definitions")
    COMPONENTS_DIR = os.path.join(ROOT_DIR, "components")
    CONFIG_DIR = os.path.join(ROOT_DIR, "config")
    OUTPUT_DIR = os.path.join(ROOT_DIR, "output")
    LOGS_DIR = os.path.join(ROOT_DIR, "logs")
    
    @staticmethod
    def get_schema_path(schema_name: str) -> str:
        """Get path to a schema file."""
        return os.path.join(PathManager.SCHEMAS_DIR, f"{schema_name}.yaml")
    
    @staticmethod
    def get_component_path(component_name: str) -> Optional[str]:
        """Get path to a component file."""
        # Check for Python file
        py_path = os.path.join(PathManager.COMPONENTS_DIR, f"{component_name}.py")
        if os.path.exists(py_path):
            return py_path
            
        # Check for directory with generator
        dir_path = os.path.join(PathManager.COMPONENTS_DIR, component_name)
        if os.path.isdir(dir_path):
            generator_path = os.path.join(dir_path, "generator.py")
            if os.path.exists(generator_path):
                return generator_path
                
            init_path = os.path.join(dir_path, "__init__.py")
            if os.path.exists(init_path):
                return init_path
                
        return None
    
    @staticmethod
    def get_prompt_path(component_name: str) -> Optional[str]:
        """Get path to a component's prompt file."""
        prompt_path = os.path.join(PathManager.COMPONENTS_DIR, component_name, "prompt.yaml")
        return prompt_path if os.path.exists(prompt_path) else None
    
    @staticmethod
    def get_config_path(config_name: str = "config") -> str:
        """Get path to a configuration file."""
        return os.path.join(PathManager.CONFIG_DIR, f"{config_name}.yaml")
    
    @staticmethod
    def get_output_path(filename: str) -> str:
        """Get path for an output file."""
        return os.path.join(PathManager.OUTPUT_DIR, filename)
    
    @staticmethod
    def get_log_path(log_name: str = "z-beam-generator") -> str:
        """Get path for a log file."""
        return os.path.join(PathManager.LOGS_DIR, f"{log_name}.log")
    
    @staticmethod
    def ensure_directories() -> None:
        """Ensure all required directories exist."""
        directories = [
            PathManager.SCHEMAS_DIR,
            PathManager.CONFIG_DIR,
            PathManager.OUTPUT_DIR,
            PathManager.LOGS_DIR
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)