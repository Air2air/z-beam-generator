"""
Frontmatter generator for Z-Beam Generator.

MODULE DIRECTIVES FOR AI ASSISTANTS:
1. FRONTMATTER-DRIVEN: All content must be extracted from frontmatter
2. NO HARDCODED SECTIONS: Section structure must be derived from frontmatter
3. DYNAMIC FORMATTING: Format content based on article_type from frontmatter
4. ERROR HANDLING: Raise exceptions when required frontmatter fields are missing
5. SCHEMA AWARENESS: Be aware of the schema structure for different article types
"""

import logging
import yaml
from typing import Dict, Any
from components.base.component import BaseComponent

logger = logging.getLogger(__name__)

class FrontmatterGenerator(BaseComponent):
    """Generator for article frontmatter."""
    
    def generate(self) -> str:
        """Generate frontmatter content.
        
        Returns:
            str: The generated frontmatter
        """
        try:
            # 1. Prepare data for prompt
            data = self._prepare_data()
            
            # 2. Format prompt
            prompt = self._format_prompt(data)
            
            # 3. Call API
            content = self._call_api(prompt)
            
            # 4. Post-process content
            return self._post_process(content)
        except Exception as e:
            logger.error(f"Error generating frontmatter: {str(e)}")
            return self._create_error_markdown(str(e))
    
    def _prepare_data(self) -> Dict[str, Any]:
        """Prepare data for frontmatter generation.
        
        Returns:
            Dict[str, Any]: Data for prompt formatting
        """
        data = super()._prepare_data()
        
        # Get component-specific configuration
        component_config = self.get_component_config()
        
        # Add required template variables - use consistent pattern
        data.update({
            "min_words": component_config["min_words"],  # Must exist
            "max_words": component_config["max_words"],  # Must exist
            "include_website": component_config["include_website"],  # Must exist
        })
        
        # Add context data with validation
        if "author_id" not in self.context:
            raise ValueError("author_id is required in context but not provided")
        if "website_url" in self.context:
            data["website_url"] = self.context["website_url"]
        
        data["author_id"] = self.context["author_id"]
        
        # Get author data from the author service
        from components.author.author_service import AuthorService
        author_service = AuthorService()
        author_info = author_service.get_author_by_id(data["author_id"])
        
        if not author_info:
            raise ValueError(f"Author with ID {data['author_id']} not found")
        
        data["author_name"] = author_info["name"]
        data["author_country"] = author_info["country"]
        
        # Debug: Log the author data being used
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Using author data: ID={data['author_id']}, Name={data['author_name']}, Country={data['author_country']}")
        
        # Format the schema for the prompt template
        if self.schema:
            # Extract the relevant parts of the schema for frontmatter generation
            profile = self.schema.get("regionProfile", {}).get("profile", {})
            validation = self.schema.get("regionProfile", {}).get("validation", {}).get("frontmatter", {})
            
            schema_text = f"REQUIRED FIELDS for {self.article_type} articles:\n"
            
            # Add required fields from validation
            required_fields = validation.get("requiredFields", [])
            if required_fields:
                schema_text += f"Required frontmatter fields: {', '.join(required_fields)}\n\n"
            
            # Add specific field requirements from profile
            schema_text += "FIELD SPECIFICATIONS:\n"
            for field_name, field_spec in profile.items():
                if isinstance(field_spec, dict):
                    field_type = field_spec.get("type", "unknown")
                    required = field_spec.get("required", False)
                    req_str = " (REQUIRED)" if required else " (optional)"
                    schema_text += f"- {field_name}: {field_type}{req_str}\n"
                    
                    # Add any items specification for arrays
                    if field_type == "array" and "items" in field_spec:
                        items_spec = field_spec["items"]
                        if isinstance(items_spec, dict):
                            items_type = items_spec.get("type", "unknown")
                            schema_text += f"  └─ Array items: {items_type}\n"
                            
                            # Add object properties if items are objects
                            if items_type == "object" and "properties" in items_spec:
                                for prop_name, prop_spec in items_spec["properties"].items():
                                    prop_type = prop_spec.get("type", "unknown")
                                    prop_required = prop_spec.get("required", False)
                                    prop_req_str = " (REQUIRED)" if prop_required else ""
                                    schema_text += f"    └─ {prop_name}: {prop_type}{prop_req_str}\n"
            
            data["schema"] = schema_text
            logger.info(f"Generated schema for prompt:\n{schema_text[:500]}...")  # Log first 500 chars
        else:
            data["schema"] = f"No specific schema available for {self.article_type} articles."
            logger.warning("No schema provided for frontmatter generation")
        
        # Set frontmatter fields based on article type
        if self.article_type == "material":
            data["required_fields"] = ["title", "description", "date", "author", "properties", "applications"]
        elif self.article_type == "application":
            data["required_fields"] = ["title", "description", "date", "author", "industries", "features"]
        elif self.article_type == "region":
            data["required_fields"] = ["title", "description", "date", "author", "location", "industries"]
        elif self.article_type == "thesaurus":
            data["required_fields"] = ["title", "description", "date", "author", "alternateNames", "relatedTerms"]
        else:
            data["required_fields"] = ["title", "description", "date", "author"]
        
        # Add website inclusion flag - no fallbacks
        data["include_website"] = component_config["include_website"]  # Must exist
        
        return data
    
    def _post_process(self, content: str) -> str:
        """Post-process the frontmatter content.
        
        Args:
            content: The API response content
            
        Returns:
            str: The processed frontmatter
        """
        # Process API response to extract YAML frontmatter
        processed = super()._post_process(content)
        
        # Since our prompt instructs AI NOT to include "---" delimiters,
        # we expect raw YAML content. Let's validate and format it.
        
        # First, try to parse the content as YAML directly
        try:
            frontmatter = yaml.safe_load(processed)
            if isinstance(frontmatter, dict) and frontmatter:
                # Valid YAML dict - use it directly
                logger.info(f"Successfully parsed raw YAML response with {len(frontmatter)} fields")
                return f"---\n{processed.strip()}\n---\n"
        except yaml.YAMLError as e:
            logger.warning(f"Failed to parse response as YAML: {e}")
        
        # If direct parsing failed, check for content in "---" delimiters
        if "---" in processed:
            # Extract everything between first and second '---'
            parts = processed.split("---", 2)
            if len(parts) >= 3:
                yaml_content = parts[1].strip()
                
                # Validate YAML content
                try:
                    frontmatter = yaml.safe_load(yaml_content)
                    if isinstance(frontmatter, dict):
                        logger.info(f"Extracted YAML from delimiters with {len(frontmatter)} fields")
                        return f"---\n{yaml_content}\n---\n"
                except Exception:
                    logger.warning("Invalid YAML found between delimiters")
        
        # Try to extract YAML from code blocks
        yaml_content = self._extract_yaml_from_code_blocks(processed)
        if yaml_content:
            try:
                frontmatter = yaml.safe_load(yaml_content)
                if isinstance(frontmatter, dict):
                    logger.info(f"Extracted YAML from code blocks with {len(frontmatter)} fields")
                    return f"---\n{yaml_content}\n---\n"
            except Exception:
                logger.warning("Invalid YAML found in code blocks")
        
        # If all parsing attempts failed, raise an error (no fallbacks)
        logger.error("Failed to extract valid YAML from API response")
        raise ValueError(f"API response could not be parsed as valid YAML. Response content: {processed[:200]}...")
