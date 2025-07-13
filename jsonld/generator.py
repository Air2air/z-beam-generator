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
            max_tokens = self.prompt_config.get("parameters", {}).get("max_tokens", 4000)
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
        # Handle different profile naming conventions
        profile_keys = [
            f"{self.article_type}Profile",  # Standard: "applicationProfile"
            "termProfile",                   # Thesaurus: "termProfile"
            f"{self.article_type}_profile",  # Snake case
            f"{self.article_type.title()}Profile"  # Title case
        ]
        
        profile = None
        for key in profile_keys:
            if key in self.schema:
                profile = self.schema[key]
                logger.info(f"✅ Found profile using key: {key}")
                break
        
        if profile:
            return self._build_schema_template_from_profile(profile)
        else:
            logger.error(f"❌ No profile found. Tried keys: {profile_keys}")
            return None
    
    def _build_schema_template_from_profile(self, profile: Dict[str, Any]) -> str:
        """Build dynamic schema template with field-specific instructions."""
        template_parts = []
        
        # Add header with field count
        field_count = len(profile)
        template_parts.append(f"TOTAL FIELDS FOR JSON-LD MAPPING: {field_count}")
        template_parts.append("=" * 50)
        
        field_index = 1
        for field_name, field_def in profile.items():
            if isinstance(field_def, dict) and "example" in field_def:
                # Add field header
                template_parts.append(f"\nFIELD {field_index}/{field_count}: {field_name}")
                template_parts.append("-" * 30)
                
                # Add field type and description
                field_type = field_def.get("type", "unknown")
                field_description = field_def.get("description", "No description")
                template_parts.append(f"Type: {field_type}")
                template_parts.append(f"Description: {field_description}")
                
                # Add example with JSON-LD mapping instruction
                example = field_def["example"]
                if isinstance(example, str):
                    processed_value = self._replace_placeholders(example)
                    template_parts.append(f"Example: {processed_value}")
                    template_parts.append(f"REQUIRED: Map {field_name} to JSON-LD property")
                elif isinstance(example, list):
                    processed_items = [self._replace_placeholders(str(item)) for item in example]
                    template_parts.append(f"Examples: {processed_items}")
                    template_parts.append(f"REQUIRED: Map ALL {field_name} values to JSON-LD array")
                
                template_parts.append("")  # Add spacing
                field_index += 1
        
        # Add validation footer
        template_parts.append("=" * 50)
        template_parts.append(f"JSON-LD MAPPING: Map ALL {field_count} fields above to JSON-LD properties")
        template_parts.append("ALL FIELDS MUST BE REPRESENTED IN JSON-LD OUTPUT")
        
        return '\n'.join(template_parts)
    
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
        
        # Remove markdown code blocks more aggressively
        if "```json" in cleaned:
            start = cleaned.find("```json")
            if start != -1:
                start = cleaned.find('\n', start) + 1
                end = cleaned.rfind('```')
                if end > start:
                    cleaned = cleaned[start:end]
        elif "```" in cleaned:
            start = cleaned.find("```")
            if start != -1:
                start = cleaned.find('\n', start) + 1
                end = cleaned.rfind('```')
                if end > start:
                    cleaned = cleaned[start:end]
        
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