"""
MODULE DIRECTIVES FOR AI ASSISTANTS:
1. SCHEMA-DRIVEN: Load and use schema definition based on article_type
2. NO FALLBACKS: Do not use hardcoded values when schema data is unavailable
3. DYNAMIC CONTENT: All frontmatter must be generated via AI, not templates
4. SCHEMA VALIDATION: Ensure generated content conforms to schema structure
5. ERROR TRANSPARENCY: Log errors but propagate exceptions to caller
"""

"""
Frontmatter generator for article metadata.
"""

import yaml
import logging
import os
import re
from typing import Dict, Any, Optional
from pathlib import Path

from components.base import BaseComponent

logger = logging.getLogger(__name__)

class FrontmatterGenerator(BaseComponent):
    """Generates YAML frontmatter for articles."""
    
    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], ai_provider: str = "deepseek"):
        """Initialize the frontmatter generator with dynamic schema support.
        
        Args:
            context: Context data including subject, article_type, etc.
            schema: Schema definition for frontmatter generation
            ai_provider: The AI provider to use
        """
        super().__init__(context, schema, ai_provider)
        logger.info(f"FrontmatterGenerator initialized for subject: {self.subject}")
        
        # Load prompt configuration from schema or from local file
        self.prompt_config = schema.get("prompt", {})
        if not self.prompt_config or "template" not in self.prompt_config:
            self.prompt_config = self._load_prompt_yaml()
        
        # Extract schema definition for dynamic schema generation
        self.schema_definition = schema.get("schema", {})
    
    def _load_prompt_yaml(self) -> Dict[str, Any]:
        """Load prompt configuration from prompt.yaml file."""
        prompt_path = os.path.join(os.path.dirname(__file__), "prompt.yaml")
        try:
            with open(prompt_path, 'r') as file:
                prompt_config = yaml.safe_load(file) or {}
                logger.info(f"Loaded prompt configuration from {prompt_path}")
                return prompt_config
        except Exception as e:
            logger.error(f"Error loading prompt.yaml: {e}")
            return {}
    
    def _generate_schema_section(self) -> str:
        """Generate schema section for the prompt based on dynamic schema definition."""
        if not self.schema_definition:
            # Use the default schema structure from the prompt template
            return ""
        
        schema_text = "Dynamic schema fields:\n"
        
        # Process each field in the schema definition
        for field_name, field_def in self.schema_definition.items():
            field_type = field_def.get("type", "string")
            description = field_def.get("description", "")
            example = field_def.get("example", "")
            
            # Format the field based on its type
            if field_type == "string":
                schema_text += f"{field_name}: \"{example or field_name}\""
                if description:
                    schema_text += f" # {description}"
                schema_text += "\n"
                
            elif field_type == "array":
                schema_text += f"{field_name}:"
                if description:
                    schema_text += f" # {description}"
                schema_text += "\n"
                
                if "items" in field_def and field_def["items"].get("type") == "object":
                    # Complex array with object items
                    item_props = field_def["items"].get("properties", {})
                    for i in range(min(2, field_def.get("minItems", 2))):
                        schema_text += f"  - "
                        for prop_name in item_props:
                            schema_text += f"{prop_name}: \"Example {prop_name}\" "
                        schema_text += "\n"
                else:
                    # Simple array of strings
                    for i in range(min(2, field_def.get("minItems", 2))):
                        schema_text += f"  - \"Example item {i+1}\"\n"
                
            elif field_type == "object":
                schema_text += f"{field_name}:"
                if description:
                    schema_text += f" # {description}"
                schema_text += "\n"
                
                properties = field_def.get("properties", {})
                for prop_name, prop_def in properties.items():
                    prop_example = prop_def.get("example", f"Example {prop_name}")
                    schema_text += f"  {prop_name}: \"{prop_example}\""
                    if prop_def.get("description"):
                        schema_text += f" # {prop_def['description']}"
                    schema_text += "\n"
        
        return schema_text
    
    def generate(self) -> str:
        """Generate frontmatter based on subject and article type."""
        try:
            # Get template from prompt config
            template = self.prompt_config.get("template", "")
            if not template:
                logger.error("No template found in prompt config")
                raise ValueError("No template found in prompt config")
            
            # Generate dynamic schema section if schema definition is available
            schema_section = self._generate_schema_section()
            
            # Format template with context variables and dynamic schema
            formatted_prompt = template.format(
                article_type=self.article_type,
                subject=self.subject,
                schema=schema_section
            )
            
            # Add explicit instruction to avoid code blocks and multiple YAML documents
            formatted_prompt += "\n\n🚨 CRITICAL FORMATTING REQUIREMENTS:\n"
            formatted_prompt += "1. DO NOT USE TRIPLE BACKTICKS (```) or ```yaml MARKERS\n"
            formatted_prompt += "2. DO NOT INCLUDE ANY --- DELIMITERS\n"
            formatted_prompt += "3. RETURN ONLY THE RAW YAML CONTENT\n"
            
            # Log formatted prompt (truncated for readability)
            logger.debug(f"Formatted prompt: {formatted_prompt[:100]}...")
            
            # Generate frontmatter using API
            frontmatter_content = self.api_client.generate_content(formatted_prompt)
            
            # Clean up the YAML to fix parsing issues
            frontmatter_content = self._clean_yaml_response(frontmatter_content)
            
            return f"---\n{frontmatter_content}\n---\n"
        
        except Exception as e:
            logger.error(f"Error generating frontmatter: {str(e)}")
            return self._create_error_markdown(str(e))
    
    def _clean_yaml_response(self, yaml_content: str) -> str:
        """Clean up YAML response to ensure it's valid.
        
        Args:
            yaml_content: Raw YAML content from AI response
            
        Returns:
            Cleaned YAML content
        """
        # Fix common issues with AI-generated YAML
        
        # 1. Handle unescaped quotes in strings
        lines = yaml_content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # If the line contains a string with unescaped quotes, wrap the value in single quotes
            if ': "' in line and line.count('"') > 2:
                # Find the position of the first quote after the colon
                colon_pos = line.find(': "')
                if colon_pos != -1:
                    # Split into key and value parts
                    key_part = line[:colon_pos + 2]  # Include the ': "'
                    value_part = line[colon_pos + 2:]
                    
                    # Strip the closing quote if present
                    if value_part.endswith('"'):
                        value_part = value_part[:-1]
                    
                    # Replace problematic characters
                    value_part = value_part.replace('"', '\\"')  # Escape double quotes
                    value_part = value_part.replace('<', '\\<')  # Escape < character
                    value_part = value_part.replace('>', '\\>')  # Escape > character
                    
                    # Reconstruct the line
                    line = f"{key_part}{value_part}\""
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _validate_frontmatter(self, content: str) -> bool:
        """Validate the generated frontmatter against schema."""
        try:
            # Special handling for content with multiple document markers
            clean_content = content
            if content.count("---") > 2:
                logger.warning("Multiple YAML document markers found during validation, cleaning")
                parts = content.split("---")
                if len(parts) >= 3:
                    # Use the part between first and second ---
                    clean_content = f"---\n{parts[1].strip()}\n---"
            
            # Parse YAML with safe_load_all and get first document
            documents = list(yaml.safe_load_all(clean_content))
            if not documents:
                logger.warning("Frontmatter parsed as empty")
                raise ValueError("Empty frontmatter")
                
            parsed_yaml = documents[0]
            if not parsed_yaml:
                logger.warning("First YAML document parsed as empty")
                raise ValueError("Empty frontmatter")
            
            # Get validation rules from prompt config instead of hardcoding
            validation = self.prompt_config.get("validation", {})
            required_fields = validation.get("required_fields", [])
            
            # Check required fields dynamically
            for field in required_fields:
                if field not in parsed_yaml:
                    logger.warning(f"Required field missing in frontmatter: {field}")
                    raise ValueError(f"Required field missing in frontmatter: {field}")
            
            return True
            
        except yaml.YAMLError as e:
            logger.warning(f"Failed to parse frontmatter YAML: {e}")
            raise ValueError(f"Failed to parse frontmatter YAML: {e}")
