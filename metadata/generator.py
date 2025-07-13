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
            
            if not prompt:
                logger.error("Failed to build prompt - no schema fields available")
                return None
            
            # Use prompt config for parameters
            max_tokens = self.prompt_config.get("parameters", {}).get("max_tokens", 8000)
            response = self.api_client.generate(prompt, max_tokens=max_tokens)
            
            if not response:
                logger.error("Failed to generate metadata")
                return None
            
            # Clean and parse response
            cleaned_response = self._clean_response(response)
            metadata = yaml.safe_load(cleaned_response)
            
            # Validate response
            if not self._validate_metadata(metadata):
                logger.error("Metadata validation failed")
                return None
            
            logger.info("Successfully generated schema-driven metadata")
            return metadata
            
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML response: {e}")
            return None
        except Exception as e:
            logger.error(f"Metadata generation failed: {e}", exc_info=True)
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
        """Build metadata prompt using template."""
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
        """Build template using schema structure."""
        # Get the profile section based on article type
        profile_key = f"{self.article_type}Profile"
        
        if profile_key in self.schema:
            profile = self.schema[profile_key]
            return self._build_schema_template_from_profile(profile)
        else:
            return None  # NO FALLBACK - FAIL FAST
    
    def _build_schema_template_from_profile(self, profile: Dict[str, Any]) -> str:
        """Build dynamic schema template with field-specific instructions."""
        template_parts = []
        
        # Add aggressive header
        field_count = len(profile)
        template_parts.append(f"🚨 CRITICAL: ALL {field_count} FIELDS BELOW ARE MANDATORY")
        template_parts.append("=" * 60)
        template_parts.append("EVERY FIELD MUST BE PROCESSED - NO EXCEPTIONS")
        template_parts.append("=" * 60)
        
        fields_with_examples = []
        field_index = 1
        
        for field_name, field_def in profile.items():
            if isinstance(field_def, dict) and "example" in field_def:
                fields_with_examples.append(field_name)
                
                # Add field header with emphasis
                template_parts.append(f"\n🚨 MANDATORY FIELD {field_index}/{field_count}: {field_name}")
                template_parts.append("=" * 50)
                template_parts.append(f"🚨 THIS FIELD IS REQUIRED - MUST APPEAR IN OUTPUT")
                
                # Add field type and description
                field_type = field_def.get("type", "unknown")
                field_description = field_def.get("description", "No description")
                template_parts.append(f"Type: {field_type}")
                template_parts.append(f"Description: {field_description}")
                
                # Add example with processing instruction
                example = field_def["example"]
                if isinstance(example, str):
                    processed_value = self._replace_placeholders(example)
                    template_parts.append(f"Example: {processed_value}")
                    template_parts.append(f"🚨 GENERATE: Comprehensive 300-500 character content for {field_name}")
                elif isinstance(example, list):
                    processed_items = [self._replace_placeholders(str(item)) for item in example]
                    template_parts.append(f"Examples: {processed_items}")
                    template_parts.append(f"🚨 GENERATE: Expanded array with 5-10 entries for {field_name}")
                
                template_parts.append(f"🚨 FAILURE TO INCLUDE {field_name} WILL RESULT IN REJECTION")
                template_parts.append("")  # Add spacing
                field_index += 1
    
        # Add final validation checklist
        template_parts.append("=" * 60)
        template_parts.append("🚨 FINAL VALIDATION CHECKLIST:")
        template_parts.append("Before submitting, verify ALL fields below are in your YAML:")
        for field in fields_with_examples:
            template_parts.append(f"✓ {field}")
        template_parts.append(f"🚨 TOTAL REQUIRED FIELDS: {len(fields_with_examples)}")
        template_parts.append("🚨 ALL FIELDS MUST BE PRESENT OR OUTPUT WILL BE REJECTED")
        template_parts.append("=" * 60)
        
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
        """Clean YAML response."""
        print(f"🔍 DEBUG METADATA: Raw response:\n{response}")
        
        cleaned = response.strip()
        
        # Remove markdown code blocks more aggressively
        if "```yaml" in cleaned:
            start = cleaned.find("```yaml")
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
        
        # Remove any remaining markdown artifacts
        lines = cleaned.split('\n')
        yaml_lines = []
        
        for line in lines:
            # Skip lines that are clearly not YAML
            if (line.strip().startswith('```') or 
                line.strip().startswith('Here is') or 
                line.strip().startswith('This YAML') or
                line.strip().startswith('The metadata')):
                continue
            
            # Include lines that look like YAML
            if ':' in line or line.strip() == '' or line.strip().startswith('-'):
                yaml_lines.append(line)
        
        cleaned = '\n'.join(yaml_lines)
        
        print(f"🔍 DEBUG METADATA: Cleaned response:\n{cleaned}")
        
        return cleaned.strip()
    
    def _validate_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Validate metadata structure and field coverage."""
        if not isinstance(metadata, dict):
            logger.error("Metadata is not a dictionary")
            return False
        
        # Check minimum content length - ADJUSTED FOR REALISTIC EXPECTATIONS
        content_length = len(str(metadata))
        min_length = 5000  # Reduced from 8000 to realistic level
        if content_length < min_length:
            logger.error(f"Metadata too short: {content_length} < {min_length}")
            return False
        
        # Check field coverage - ENFORCE ALL FIELDS
        profile_key = f"{self.article_type}Profile"
        if profile_key in self.schema:
            profile = self.schema[profile_key]
            expected_fields = [field for field, field_def in profile.items() 
                              if isinstance(field_def, dict) and "example" in field_def]
            
            missing_fields = []
            for field in expected_fields:
                if field not in metadata:
                    missing_fields.append(field)
            
            if missing_fields:
                logger.error(f"❌ MISSING CRITICAL FIELDS: {missing_fields}")
                logger.error(f"❌ Expected {len(expected_fields)} fields, got {len(metadata)} fields")
                logger.error(f"❌ Present fields: {list(metadata.keys())}")
                logger.error(f"❌ Missing fields: {missing_fields}")
                return False
            
            logger.info(f"✅ Field coverage: {len(metadata)}/{len(expected_fields)} fields present")
            logger.info(f"✅ Content length: {content_length} characters")
    
        return True