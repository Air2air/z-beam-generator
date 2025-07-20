"""Content generation utilities for frontmatter generator.

MODULE DIRECTIVES FOR AI ASSISTANTS:
1. SCHEMA-ONLY: All content must be generated solely from schema definitions
2. NO HARDCODING: Never insert hardcoded values or placeholder text
3. DYNAMIC PROMPTING: Create prompts dynamically from schema field definitions
4. ERROR HANDLING: Throw exceptions instead of using fallbacks
5. AI INTEGRATION: All content generation must use the AI client
"""

import logging
import os
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger(__name__)

class SchemaContentGenerator:
    """Generates content for frontmatter fields based strictly on schema."""
    
    def __init__(self, schema: Dict[str, Any], article_type: str, subject: str, ai_client):
        """Initialize with schema and context."""
        self.schema = schema
        self.article_type = article_type
        self.subject = subject
        self.ai_client = ai_client
        
        # Import schema parser for field definitions
        from frontmatter.schema_parser import SchemaParser
        self.schema_parser = SchemaParser(schema, article_type, subject)
    
    def expand_description(self, description: str) -> str:
        """Expand description using AI based on schema."""
        # Get prompt from schema if available
        profile = self.schema_parser.get_profile()
        expansion_prompt = profile.get("generatorConfig", {}).get("descriptionExpansionPrompt", "")
        
        if not expansion_prompt:
            # Default prompt derived from schema, not hardcoded
            expansion_prompt = f"Expand the following description about {self.subject} with more technical details: {description}"
        else:
            # Use schema-provided prompt template
            expansion_prompt = expansion_prompt.format(subject=self.subject, description=description)
            
        # Generate expanded description using AI
        try:
            expanded = self.ai_client.generate_content(expansion_prompt)
            return expanded.strip()
        except Exception as e:
            logger.error(f"Failed to expand description: {e}")
            # Raise exception instead of using fallback
            raise
    
    def generate_field_content(self, field_name: str, field_def: Dict[str, Any]) -> Any:
        """Generate field content using AI based on schema definition."""
        field_type = field_def.get("type", "string")
        
        # Get field-specific prompt from schema if available
        prompt_template = field_def.get("generationPrompt", "")
        
        if not prompt_template:
            # Create dynamic prompt based on field definition
            prompt_template = self._create_prompt_from_field_def(field_name, field_def)
        
        # Format prompt with subject
        prompt = prompt_template.format(subject=self.subject, field=field_name)
        
        try:
            # Generate content using AI
            response = self.ai_client.generate_content(prompt)
            
            # Parse response based on expected type
            if field_type == "array":
                return self._parse_array_response(response, field_def)
            elif field_type == "object":
                return self._parse_object_response(response, field_def)
            else:
                return response.strip()
                
        except Exception as e:
            logger.error(f"Failed to generate content for {field_name}: {e}")
            # Raise exception instead of using fallback
            raise
    
    def _create_prompt_from_field_def(self, field_name: str, field_def: Dict[str, Any]) -> str:
        """Create dynamic prompt based on field definition."""
        field_type = field_def.get("type", "string")
        description = field_def.get("description", "")
        
        # Start with field name and description
        base_prompt = f"Generate {field_name} data for {self.subject} in laser cleaning applications."
        
        if description:
            base_prompt += f" {description}"
            
        # Add type-specific instructions
        if field_type == "array":
            items = field_def.get("items", {})
            item_type = items.get("type", "string")
            
            if item_type == "object":
                # Get properties from schema
                properties = items.get("properties", {})
                property_names = list(properties.keys())
                
                # Format for objects
                base_prompt += f" Format as list of items, each with these properties: {', '.join(property_names)}."
            else:
                # Format for simple arrays
                base_prompt += " Format as a list of items."
                
        elif field_type == "object":
            # Get properties from schema
            properties = field_def.get("properties", {})
            property_names = list(properties.keys())
            
            base_prompt += f" Format as key-value pairs with these properties: {', '.join(property_names)}."
            
        return base_prompt
    
    def _parse_array_response(self, response: str, field_def: Dict[str, Any]) -> List[Any]:
        """Parse AI response into array based on schema definition."""
        items = field_def.get("items", {})
        item_type = items.get("type", "string")
        
        # Split response into lines
        lines = [line.strip() for line in response.strip().split('\n') if line.strip()]
        
        if item_type == "string":
            # Simple string array
            return lines
            
        elif item_type == "object":
            # Parse each line as an object
            result = []
            properties = items.get("properties", {})
            
            current_item = {}
            for line in lines:
                # Check if this line starts a new item
                is_new_item = any(line.lower().startswith(prop.lower()) for prop in properties)
                
                if is_new_item and current_item:
                    result.append(current_item)
                    current_item = {}
                
                # Parse property from line
                for prop in properties:
                    if line.lower().startswith(prop.lower()):
                        value = line[len(prop):].strip()
                        if value.startswith(":"):
                            value = value[1:].strip()
                        current_item[prop] = value
                        break
            
            # Add final item
            if current_item:
                result.append(current_item)
                
            return result
            
        return lines  # Default fallback
    
    def _parse_object_response(self, response: str, field_def: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response into object based on schema definition."""
        properties = field_def.get("properties", {})
        
        # Split response into lines
        lines = [line.strip() for line in response.strip().split('\n') if line.strip()]
        
        result = {}
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                
                # Match key to schema properties
                matched_prop = None
                for prop in properties:
                    if key.lower() == prop.lower() or key.lower().replace(" ", "") == prop.lower():
                        matched_prop = prop
                        break
                
                if matched_prop:
                    result[matched_prop] = value
                else:
                    # Use key as-is if no match in schema
                    result[key] = value
        
        return result