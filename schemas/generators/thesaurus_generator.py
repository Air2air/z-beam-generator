#!/usr/bin/env python3
"""
Thesaurus Schema Generator
Parses thesaurus schema definition and delegates to specialized generators
"""

import os
import yaml
import logging
from typing import Dict, Any

class ThesaurusGenerator:
    """
    Generator for thesaurus articles that delegates to specialized generators
    Schema is the ONLY source of truth - NO fallbacks or defaults
    """
    
    def __init__(self, json_ld_generator, tags_generator, metadata_generator, logger=None):
        """
        Initialize with specialized generators
        """
        self.json_ld_generator = json_ld_generator
        self.tags_generator = tags_generator
        self.metadata_generator = metadata_generator
        self.logger = logger or logging.getLogger(__name__)
        self.schema_definition = self._load_schema_definition()
    
    def _load_schema_definition(self) -> Dict[str, Any]:
        """
        Load thesaurus schema definition
        """
        schema_path = os.path.join(
            "schemas", "definitions", "thesaurus_schema_definition.md"
        )
        
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema definition not found: {schema_path}")
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            content = f.read()
            schema_definition = yaml.safe_load(content)
            self.logger.info(f"Loaded thesaurus schema definition")
            return schema_definition
    
    def generate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate thesaurus article and delegate specialized parts
        NO defaults or fallbacks - schema is the only source of truth
        """
        self.logger.info(f"Generating thesaurus article for: {context['subject']}")
        
        # Replace placeholders in schema
        schema_with_values = self._replace_placeholders(context)
        
        # Extract data for specialized generators
        json_ld_data = self._extract_schema_section(schema_with_values, context)
        tags_data = self._extract_schema_section(schema_with_values, context)
        metadata_data = self._extract_schema_section(schema_with_values, context)
        content_data = self._extract_schema_section(schema_with_values, context)
        
        # Generate specialized components using specialized generators
        json_ld = self.json_ld_generator.generate(json_ld_data)
        tags = self.tags_generator.generate(tags_data)
        metadata = self.metadata_generator.generate(metadata_data)
        
        # Return all components for orchestrator to assemble
        return {
            "json_ld": json_ld,
            "tags": tags,
            "metadata": metadata,
            "schema_type": "thesaurus",
            "subject": context["subject"],
            "schema": schema_with_values  # Pass the complete schema for orchestrator
        }
    
    def _replace_placeholders(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Replace placeholders in schema definition with actual values
        NO defaults or fallbacks
        """
        # Create a copy of the schema definition
        schema = self.schema_definition.copy()
        
        # Get term from context
        term = context["subject"]
        
        # Replace placeholders recursively in the schema
        schema = self._replace_placeholders_recursive(
            schema, 
            {"term": term}
        )
        
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
    
    def _extract_schema_section(self, schema: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract complete schema section for use by specialized generators
        NO defaults or fallbacks - pass the raw schema section
        """
        return {
            "schema": schema,
            "context": context,
            "schema_type": "thesaurus",
            "subject": context["subject"]
        }