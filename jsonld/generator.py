"""Simplified JSON-LD generator - SCHEMA-DRIVEN ONLY."""

import logging
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from api_client import APIClient

logger = logging.getLogger(__name__)

class JsonLdGenerator:
    """Generates JSON-LD ONLY from schema definitions."""
    
    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], ai_provider: str):
        self.context = context
        self.schema = schema
        self.ai_provider = ai_provider
        self.api_client = APIClient(ai_provider)
        
        # NO DEFAULT VALUES - Must come from context
        self.subject = context["subject"]  # Will fail if not provided
        self.article_type = context["article_type"]  # Will fail if not provided
        
        # Load prompt template
        self.prompt_config = self._load_prompt_template()
        
        logger.info(f"JsonLdGenerator initialized for {self.article_type}: {self.subject}")
    
    def generate(self) -> Optional[Dict[str, Any]]:
        """Generate JSON-LD using schema-driven approach."""
        try:
            prompt = self._build_prompt()
            
            if not prompt:
                logger.error("Failed to build prompt - no schema fields available")
                return None
            
            # Use prompt config for parameters
            max_tokens = self.prompt_config.get("parameters", {}).get("max_tokens", 3000)
            response = self.api_client.generate(prompt, max_tokens=max_tokens)
            
            if not response:
                logger.error("Failed to generate JSON-LD")
                return None
            
            # Clean and parse response
            cleaned_response = self._clean_response(response)
            jsonld_data = json.loads(cleaned_response)
            
            # Validate response
            if not self._validate_jsonld(jsonld_data):
                logger.error("JSON-LD validation failed")
                return None
            
            logger.info("Successfully generated schema-driven JSON-LD")
            return jsonld_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON-LD response: {e}")
            return None
        except Exception as e:
            logger.error(f"JSON-LD generation failed: {e}", exc_info=True)
            return None
    
    def _load_prompt_template(self) -> Dict[str, Any]:
        """Load prompt template from YAML file."""
        try:
            prompt_path = Path(__file__).parent / "prompt.yaml"
            with open(prompt_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load prompt template: {e}")
            return {}
    
    def _build_prompt(self) -> str:
        """Build JSON-LD prompt using template."""
        schema_template = self._build_schema_template()
        
        if not schema_template:
            logger.error("No schema fields available for JSON-LD generation")
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
    
    def _build_schema_template(self) -> str:
        """Build template using schema structure."""
        # Get the profile section based on article type
        profile_key = f"{self.article_type}Profile"
        
        print(f"🔍 DEBUG JSON-LD: Looking for profile key: {profile_key}")
        print(f"🔍 DEBUG JSON-LD: Schema keys: {list(self.schema.keys())}")
        
        if profile_key in self.schema:
            profile = self.schema[profile_key]
            print(f"✅ DEBUG JSON-LD: Found profile with {len(profile)} fields")
            return self._build_schema_template_from_profile(profile)
        else:
            print(f"❌ DEBUG JSON-LD: Profile key {profile_key} not found")
            return None  # NO FALLBACK - FAIL FAST
    
    def _build_schema_template_from_profile(self, profile: Dict[str, Any]) -> str:
        """Build JSON-LD template from profile structure."""
        json_parts = []
        
        # Add context and type
        json_parts.append('"@context": "https://schema.org"')
        json_parts.append('"@type": "TechnicalArticle"')
        
        for field_name, field_def in profile.items():
            if isinstance(field_def, dict) and "example" in field_def:
                example = field_def["example"]
                
                # Map schema fields to JSON-LD properties
                jsonld_field = self._map_to_jsonld_field(field_name)
                if jsonld_field:
                    if isinstance(example, str):
                        processed_value = self._replace_placeholders(example)
                        json_parts.append(f'"{jsonld_field}": "{processed_value}"')
                    elif isinstance(example, list):
                        processed_items = [self._replace_placeholders(str(item)) for item in example]
                        json_parts.append(f'"{jsonld_field}": {processed_items}')
        
        return '{\n  ' + ',\n  '.join(json_parts) + '\n}' if json_parts else None
    
    def _map_to_jsonld_field(self, schema_field: str) -> str:
        """Map schema field names to JSON-LD property names."""
        mapping = {
            "name": "headline",
            "description": "description",
            "keywords": "keywords",
            "industries": "industry",
            "primaryAudience": "audience",
            "author": "author"
        }
        return mapping.get(schema_field)
    
    def _replace_placeholders(self, value: str) -> str:
        """Replace schema placeholders."""
        placeholder_map = {
            "materialName": self.subject,
            "applicationName": self.subject,
            "regionName": self.subject,
            "term": self.subject,
            "{{materialName}}": self.subject,
            "{{applicationName}}": self.subject,
            "{{regionName}}": self.subject,
            "{{term}}": self.subject
        }
        
        for placeholder, replacement in placeholder_map.items():
            value = value.replace(placeholder, replacement)
        
        return value
    
    def _clean_response(self, response: str) -> str:
        """Clean JSON response."""
        print(f"🔍 DEBUG JSON-LD: Raw response:\n{response}")
        
        cleaned = response.strip()
        
        # Remove markdown code blocks
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        # Find JSON content between explanatory text
        lines = cleaned.split('\n')
        json_start = -1
        json_end = -1
        
        for i, line in enumerate(lines):
            if line.strip().startswith('{'):
                json_start = i
                break
        
        for i in range(len(lines)-1, -1, -1):
            if lines[i].strip().endswith('}'):
                json_end = i + 1
                break
        
        if json_start != -1 and json_end != -1:
            cleaned = '\n'.join(lines[json_start:json_end])
        
        print(f"🔍 DEBUG JSON-LD: Cleaned response:\n{cleaned}")
        
        return cleaned.strip()
    
    def _validate_jsonld(self, jsonld_data: Dict[str, Any]) -> bool:
        """Validate JSON-LD structure."""
        validation_config = self.prompt_config.get("validation", {})
        required_fields = validation_config.get("required_fields", [])
        
        for field in required_fields:
            if field not in jsonld_data:
                logger.error(f"Missing required JSON-LD field: {field}")
                return False
        
        # Check Schema.org type
        expected_type = validation_config.get("schema_org_type")
        if expected_type and jsonld_data.get("@type") != expected_type:
            logger.error(f"Invalid Schema.org type: {jsonld_data.get('@type')}")
            return False
        
        return True