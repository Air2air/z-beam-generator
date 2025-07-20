"""
MODULE DIRECTIVES FOR AI ASSISTANTS:
1. NO CACHING: This module must not cache any registry instances
2. FRESH LOADING: Always create fresh registry instances
3. REGISTRY TYPES: Support schema, component, config, and prompt registries
4. ERROR HANDLING: Provide clear error messages for registry loading issues
5. TYPE ANNOTATIONS: Maintain proper type annotations on all methods
"""

import logging
from typing import Any, Dict, List, Type, Optional

logger = logging.getLogger(__name__)

class RegistryLoader:
    """Universal loader for all registry types without caching."""
    
    @staticmethod
    def get_schema_registry() -> Any:
        """Get a fresh SchemaRegistry instance.
        
        Returns:
            SchemaRegistry instance
        """
        try:
            # Dynamic import to avoid module-level caching
            from schemas.registry import SchemaRegistry
            return SchemaRegistry()
        except ImportError as e:
            logger.error(f"Failed to import SchemaRegistry: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating SchemaRegistry: {e}")
            return None
    
    @staticmethod
    def get_component_registry() -> Any:
        """Get a fresh ComponentRegistry instance.
        
        Returns:
            ComponentRegistry instance
        """
        try:
            # Dynamic import to avoid module-level caching
            from components.registry import ComponentRegistry
            return ComponentRegistry()
        except ImportError as e:
            logger.error(f"Failed to import ComponentRegistry: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating ComponentRegistry: {e}")
            return None
    
    @staticmethod
    def get_config_registry() -> Any:
        """Get a fresh ConfigRegistry instance.
        
        Returns:
            ConfigRegistry instance
        """
        try:
            # Dynamic import to avoid module-level caching
            from utils.config_registry import ConfigRegistry
            return ConfigRegistry()
        except ImportError as e:
            logger.error(f"Failed to import ConfigRegistry: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating ConfigRegistry: {e}")
            return None
    
    @staticmethod
    def get_prompt_registry() -> Any:
        """Get a fresh PromptRegistry instance.
        
        Returns:
            PromptRegistry instance
        """
        try:
            # Dynamic import to avoid module-level caching
            from utils.prompt_registry import PromptRegistry
            return PromptRegistry()
        except ImportError as e:
            logger.error(f"Failed to import PromptRegistry: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating PromptRegistry: {e}")
            return None