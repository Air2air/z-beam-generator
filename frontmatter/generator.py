"""Main frontmatter generator class."""

import logging
import yaml
import re
from pathlib import Path
from typing import Dict, Any, Optional

from api_client import APIClient
from utils.yaml_formatter import YAMLFormatter
from frontmatter.template_builder import SchemaTemplateBuilder
from frontmatter.schema_parser import SchemaParser
from frontmatter.content_generator import DefaultContentGenerator

logger = logging.getLogger(__name__)

class FrontmatterGenerator:
    """Generates frontmatter from schema definitions with support for new schema structures."""
    
    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], ai_provider: str):
        self.context = context
        self.schema = schema
        self.ai_provider = ai_provider
        self.api_client = APIClient(ai_provider)
        
        # NO DEFAULT VALUES - Must come from context
        self.subject = context["subject"]  # Will fail if not provided
        self.article_type = context["article_type"]  # Will fail if not provided
        
        # Initialize helpers
        self.schema_parser = SchemaParser(self.schema, self.article_type, self.subject)
        self.template_builder = SchemaTemplateBuilder(self.schema, self.article_type, self.subject)
        self.content_generator = DefaultContentGenerator(self.schema, self.article_type, self.subject)
        
        # Load prompt template
        self.prompt_config = self._load_prompt_template()
        
        logger.info(f"FrontmatterGenerator initialized for {self.article_type}: {self.subject}")
    
    def generate(self) -> Optional[str]:
        """Generate comprehensive frontmatter."""
        try:
            prompt = self._build_prompt()
            
            # Generate content using API
            response = self.api_client.generate(prompt)
            
            # Clean and format the response
            frontmatter = YAMLFormatter.clean_response(response)
            
            # Check if we need to expand the content
            if len(frontmatter) < 3500:
                logger.warning(f"Frontmatter too short ({len(frontmatter)} chars), expanding content...")
                try:
                    # Apply extract_first_document_only before expanding
                    frontmatter = YAMLFormatter.extract_first_document_only(frontmatter)
                    expanded = self._expand_frontmatter_content(frontmatter)
                    logger.info(f"Expanded to {len(expanded)} characters")
                    frontmatter = expanded
                except Exception as e:
                    logger.error(f"Error expanding frontmatter: {e}")
                    # Continue with original frontmatter
        
            # Validate and process the frontmatter
            try:
                # Apply extract_first_document_only again before parsing
                clean_frontmatter = YAMLFormatter.extract_first_document_only(frontmatter)
                # Test parse to ensure it's valid
                parsed = yaml.safe_load(YAMLFormatter.extract_first_document_only(
                    re.sub(r'^---\s*|\s*---$', '', clean_frontmatter)
                ))
                
                # Parse the YAML for dynamic modification
                clean_yaml = YAMLFormatter.extract_first_document_only(frontmatter)
                parsed_yaml = yaml.safe_load(clean_yaml)
                
                # Remove any fields that aren't in the schema definition
                # This ensures frontmatter adapts when schema changes
                allowed_fields = self.schema_parser.get_schema_defined_fields()
                
                # If we have a valid list of allowed fields, enforce it
                if allowed_fields:
                    # Get all keys at the root level of the frontmatter
                    frontmatter_keys = list(parsed_yaml.keys())
                    
                    # Check each key against the schema
                    for key in frontmatter_keys:
                        if key not in allowed_fields and key != 'name':  # Always keep 'name'
                            logger.info(f"🧬 Adapting schema: Removing '{key}' not in schema definition")
                            del parsed_yaml[key]
                
                # For testing: remove specific fields if requested
                test_remove_fields = self.context.get('test_remove_fields', [])
                for field in test_remove_fields:
                    if field in parsed_yaml:
                        logger.info(f"🧪 TEST: Removing '{field}' field from frontmatter")
                        del parsed_yaml[field]
                        
                # For testing: add specific fields if requested
                test_add_fields = self.context.get('test_add_fields', {})
                for field_name, field_value in test_add_fields.items():
                    logger.info(f"🧪 TEST: Adding '{field_name}' field to frontmatter")
                    parsed_yaml[field_name] = field_value
                
                # Ensure all required fields are present
                self._ensure_required_fields_present(parsed_yaml)
                
                # Convert back to YAML
                frontmatter = yaml.dump(parsed_yaml, sort_keys=False, default_flow_style=False)
                
                return frontmatter
                
            except yaml.YAMLError as e:
                logger.error(f"Failed to parse YAML response: {e}")
                return None
            
        except Exception as e:
            logger.error(f"Frontmatter generation failed: {e}", exc_info=True)
            return None
    
    def _load_prompt_template(self) -> Dict[str, Any]:
        """Load prompt template from local YAML file."""
        try:
            prompt_path = Path(__file__).parent / "prompt.yaml"
            with open(prompt_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load prompt template: {e}")
            return {}
    
    def _build_prompt(self) -> str:
        """Build frontmatter prompt using template."""
        schema_template = self.template_builder.build_schema_template()
        
        if not schema_template:
            logger.error("No schema fields available for frontmatter generation")
            return None
        
        # Use template from prompt config
        template = self.prompt_config.get("template", "")
        if not template:
            logger.error("No prompt template found")
            return None
        
        return template.format(
            article_type=self.article_type,
            subject=self.subject,
            schema_template=schema_template
        )
    
    def _expand_frontmatter_content(self, frontmatter: str) -> str:
        """Expand frontmatter content to meet minimum length requirements."""
        try:
            from frontmatter.utils import extract_yaml_content
            
            # Parse the YAML
            yaml_content = extract_yaml_content(frontmatter)
            parsed = yaml.safe_load(yaml_content)
            original_length = len(frontmatter)
            
            logger.info(f"Expanding frontmatter content from {original_length} characters")
            
            # 1. Expand description if needed
            if "description" in parsed and isinstance(parsed["description"], str):
                current_length = len(parsed["description"])
                # Get threshold from schema if available
                profile = self.schema_parser.get_profile()
                min_length = profile.get("generatorConfig", {}).get("descriptionMinLength", 500)
                
                if current_length < min_length:
                    logger.info(f"Expanding description from {current_length} characters")
                    parsed["description"] = self.content_generator.expand_description(parsed["description"])
            
            # 2. Add missing core fields based on schema
            self._add_missing_fields(parsed)
            
            # Convert back to YAML
            expanded_frontmatter = yaml.dump(parsed, sort_keys=False, default_flow_style=False)
            expanded_length = len(expanded_frontmatter)
            
            logger.info(f"Expanded frontmatter from {original_length} to {expanded_length} characters")
            
            return expanded_frontmatter
            
        except Exception as e:
            logger.error(f"Error expanding frontmatter: {e}")
            return YAMLFormatter.extract_first_document_only(frontmatter)
    
    def _add_missing_fields(self, parsed: dict) -> None:
        """Add missing fields based on schema definition dynamically."""
        # Get required fields from schema
        required_fields = self.schema_parser.get_required_fields()
        
        # Add missing fields that are required
        for field_name in required_fields:
            if field_name not in parsed:
                logger.info(f"Adding missing required field: {field_name}")
                
                # Get field definition from schema
                field_def = self.schema_parser.get_field_definition(field_name)
                
                if not field_def:
                    logger.warning(f"No schema definition found for field: {field_name}")
                    continue
                    
                # Generate content based on field type and schema definition
                field_type = self.schema_parser.get_field_type(field_name)
                
                # Add field with dynamic value based on schema definition
                parsed[field_name] = self.content_generator.generate_default_value(field_name, field_def, field_type)
    
    def _ensure_required_fields_present(self, parsed_yaml: dict) -> None:
        """Ensure all schema-required fields are present in the frontmatter."""
        # Get all required fields from schema validation section if available
        profile = self.schema_parser.get_profile()
        validation_required = []
        
        if profile and "validation" in profile and "requiredFields" in profile["validation"]:
            validation_required = profile["validation"]["requiredFields"]
        
        # Combine with standard required fields
        required_fields = list(set(validation_required + self.schema_parser.get_required_fields()))
        
        for field_name in required_fields:
            if field_name not in parsed_yaml:
                logger.warning(f"🚨 Required field missing: {field_name}")
                
                # Get field definition
                field_def = self.schema_parser.get_field_definition(field_name)
                if not field_def:
                    logger.error(f"No definition found for required field: {field_name}")
                    continue
                    
                # Generate default value for missing field
                field_type = self.schema_parser.get_field_type(field_name)
                parsed_yaml[field_name] = self.content_generator.generate_default_value(field_name, field_def, field_type)
                logger.info(f"Added missing required field: {field_name}")
