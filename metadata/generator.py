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
    
    def generate(self) -> Optional[Dict[str, Any]]:
        """Generate metadata using AI provider."""
        try:
            # Use best practices prompt instead of schema-driven for now
            prompt = self._build_best_practices_prompt()
            
            # Generate using API with more tokens for complex content
            response = self.api_client.generate(prompt, max_tokens=3000)
            
            if not response:
                logger.error("Failed to generate metadata")
                return None
            
            # Validate and clean response
            if not self._validate_response(response):
                logger.error("Response validation failed")
                return None
            
            cleaned_response = self._clean_response(response)
            
            # Debug the cleaned response
            logger.info(f"Cleaned response preview: {cleaned_response[:200]}...")
            
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
                logger.error(f"Full cleaned response: {repr(cleaned_response)}")
                return None
                
        except Exception as e:
            logger.error(f"Metadata generation failed: {e}", exc_info=True)
            return None
    
    def _validate_response(self, response: str) -> bool:
        """Validate AI response before parsing."""
        if not response or len(response.strip()) < 50:
            logger.error("Response too short")
            return False
        
        if response.strip().startswith('{'):
            logger.error("AI returned JSON instead of YAML")
            return False
        
        if '"type": "string"' in response:
            logger.error("AI returned schema definition instead of actual data")
            return False
        
        return True
    
    def _clean_response(self, response: str) -> str:
        """Clean AI response to extract valid YAML."""
        cleaned = response.strip()
        
        # Remove markdown code blocks
        if cleaned.startswith("```yaml") or cleaned.startswith("```yml"):
            cleaned = cleaned.split('\n', 1)[1]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        # Remove YAML document separators that cause parsing issues
        lines = cleaned.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            # Skip YAML document separators and comments
            if line_stripped == '---' or line_stripped.startswith('#'):
                continue
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    def _build_schema_driven_prompt(self) -> str:
        """Build prompt using actual schema structure."""
        subject = self.context.get("subject")
        article_type = self.context.get("article_type")
        
        # Extract ALL schema fields and their structures
        schema_fields = self._extract_schema_fields()
        
        # Build examples from schema
        field_examples = self._build_field_examples(schema_fields, subject)
        
        prompt = f"""Generate YAML metadata for a laser cleaning article about {subject}.

Use this exact structure based on the schema definition:

{field_examples}

CRITICAL REQUIREMENTS:
- Use the EXACT field names from the schema
- Replace all placeholders with "{subject}"
- Include ALL fields shown above
- Return ONLY valid YAML format
- No explanations, no JSON, no markdown
- Every field must have meaningful content

Generate the complete YAML now:"""
        
        return prompt
    
    def _extract_schema_fields(self) -> Dict[str, Any]:
        """Extract all field definitions from schema."""
        schema_fields = {}
        
        # Get all top-level fields from schema
        for field_name, field_def in self.schema.items():
            if isinstance(field_def, dict):
                schema_fields[field_name] = field_def
        
        return schema_fields
    
    def _build_field_examples(self, schema_fields: Dict[str, Any], subject: str) -> str:
        """Build YAML examples from schema field definitions."""
        examples = []
        
        for field_name, field_def in schema_fields.items():
            if isinstance(field_def, dict):
                # Get example from schema
                example = field_def.get("example")
                if example is not None:
                    # Replace placeholders
                    example_str = self._replace_placeholders(example, subject)
                    examples.append(f"{field_name}: {example_str}")
        
        return "\n".join(examples)
    
    def _replace_placeholders(self, value: Any, subject: str) -> str:
        """Replace schema placeholders with actual subject."""
        if isinstance(value, str):
            # Replace common placeholders
            value = value.replace("{{materialName}}", subject)
            value = value.replace("{{applicationName}}", subject)
            value = value.replace("{{regionName}}", subject)
            value = value.replace("{{term}}", subject)
            return f'"{value}"'
        elif isinstance(value, list):
            # Handle arrays
            replaced_items = []
            for item in value:
                if isinstance(item, str):
                    item = item.replace("{{materialName}}", subject)
                    item = item.replace("{{applicationName}}", subject)
                    item = item.replace("{{regionName}}", subject)
                    item = item.replace("{{term}}", subject)
                    replaced_items.append(f'"{item}"')
                elif isinstance(item, dict):
                    # Handle objects in arrays
                    replaced_items.append(self._dict_to_yaml_string(item, subject))
                else:
                    replaced_items.append(str(item))
            return f"[{', '.join(replaced_items)}]"
        elif isinstance(value, dict):
            return self._dict_to_yaml_string(value, subject)
        else:
            return str(value)
    
    def _dict_to_yaml_string(self, obj: Dict[str, Any], subject: str) -> str:
        """Convert dict to YAML string representation."""
        yaml_lines = []
        for key, val in obj.items():
            if isinstance(val, str):
                val = val.replace("{{materialName}}", subject)
                val = val.replace("{{applicationName}}", subject)
                val = val.replace("{{regionName}}", subject)
                val = val.replace("{{term}}", subject)
                yaml_lines.append(f'  {key}: "{val}"')
            elif isinstance(val, list):
                yaml_lines.append(f'  {key}: {self._replace_placeholders(val, subject)}')
            else:
                yaml_lines.append(f'  {key}: {val}')
        return "{\n" + "\n".join(yaml_lines) + "\n}"
    
    def _build_best_practices_prompt(self) -> str:
        """Build prompt using metadata best practices."""
        subject = self.context.get("subject")
        article_type = self.context.get("article_type")
        
        prompt = f"""Generate professional YAML metadata for a laser cleaning article about {subject}.

Return a single YAML document with these fields:

title: "{subject} Laser Cleaning: Complete Technical Guide"
slug: "{subject.lower().replace(' ', '-')}-laser-cleaning-guide"
description: "Comprehensive guide to laser cleaning {subject} surfaces including optimal parameters, techniques, and industrial applications"
excerpt: "Professional laser cleaning techniques for {subject} surfaces in aerospace, manufacturing, and medical device industries"
metaDescription: "Expert guide to {subject.lower()} laser cleaning: techniques, parameters, safety considerations, and industrial applications for materials engineers"
keywords:
  - "{subject.lower()} laser cleaning"
  - "laser surface treatment"
  - "industrial cleaning"
  - "{subject.lower()} oxide removal"
  - "precision cleaning"
  - "surface preparation"
tags:
  - "{subject.lower()}"
  - "laser-cleaning"
  - "surface-preparation"
  - "industrial-processes"
  - "materials-engineering"
category: "Materials"
type: "technical-guide"
articleType: "material-profile"
difficulty: "intermediate"
audience: "materials-engineers"
primaryAudience: "Materials Engineers"
secondaryAudience: "Manufacturing Technicians"
publishedAt: "{self.context.get('publishedAt', '2024-01-15T10:00:00Z')}"
lastModified: "{self.context.get('lastUpdated', '2024-01-15T10:00:00Z')}"
author:
  name: "Dr. Sarah Chen"
  title: "Senior Materials Engineer"
  organization: "Z-Beam Technologies"
  specialization: "Laser Surface Processing"
readingTime: "8 minutes"
wordCount: 2400
tableOfContents: true
applications:
  - "Aerospace Components"
  - "Medical Devices"
  - "Electronics Manufacturing"
  - "Automotive Parts"
industries:
  - "Aerospace"
  - "Medical"
  - "Electronics"
  - "Automotive"
  - "Manufacturing"
laserSpecs:
  wavelength: "1064nm"
  pulseEnergy: "0.5-2.0mJ"
  scanSpeed: "5-12mm/s"
  applications: "{subject} surface cleaning"
schemaType: "TechArticle"
url: "https://z-beam.com/materials/{subject.lower().replace(' ', '-')}"
canonicalUrl: "https://z-beam.com/materials/{subject.lower().replace(' ', '-')}-laser-cleaning"
featured: false
draft: false
language: "en"
region: "global"
lastReviewed: "{self.context.get('lastUpdated', '2024-01-15')}"

CRITICAL REQUIREMENTS:
- Return ONLY valid YAML format
- NO document separators (---)
- NO comments (# lines)
- NO markdown formatting
- NO explanations
- Replace {subject} with "{subject}"
- Use professional technical language

Generate the YAML metadata now:"""
        
        return prompt