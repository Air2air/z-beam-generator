"""Simplified JSON-LD generator - SCHEMA-DRIVEN ONLY."""

import logging
import json
import yaml
import re
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
    
    def generate(self) -> Optional[str]:
        """Generate JSON-LD structured data."""
        try:
            prompt = self._build_prompt()
            
            if not prompt:
                logger.error("Failed to build prompt - no schema fields available")
                return None
            
            # Use prompt config for parameters
            max_tokens = self.prompt_config.get("parameters", {}).get("max_tokens", 4000)
            response = self.api_client.generate(prompt, max_tokens=max_tokens)
            
            if not response:
                logger.error("Failed to generate JSON-LD - empty response from API")
                return self._generate_fallback_jsonld()
            
            # Log response for debugging
            logger.debug(f"Raw JSON-LD response first 100 chars: {response[:100]}...")
            
            # Clean and parse response
            cleaned_response = self._clean_response(response)
            
            # Debug output after cleaning
            logger.debug(f"Cleaned JSON-LD (first 100 chars): {cleaned_response[:100]}...")
            
            if not cleaned_response:
                logger.error("Cleaned response is empty, using fallback")
                return self._generate_fallback_jsonld()
            
            try:
                # First attempt - direct parsing
                jsonld_data = json.loads(cleaned_response)
            except json.JSONDecodeError as e:
                logger.warning(f"Initial JSON parse failed: {e}, trying recovery methods...")
                
                # Try more aggressive JSON extraction
                json_pattern = r'(\{[\s\S]*\})'
                matches = re.search(json_pattern, cleaned_response)
                
                if matches:
                    try:
                        jsonld_data = json.loads(matches.group(1))
                        logger.info("Successfully extracted JSON with regex pattern")
                    except json.JSONDecodeError:
                        logger.error("Extracted content still not valid JSON, using fallback")
                        return self._generate_fallback_jsonld()
                else:
                    logger.error("No JSON-like content found, using fallback")
                    return self._generate_fallback_jsonld()
            
            # Force correct URL
            jsonld_data["url"] = self.generate_url(self.subject)
            
            # Format properly
            jsonld_string = json.dumps(jsonld_data, indent=2)
            
            # Final URL check
            jsonld_string = self._final_url_check(jsonld_string)
            
            logger.info(f"Successfully generated valid JSON-LD")
            return jsonld_string
            
        except Exception as e:
            logger.error(f"JSON-LD generation failed: {e}", exc_info=True)
            return self._generate_fallback_jsonld()
        
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
    
    def _normalize_for_url(self, text):
        """Normalize text for URL usage.
        
        Converts subject to URL-friendly format:
        1. Lowercase
        2. Remove special characters
        3. Replace spaces with dashes
        4. Clean up extra dashes
        """
        import re
        
        # Convert to lowercase
        normalized = text.lower()
        
        # Remove special characters and punctuation
        normalized = re.sub(r'[,\'"!@#$%^&*()+=]', '', normalized)
        
        # Replace spaces, underscores and parentheses with dashes
        normalized = re.sub(r'[\s_()\[\]]', '-', normalized)
        
        # Remove any extra dashes
        normalized = re.sub(r'-+', '-', normalized)
        
        # Remove leading/trailing dashes
        normalized = normalized.strip('-')
        
        return normalized

    def generate_url(self, subject):
        """Generate correct URL based on subject."""
        # Clean the subject name for URL
        cleaned_subject = self._normalize_for_url(subject)
        
        # Use correct domain and format with www prefix
        url = f"https://www.z-beam.com/{cleaned_subject}-laser-cleaning"
        return url
    
    def _final_url_check(self, jsonld_string):
        """Final check to ensure no example.com URLs remain."""
        if "example.com" in jsonld_string:
            logger.warning("Found 'example.com' in JSON-LD, replacing with www.z-beam.com")
            jsonld_string = jsonld_string.replace("example.com", "www.z-beam.com")
            
            # Also ensure the path format is correct
            import re
            pattern = r'https://www\.z-beam\.com/([^/"]+)'
            
            def fix_path(match):
                path = match.group(1)
                if not path.endswith("-laser-cleaning"):
                    return f"https://www.z-beam.com/{path}-laser-cleaning"
                return match.group(0)
                
            jsonld_string = re.sub(pattern, fix_path, jsonld_string)
        
        return jsonld_string
    
    def _generate_fallback_jsonld(self) -> str:
        """Generate basic fallback JSON-LD when API fails."""
        logger.info("Generating fallback JSON-LD")
        
        fallback_data = {
            "@context": "https://schema.org",
            "@type": "TechnicalArticle",
            "headline": f"{self.subject} Laser Cleaning Applications",
            "description": f"Technical information about {self.subject} laser cleaning applications, including surface preparation techniques, equipment specifications, and industrial use cases.",
            "url": self.generate_url(self.subject),
            "keywords": [
                "laser cleaning", 
                f"{self.subject} surface preparation", 
                "industrial cleaning", 
                "surface treatment"
            ],
            "author": {
                "@type": "Organization",
                "name": "Z-Beam Laser Technologies"
            }
        }
        
        return json.dumps(fallback_data, indent=2)
    
    def _format_jsonld(self, jsonld_str: str) -> str:
        """Format JSON-LD for inclusion in markdown."""
        try:
            # Remove surrounding quotes if present
            if jsonld_str.startswith('"') and jsonld_str.endswith('"'):
                jsonld_str = jsonld_str[1:-1]
            
            # Unescape internal quotes if needed
            jsonld_str = jsonld_str.replace('\\"', '"')
            
            # Try to parse and pretty-print
            try:
                data = json.loads(jsonld_str)
                jsonld_str = json.dumps(data, indent=2)
            except:
                # If parsing fails, leave as is
                pass
                
            return f'<script type="application/ld+json">\n{jsonld_str}\n</script>'
            
        except Exception as e:
            logger.error(f"Error formatting JSON-LD: {e}")
            return f'<script type="application/ld+json">\n{jsonld_str}\n</script>'
    
    def clean_json_ld(self, json_content: str) -> str:
        """
        Clean up JSON-LD output by removing extra quotes and fixing escape characters.
        
        Args:
            json_content: Raw JSON-LD string
            
        Returns:
            Properly formatted JSON-LD string
        """
        if not json_content:
            return "{}"
        
        # Remove extra quotes at the beginning if they exist
        if json_content.startswith('"'):
            json_content = json_content[1:]
        
        # Remove extra quotes at the end if they exist
        if json_content.endswith('"') and not json_content.endswith('\\\"'):
            json_content = json_content[:-1]
        
        return json_content

    def get_json_ld(self, schema_data):
        """
        Generate JSON-LD from schema data and clean it.
        
        Args:
            schema_data: Schema data to generate JSON-LD from
            
        Returns:
            Cleaned JSON-LD string
        """
        # Your existing code to generate json_ld
        # For example:
        json_ld = self._generate_from_schema(schema_data)
        
        # Before returning, clean the JSON-LD
        json_ld = self.clean_json_ld(json_ld)
        return json_ld