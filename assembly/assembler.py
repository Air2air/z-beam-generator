"""
Article assembly module that handles component ordering and assembly.
"""

import os
import logging
import importlib
from typing import Dict, Any, List, Optional, Tuple, Type

from components.base import BaseComponent
from components.registry import ComponentRegistry
from utils.frontmatter_handler import parse_frontmatter

logger = logging.getLogger(__name__)

class ArticleAssembler:
    """
    Assembles article components according to specified order and configuration.
    """
    
    # Default component order if not specified in context
    DEFAULT_COMPONENT_ORDER = [
        "frontmatter",   # Material research, YAML frontmatter
        "content",       # Main markdown content
        "table",         # Data tables
        "bullets",       # Bullet point lists
        "chart",         # Charts and diagrams
        "author",        # Author information
        "tags",          # Tags section
        "jsonld"         # JSON-LD structured data
    ]
    
    def __init__(self, context: Dict[str, Any]):
        """
        Initialize the article assembler with context.
        
        Args:
            context: Dictionary containing article context including subject, 
                    author_id, component_config, etc.
        """
        self.context = context
        self.output_dir = context.get("output_dir")
        self.subject = context.get("subject")
        self.article_type = context.get("article_type")
        self.ai_provider = context.get("ai_provider", "deepseek")
        
        # Set component order from context or use default
        self.component_order = context.get("component_order", self.DEFAULT_COMPONENT_ORDER)
        
        # Dictionary to store component output
        self.component_outputs = {}
        
        # Get the layout template
        self.layout_template = context.get("layout_template", "standard")
        
        # Initialize component registry
        self.registry = ComponentRegistry()
    
    def assemble_article(self) -> Tuple[bool, str]:
        """
        Assemble an article by executing components in the specified order.
        
        Returns:
            Tuple of (success: bool, output_path: str)
        """
        try:
            # Ensure frontmatter is processed first
            self._ensure_frontmatter_first()
            
            # Resolve any component dependencies
            self._resolve_component_dependencies()
            
            # Process each component in order
            for component_name in self.component_order:
                self._process_component(component_name)
            
            # Sanitize component outputs
            self._sanitize_component_outputs()
            
            # Assemble final article using layout template
            final_content = self._apply_layout_template()
            
            # Save to file
            output_path = self._save_article(final_content)
            
            return True, output_path
            
        except Exception as e:
            logger.error(f"Error assembling article: {e}", exc_info=True)
            return False, ""
    
    def _ensure_frontmatter_first(self):
        """Ensure frontmatter is the first component to be processed."""
        if "frontmatter" in self.component_order and self.component_order[0] != "frontmatter":
            self.component_order.remove("frontmatter")
            self.component_order.insert(0, "frontmatter")
    
    def _resolve_component_dependencies(self):
        """Resolve component dependencies to ensure correct processing order."""
        # Implementation of dependency resolution if needed
        pass
    
    def _process_component(self, component_name: str):
        """Process a single component and store its output."""
        logger.info(f"Processing component: {component_name}")
        
        try:
            # Get component class from registry
            component_class = self.registry.get_component_class(component_name)
            
            if not component_class:
                logger.warning(f"Component '{component_name}' not found in registry, skipping")
                return
            
            # Create component instance
            component = component_class(
                self.context,
                self.context.get("schema", {}),
                self.ai_provider
            )
            
            # Set component options if available
            if component_name in self.context.get("component_config", {}):
                component.set_options(self.context["component_config"][component_name])
            
            # Set previous outputs for all components except frontmatter
            if component_name != "frontmatter":
                component.set_previous_outputs(self.component_outputs)
            
            # If frontmatter exists and this isn't the frontmatter component,
            # extract and provide frontmatter data
            if "frontmatter" in self.component_outputs and component_name != "frontmatter":
                frontmatter_data = parse_frontmatter(self.component_outputs["frontmatter"])
                if frontmatter_data:
                    component.set_frontmatter(frontmatter_data)
            
            # Generate content
            output = component.generate()
            
            # Store component output
            self.component_outputs[component_name] = output if output is not None else ""
            
        except Exception as e:
            logger.error(f"Error processing component '{component_name}': {e}", exc_info=True)
            self.component_outputs[component_name] = f"<!-- Error in {component_name}: {str(e)} -->"
    
    def _sanitize_component_outputs(self):
        """Ensure all component outputs are strings."""
        for name, output in self.component_outputs.items():
            if not isinstance(output, str):
                self.component_outputs[name] = str(output)
    
    def _apply_layout_template(self) -> str:
        """Apply layout template to assembled components."""
        # Simple implementation - just concatenate all components
        parts = []
        
        # Start with frontmatter if available
        if "frontmatter" in self.component_outputs:
            parts.append(self.component_outputs["frontmatter"])
        
        # Add content if available
        if "content" in self.component_outputs:
            parts.append(self.component_outputs["content"])
        
        # Add other components in order
        for name in self.component_order:
            if name not in ["frontmatter", "content"] and name in self.component_outputs:
                parts.append(self.component_outputs[name])
        
        # Join all parts with double newlines
        return "\n\n".join(parts)
    
    def _save_article(self, content: str) -> str:
        """
        Save the assembled article to a file.
        
        Args:
            content: Article content to save
            
        Returns:
            Path to the saved file
        """
        if not self.output_dir:
            self.output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
            
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Generate filename from subject
        filename = self.subject.lower().replace(' ', '-') + '.md'
        output_path = os.path.join(self.output_dir, filename)
        
        # Save content to file
        with open(output_path, 'w') as f:
            f.write(content)
            
        logger.info(f"Saved article to {output_path}")
        return output_path
    
    def _initialize_component(self, component_class, component_name):
        """Initialize a component with proper arguments."""
        # Create context object
        context = {
            "subject": self.subject,
            "article_type": self.article_type,
            # Add any other context needed by components
        }
        
        # Get schema for this component from config
        component_schema = self.config.get("components", {}).get(component_name, {})
        
        # Create the component instance with BaseComponent parameters
        component = component_class(context, component_schema, self.ai_provider)
        
        # Set frontmatter if available
        if self.frontmatter_data:
            component.set_frontmatter(self.frontmatter_data)
        
        # Set previous outputs
        component.set_previous_outputs(self.outputs)
        
        return component