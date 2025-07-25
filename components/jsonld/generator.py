"""
MODULE DIRECTIVES FOR AI ASSISTANTS:
1. SCHEMA-COMPLIANT: JSON-LD must follow Schema.org specifications
2. ARTICLE_TYPE AWARENESS: Different schema types based on article_type
3. PROPERTY MAPPING: Map frontmatter fields to JSON-LD properties
4. FORMAT CONSISTENCY: Format keywords as comma-separated string
5. STRATEGY PATTERN: Use type-specific generators for each article type
"""

import logging
import json
import importlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class JsonldGenerator(BaseComponent):
    """Generates JSON-LD structured data following schema definitions."""
    
    # Map of article types to their schema types
    SCHEMA_TYPE_MAP = {
        "region": "Article",
        "application": "TechnicalArticle", 
        "thesaurus": "DefinedTerm",
        "material": "Product"
    }
    
    def generate(self) -> str:
        """Abstract method implementation required by BaseComponent.
        
        Returns:
            JSON-LD content as string
        """
        return self._generate()
    
    def _generate(self) -> str:
        """Generate JSON-LD content based on article type.
        
        Returns:
            JSON-LD content as string
        """
        try:
            # Get frontmatter data
            frontmatter = self.frontmatter_data or {}
            
            # Get the appropriate generator for this article type
            type_generator = self._get_type_generator()
            
            if type_generator:
                # Use the type-specific generator
                jsonld = type_generator.generate_jsonld(frontmatter)
            else:
                # Use default generator as fallback
                jsonld = self._generate_default_jsonld(frontmatter)
                
            # Format as JSON with indentation
            jsonld_str = json.dumps(jsonld, indent=2)
            
            # Return as code block
            return f"""```json
{jsonld_str}
```"""
            
        except Exception as e:
            logger.error(f"Error generating JSON-LD: {str(e)}")
            return self._generate_fallback_jsonld()
    
    def _get_type_generator(self):
        """Get the appropriate type-specific generator for this article type.
        
        Returns:
            Type-specific generator instance or None if not found
        """
        try:
            # Convert article_type to proper module name (e.g., "region" -> "region_generator")
            module_name = f"{self.article_type}_generator"
            
            # Try to import the module
            module = importlib.import_module(f"components.jsonld.types.{module_name}")
            
            # Get the generator class (naming convention: RegionJsonldGenerator, etc.)
            class_name = f"{self.article_type.capitalize()}JsonldGenerator"
            generator_class = getattr(module, class_name)
            
            # Create an instance with the same context as this generator
            return generator_class(self.subject, self.frontmatter_data)
            
        except (ImportError, AttributeError) as e:
            logger.warning(f"No specific generator found for article type '{self.article_type}': {str(e)}")
            return None
    
    def _generate_default_jsonld(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """Generate JSON-LD for articles without a specific generator.
        
        Args:
            frontmatter: Article frontmatter data
            
        Returns:
            JSON-LD structure for default articles
        """
        # Get name/title
        name = frontmatter.get("name", self.subject)
        description = frontmatter.get("description", f"Information about {name}.")
        
        # Get schema type for this article type or default to Article
        schema_type = self.SCHEMA_TYPE_MAP.get(self.article_type, "Article")
        
        # Create simple JSON-LD
        return {
            "@context": "https://schema.org",
            "@type": schema_type,
            "headline": name,
            "description": description,
            "author": {
                "@type": "Organization",
                "name": "Z-Beam"
            }
        }
    
    def _generate_fallback_jsonld(self) -> str:
        """Generate fallback JSON-LD when errors occur.
        
        Returns:
            Fallback JSON-LD as string
        """
        # Get schema type for this article type or default to Article
        schema_type = self.SCHEMA_TYPE_MAP.get(self.article_type, "Article")
        
        fallback = {
            "@context": "https://schema.org",
            "@type": schema_type,
            "headline": self.subject,
            "description": f"Information about {self.subject}."
        }
        
        # Format as JSON
        fallback_str = json.dumps(fallback, indent=2)
        
        # Return as code block
        return f"""```json
{fallback_str}
```"""
