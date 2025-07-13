"""Simplified tags generator - SCHEMA-DRIVEN ONLY."""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from api_client import APIClient

logger = logging.getLogger(__name__)

class TagsGenerator:
    """Generates tags ONLY from schema definitions."""
    
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
        
        logger.info(f"TagsGenerator initialized for {self.article_type}: {self.subject}")
    
    def generate(self) -> Optional[List[str]]:
        """Generate tags using schema-driven approach."""
        try:
            prompt = self._build_prompt()
            
            if not prompt:
                logger.error("Failed to build prompt - no schema fields available")
                return None
            
            # Use prompt config for parameters
            max_tokens = self.prompt_config.get("parameters", {}).get("max_tokens", 3000)
            response = self.api_client.generate(prompt, max_tokens=max_tokens)
            
            if not response:
                logger.error("Failed to generate tags")
                return None
            
            # Clean and parse response
            tags = self._clean_response(response)
            
            # Validate response
            if not self._validate_tags(tags):
                logger.error("Tags validation failed")
                return None
            
            logger.info(f"Successfully generated {len(tags)} schema-driven tags")
            return tags
            
        except Exception as e:
            logger.error(f"Tags generation failed: {e}", exc_info=True)
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
        """Build tags prompt using template."""
        schema_template = self._build_schema_template()
        
        if not schema_template:
            logger.error("No schema fields available for tags generation")
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
        
        print(f"🔍 DEBUG TAGS: Looking for profile key: {profile_key}")
        print(f"🔍 DEBUG TAGS: Schema keys: {list(self.schema.keys())}")
        
        if profile_key in self.schema:
            profile = self.schema[profile_key]
            print(f"✅ DEBUG TAGS: Found profile with {len(profile)} fields")
            return self._build_schema_template_from_profile(profile)
        else:
            print(f"❌ DEBUG TAGS: Profile key {profile_key} not found")
            return None  # NO FALLBACK - FAIL FAST
    
    def _build_schema_template_from_profile(self, profile: Dict[str, Any]) -> str:
        """Build dynamic schema template with field-specific instructions."""
        template_parts = []
        
        # Add header with field count
        field_count = len(profile)
        template_parts.append(f"TOTAL FIELDS FOR TAG EXTRACTION: {field_count}")
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
                
                # Add example with tag extraction instruction
                example = field_def["example"]
                if isinstance(example, str):
                    processed_value = self._replace_placeholders(example)
                    template_parts.append(f"Example: {processed_value}")
                    template_parts.append(f"REQUIRED: Extract 3-5 technical tags from {field_name}")
                elif isinstance(example, list):
                    processed_items = [self._replace_placeholders(str(item)) for item in example]
                    template_parts.append(f"Examples: {processed_items}")
                    template_parts.append(f"REQUIRED: Extract tags from ALL examples in {field_name}")
                
                template_parts.append("")  # Add spacing
                field_index += 1
        
        # Add validation footer
        template_parts.append("=" * 50)
        template_parts.append(f"TAG EXTRACTION: Generate tags from ALL {field_count} fields above")
        template_parts.append("MINIMUM 3-5 TAGS PER FIELD - NO FIELD SHOULD BE IGNORED")
        
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
    
    def _clean_response(self, response: str) -> List[str]:
        """Clean and parse tags from response."""
        print(f"🔍 DEBUG TAGS: Raw response:\n{response}")
        
        # Remove markdown code blocks
        cleaned = response.strip()
        if "```" in cleaned:
            start = cleaned.find('```')
            if start != -1:
                start = cleaned.find('\n', start) + 1
                end = cleaned.rfind('```')
                if end > start:
                    cleaned = cleaned[start:end]
        
        # Remove explanatory text
        lines = cleaned.split('\n')
        tags = []
        
        for line in lines:
            line = line.strip()
            # Skip explanatory lines
            if (not line or 
                line.startswith('Here are') or 
                line.startswith('These tags') or
                line.startswith('#') or
                line.startswith('Tags:') or
                line.startswith('Generated')):
                continue
                
            # Remove prefixes and clean
            tag = line.lstrip('0123456789.- •*')
            tag = tag.strip()
            
            # Valid tag check: must be kebab-case format
            if tag and len(tag) > 2 and '-' in tag and tag.replace('-', '').replace('_', '').isalnum():
                tags.append(tag)
        
        print(f"🔍 DEBUG TAGS: Extracted {len(tags)} clean tags: {tags[:10]}...")
        
        return tags
    
    def _validate_tags(self, tags: List[str]) -> bool:
        """Validate tags."""
        validation_config = self.prompt_config.get("validation", {})
        min_tags = validation_config.get("min_tags", 75)
        max_tags = validation_config.get("max_tags", 100)
        
        if len(tags) < min_tags:
            logger.error(f"Too few tags: {len(tags)} < {min_tags}")
            return False
        
        if len(tags) > max_tags:
            logger.warning(f"Too many tags: {len(tags)} > {max_tags}, truncating")
            tags = tags[:max_tags]
        
        return True