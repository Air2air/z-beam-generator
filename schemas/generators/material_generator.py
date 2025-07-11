#!/usr/bin/env python3
"""
Material Schema Generator
Generates article components based on material schema definition
"""

import logging
from typing import Dict, Any, List, Optional

class MaterialGenerator:
    """
    Generator for material articles based on schema definition
    """
    
    def __init__(self, schemas=None, author_profiles=None, json_ld_generator=None, 
                 tags_generator=None, metadata_generator=None, api_client=None, logger=None):
        """Initialize the material generator."""
        # Store all dependencies as instance variables
        self.schemas = schemas or {}
        self.author_profiles = author_profiles or []
        self.json_ld_generator = json_ld_generator
        self.tags_generator = tags_generator
        self.metadata_generator = metadata_generator
        self.api_client = api_client
        self.logger = logger or logging.getLogger(__name__)
        
        # Log initialization
        self.logger.info("Loaded material schema definition")
    
    def _get_author(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get author from context or profiles"""
        # If author already in context, use it
        if "author" in context:
            return context["author"]
            
        # Otherwise, get author by ID
        author_id = context.get("author_id")
        if not author_id:
            # No fallbacks - return empty
            self.logger.warning("No author_id specified in context")
            return {}
            
        # Adjust for 0-indexed list vs 1-indexed input
        try:
            index = int(author_id) - 1
        except (ValueError, TypeError):
            self.logger.warning(f"Invalid author_id: {author_id}")
            return {}
            
        # Get author if available
        if 0 <= index < len(self.author_profiles):
            return self.author_profiles[index]
        
        # No fallbacks - return empty
        self.logger.warning(f"Author ID {author_id} not found")
        return {}
    
    def _generate_section_content(self, subject: str, section_name: str, section_schema: Dict[str, Any]) -> str:
        """Generate content for a specific section using the schema definition - NO fallbacks"""
        # Check for API client
        if not self.api_client:
            raise RuntimeError(f"Cannot generate {section_name} content: No API client available")
        
        # Extract section prompt from schema
        prompt_template = section_schema.get("prompt")
        if not prompt_template:
            raise RuntimeError(f"No prompt defined in schema for section: {section_name}")
        
        # Format prompt with subject
        prompt = prompt_template.replace("{subject}", subject)
    
        # Make API call to generate section content
        self.logger.info(f"Generating {section_name} content for {subject}")
        content = self.api_client.call(prompt, f"generate_{section_name}")
    
        if not content.strip():
            raise RuntimeError(f"API returned empty content for {section_name}")
        
        return content.strip()
        
    def generate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate all components for a material article based on schema"""
        # Load material schema
        schema = self.schemas.get("material", {})
        subject = context.get("subject", "")
        
        if not subject:
            raise ValueError("Subject is required for material article generation")
        
        author = self._get_author(context)
        
        # Prepare data for metadata generation
        metadata_data = {
            "context": context,
            "schema": schema,
            "schema_type": "material"
        }
        
        # Generate metadata
        metadata = {}
        if self.metadata_generator:
            try:
                metadata = self.metadata_generator.generate(metadata_data)
            except Exception as e:
                self.logger.error(f"Error generating metadata: {e}")
                raise
    
        # Prepare data for JSON-LD generation
        json_ld_data = {
            "context": context,
            "schema": schema,
            "schema_type": "material",
            "metadata": metadata,
            "author": author
        }
        
        # Generate JSON-LD
        json_ld = ""
        if self.json_ld_generator:
            try:
                json_ld = self.json_ld_generator.generate(json_ld_data)
            except Exception as e:
                self.logger.error(f"Error generating JSON-LD: {e}")
                raise
    
        # Prepare data for tags generation
        tags_data = {
            "context": context,
            "schema": schema,
            "schema_type": "material",
            "metadata": metadata,
            "author": author
        }
        
        # Generate tags
        tags = []
        if self.tags_generator:
            try:
                tags = self.tags_generator.generate(tags_data)
            except Exception as e:
                self.logger.error(f"Error generating tags: {e}")
                raise
    
        # Generate content for each required section defined in the schema
        content_sections = {}
        sections_schema = schema.get("sections", {})
        
        # Check if we have sections defined
        if not sections_schema:
            raise ValueError("No sections defined in material schema")
        
        # Process each section - especially focus on Overview section which is required
        for section_name, section_schema in sections_schema.items():
            # Skip non-required sections
            if not section_schema.get("required", False):
                continue
                
            # Generate content for this section
            section_content = self._generate_section_content(subject, section_name, section_schema)
            
            # Ensure we have content - no silent failures
            if not section_content:
                raise ValueError(f"Failed to generate content for required section: {section_name}")
            
            # Store the content
            content_sections[section_name] = section_content
    
        # Ensure we have all required sections
        required_sections = ["overview", "properties", "applications", "specifications"]
        for section in required_sections:
            if section not in content_sections:
                raise ValueError(f"Missing required section: {section}")
    
        # Return all components
        return {
            "components": {
                "metadata": metadata,
                "tags": tags,
                "json_ld": json_ld,
                "schema_type": "material",
                "subject": subject,
                "schema": schema,
                "content_sections": content_sections,
            }
        }