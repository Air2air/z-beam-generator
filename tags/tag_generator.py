#!/usr/bin/env python3
"""
Tags Generator
Generates tags based on schema definitions
"""

from typing import Dict, Any, List
import logging

class TagsGenerator:
    """Generates tags for articles"""
    
    def __init__(self, api_client=None, logger=None):
        self.api_client = api_client
        self.logger = logger or logging.getLogger(__name__)
    
    def generate(self, data: Dict[str, Any]) -> List[str]:
        """Generate tags based on schema"""
        if not self.api_client:
            self.logger.error("Cannot generate tags: No API client available")
            # Return minimal tags
            subject = data.get("context", {}).get("subject", "")
            schema_type = data.get("schema_type", "")
            return [subject, schema_type]
            
        try:
            prompt = self._create_tags_prompt(data)
            response = self.api_client.call(prompt, "tags_generation")
            
            # Process response to get tags
            tags = self._process_tags_response(response)
            return tags
            
        except Exception as e:
            self.logger.error(f"Error generating tags: {e}")
            # Return minimal tags on error
            subject = data.get("context", {}).get("subject", "")
            schema_type = data.get("schema_type", "")
            return [subject, schema_type]
    
    def _create_tags_prompt(self, data: Dict[str, Any]) -> str:
        """Create a prompt for tags generation"""
        subject = data.get("context", {}).get("subject", "")
        schema_type = data.get("schema_type", "")
        
        prompt = f"""Generate 5-10 relevant hashtags for a {schema_type} article about {subject}.
Include both general and specific tags that would help with content discovery.
Format as a comma-separated list without # symbols.
Example: technology, artificial intelligence, machine learning, neural networks, deep learning"""
        
        return prompt
    
    def _process_tags_response(self, response: str) -> List[str]:
        """Process API response to extract tags"""
        if not response:
            return []
            
        # Split by commas or newlines
        if "," in response:
            tags = [tag.strip() for tag in response.split(",")]
        else:
            tags = [tag.strip() for tag in response.split("\n")]
            
        # Filter out empty tags
        tags = [tag for tag in tags if tag]
        
        # Add # to tags that don't have it
        tags = [f"#{tag}" if not tag.startswith("#") else tag for tag in tags]
        
        return tags