"""Tags generator for schema-driven article tags."""

import logging
import json
from typing import Dict, Any, Optional, List
from api_client import APIClient

logger = logging.getLogger(__name__)

class TagsGenerator:
    """Generates article tags based on schema definitions."""
    
    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], ai_provider: str):
        self.context = context
        self.schema = schema
        self.ai_provider = ai_provider
        self.api_client = APIClient(ai_provider)
        
        logger.info(f"Tags generator initialized for {context.get('article_type')}")
    
    def generate(self) -> Optional[List[str]]:
        """Generate tags using AI provider."""
        try:
            # Build prompt using schema
            prompt = self._build_tags_prompt()
            
            # Generate using API
            response = self.api_client.generate(prompt, max_tokens=300)
            
            if not response:
                logger.error("Failed to generate tags")
                return None
            
            # Parse response (could be YAML or JSON)
            import yaml
            try:
                tags_data = yaml.safe_load(response)
                
                # Extract tags from response
                if isinstance(tags_data, dict):
                    tags = tags_data.get("tags", [])
                elif isinstance(tags_data, list):
                    tags = tags_data
                else:
                    # Try to extract from string
                    tags = []
                
                logger.info(f"Successfully generated {len(tags)} tags")
                return tags
                
            except yaml.YAMLError as e:
                logger.error(f"Failed to parse tags response: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Tags generation failed: {e}", exc_info=True)
            return None
    
    def _build_tags_prompt(self) -> str:
        """Build tags generation prompt using schema structure."""
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
        
        # Find tags section in schema (flexible naming)
        tags_section = None
        for key, value in self.schema.items():
            if "tags" in key.lower() and isinstance(value, dict):
                tags_section = value
                break
        
        if not tags_section:
            # Create a simple tags structure
            tags_section = {"tags": [f"{{{{{placeholder}}}}}", "laser-cleaning"]}
        
        # Replace system placeholders in schema
        schema_with_system = json.dumps(tags_section, indent=2)
        for sys_key, sys_value in self.context.items():
            if sys_key in ["generation_timestamp", "model_used", "lastUpdated", "publishedAt"]:
                schema_with_system = schema_with_system.replace(f"{{{{{sys_key}}}}}", str(sys_value))
        
        prompt = f"""You are an expert technical writer creating tags for a laser cleaning article.

Subject: {subject}
Article Type: {article_type}

Generate tags following this exact schema structure:
{schema_with_system}

CRITICAL REQUIREMENTS:
- Replace ALL instances of {{{{{placeholder}}}}} with "{subject}"
- Use the subject "{subject}" appropriately in all tag fields
- Include ALL fields from the schema - no omissions
- Follow the schema data types and formats exactly
- Return ONLY valid YAML format
- Do NOT include any explanatory text or markdown formatting
- Ensure every field has meaningful content (no empty arrays)

Generate the tags now:"""
        
        return prompt