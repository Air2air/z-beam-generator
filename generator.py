"""Metadata generator for schema-driven article metadata."""

import logging
from typing import Dict, Any, Optional
from api_client import APIClient
from .prompt import build_metadata_prompt

logger = logging.getLogger(__name__)

class MetadataGenerator:
    """Generates article metadata based on schema definitions."""
    
    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], ai_provider: str):
        self.context = context
        self.schema = schema
        self.ai_provider = ai_provider
        self.api_client = APIClient(ai_provider)
        
        logger.info(f"Metadata generator initialized for {context.get('article_type')}")
    
    def generate(self) -> Optional[Dict[str, Any]]:
        """Generate metadata using AI provider."""
        try:
            # Build prompt using schema
            prompt = build_metadata_prompt(self.context, self.schema)
            
            # Generate using API
            response = self.api_client.generate(prompt, max_tokens=800)
            
            if not response:
                logger.error("Failed to generate metadata")
                return None
            
            # Parse YAML response
            import yaml
            try:
                metadata = yaml.safe_load(response)
                logger.info("Successfully generated and parsed metadata")
                return metadata
            except yaml.YAMLError as e:
                logger.error(f"Failed to parse metadata YAML: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Metadata generation failed: {e}", exc_info=True)
            return None