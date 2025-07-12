"""Simplified metadata generator - SCHEMA-DRIVEN ONLY."""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from api_client import APIClient

logger = logging.getLogger(__name__)

class MetadataGenerator:
    """Generates metadata ONLY from schema definitions."""
    
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
        
        logger.info(f"MetadataGenerator initialized for {self.article_type}: {self.subject}")
    
    def generate(self) -> Optional[Dict[str, Any]]:
        """Generate metadata using schema-driven approach."""
        try:
            prompt = self._build_prompt()
            
            # Use prompt config for parameters
            max_tokens = self.prompt_config.get("parameters", {}).get("max_tokens", 4000)
            response = self.api_client.generate(prompt, max_tokens=max_tokens)
            
            if not response:
                logger.error("Failed to generate metadata")
                return None
            
            # Clean and validate response
            cleaned_response = self._clean_response(response)
            if not self._validate_response(cleaned_response):
                logger.error("Response validation failed")
                return None
            
            metadata = yaml.safe_load(cleaned_response)
            if not metadata:
                logger.error("Empty metadata response")
                return None
            
            # Validate metadata structure
            if not self._validate_metadata(metadata):
                logger.error("Metadata validation failed")
                return None
            
            logger.info("Successfully generated schema-driven metadata")
            return metadata
            
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse metadata YAML: {e}")
            return None
        except Exception as e:
            logger.error(f"Metadata generation failed: {e}", exc_info=True)
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
        """Build prompt using template."""
        schema_template = self._build_schema_template()
        
        if not schema_template:
            logger.error("No schema fields available for metadata generation")
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
        """Build template from schema fields."""
        # Get the profile section based on article type
        profile_key = f"{self.article_type}Profile"
        
        print(f"🔍 DEBUG: Looking for profile key: {profile_key}")
        print(f"🔍 DEBUG: Schema keys: {list(self.schema.keys())}")
        
        if profile_key in self.schema:
            profile = self.schema[profile_key]
            print(f"✅ DEBUG: Found profile with {len(profile)} fields")
            return self._build_schema_template_from_profile(profile)
        else:
            print(f"❌ DEBUG: Profile key {profile_key} not found")
            # Add basic fields as fallback
            template_parts = []
            template_parts.append(f'name: "Laser Cleaning of {self.subject}"')
            template_parts.append(f'description: "Comprehensive guide to {self.subject} laser cleaning applications."')
            template_parts.append(f'keywords: ["laser cleaning {self.subject.lower()}", "{self.subject.lower()} applications"]')
            
            return '\n'.join(template_parts)

    def _build_schema_template_from_profile(self, profile: Dict[str, Any]) -> str:
        """Build template from nested profile structure."""
        template_parts = []
        
        print(f"🔍 DEBUG: Profile keys: {list(profile.keys())}")  # Debug line
        
        for field_name, field_def in profile.items():
            print(f"🔍 DEBUG: Checking field {field_name}: {type(field_def)}")  # Debug line
            
            if isinstance(field_def, dict) and "example" in field_def:
                print(f"✅ DEBUG: Found example in {field_name}")  # Debug line
                example = field_def["example"]
                
                if isinstance(example, str):
                    processed_value = self._replace_placeholders(example)
                    template_parts.append(f'{field_name}: "{processed_value}"')
                elif isinstance(example, list):
                    template_parts.append(f'{field_name}:')
                    for item in example:
                        if isinstance(item, str):
                            processed_item = self._replace_placeholders(item)
                            template_parts.append(f'  - "{processed_item}"')
                        elif isinstance(item, dict):
                            template_parts.append(f'  - ')
                            for key, value in item.items():
                                processed_value = self._replace_placeholders(str(value))
                                template_parts.append(f'    {key}: "{processed_value}"')
                elif isinstance(example, dict):
                    template_parts.append(f'{field_name}:')
                    for key, value in example.items():
                        processed_value = self._replace_placeholders(str(value))
                        template_parts.append(f'  {key}: "{processed_value}"')
        
        print(f"🎯 DEBUG: Template parts: {len(template_parts)}")  # Debug line
        return '\n'.join(template_parts) if template_parts else None
    
    def _build_schema_template_from_root(self) -> str:
        """Build template from root schema structure (fallback)."""
        template_parts = []
        
        for field_name, field_def in self.schema.items():
            if isinstance(field_def, dict) and "example" in field_def:
                example = field_def["example"]
                
                if isinstance(example, str):
                    processed_value = self._replace_placeholders(example)
                    template_parts.append(f'{field_name}: "{processed_value}"')
                elif isinstance(example, list):
                    template_parts.append(f'{field_name}:')
                    for item in example:
                        processed_item = self._replace_placeholders(str(item))
                        template_parts.append(f'  - "{processed_item}"')
                elif isinstance(example, dict):
                    template_parts.append(f'{field_name}:')
                    for key, value in example.items():
                        processed_value = self._replace_placeholders(str(value))
                        template_parts.append(f'  {key}: "{processed_value}"')
        
        return '\n'.join(template_parts) if template_parts else None
    
    def _replace_placeholders(self, value: str) -> str:
        """Replace schema placeholders with subject."""
        placeholder_map = {
            "materialName": self.subject,
            "applicationName": self.subject,
            "regionName": self.subject,
            "term": self.subject
        }
        
        for placeholder, replacement in placeholder_map.items():
            value = value.replace(f"{{{{{placeholder}}}}}", replacement)
        
        return value
    
    def _clean_response(self, response: str) -> str:
        """Clean AI response."""
        cleaned = response.strip()
        
        # Remove markdown code blocks
        if cleaned.startswith("```yaml") or cleaned.startswith("```yml"):
            cleaned = cleaned.split('\n', 1)[1]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        # Remove YAML document separators
        lines = cleaned.split('\n')
        cleaned_lines = []
        for line in lines:
            line_stripped = line.strip()
            if line_stripped == '---' or line_stripped.startswith('#'):
                continue
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    def _validate_response(self, response: str) -> bool:
        """Validate response."""
        validation_config = self.prompt_config.get("validation", {})
        min_length = validation_config.get("min_length", 100)
        
        if not response or len(response.strip()) < min_length:
            logger.error(f"Response too short: {len(response)} characters")
            return False
        
        if response.strip().startswith('{'):
            logger.error("AI returned JSON instead of YAML")
            return False
        
        if '"type": "string"' in response:
            logger.error("AI returned schema instead of data")
            return False
        
        return True
    
    def _validate_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Validate metadata structure."""
        validation_config = self.prompt_config.get("validation", {})
        required_fields = validation_config.get("required_fields", [])
        
        for field in required_fields:
            if field not in metadata:
                logger.error(f"Missing required metadata field: {field}")
                return False
        
        return True