"""JSON-LD generator for schema-driven structured data."""

import logging
import json
from typing import Dict, Any, Optional
from api_client import APIClient

logger = logging.getLogger(__name__)

class JsonLdGenerator:
    """Generates JSON-LD structured data based on schema definitions."""
    
    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], ai_provider: str):
        self.context = context
        self.schema = schema
        self.ai_provider = ai_provider
        self.api_client = APIClient(ai_provider)
        
        logger.info(f"JSON-LD generator initialized for {context.get('article_type')}")
    
    def generate(self) -> Optional[Dict[str, Any]]:
        """Generate JSON-LD using AI provider."""
        try:
            # Build schema-driven prompt
            prompt = self._build_schema_driven_jsonld_prompt()
            
            # Generate using API with more tokens
            response = self.api_client.generate(prompt, max_tokens=2500)
            
            if not response:
                logger.error("Failed to generate JSON-LD")
                return None
            
            # Parse JSON response
            try:
                # Clean response (remove potential markdown formatting)
                clean_response = self._clean_json_response(response)
                
                jsonld_data = json.loads(clean_response)
                logger.info("Successfully generated and parsed JSON-LD")
                return jsonld_data
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON-LD response: {e}")
                logger.error(f"Response: {repr(response)}")
                return None
                
        except Exception as e:
            logger.error(f"JSON-LD generation failed: {e}", exc_info=True)
            return None
    
    def _clean_json_response(self, response: str) -> str:
        """Clean JSON response from AI."""
        clean_response = response.strip()
        
        # Remove markdown code blocks
        if clean_response.startswith("```json"):
            clean_response = clean_response[7:]
        if clean_response.startswith("```"):
            clean_response = clean_response[3:]
        if clean_response.endswith("```"):
            clean_response = clean_response[:-3]
        
        return clean_response.strip()
    
    def _build_schema_driven_jsonld_prompt(self) -> str:
        """Build JSON-LD prompt using actual schema structure."""
        subject = self.context.get("subject")
        article_type = self.context.get("article_type")
        
        # Extract schema fields for JSON-LD
        schema_fields = self._extract_schema_fields()
        
        # Build JSON-LD structure from schema
        jsonld_structure = self._build_jsonld_structure(schema_fields, subject)
        
        prompt = f"""Generate JSON-LD structured data for a laser cleaning article about {subject}.

Use this exact structure based on the schema definition:

{jsonld_structure}

CRITICAL REQUIREMENTS:
- Return ONLY valid JSON format
- No explanations, no markdown formatting
- Replace all placeholders with "{subject}"
- Use Schema.org standards
- Include ALL fields shown above
- Professional technical language

Generate the complete JSON-LD now:"""
        
        return prompt
    
    def _extract_schema_fields(self) -> Dict[str, Any]:
        """Extract relevant fields from schema for JSON-LD."""
        schema_fields = {}
        
        # Get all top-level fields from schema
        for field_name, field_def in self.schema.items():
            if isinstance(field_def, dict):
                schema_fields[field_name] = field_def
        
        return schema_fields
    
    def _build_jsonld_structure(self, schema_fields: Dict[str, Any], subject: str) -> str:
        """Build JSON-LD structure from schema fields."""
        # Extract key information from schema
        title = self._get_schema_value(schema_fields, "name", f"{subject} Laser Cleaning")
        description = self._get_schema_value(schema_fields, "description", f"Laser cleaning guide for {subject}")
        keywords = self._get_schema_array(schema_fields, "keywords", [subject.lower(), "laser cleaning"])
        industries = self._get_schema_array(schema_fields, "industries", ["Manufacturing", "Aerospace"])
        author_info = self._get_schema_object(schema_fields, "author", {"name": "Expert", "title": "Engineer"})
        
        # Build comprehensive JSON-LD structure
        jsonld_template = {
            "@context": "https://schema.org",
            "@type": "TechArticle",
            "headline": self._replace_placeholders_in_string(title, subject),
            "description": self._replace_placeholders_in_string(description, subject),
            "keywords": self._replace_placeholders_in_array(keywords, subject),
            "author": {
                "@type": "Person",
                "name": author_info.get("name", "Technical Expert"),
                "jobTitle": author_info.get("title", "Senior Engineer"),
                "worksFor": {
                    "@type": "Organization",
                    "name": "Z-Beam Technologies"
                }
            },
            "publisher": {
                "@type": "Organization",
                "name": "Z-Beam Technologies",
                "url": "https://z-beam.com"
            },
            "datePublished": self.context.get("publishedAt", "2024-01-01"),
            "dateModified": self.context.get("lastUpdated", "2024-01-01"),
            "url": f"https://z-beam.com/materials/{subject.lower().replace(' ', '-')}",
            "articleSection": "Materials",
            "about": {
                "@type": "Thing",
                "name": f"{subject} Laser Cleaning",
                "description": f"Industrial laser cleaning process for {subject} surfaces"
            },
            "applicationCategory": self._replace_placeholders_in_array(industries, subject),
            "mainEntity": {
                "@type": "Product",
                "name": subject,
                "description": f"Material used in industrial applications requiring laser cleaning",
                "category": "Industrial Material",
                "material": subject
            }
        }
        
        # Add schema-specific fields if they exist
        if "outcomes" in schema_fields:
            outcomes = schema_fields["outcomes"].get("example", [])
            if outcomes:
                jsonld_template["mentions"] = []
                for outcome in outcomes[:3]:  # Limit to 3 mentions
                    if isinstance(outcome, dict):
                        jsonld_template["mentions"].append({
                            "@type": "Thing",
                            "name": self._replace_placeholders_in_string(outcome.get("name", ""), subject),
                            "description": self._replace_placeholders_in_string(outcome.get("description", ""), subject)
                        })
        
        return json.dumps(jsonld_template, indent=2)
    
    def _get_schema_value(self, schema_fields: Dict[str, Any], field_name: str, default: str) -> str:
        """Get a string value from schema fields."""
        if field_name in schema_fields:
            field_def = schema_fields[field_name]
            if isinstance(field_def, dict):
                return field_def.get("example", default)
        return default
    
    def _get_schema_array(self, schema_fields: Dict[str, Any], field_name: str, default: list) -> list:
        """Get an array value from schema fields."""
        if field_name in schema_fields:
            field_def = schema_fields[field_name]
            if isinstance(field_def, dict):
                example = field_def.get("example", default)
                if isinstance(example, list):
                    return example
        return default
    
    def _get_schema_object(self, schema_fields: Dict[str, Any], field_name: str, default: dict) -> dict:
        """Get an object value from schema fields."""
        if field_name in schema_fields:
            field_def = schema_fields[field_name]
            if isinstance(field_def, dict):
                example = field_def.get("example", default)
                if isinstance(example, dict):
                    return example
        return default
    
    def _replace_placeholders_in_string(self, value: str, subject: str) -> str:
        """Replace placeholders in a string."""
        if isinstance(value, str):
            value = value.replace("{{materialName}}", subject)
            value = value.replace("{{applicationName}}", subject)
            value = value.replace("{{regionName}}", subject)
            value = value.replace("{{term}}", subject)
        return value
    
    def _replace_placeholders_in_array(self, value: list, subject: str) -> list:
        """Replace placeholders in an array."""
        if isinstance(value, list):
            return [self._replace_placeholders_in_string(str(item), subject) for item in value]
        return value