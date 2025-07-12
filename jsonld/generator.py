"""JSON-LD generator for schema-driven structured data."""

import logging
import json
from typing import Dict, Any, Optional
from api_client import APIClient

logger = logging.getLogger(__name__)

class JsonLdGenerator:
    """Generates JSON-LD structured data based on schema definitions."""
    
    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], ai_provider: str):
        self.context = context
        self.schema = schema
        self.ai_provider = ai_provider
        self.api_client = APIClient(ai_provider)
        
        logger.info(f"JSON-LD generator initialized for {context.get('article_type')}")
    
    def generate(self) -> Optional[Dict[str, Any]]:
        """Generate JSON-LD using AI provider."""
        try:
            # Build prompt using schema
            prompt = self._build_jsonld_prompt()
            
            # Generate using API
            response = self.api_client.generate(prompt, max_tokens=800)
            
            if not response:
                logger.error("Failed to generate JSON-LD")
                return None
            
            # Parse JSON response
            try:
                # Clean response (remove potential markdown formatting)
                clean_response = response.strip()
                if clean_response.startswith("```json"):
                    clean_response = clean_response[7:]
                if clean_response.endswith("```"):
                    clean_response = clean_response[:-3]
                
                jsonld_data = json.loads(clean_response.strip())
                logger.info("Successfully generated and parsed JSON-LD")
                return jsonld_data
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON-LD response: {e}")
                return None
                
        except Exception as e:
            logger.error(f"JSON-LD generation failed: {e}", exc_info=True)
            return None
    
    def _build_jsonld_prompt(self) -> str:
        """Build JSON-LD generation prompt using schema structure."""
        article_type = self.context.get("article_type")
        subject = self.context.get("subject")
        
        # Map context subject to schema placeholder
        placeholder_map = {
            "material": "materialName",
            "application": "applicationName", 
            "region": "regionName",
            "thesaurus": "term"
        }
        
        placeholder = placeholder_map.get(article_type, "subject")
        
        # Find JSON-LD section in schema (flexible naming)
        jsonld_section = None
        for key, value in self.schema.items():
            if "jsonld" in key.lower() or "structured" in key.lower():
                jsonld_section = value
                break
        
        if not jsonld_section:
            # Create a basic JSON-LD structure
            jsonld_section = {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": f"{{{{{placeholder}}}}} Laser Cleaning",
                "description": f"Guide to {{{{{placeholder}}}}} laser cleaning"
            }
        
        # Replace system placeholders in schema
        schema_with_system = json.dumps(jsonld_section, indent=2)
        for sys_key, sys_value in self.context.items():
            if sys_key in ["generation_timestamp", "model_used", "lastUpdated", "publishedAt"]:
                schema_with_system = schema_with_system.replace(f"{{{{{sys_key}}}}}", str(sys_value))
        
        prompt = f"""You are an expert technical writer creating JSON-LD structured data for a laser cleaning article.

Subject: {subject}
Article Type: {article_type}

Generate JSON-LD following this exact schema structure:
{schema_with_system}

CRITICAL REQUIREMENTS:
- Replace ALL instances of {{{{{placeholder}}}}} with "{subject}"
- Use the subject "{subject}" appropriately in all JSON-LD fields
- Include ALL fields from the schema - no omissions
- Follow the schema data types and formats exactly
- Return ONLY valid JSON format
- Do NOT include any explanatory text or markdown formatting
- Ensure every field has meaningful content (no empty strings)
- Follow Schema.org standards for structured data

Generate the JSON-LD now:"""
        
        return prompt