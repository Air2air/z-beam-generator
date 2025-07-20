"""
Component adapter for consistent handling of all generator components.
"""

import logging
from typing import Dict, Any, Optional, Type

from components.base import BaseComponent

logger = logging.getLogger(__name__)

class ComponentAdapter(BaseComponent):
    """Adapts various component implementations to the BaseComponent interface."""
    
    def __init__(self, component_name: str, handler_class: Type, 
                 context: Dict[str, Any], schema: Dict[str, Any], 
                 ai_provider: str, previous_outputs: Dict[str, Any] = None):
        """Initialize component adapter."""
        super().__init__(context, schema, ai_provider)
        self.component_name = component_name
        self.previous_outputs = previous_outputs or {}
        
        try:
            # Initialize the actual handler
            self.handler = handler_class(context, schema, ai_provider)
            
            # Pass previous outputs to the handler
            self.handler.set_previous_outputs(self.previous_outputs)
            
            # Extract frontmatter and set it
            frontmatter_data = self.extract_frontmatter_data()
            if frontmatter_data:
                self.handler.set_frontmatter(frontmatter_data)
                
        except Exception as e:
            logger.error(f"Error initializing handler for {component_name}: {e}")
            self.handler = None
    
    def generate(self) -> str:
        """Generate content using the handler."""
        if not hasattr(self, "handler") or not self.handler:
            return f"<!-- Failed to initialize {self.component_name} component -->"
        
        try:
            return self.handler.generate()
        except Exception as e:
            logger.error(f"Error generating content for {self.component_name}: {e}")
            return f"<!-- Error generating {self.component_name}: {str(e)} -->"