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
"""

import os
import logging
import yaml
import re
from typing import Dict, Any, List, Optional, Tuple

from utils.registry_factory import RegistryFactory
from utils.string_utils import StringUtils
from utils.path_manager import PathManager

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
        self.outputs = {}
        self.frontmatter_data = None
        
        logger.info(f"Initializing ArticleAssembler for {article_type}: {subject}")
    
    def generate_article(self) -> str:
        """Generate a complete article by assembling components.
        
        Returns:
            Path to the generated article file
        """
        # Get component order from config or use default
        component_order = self._get_component_order()
        
        # Generate each component
        for component_name in component_order:
            # Check if component is enabled
            if not self._is_component_enabled(component_name):
                logger.info(f"Skipping disabled component: {component_name}")
                continue
                
            self._generate_component(component_name)
        
        # Assemble and save the article
        article_content = self._assemble_content(component_order)
        return self._save_article(article_content)
    
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
    
    def _extract_frontmatter(self, content: str) -> None:
        """Extract frontmatter data from content.
        
        Args:
            content: Generated frontmatter content
        """
        try:
            yaml_content = StringUtils.extract_frontmatter(content)
            if yaml_content:
                self.frontmatter_data = yaml.safe_load(yaml_content) or {}
                logger.debug(f"Extracted frontmatter with {len(self.frontmatter_data)} fields")
            else:
                # No frontmatter found, check if we have an error message with frontmatter
                if "---" in content:
                    # Try again with a more lenient approach - get content between first two --- markers
                    sections = content.split('---', 2)
                    if len(sections) >= 3:
                        yaml_content = sections[1].strip()
                        self.frontmatter_data = yaml.safe_load(yaml_content) or {}
                        logger.info(f"Extracted frontmatter from error content with {len(self.frontmatter_data)} fields")
                        return
                        
                logger.warning("No frontmatter delimiters found")
                
        except Exception as e:
            logger.error(f"Error extracting frontmatter: {e}")
    
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
    
    def _save_article(self, content: str) -> str:
        """Save the article to a file.
        
        Args:
            content: Article content
            
        Returns:
            Path to the saved file
        """
        # Create slug
        slug = StringUtils.create_slug(self.subject)
        
        # Get output directory
        output_dir = self.config.get("output", {}).get("directory", "output")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Create file path
        file_path = os.path.join(output_dir, f"{slug}.md")
        
        # Add filepath comment
        file_comment = f"<!-- filepath: {os.path.abspath(file_path)} -->\n"
        content_with_comment = file_comment + content
        
        # Write to file
        with open(file_path, 'w') as f:
            f.write(content_with_comment)
        
        logger.info(f"Saved article to {file_path}")
        return file_path