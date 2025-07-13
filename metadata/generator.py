"""Simplified metadata generator - SCHEMA-DRIVEN ONLY."""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from api_client import APIClient
from .yaml_formatter import YAMLFormatter

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
            
            # Clean and parse response using external formatter
            cleaned_response = YAMLFormatter.clean_response(response)
            
            # Validate YAML structure before parsing
            if not YAMLFormatter.validate_yaml_structure(cleaned_response):
                logger.error("YAML structure validation failed")
                return None
            
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
            logger.error(f"❌ Available schema keys: {list(self.schema.keys())}")
            return None  # NO FALLBACK - FAIL FAST
    
    def _build_schema_template_from_profile(self, profile: Dict[str, Any]) -> str:
        """Build dynamic schema template with field-specific instructions."""
        template_parts = []
        
        # Add context-specific header
        template_parts.append(f"🚨 LASER CLEANING CONTEXT: This is about {self.subject} in laser cleaning applications")
        template_parts.append(f"🚨 FOCUS: Industrial surface treatment, rust removal, corrosion control, metal restoration")
        template_parts.append(f"🚨 NOT ABOUT: Programming languages, software, or unrelated topics")
        template_parts.append("=" * 60)
        
        # Add aggressive field header
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
        """Replace schema placeholders with laser cleaning context."""
        # Enhanced context mapping
        placeholder_map = {
            "materialName": f"{self.subject} (laser cleaning applications)",
            "applicationName": f"{self.subject} removal using laser technology",
            "regionName": f"{self.subject} in industrial laser cleaning",
            "term": f"{self.subject} (laser cleaning terminology)",
            "{{materialName}}": f"{self.subject} (laser cleaning applications)",
            "{{applicationName}}": f"{self.subject} removal using laser technology",
            "{{regionName}}": f"{self.subject} in industrial laser cleaning",
            "{{term}}": f"{self.subject} (laser cleaning terminology)"
        }
        
        for placeholder, replacement in placeholder_map.items():
            value = value.replace(placeholder, replacement)
        
        return value
    
    def _validate_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Validate metadata structure and field coverage."""
        if not isinstance(metadata, dict):
            logger.error("Metadata is not a dictionary")
            return False
        
        # Check minimum content length - ADJUST FOR ARTICLE TYPE
        content_length = len(str(metadata))
        if self.article_type == "thesaurus":
            min_length = 2000  # Thesaurus entries are naturally shorter
        elif self.article_type == "region":
            min_length = 2500  # Region articles are medium length - REDUCED
        else:
            min_length = 5000  # Application articles are longer
            
        if content_length < min_length:
            logger.error(f"Metadata too short: {content_length} < {min_length}")
            return False
        
        # Check field coverage - handle different profile naming conventions
        profile_keys = [
            f"{self.article_type}Profile",
            "termProfile",
            f"{self.article_type}_profile",
            f"{self.article_type.title()}Profile"
        ]
        
        profile = None
        for key in profile_keys:
            if key in self.schema:
                profile = self.schema[key]
                break
        
        if profile:
            expected_fields = [field for field, field_def in profile.items() 
                              if isinstance(field_def, dict) and "example" in field_def]
            
            missing_fields = []
            for field in expected_fields:
                if field not in metadata:
                    missing_fields.append(field)
            
            if missing_fields:
                logger.error(f"❌ MISSING CRITICAL FIELDS: {missing_fields}")
                return False
            
            logger.info(f"✅ Field coverage: {len(metadata)}/{len(expected_fields)} fields present")

        return True