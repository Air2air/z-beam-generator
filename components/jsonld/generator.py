"""
JSON-LD generator for Z-Beam Generator.

MODULE DIRECTIVES FOR AI ASSISTANTS:
1. FRONTMATTER-DRIVEN: All content must be extracted from frontmatter
2. NO HARDCODED SECTIONS: Section structure must be derived from frontmatter
3. DYNAMIC FORMATTING: Format content based on article_type from frontmatter
4. ERROR HANDLING: Raise exceptions when required frontmatter fields are missing
5. SCHEMA AWARENESS: Be aware of the schema structure for different article types
"""

import logging
import json
import re
from typing import Dict, Any, List, Optional
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class JsonldGenerator(BaseComponent):
    """Generator for JSON-LD structured data."""
    
    def generate(self) -> str:
        """Generate JSON-LD content.
        
        Returns:
            str: The generated JSON-LD
        """
        try:
            # Check if we should use type-specific generator
            type_generator = self._get_type_generator()
            if type_generator:
                return self._generate_with_type_generator(type_generator)
            
            # No type generator, use standard approach
            # 1. Prepare data for prompt
            data = self._prepare_data()
            
            # 2. Format prompt
            prompt = self._format_prompt(data)
            
            # 3. Call API
            content = self._call_api(prompt)
            
            # 4. Post-process content
            return self._post_process(content)
        except Exception as e:
            logger.error(f"Error generating JSON-LD: {str(e)}")
            return self._create_error_markdown(str(e))
    
    def _get_type_generator(self):
        """Get a type-specific generator based on article type.
        
        Returns:
            object: Type generator instance or None
        """
        try:
            # Import type-specific generator
            if self.article_type == "material":
                from components.jsonld.types.material_generator import MaterialJsonldGenerator
                return MaterialJsonldGenerator(self.subject, self.get_frontmatter_data())
            elif self.article_type == "application":
                from components.jsonld.types.application_generator import ApplicationJsonldGenerator
                return ApplicationJsonldGenerator(self.subject, self.get_frontmatter_data())
            elif self.article_type == "region":
                from components.jsonld.types.region_generator import RegionJsonldGenerator
                return RegionJsonldGenerator(self.subject, self.get_frontmatter_data())
            elif self.article_type == "thesaurus":
                from components.jsonld.types.thesaurus_generator import ThesaurusJsonldGenerator
                return ThesaurusJsonldGenerator(self.subject, self.get_frontmatter_data())
            else:
                return None
        except ImportError:
            logger.warning(f"No type-specific generator found for {self.article_type}")
            return None
    
    def _generate_with_type_generator(self, generator) -> str:
        """Generate JSON-LD using type-specific generator.
        
        Args:
            generator: Type-specific generator instance
            
        Returns:
            str: The generated JSON-LD
        """
        # Pass frontmatter to generator if it has a method for it
        if hasattr(generator, "set_frontmatter"):
            generator.set_frontmatter(self.get_frontmatter_data())
        
        # Generate JSON-LD
        try:
            if hasattr(generator, "generate"):
                return generator.generate()
            elif hasattr(generator, "generate_jsonld"):
                jsonld = generator.generate_jsonld()
                return self._format_jsonld(jsonld)
            else:
                raise AttributeError("Generator has no generate or generate_jsonld method")
        except Exception as e:
            logger.error(f"Error in type generator: {str(e)}")
            return self._create_error_markdown(f"Error in type generator: {str(e)}")
    
    def _prepare_data(self) -> Dict[str, Any]:
        """Prepare data for JSON-LD generation.
        
        Returns:
            Dict[str, Any]: Data for prompt formatting
        """
        data = super()._prepare_data()
        
        # Get frontmatter data
        frontmatter = self.get_frontmatter_data()
        if frontmatter:
            # Extract common fields
            data["title"] = frontmatter.get("title", self.subject.capitalize())
            data["description"] = frontmatter.get("description", f"Information about {self.subject}")
            
            # Extract author information
            author = frontmatter.get("author", {})
            if isinstance(author, dict):
                data["author"] = author
            elif isinstance(author, str):
                data["author"] = {"name": author}
            
            # Extract date
            data["date"] = frontmatter.get("date", self._get_current_date())
            
            # Extract article type-specific fields
            if self.article_type == "material":
                data["properties"] = frontmatter.get("properties", {})
                data["applications"] = frontmatter.get("applications", [])
            elif self.article_type == "application":
                data["industries"] = frontmatter.get("industries", [])
                data["features"] = frontmatter.get("features", [])
            elif self.article_type == "region":
                data["location"] = frontmatter.get("location", {})
                data["companies"] = frontmatter.get("companies", [])
            elif self.article_type == "thesaurus":
                data["alternateNames"] = frontmatter.get("alternateNames", [])
                data["relatedTerms"] = frontmatter.get("relatedTerms", [])
        
        return data
    
    def _post_process(self, content: str) -> str:
        """Post-process the JSON-LD content.
        
        Args:
            content: The API response content
            
        Returns:
            str: The processed JSON-LD
        """
        # Extract JSON-LD from content
        jsonld = self._extract_jsonld(content)
        
        # Format as script tag
        if jsonld:
            return self._format_jsonld(jsonld)
        else:
            # Create fallback JSON-LD
            fallback = self._create_fallback_jsonld()
            return self._format_jsonld(fallback)
    
    def _extract_jsonld(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract JSON-LD from content.
        
        Args:
            content: Content that might contain JSON-LD
            
        Returns:
            Optional[Dict[str, Any]]: Extracted JSON-LD or None
        """
        # Try to extract JSON object
        try:
            # First, try to find JSON in a code block
            json_pattern = r'```(?:json)?\s*(.*?)\s*```'
            match = re.search(json_pattern, content, re.DOTALL)
            if match:
                json_str = match.group(1).strip()
                return json.loads(json_str)
            
            # Next, try to find JSON in script tags
            script_pattern = r'<script[^>]*>\s*(.*?)\s*</script>'
            match = re.search(script_pattern, content, re.DOTALL)
            if match:
                json_str = match.group(1).strip()
                return json.loads(json_str)
            
            # Next, try to find a raw JSON object
            json_obj_pattern = r'(\{\s*"@context".*\})'
            match = re.search(json_obj_pattern, content, re.DOTALL)
            if match:
                json_str = match.group(1).strip()
                return json.loads(json_str)
            
            # Finally, try to parse the whole content as JSON
            return json.loads(content)
        except Exception as e:
            logger.error(f"Error extracting JSON-LD: {str(e)}")
            return None
    
    def _format_jsonld(self, jsonld: Dict[str, Any]) -> str:
        """Format JSON-LD as script tag.
        
        Args:
            jsonld: JSON-LD data
            
        Returns:
            str: Formatted JSON-LD script tag
        """
        # Ensure we have valid JSON-LD
        if not jsonld:
            jsonld = self._create_fallback_jsonld()
        
        # Ensure @context is present
        if "@context" not in jsonld:
            jsonld["@context"] = "https://schema.org"
        
        # Format as JSON with indentation
        try:
            json_str = json.dumps(jsonld, indent=2)
            return f'<script type="application/ld+json">\n{json_str}\n</script>'
        except Exception as e:
            logger.error(f"Error formatting JSON-LD: {str(e)}")
            return f"<!-- Error formatting JSON-LD: {str(e)} -->"
    
    def _create_fallback_jsonld(self) -> Dict[str, Any]:
        """Create fallback JSON-LD when extraction fails.
        
        Returns:
            Dict[str, Any]: Fallback JSON-LD
        """
        # Get frontmatter data
        frontmatter = self.get_frontmatter_data()
        title = frontmatter.get("title", self.subject.capitalize()) if frontmatter else self.subject.capitalize()
        description = frontmatter.get("description", f"Information about {self.subject}") if frontmatter else f"Information about {self.subject}"
        
        # Create basic JSON-LD
        if self.article_type == "material":
            return {
                "@context": "https://schema.org",
                "@type": "Product",
                "name": title,
                "description": description,
                "category": "Material"
            }
        elif self.article_type == "application":
            return {
                "@context": "https://schema.org",
                "@type": "TechArticle",
                "headline": title,
                "description": description,
                "about": {"@type": "Thing", "name": self.subject}
            }
        elif self.article_type == "region":
            return {
                "@context": "https://schema.org",
                "@type": "Place",
                "name": title,
                "description": description
            }
        elif self.article_type == "thesaurus":
            return {
                "@context": "https://schema.org",
                "@type": "DefinedTerm",
                "name": title,
                "description": description
            }
        else:
            return {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": title,
                "description": description
            }
    
    def _get_current_date(self) -> str:
        """Get current date in ISO format.
        
        Returns:
            str: Current date
        """
        import datetime
        return datetime.date.today().isoformat()
