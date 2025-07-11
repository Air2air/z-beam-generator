#!/usr/bin/env python3
"""
Dynamic JSON-LD Generator
Generates JSON-LD based on schema definitions using API
"""

from typing import Dict, Any
from datetime import datetime
from .jsonld_generator import JSONLDGenerator  # Import the base class

class DynamicJSONLDGenerator(JSONLDGenerator):
    """Generates JSON-LD dynamically from schema"""
    
    def _create_jsonld_prompt(self, data: Dict[str, Any]) -> str:
        """Create a prompt for JSON-LD generation based on schema"""
        schema_type = data.get("schema_type", "")
        subject = data.get("context", {}).get("subject", "")
        schema = data.get("schema", {})
        
        # Get JSON-LD schema from schema definition
        jsonld_schema = schema.get("jsonLD", {})
        required_type = jsonld_schema.get("@type", "Article")
        required_props = jsonld_schema.get("requiredProperties", [])
        recommended_props = jsonld_schema.get("recommendedProperties", [])
        
        # Build schema-driven prompt
        prompt = f"""Generate valid JSON-LD for a {schema_type} about {subject}.

The JSON-LD should:
1. Use https://schema.org as the context
2. Use '@type': '{required_type}' (THIS IS REQUIRED)
"""

        # Add required properties
        if required_props:
            prompt += "3. Include these required properties:\n"
            for prop in required_props:
                prompt += f"   - {prop}\n"

        # Add recommended properties
        if recommended_props:
            prompt += f"{4 if required_props else 3}. Include these recommended properties if possible:\n"
            for prop in recommended_props:
                prompt += f"   - {prop}\n"
        
        prompt += """
Return ONLY the JSON-LD code without explanations or markdown formatting.
"""
        return prompt

    def generate(self, data: Dict[str, Any]) -> str:
        """Generate JSON-LD based on schema - NO fallbacks"""
        if not self.api_client:
            raise RuntimeError("Cannot generate JSON-LD: No API client available")
        
        try:
            prompt = self._create_jsonld_prompt(data)
            response = self.api_client.call(prompt, "json_ld_generation")
            
            # Ensure we have valid JSON-LD format
            if not response.strip().startswith("{"):
                response = "{\n" + response
            if not response.strip().endswith("}"):
                response = response + "\n}"
                
            return f"""
<script type="application/ld+json">
{response}
</script>
"""
        except Exception as e:
            # No fallback - just raise the exception
            raise RuntimeError(f"JSON-LD generation failed: {e}")