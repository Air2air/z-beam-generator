"""Simplified tags generator - SCHEMA-DRIVEN ONLY."""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from api_client import APIClient
import re

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
    
    def generate(self) -> Optional[str]:
        """Generate tags for an article."""
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
            tags = self._clean_response(response)  # This returns a list of tags
            
            # Simple minimum tags check
            if len(tags) < 5:
                logger.error(f"Too few tags generated: {len(tags)} < 5")
                return None
            
            # LIMIT TAGS TO 15 - this is the only place we need to truncate
            MAX_TAGS = 15
            if len(tags) > MAX_TAGS:
                logger.warning(f"Too many tags: {len(tags)} > {MAX_TAGS}, truncating")
                tags = tags[:MAX_TAGS]
            
            logger.info(f"Successfully generated {len(tags)} schema-driven tags")
            
            # Return as comma-separated string
            return ', '.join(tags)
            
        except Exception as e:
            logger.error(f"Tags generation failed: {e}")
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
        """Clean the API response to extract tags."""
        try:
            # Split the response by lines and cleanup
            lines = response.strip().split('\n')
            
            # Extract tags (one per line or comma-separated)
            tags = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Split by comma if present (handles both formats)
                if ',' in line:
                    parts = [p.strip() for p in line.split(',')]
                    tags.extend([p for p in parts if p])
                else:
                    # Remove bullet points or other markers
                    line = re.sub(r'^[-•*]\s*', '', line)
                    if line:
                        tags.append(line)
            
            # Clean up any remaining issues
            clean_tags = []
            for tag in tags:
                # Remove quotes and formatting
                tag = tag.strip('"\'')
                tag = re.sub(r'\s+', '-', tag)
                
                # CRITICAL: Ensure we're not adding characters individually
                if len(tag) > 1:  # Only add tags longer than a single character
                    clean_tags.append(tag)
            
            logger.debug(f"Extracted {len(clean_tags)} clean tags: {clean_tags[:10]}...")
            return clean_tags
            
        except Exception as e:
            logger.error(f"Error cleaning tags: {e}")
            return []
    
    def _validate_tags(self, tags: List[str]) -> bool:
        """Validate tags."""
        # Update the defaults here to match your new requirements
        validation_config = self.prompt_config.get("validation", {})
        min_tags = validation_config.get("min_tags", 5)  # Changed from 75 to 5
        max_tags = validation_config.get("max_tags", 15)  # Changed from 100 to 15
        
        if len(tags) < min_tags:
            logger.error(f"Too few tags: {len(tags)} < {min_tags}")
            return False
        
        if len(tags) > max_tags:
            logger.warning(f"Too many tags: {len(tags)} > {max_tags}, truncating")
            tags = tags[:max_tags]  # This truncation happens here, but doesn't affect the original list
        
        return True
    
    def process_tags(self, tags_string: str) -> str:
        """
        Process raw tags into a properly formatted string.
        
        Args:
            tags_string: Raw tags string from the API
            
        Returns:
            Properly formatted tags string
        """
        formatted_tags = []
        current_tag = ""
        
        # Split by commas
        parts = tags_string.split(',')
        for part in parts:
            part = part.strip()
            if part:
                # Skip the spaces that were added as individual characters
                if part == " ":
                    current_tag += "-" if current_tag else ""
                else:
                    current_tag += part
            else:
                # Empty part after comma indicates end of tag
                if current_tag:
                    formatted_tags.append(current_tag)
                    current_tag = ""
        
        # Add the last tag if there is one
        if current_tag:
            formatted_tags.append(current_tag)
        
        # Remove duplicate tags and join with commas
        unique_tags = list(dict.fromkeys(formatted_tags))
        return ", ".join(unique_tags)