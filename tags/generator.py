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
            max_tokens = self.prompt_config.get("parameters", {}).get("max_tokens", 2000)
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
        
        if profile_key in self.schema:
            profile = self.schema[profile_key]
            return self._build_schema_template_from_profile(profile)
        else:
            # ✅ NO FALLBACK - FAIL FAST
            return None
    
    def _build_schema_template_from_profile(self, profile: Dict[str, Any]) -> str:
        """Build template from profile structure."""
        template_parts = []
        
        for field_name, field_def in profile.items():
            if isinstance(field_def, dict) and "example" in field_def:
                example = field_def["example"]
                
                if isinstance(example, str):
                    processed_value = self._replace_placeholders(example)
                    template_parts.append(f'{field_name}: "{processed_value}"')
                elif isinstance(example, list):
                    processed_items = [self._replace_placeholders(str(item)) for item in example]
                    template_parts.append(f'{field_name}: {processed_items}')
        
        return '\n'.join(template_parts) if template_parts else None
    
    def _clean_response(self, response: str) -> List[str]:
        """Clean and parse tags from response."""
        print(f"🔍 DEBUG TAGS: Raw response:\n{response}")
        
        # Remove markdown code blocks
        cleaned = response.strip()
        if cleaned.startswith("```") or "```" in cleaned:
            # Extract content between code blocks
            start = cleaned.find('```')
            if start != -1:
                start = cleaned.find('\n', start) + 1
                end = cleaned.rfind('```')
                if end > start:
                    cleaned = cleaned[start:end]
    
        # Extract tags from various formats
        tags = []
        lines = cleaned.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('Here are'):
                continue
                
            # Remove prefixes and clean
            tag = line.lstrip('0123456789.- •*')
            tag = tag.strip()
            
            # Valid tag check: must be kebab-case format
            if tag and len(tag) > 2 and '-' in tag and tag.replace('-', '').isalnum():
                tags.append(tag)
        
        print(f"🔍 DEBUG TAGS: Extracted {len(tags)} clean tags: {tags[:10]}...")
        
        return tags
    
    def _process_tags(self, tags: List[str]) -> List[str]:
        """Process tags to kebab-case."""
        processed = []
        seen = set()
        
        for tag in tags:
            clean_tag = tag.lower().replace(' ', '-').replace('_', '-')
            clean_tag = ''.join(c for c in clean_tag if c.isalnum() or c == '-')
            clean_tag = clean_tag.strip('-')
            
            if clean_tag and len(clean_tag) > 1 and clean_tag not in seen:
                seen.add(clean_tag)
                processed.append(clean_tag)
        
        return processed
    
    def _validate_tags(self, tags: List[str]) -> bool:
        """Validate tags against config."""
        validation_config = self.prompt_config.get("validation", {})
        min_tags = validation_config.get("min_tags", 25)
        max_tags = validation_config.get("max_tags", 35)
        
        if len(tags) < min_tags:
            logger.error(f"Too few tags: {len(tags)} < {min_tags}")
            return False
        
        if len(tags) > max_tags:
            logger.warning(f"Too many tags: {len(tags)} > {max_tags}, truncating")
            tags = tags[:max_tags]
        
        return True
    
    def _replace_placeholders(self, text: str) -> str:
        """Replace placeholders in the text with actual values."""
        # Simple placeholder replacement logic
        return text.replace("{subject}", self.subject).replace("{article_type}", self.article_type)