#!/usr/bin/env python3
"""
Dynamic Tag Generator - 100% AI-driven, no rules required
"""
import logging
import json
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class DynamicTagGenerator:
    """Fully dynamic tag generator - AI generates tags from metadata"""
    
    def __init__(self, api_client, config: Dict[str, Any]):
        self.api_client = api_client
        self.config = config
    
    def generate_tags(self, metadata: Dict[str, Any]) -> List[str]:
        """Generate tags dynamically from metadata using AI"""
        logger.info("🏷️ Generating tags dynamically from metadata")
        
        # Create prompt for AI tag generation
        prompt = self._create_tag_prompt(metadata)
        
        # Get AI response
        try:
            response = self.api_client.call(prompt)
            tags = self._parse_tag_response(response)
            
            logger.info(f"🏷️ Generated {len(tags)} tags dynamically")
            return tags
            
        except Exception as e:
            raise ValueError(f"Dynamic tag generation failed: {e}")
    
    def _create_tag_prompt(self, metadata: Dict[str, Any]) -> str:
        """Create prompt for AI tag generation"""
        article_type = metadata.get("articleType", "article")
        subject = metadata.get("subject", "laser cleaning")
        
        prompt = f"""Generate relevant tags for this laser cleaning {article_type}:

Subject: {subject}
Metadata: {json.dumps(metadata, indent=2)}

Generate 8-12 relevant hashtags based on:
- Technical terminology and concepts
- Material properties and characteristics
- Application areas and use cases
- Industry relevance and categories
- Scientific domains and processes

Requirements:
- Use # prefix for each tag
- Keep tags concise (1-3 words)
- Focus on searchable keywords
- Include both specific and general terms
- Avoid duplicate concepts

Return format: #tag1 #tag2 #tag3 #tag4 etc.
Return only the tags, no explanations."""
        
        return prompt
    
    def _parse_tag_response(self, response: str) -> List[str]:
        """Parse AI response to extract tags"""
        if not response:
            raise ValueError("Empty tag response from AI")
        
        # Clean response
        response = response.strip()
        
        # Extract hashtags
        import re
        hashtags = re.findall(r'#\w+', response)
        
        if not hashtags:
            # Try to extract words and add # prefix
            words = re.findall(r'\b[A-Za-z][A-Za-z0-9]*\b', response)
            hashtags = [f"#{word}" for word in words if len(word) > 2]
        
        if not hashtags:
            raise ValueError("No valid tags found in AI response")
        
        # Remove duplicates and limit count
        unique_tags = []
        seen = set()
        for tag in hashtags:
            tag_lower = tag.lower()
            if tag_lower not in seen:
                unique_tags.append(tag)
                seen.add(tag_lower)
        
        return unique_tags[:12]  # Limit to 12 tags
    
    def format_tags(self, tags: List[str]) -> str:
        """Format tags for output"""
        if not tags:
            raise ValueError("No tags provided for formatting")
        
        # Tags already have # prefix from generation
        return " ".join(tags)