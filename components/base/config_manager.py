"""
Configuration management utilities for components.

This module provides methods for loading and managing component-specific
configuration, prompt templates, and other component resources.
"""

import os
import yaml
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ComponentConfigManager:
    """Manages component configuration loading and access."""
    
    @staticmethod
    def extract_component_name(class_name: str) -> str:
        """Extract component name from class name.
        
        Args:
            class_name: Class name to extract from (e.g., "ContentGenerator")
            
        Returns:
            Component name (e.g., "content")
        """
        component_name = class_name.lower()
        if "generator" in component_name:
            component_name = component_name.replace("generator", "")
        if "component" in component_name:
            component_name = component_name.replace("component", "")
        return component_name
    
    @staticmethod
    def get_component_config(context: Dict[str, Any], class_name: str) -> Dict[str, Any]:
        """Get component-specific configuration from context.
        
        Args:
            context: Application context dictionary
            class_name: Name of the component class
            
        Returns:
            Component configuration dictionary
        """
        if not context:
            logger.warning(f"Empty context when getting config for {class_name}")
            return {}
            
        component_name = ComponentConfigManager.extract_component_name(class_name)
        components = context.get("components", {})
        return components.get(component_name, {})
    
    @staticmethod
    def load_prompt_config(component_dir: str) -> Dict[str, Any]:
        """Load prompt configuration for a component.
        
        Args:
            component_dir: Directory name for the component
            
        Returns:
            Prompt configuration dictionary
        """
        try:
            # Build path to prompt.yaml
            prompt_file = f"components/{component_dir}/prompt.yaml"
            
            # Check if file exists
            if not os.path.exists(prompt_file):
                logger.warning(f"Prompt configuration file not found: {prompt_file}")
                return {}
            
            # Load configuration
            with open(prompt_file, "r") as f:
                config = yaml.safe_load(f)
                logger.debug(f"Loaded prompt configuration from {prompt_file}")
                return config or {}
        except Exception as e:
            logger.error(f"Error loading prompt configuration: {str(e)}")
            return {}