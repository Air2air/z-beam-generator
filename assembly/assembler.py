"""
Article assembly module that handles component ordering and assembly.
"""

"""
MODULE DIRECTIVES FOR AI ASSISTANTS:
1. NO CACHING: This assembler must not cache any data between runs
2. FRESH LOADING: Always load components and schemas fresh for each assembly
3. COMPONENT ISOLATION: Each component should be initialized independently
4. DYNAMIC COMPONENTS: Use registry to discover components
5. PURE SCHEMA: Use schemas directly without hardcoded field mappings
6. ARTICLE_CONTEXT DRIVEN: All configuration derives from the article context
7. ERROR HANDLING: Provide clear error messages with proper component attribution
8. OUTPUT NORMALIZATION: Remove duplicate filepath comments and normalize spacing
9. NO FALLBACKS: Components must fail explicitly rather than using fallback content
10. CONTEXT PROPAGATION: Pass complete context to all components for consistency
"""

import os
import logging
import yaml
import re
from typing import Dict, Any, List, Optional, Tuple

from utils.registry_factory import RegistryFactory
from utils.string_utils import StringUtils
from utils.path_manager import PathManager
from components.base import BaseComponent
from api.client import ApiClient  # Import ApiClient
from components.table.generator import TableGenerator  # Import TableGenerator
from utils.slug_manager import SlugManager

logger = logging.getLogger(__name__)

class ArticleAssembler:
    """Assembles articles from components using dynamic schemas."""
    
    def __init__(self, subject: str, article_type: str, config: Dict[str, Any] = None, ai_provider: str = "deepseek"):
        """Initialize the article assembler.
        
        Args:
            subject: Subject of the article
            article_type: Type of article (material, region, etc.)
            config: Configuration for the assembler
            ai_provider: AI provider to use
        """
        self.subject = subject
        self.article_type = article_type
        self.config = config or {}
        self.ai_provider = ai_provider
        
        # Create the context from existing attributes
        self.context = {
            "subject": subject,
            "article_type": article_type,
            "ai_provider": ai_provider,
            **config  # Include all config items
        }
        
        # Initialize schema
        self.schema = self._load_schema()
        
        # Make sure the ApiClient gets the full ARTICLE_CONTEXT
        self.api_client = ApiClient(
            provider=ai_provider,
            article_context=config  # Pass the entire config/ARTICLE_CONTEXT
        )
        
        logger.info(f"Initializing ArticleAssembler for {article_type}: {subject}")

    def _load_schema(self) -> Dict[str, Any]:
        """Load schema for the article type.
        
        Returns:
            Schema dictionary
        """
        try:
            # Get schema registry
            schema_registry = RegistryFactory.schema_registry()
            
            # Get schema for this article type
            schema = schema_registry.get_schema(self.article_type)
            
            # If schema is None, return empty dictionary
            if not schema:
                logger.warning(f"No schema found for article type: {self.article_type}")
                return {}
                
            return schema
        except Exception as e:
            logger.error(f"Error loading schema: {str(e)}")
            return {}
    
    def generate_article(self):
        """Generate the complete article."""
        # Initialize outputs dictionary and frontmatter data
        self.outputs = {}
        self.frontmatter_data = {}
        
        # Keep track of components for later frontmatter injection
        self.components = {}
        
        # First, generate frontmatter
        frontmatter_name = "frontmatter"
        logger.info(f"Generating {frontmatter_name} for {self.article_type}: {self.subject}")
        
        try:
            frontmatter_component = self._get_component_generator(frontmatter_name)
            if frontmatter_component:
                frontmatter_content = frontmatter_component.generate()
                self.outputs[frontmatter_name] = frontmatter_content
                
                # Extract frontmatter
                self._extract_frontmatter(frontmatter_content)
        except Exception as e:
            logger.error(f"Error in ComponentLoader-{frontmatter_name}: {str(e)}")
            self.outputs[frontmatter_name] = f"<!-- Error in {frontmatter_name}: {str(e)} -->"
    
        # Now generate other components in order
        component_order = self._get_component_order()
        for component_name in component_order:
            if component_name == "frontmatter":
                continue  # Already handled
                
            logger.info(f"Generating {component_name} for {self.article_type}: {self.subject}")
            
            try:
                # Get component generator
                component = self._get_component_generator(component_name)
                if not component:
                    continue
                    
                # Explicitly set frontmatter data
                if hasattr(self, 'frontmatter_data') and self.frontmatter_data:
                    if hasattr(component, 'set_frontmatter'):
                        component.set_frontmatter(self.frontmatter_data)
                        logger.info(f"Set frontmatter data for {component_name} component")
                
                # Generate component content
                component_content = component.generate()
                self.outputs[component_name] = component_content
                
            except Exception as e:
                logger.error(f"Error in ComponentLoader-{component_name}: {str(e)}")
                self.outputs[component_name] = f"<!-- Error in {component_name}: {str(e)} -->"
    
        # Assemble components into final article
        article = self._assemble_content(component_order)
        
        # Save to file
        filename = f"{self.subject}.md"
        output_path = self._save_article(article, filename)
        
        return output_path
    
    def _get_component_order(self) -> List[str]:
        """Get component order from config or use default.
        
        Returns:
            List of component names in order
        """
        return self.config.get("assembly", {}).get("component_order", [
            "frontmatter", "content", "bullets", "table", "tags", "jsonld"
        ])
    
    def _is_component_enabled(self, component_name: str) -> bool:
        """Check if a component is enabled in configuration.
        
        Args:
            component_name: Name of the component
            
        Returns:
            True if enabled or not specified, False if explicitly disabled
        """
        component_config = self.config.get("components", {}).get(component_name, {})
        return component_config.get("enabled", True)
    
    def _get_component_schema(self, component_name: str) -> Dict[str, Any]:
        """Get schema for a component, combining article type schema and component config.
        
        Args:
            component_name: Name of the component
            
        Returns:
            Schema for the component
        """
        # Get article schema
        schema_registry = RegistryFactory.schema_registry()
        article_schema = schema_registry.get_schema(self.article_type)
        
        # Get component config
        component_config = self.config.get("components", {}).get(component_name, {})
        
        # Combine schemas
        component_schema = component_config.copy()
        if article_schema:
            if "schema" not in component_schema:
                component_schema["schema"] = {}
            component_schema["schema"].update(article_schema)
        
        return component_schema
    
    def _generate_component(self, component_name: str) -> None:
        """Generate content for a component.
        
        Args:
            component_name: Name of the component
        """
        logger.info(f"Generating {component_name} for {self.article_type}: {self.subject}")
        
        try:
            # Get component class
            component_registry = RegistryFactory.component_registry()
            component_class = component_registry.get_component(component_name)
            
            if not component_class:
                logger.warning(f"Component not found: {component_name}")
                self.outputs[component_name] = f"<!-- Component not found: {component_name} -->\n\n"
                return
            
            # Create context
            context = {
                "subject": self.subject,
                "article_type": self.article_type,
            }
            
            # Get schema for this component
            component_schema = self._get_component_schema(component_name)
            
            # Create component instance
            component = component_class(context, component_schema, self.ai_provider)
            
            # Set frontmatter if available
            if self.frontmatter_data:
                component.set_frontmatter(self.frontmatter_data)
            
            # Set previous outputs
            component.set_previous_outputs(self.outputs)
            
            # Generate content
            content = component.generate_safe()
            self.outputs[component_name] = content
            
            # Extract frontmatter data if this is the frontmatter component
            if component_name == "frontmatter":
                self._extract_frontmatter(content)
                
        except Exception as e:
            logger.error(f"Error generating {component_name}: {e}")
            self.outputs[component_name] = f"<!-- Error generating {component_name}: {str(e)} -->\n\n"
    
    def _extract_frontmatter(self, content):
        """Extract frontmatter data from content."""
        self.frontmatter_data = BaseComponent.extract_frontmatter(content)
    
    def _assemble_content(self, component_order: List[str]) -> str:
        """Assemble all component outputs into a single article.
        
        Args:
            component_order: Order of components
            
        Returns:
            Assembled article content
        """
        parts = []
        for component_name in component_order:
            if component_name in self.outputs and self._is_component_enabled(component_name):
                parts.append(self.outputs[component_name])
        
        return "\n".join(parts)
    
    def _save_article(self, article: str, filename: str) -> str:
        """Save article to output file."""
        # Create output directory if needed
        output_dir = self.config.get("output_dir", "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate full path
        file_path = os.path.join(output_dir, filename)
        
        # Remove any existing filepath comments
        article = re.sub(r'<!--\s*filepath:.+?-->\s*', '', article)
        
        # Add a single filepath comment
        filepath_comment = f"<!-- filepath: {file_path} -->\n"
        article = filepath_comment + article
        
        # Write to file
        with open(file_path, 'w') as f:
            f.write(article)
        
        logging.info(f"Saved article to {file_path}")
        return file_path
    
    def _get_component_generator(self, component_name):
        """Get component generator instance."""
        try:
            # Check if component is enabled
            component_config = self.config.get("components", {}).get(component_name, {})
            if component_config.get("enabled", True) is False:
                logger.info(f"Component {component_name} is disabled")
                return None
            
            # Special case for table component (needs different initialization)
            if component_name == "table":
                # Import TableGenerator here to avoid circular imports
                from components.table.generator import TableGenerator
                
                # Correct initialization for TableGenerator
                component = TableGenerator(self.subject, self.article_type, component_config)
                
                # Set frontmatter data if available
                if hasattr(self, 'frontmatter_data') and self.frontmatter_data:
                    if hasattr(component, 'set_frontmatter'):
                        component.set_frontmatter(self.frontmatter_data)
                
                return component
            
            # Special case for tags component (needs direct initialization)
            if component_name == "tags":
                # Import TagsGenerator here to avoid circular imports
                from components.tags.generator import TagsGenerator
                
                # Correct initialization for TagsGenerator
                component = TagsGenerator(self.subject, self.article_type, component_name, component_config)
                
                # Set frontmatter data if available
                if hasattr(self, 'frontmatter_data') and self.frontmatter_data:
                    if hasattr(component, 'set_frontmatter'):
                        component.set_frontmatter(self.frontmatter_data)
                
                return component
            
            # Get component provider
            provider = component_config.get("provider", self.ai_provider)
            
            # Get component class from registry
            component_registry = RegistryFactory.component_registry()
            component_class = component_registry.get_component(component_name)
            
            if not component_class:
                logger.error(f"Component {component_name} not found in registry")
                return None
            
            # Create component instance
            component = component_class(self.context, self.schema, provider)
            
            # Set frontmatter data if available and this is not the frontmatter component
            if component_name != "frontmatter" and hasattr(self, 'frontmatter_data') and self.frontmatter_data:
                if hasattr(component, 'set_frontmatter'):
                    component.set_frontmatter(self.frontmatter_data)
            
            return component
        
        except Exception as e:
            logger.error(f"Error in ComponentLoader-{component_name}: {str(e)}")
            return None
    
    def get_frontmatter_data(self) -> Dict[str, Any]:
        """Get frontmatter data for component generation."""
        if hasattr(self, 'frontmatter_data') and self.frontmatter_data:
            logger.debug(f"{self.__class__.__name__} using frontmatter with {len(self.frontmatter_data)} fields")
            return self.frontmatter_data
        
        logger.warning(f"No frontmatter data available for {self.__class__.__name__}")
        return {}
    
    def _load_component(self, component_name):
        """Load a component by name, initializing it with the correct context and schema.
        
        Args:
            component_name: Name of the component to load
            
        Returns:
            Initialized component instance, or None if loading failed
        """
        logger.info(f"Loading component {component_name} for {self.article_type}: {self.subject}")
        
        try:
            # Get component config
            component_config = self.config.get("components", {}).get(component_name, {})
            
            # Check if component is enabled
            if component_config.get("enabled", True) is False:
                logger.info(f"Component {component_name} is disabled")
                return None
            
            # Get component class from registry
            component_registry = RegistryFactory.component_registry()
            component_class = component_registry.get_component(component_name)
            
            if not component_class:
                logger.error(f"Component {component_name} not found in registry")
                return None
            
            # Initialize component with correct arguments
            if component_name == "table":
                # Correct initialization - right number of arguments
                component = TableGenerator(self.subject, self.article_type, component_config)
            else:
                # Default initialization
                component = component_class(self.context, self.schema, self.ai_provider)
            
            # Set frontmatter data if available and this is not the frontmatter component
            if component_name != "frontmatter" and hasattr(self, 'frontmatter_data') and self.frontmatter_data:
                if hasattr(component, 'set_frontmatter'):
                    component.set_frontmatter(self.frontmatter_data)
            
            logger.info(f"Component {component_name} loaded successfully")
            return component
        
        except Exception as e:
            logger.error(f"Error loading component {component_name}: {str(e)}")
            return None