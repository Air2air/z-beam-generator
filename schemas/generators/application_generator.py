#!/usr/bin/env python3
"""
Application Schema Generator
Parses application schema definition and delegates to specialized generators
ZERO defaults or hardcoded values - everything comes from schema definition
"""

import os
import yaml
import logging
from typing import Dict, Any

class ApplicationGenerator:
    """
    Generator for application articles that delegates to specialized generators
    Schema is the ONLY source of truth - NO fallbacks or defaults
    """
    
    def __init__(self, json_ld_generator, tag_generator, metadata_generator, logger=None):
        """
        Initialize with specialized generators
        
        Args:
            json_ld_generator: Generator for JSON-LD structured data (JSONLDGenerator instance)
            tag_generator: Generator for article tags (DynamicTagGenerator instance)
            metadata_generator: Generator for article metadata (MetadataGenerator instance)
        """
        self.json_ld_generator = json_ld_generator
        self.tag_generator = tag_generator
        self.metadata_generator = metadata_generator
        self.logger = logger or logging.getLogger(__name__)
        self.schema_definition = self._load_schema_definition()
    
    def _load_schema_definition(self) -> Dict[str, Any]:
        """
        Load application schema definition - NO defaults
        
        Raises:
            FileNotFoundError: If schema file doesn't exist
            ValueError: If schema file is invalid or missing required sections
        """
        schema_path = os.path.join(
            "schemas", "definitions", "application_schema_definition.md"
        )
        
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema definition not found: {schema_path}")
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            content = f.read()
            schema_definition = yaml.safe_load(content)
            
            # Validate required schema structure - NO defaults
            if not schema_definition:
                raise ValueError(f"Empty schema definition in {schema_path}")
            
            if "applicationProfile" not in schema_definition:
                raise ValueError(f"Missing 'applicationProfile' section in schema: {schema_path}")
            
            self.logger.info(f"Loaded application schema definition")
            return schema_definition
    
    def generate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate application article and delegate specialized parts
        NO defaults or fallbacks - schema is the only source of truth
        
        Args:
            context: Dictionary with generation context
            
        Returns:
            Dict containing article components
        """
        self.logger.info(f"Generating application article for: {context['subject']}")
        
        # Validate required context
        if "subject" not in context:
            raise ValueError("Missing required context field: subject")
        
        if "author" not in context:
            raise ValueError("Missing required context field: author")
        
        # Replace placeholders in schema
        schema_with_values = self._replace_placeholders(context)
        
        # Extract data needed for specialized generators
        schema_data = self._extract_schema_data(schema_with_values, context)
        
        # Use specialized generators with their interfaces
        # Note: Updated to pass both technical and content configurations
        json_ld = self.json_ld_generator.generate_jsonld(schema_data)
        tags = self.tag_generator.generate_tags(schema_data)
        metadata = self.metadata_generator.generate_metadata(schema_data)
        
        # Return all components for orchestrator to assemble
        return {
            "json_ld": json_ld,
            "tags": tags,
            "metadata": metadata,
            "schema_type": "application",
            "subject": context["subject"],
            "schema": schema_with_values
        }
    
    def _replace_placeholders(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Replace placeholders in schema definition with actual values
        NO defaults or fallbacks
        """
        # Create a copy of the schema definition
        schema = self.schema_definition.copy()
        
        # Get required values from context - NO defaults
        if "subject" not in context:
            raise ValueError("Missing required context field: subject")
        
        if "author" not in context:
            raise ValueError("Missing required context field: author")
        
        application_name = context["subject"]
        author = context["author"]
        
        # Validate required author fields - NO defaults
        required_author_fields = ["name", "title", "country"]
        missing_author_fields = [field for field in required_author_fields if field not in author]
        
        if missing_author_fields:
            raise ValueError(f"Author missing required fields: {missing_author_fields}")
        
        # Replace placeholders recursively in the schema
        replacements = {
            "applicationName": application_name,
            "authorName": author["name"],
            "authorTitle": author["title"], 
            "authorCountry": author["country"]
        }
        
        schema = self._replace_placeholders_recursive(schema, replacements)
        return schema
    
    def _replace_placeholders_recursive(self, obj, replacements: Dict[str, str]):
        """
        Recursively replace placeholders in an object
        NO defaults or fallbacks
        """
        if isinstance(obj, dict):
            return {k: self._replace_placeholders_recursive(v, replacements) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._replace_placeholders_recursive(item, replacements) for item in obj]
        elif isinstance(obj, str):
            result = obj
            for placeholder, value in replacements.items():
                result = result.replace(f"{{{{{placeholder}}}}}", value)
            return result
        else:
            return obj
    
    def _extract_schema_data(self, schema: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract data from schema for specialized generators
        NO defaults or fallbacks - pass raw schema data
        """
        # Validate schema structure - NO defaults
        if "applicationProfile" not in schema:
            raise ValueError("Missing 'applicationProfile' section in schema")
        
        # Pass raw schema data to specialized generators
        return {
            "schema": schema,
            "context": context,
            "schema_type": "application",
            "subject": context["subject"],
            "application_profile": schema["applicationProfile"]
        }