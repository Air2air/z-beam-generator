"""
MODULE DIRECTIVES FOR AI ASSISTANTS:
1. FRONTMATTER-DRIVEN: All content must be extracted from frontmatter
2. NO HARDCODED SECTIONS: Section structure must be derived from frontmatter
3. DYNAMIC FORMATTING: Format content based on article_type from frontmatter
4. ERROR HANDLING: Raise exceptions when required frontmatter fields are missing
5. SCHEMA AWARENESS: Be aware of the schema structure for different article types
"""

import logging
from typing import Dict, Any, Type

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
        self.external_component = None  # Initialize external_component attribute
        
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
    
    def set_external_component(self, external_component: Any):
        """Set an external component for adaptation."""
        self.external_component = external_component
    
    def _call_external_component(self, adapter_data: Dict[str, Any]) -> str:
        """Call the external component with adapted data."""
        try:
            if hasattr(self.external_component, "generate"):
                # Pass adapted data to external component
                return self.external_component.generate(adapter_data)
            elif callable(self.external_component):
                # Call external component as a function
                return self.external_component(adapter_data)
            else:
                raise ValueError("External component has no generate method or is not callable")
        except Exception as e:
            logger.error(f"Error calling external component: {str(e)}")
            raise
    
    def _post_process(self, content: str) -> str:
        """Post-process content from external component."""
        if not content:
            return ""
            
        # Apply any necessary transformations to external component output
        # This could involve formatting fixes, adding headers, etc.
        
        return content