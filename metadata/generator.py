"""Metadata generator for schema-driven article metadata."""

import logging
import json
import re
from typing import Dict, Any, Optional
from api_client import APIClient

logger = logging.getLogger(__name__)

class MetadataGenerator:
    """Generates article metadata based on schema definitions."""
    
    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], ai_provider: str):
        self.context = context
        self.schema = schema
        self.ai_provider = ai_provider
        self.api_client = APIClient(ai_provider)
        
        logger.info(f"Metadata generator initialized for {context.get('article_type')}")
    
    def _validate_response(self, response: str) -> bool:
        """Validate AI response before parsing."""
        # Check for common issues
        if not response or len(response.strip()) < 50:
            logger.error("Response too short")
            return False
        
        if response.strip().startswith('{'):
            logger.error("AI returned JSON instead of YAML")
            return False
        
        if '"type": "string"' in response:
            logger.error("AI returned schema definition instead of actual data")
            return False
        
        if not ':' in response:
            logger.error("Response doesn't appear to be YAML")
            return False
        
        return True
    
    def generate(self) -> Optional[Dict[str, Any]]:
        """Generate metadata using AI provider."""
        try:
            # Build simplified prompt
            prompt = self._build_simple_prompt()
            
            # Generate using API with more tokens
            response = self.api_client.generate(prompt, max_tokens=2000)
            
            if not response:
                logger.error("Failed to generate metadata")
                return None
            
            # Validate response before processing
            if not self._validate_response(response):
                logger.error("Response validation failed")
                return None
            
            # Clean and parse response
            cleaned_response = self._clean_response(response)
            
            # Parse YAML response
            import yaml
            try:
                metadata = yaml.safe_load(cleaned_response)
                if not metadata:
                    logger.error("Empty metadata response")
                    return None
                    
                logger.info("Successfully generated and parsed metadata")
                return metadata
                
            except yaml.YAMLError as e:
                logger.error(f"Failed to parse metadata YAML: {e}")
                logger.error(f"Cleaned response: {repr(cleaned_response)}")
                return None
                
        except Exception as e:
            logger.error(f"Metadata generation failed: {e}", exc_info=True)
            return None
    
    def _clean_response(self, response: str) -> str:
        """Clean API response to extract valid YAML."""
        cleaned = response.strip()
        
        # Remove markdown code blocks
        if cleaned.startswith("```yaml") or cleaned.startswith("```yml"):
            cleaned = cleaned.split('\n', 1)[1]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        return cleaned.strip()
    
    def _build_simple_prompt(self) -> str:
        """Build a simple, clear prompt that avoids schema confusion."""
        subject = self.context.get("subject")
        
        prompt = f"""Generate YAML metadata for a laser cleaning article about {subject}.

Create professional metadata with these fields:

title: "{subject} Laser Cleaning: Complete Technical Guide"
description: "Comprehensive guide to laser cleaning {subject} surfaces, including optimal parameters, techniques, and industry applications"
category: "Materials"
type: "material-profile"
difficulty: "intermediate"
keywords:
  - "{subject.lower()}"
  - "laser cleaning"
  - "surface preparation"
  - "industrial cleaning"
  - "{subject.lower()} oxide removal"
  - "surface treatment"
industries:
  - "Aerospace"
  - "Manufacturing"
  - "Medical Devices"
  - "Electronics"
class: "Metal"
primaryAudience: "Materials Engineers"
secondaryAudience: "Technicians"
schemaOrgType: "TechArticle"
url: "https://z-beam.com/materials/{subject.lower().replace(' ', '-')}"
publishedAt: "{self.context.get('publishedAt', '2024-01-01')}"
lastUpdated: "{self.context.get('lastUpdated', '2024-01-01')}"
author:
  name: "Laser Cleaning Expert"
  title: "Senior Materials Engineer"
  organization: "Z-Beam Technologies"

CRITICAL REQUIREMENTS:
- Return ONLY valid YAML format
- No explanations, no JSON, no markdown formatting
- Use "{subject}" in all relevant fields
- Every field must have meaningful, professional content
- No empty strings, no null values
- Follow the exact structure shown above

Generate the YAML metadata now:"""
        
        return prompt
    
    def _extract_schema_fields(self) -> list:
        """Extract required field names from schema without sending full structure."""
        required_fields = []
        
        # Find the metadata/profile section
        profile_section = None
        for key, value in self.schema.items():
            if "profile" in key.lower() and isinstance(value, dict):
                profile_section = value
                break
        
        if profile_section:
            # Extract field names (not full schema)
            for field_name in profile_section.keys():
                if not field_name.startswith('_'):  # Skip private fields
                    required_fields.append(field_name)
        
        return required_fields
    
    def _build_schema_aware_prompt(self) -> str:
        """Build prompt that's aware of schema fields but doesn't send full schema."""
        subject = self.context.get("subject")
        required_fields = self._extract_schema_fields()
        
        # Create field examples based on schema requirements
        field_examples = []
        for field in required_fields:
            if field == "name":
                field_examples.append(f'name: "{subject}"')
            elif field == "description":
                field_examples.append(f'description: "Comprehensive guide to {subject} laser cleaning"')
            elif field == "keywords":
                field_examples.append(f'keywords: ["{subject.lower()}", "laser cleaning", "surface preparation"]')
            elif field == "category":
                field_examples.append(f'category: "Materials"')
            else:
                # Generic field based on name
                field_examples.append(f'{field}: "{subject} {field}"')
        
        prompt = f"""Generate YAML metadata for a {subject} laser cleaning article.

Required fields to include:
{chr(10).join(field_examples)}

CRITICAL REQUIREMENTS:
- Return ONLY valid YAML format
- Include ALL required fields
- Use "{subject}" appropriately in all fields
- No explanations, no JSON, no markdown
- Professional, technical content
- No empty values

Generate the YAML now:"""
        
        return prompt