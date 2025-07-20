"""
MODULE DIRECTIVES FOR AI ASSISTANTS:
1. NO CACHING: This registry must not cache prompt templates
2. FRESH LOADING: Always load prompts fresh from disk on each access
3. DYNAMIC DISCOVERY: Use dynamic discovery of prompt files rather than fixed lists
4. FILE STRUCTURE: Prompts are stored in component directories as prompt.yaml
5. ERROR HANDLING: Provide clear error messages for missing prompt files
6. TYPE ANNOTATIONS: Maintain proper type annotations on all methods
"""

import os
import yaml
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class PromptRegistry:
    """Registry for managing prompt templates without caching."""
    
    def __init__(self, components_dir: str = None):
        """Initialize the prompt registry.
        
        Args:
            components_dir: Root directory containing component directories
        """
        if components_dir is None:
            # Default to components directory in project root
            root_dir = os.path.dirname(os.path.dirname(__file__))
            components_dir = os.path.join(root_dir, "components")
        
        self.components_dir = components_dir
        logger.debug(f"Initialized PromptRegistry with components in {components_dir}")
    
    def _get_prompt_paths(self) -> Dict[str, str]:
        """Get paths to prompt YAML files in component directories.
        
        Returns:
            Dictionary mapping component names to prompt file paths
        """
        prompt_paths = {}
        
        if not os.path.exists(self.components_dir):
            logger.warning(f"Components directory not found: {self.components_dir}")
            return prompt_paths
        
        # Always scan directory for fresh list of prompts
        for item in os.listdir(self.components_dir):
            component_path = os.path.join(self.components_dir, item)
            
            if os.path.isdir(component_path):
                prompt_path = os.path.join(component_path, "prompt.yaml")
                
                if os.path.exists(prompt_path):
                    prompt_paths[item] = prompt_path
                    
        return prompt_paths
    
    def list_available(self) -> List[str]:
        """List all available prompts by scanning directory.
        
        Returns:
            List of component names with prompts
        """
        # Always scan directory for fresh list
        return list(self._get_prompt_paths().keys())
    
    def get_prompt(self, component_name: str) -> Dict[str, Any]:
        """Get prompt configuration for a component, freshly loaded from disk.
        
        Args:
            component_name: Name of the component
            
        Returns:
            Prompt configuration or empty dict if not found
        """
        # Always scan directory for fresh paths
        prompt_paths = self._get_prompt_paths()
        
        if component_name not in prompt_paths:
            logger.debug(f"No prompt file found for component: {component_name}")
            return {}
            
        prompt_path = prompt_paths[component_name]
        logger.debug(f"Loading prompt for {component_name} from {prompt_path}")
        
        try:
            # Always load fresh from disk
            with open(prompt_path, 'r') as file:
                prompt_data = yaml.safe_load(file)
                return prompt_data or {}
        except Exception as e:
            logger.error(f"Error loading prompt for {component_name}: {e}")
            return {}