#!/usr/bin/env python3
"""
Dynamic JSON-LD Generator - 100% AI-driven, no rules required
"""
import logging
import json
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DynamicJSONLDGenerator:
    """Fully dynamic JSON-LD generator - AI generates structured data from metadata"""
    
    def __init__(self, api_client, config: Dict[str, Any]):
        self.api_client = api_client
        self.config = config
    
    def generate_jsonld(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate JSON-LD dynamically from metadata using AI"""
        logger.info("📊 Generating JSON-LD dynamically from metadata")
        
        # Create prompt for AI JSON-LD generation
        prompt = self._create_jsonld_prompt(metadata)
        
        # Get AI response
        try:
            response = self.api_client.call(prompt)
            jsonld = self._parse_jsonld_response(response)
            
            logger.info("📊 Generated JSON-LD dynamically")
            return jsonld
            
        except Exception as e:
            raise ValueError(f"Dynamic JSON-LD generation failed: {e}")
    
    def _create_jsonld_prompt(self, metadata: Dict[str, Any]) -> str:
        """Create prompt for AI JSON-LD generation"""
        article_type = metadata.get("articleType", "article")
        subject = metadata.get("subject", "laser cleaning")
        
        prompt = f"""Generate Schema.org JSON-LD structured data for this laser cleaning {article_type}:

Subject: {subject}
Metadata: {json.dumps(metadata, indent=2)}

Requirements:
- Use appropriate Schema.org @type based on article type
- Include all relevant metadata fields
- Use proper Schema.org property names
- Include author information if available
- Include publication dates
- Make it SEO-friendly and rich

For {article_type} articles, consider these @types:
- thesaurus: Article with about.@type = "DefinedTerm"
- material: Article with about.@type = "Product" or "Material"
- application: Article with about.@type = "Service" or "Process"
- region: Article with about.@type = "Place"

Return only valid JSON-LD, no explanations or markdown."""
        
        return prompt
    
    def _parse_jsonld_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response to extract JSON-LD"""
        if not response:
            raise ValueError("Empty JSON-LD response from AI")
        
        # Clean response - remove markdown if present
        response = response.strip()
        if response.startswith('```json'):
            response = response.replace('```json', '').replace('```', '').strip()
        elif response.startswith('```'):
            response = response.replace('```', '').strip()
        
        # Parse JSON
        try:
            jsonld = json.loads(response)
            if not isinstance(jsonld, dict):
                raise ValueError("JSON-LD response is not a JSON object")
            
            # Validate basic structure
            if "@context" not in jsonld:
                jsonld["@context"] = "https://schema.org"
            
            if "@type" not in jsonld:
                jsonld["@type"] = "Article"
            
            return jsonld
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON-LD response: {e}")
    
    def format_jsonld(self, jsonld: Dict[str, Any]) -> str:
        """Format JSON-LD for output"""
        if not jsonld:
            raise ValueError("No JSON-LD data provided for formatting")
        
        try:
            formatted = json.dumps(jsonld, indent=2, ensure_ascii=False)
            return f'<script type="application/ld+json">\n{formatted}\n</script>'
        except Exception as e:
            raise ValueError(f"Failed to format JSON-LD: {e}")