#!/usr/bin/env python3
"""
JSON-LD Generator - Creates structured data
"""
import json
import logging
from typing import Dict, Any

class JSONLDGenerator:
    """Base class for JSON-LD generators"""
    
    def __init__(self, api_client=None, logger=None):
        self.api_client = api_client
        self.logger = logger or logging.getLogger(__name__)
        
    def generate(self, data: Dict[str, Any]) -> str:
        """Generate JSON-LD"""
        raise NotImplementedError("Subclasses must implement generate()")

class DynamicJSONLDGenerator(JSONLDGenerator):
    """Dynamic JSON-LD generator for structured data"""
    
    def __init__(self, api_client, config=None):
        super().__init__(api_client)
        self.config = config or {}
        self.max_prompt_size = 8000  # Set a safer limit for API calls
    
    def generate(self, data: Dict[str, Any]) -> str:
        """Generate JSON-LD from data - SINGLE IMPLEMENTATION with NO FALLBACKS"""
        if not self.api_client:
            raise RuntimeError("Cannot generate JSON-LD: API client is not available")
            
        # Prepare a simplified data structure for the prompt
        simplified_data = self._simplify_data(data)
        
        # Create prompt
        prompt = self._create_jsonld_prompt(simplified_data)
        
        # Check if prompt is too long and truncate if necessary
        if len(prompt) > self.max_prompt_size:
            self.logger.warning(f"JSON-LD prompt too long ({len(prompt)} chars), truncating")
            prompt = prompt[:self.max_prompt_size] + "\n\nPlease generate JSON-LD with available information."
        
        # Make API call
        self.logger.info("📊 Generating JSON-LD dynamically from metadata")
        response = self.api_client.call(prompt, "json_ld_generation")
        
        # Extract JSON-LD from response
        json_ld_text = self._extract_jsonld_from_response(response)
        
        # Format the JSON-LD for output
        return f"""
<script type="application/ld+json">
{json_ld_text}
</script>
"""
    
    def _simplify_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Simplify data structure to reduce prompt size"""
        simplified = {}
        
        # Extract only what's needed for JSON-LD
        if "context" in data:
            simplified["context"] = {
                "subject": data["context"].get("subject", ""),
                "author": data["context"].get("author", {}).get("name", "")
            }
        
        if "schema_type" in data:
            simplified["schema_type"] = data["schema_type"]
        
        # Include basic profile data but limit nested structures
        for profile_key in ["application_profile", "material_profile", "region_profile", "thesaurus_profile"]:
            if profile_key in data:
                simplified[profile_key] = {}
                profile = data[profile_key]
                
                # Copy top-level simple attributes
                for key, value in profile.items():
                    if isinstance(value, (str, int, float, bool)):
                        simplified[profile_key][key] = value
        
        return simplified
    
    def _create_jsonld_prompt(self, data: Dict[str, Any]) -> str:
        """Create a prompt for JSON-LD generation"""
        schema_type = data.get("schema_type", "")
        subject = data.get("context", {}).get("subject", "")
        
        # Map schema types to correct Schema.org types
        type_mapping = {
            "application": "TechnicalArticle",
            "material": "Product",
            "region": "Place",
            "thesaurus": "DefinedTerm"
        }
        
        schema_org_type = type_mapping.get(schema_type, "Article")
        
        prompt = f"""Generate valid JSON-LD for a {schema_type} about {subject}.
        
Data:
{json.dumps(data, indent=2)}

The JSON-LD should:
1. Use https://schema.org as the context
2. Use '@type': '{schema_org_type}' (THIS IS REQUIRED)
3. Include all relevant properties from the data
4. Be properly nested and formatted
5. Return ONLY the JSON-LD code without explanations

JSON-LD:
"""
        return prompt
    
    def _extract_jsonld_from_response(self, response: str) -> str:
        """Extract JSON-LD from API response"""
        # Try to find JSON-LD code block
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            json_ld_text = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            json_ld_text = response[start:end].strip()
        else:
            # Just use the whole response
            json_ld_text = response.strip()
        
        # Validate it's proper JSON
        try:
            json_obj = json.loads(json_ld_text)
            return json.dumps(json_obj, indent=2)
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON-LD generated")
            raise ValueError("Generated JSON-LD is not valid JSON")