# Create a new file: assembly/component_adapter.py
"""Component adapter to bridge legacy components with the assembler architecture."""

import logging
from typing import Dict, Any, Optional
from components import BaseComponent
from utils.frontmatter_utils import extract_frontmatter

from components.base import BaseComponent
logger = logging.getLogger(__name__)

class ComponentAdapter(BaseComponent):
    """Adapts existing component handlers to BaseComponent interface."""
    
    def __init__(self, component_name: str, handler_class: Any, context: Dict[str, Any], 
                 component_config: Dict[str, Any], previous_outputs: Dict[str, Any]):
        """Initialize adapter with component handler and context."""
        super().__init__(context, component_config, previous_outputs)
        self.component_name = component_name
        
        # Extract frontmatter data for components that need it
        self.frontmatter_data = self._parse_frontmatter(previous_outputs)
        
        # Initialize the appropriate handler
        self.handler = self._init_handler(handler_class, context)
    
    def _parse_frontmatter(self, previous_outputs: Dict[str, Any]) -> Dict[str, Any]:
        """Parse frontmatter from previous outputs."""
        if "frontmatter" not in previous_outputs:
            return {}
        
        return BaseComponent.extract_frontmatter(previous_outputs["frontmatter"])
    
    def _init_handler(self, handler_class: Any, context: Dict[str, Any]) -> Any:
        """Initialize the appropriate handler based on component type."""
        try:
            if self.component_name == "frontmatter":
                return handler_class(
                    context, 
                    context.get("schema", {}), 
                    context.get("ai_provider")
                )
                
            elif self.component_name == "content":
                handler = handler_class(
                    context, 
                    context.get("schema", {}), 
                    context.get("ai_provider")
                )
                
                # Pass frontmatter data consistently to content generator
                if self.frontmatter_data:
                    if hasattr(handler, "set_frontmatter"):
                        handler.set_frontmatter(self.frontmatter_data)
                    if hasattr(handler, "set_frontmatter_data"):
                        handler.set_frontmatter_data(self.frontmatter_data)
                return handler
                
            elif self.component_name == "table":
                return handler_class(
                    context=context,
                    schema=context.get("schema", {}),
                    frontmatter_dict=self.frontmatter_data
                )
                
            elif self.component_name == "tags":
                return handler_class(
                    context, 
                    context.get("schema", {})
                )
                    
            elif self.component_name == "jsonld":
                return handler_class(
                    context, 
                    context.get("schema", {}),
                    context.get("ai_provider")
                )
                
            elif self.component_name == "bullets":
                # Ensure we're passing all required arguments to BulletsComponent
                return handler_class(
                    context,
                    self.component_config,
                    self.previous_outputs
                )
                
            else:
                # Try different constructor patterns
                for pattern in [
                    lambda: handler_class(context, context.get("schema", {})),
                    lambda: handler_class(context),
                    lambda: handler_class(context.get("subject")),
                    lambda: handler_class()
                ]:
                    try:
                        return pattern()
                    except TypeError:
                        continue
                
                raise TypeError(f"Could not initialize {handler_class.__name__} with any known pattern")
                    
        except Exception as e:
            logger.error(f"Error initializing handler for {self.component_name}: {e}")
            raise ValueError(f"Failed to initialize {self.component_name} component")
    
    def generate(self) -> str:
        """Generate content using the existing handler."""
        if not self.handler:
            raise ValueError(f"No handler available for {self.component_name}")
        
        try:
            # Component-specific generation
            if self.component_name == "frontmatter":
                if hasattr(self.handler, "research_material"):
                    self.handler.research_material(self.subject, self.schema)
                    
                # Use the most appropriate generate method
                for method_name in ["generate_frontmatter", "generate"]:
                    if hasattr(self.handler, method_name):
                        return getattr(self.handler, method_name)()
                        
                raise ValueError(f"No generation method found for {self.component_name}")
                    
            # For all other components, try component-specific methods first, then fallback to generic
            specific_method = f"generate_{self.component_name}"
            if hasattr(self.handler, specific_method):
                return getattr(self.handler, specific_method)()
            elif hasattr(self.handler, "generate"):
                return self.handler.generate()
            else:
                raise ValueError(f"No generation method found for {self.component_name}")
                    
        except Exception as e:
            logger.error(f"Error generating content with handler for {self.component_name}: {e}")
            raise RuntimeError(f"Failed to generate {self.component_name} content: {str(e)}")