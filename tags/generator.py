"""Tags generator for schema-driven article tagging."""

import logging
from typing import Dict, Any, Optional, List
from api_client import APIClient

logger = logging.getLogger(__name__)

class TagsGenerator:
    """Generates comprehensive tags based on schema definitions."""
    
    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], ai_provider: str):
        self.context = context
        self.schema = schema
        self.ai_provider = ai_provider
        self.api_client = APIClient(ai_provider)
        
        logger.info(f"Tags generator initialized for {context.get('article_type')}")
    
    def generate(self) -> Optional[List[str]]:
        """Generate comprehensive tags using AI provider."""
        try:
            # Build schema-driven prompt
            prompt = self._build_schema_driven_tags_prompt()
            
            # Generate using API with more tokens
            response = self.api_client.generate(prompt, max_tokens=1500)
            
            if not response:
                logger.error("Failed to generate tags")
                return None
            
            # Parse and clean tags
            tags = self._parse_tags_response(response)
            
            if not tags:
                logger.error("No valid tags extracted from response")
                return None
            
            # Process and validate tags
            final_tags = self._process_tags(tags)
            
            logger.info(f"Successfully generated {len(final_tags)} tags")
            return final_tags
            
        except Exception as e:
            logger.error(f"Tags generation failed: {e}", exc_info=True)
            return None
    
    def _parse_tags_response(self, response: str) -> List[str]:
        """Parse AI response to extract tags."""
        tags = []
        
        # Clean response
        clean_response = response.strip()
        
        # Remove any markdown formatting
        if clean_response.startswith("```"):
            lines = clean_response.split('\n')
            clean_response = '\n'.join(lines[1:-1]) if len(lines) > 2 else clean_response
        
        # Try different parsing methods
        lines = clean_response.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Handle different formats
            if line.startswith('- '):
                tag = line[2:].strip()
                if tag:
                    tags.append(tag)
            elif line.startswith('* '):
                tag = line[2:].strip()
                if tag:
                    tags.append(tag)
            elif ',' in line:
                # Comma-separated format
                line_tags = [t.strip() for t in line.split(',')]
                tags.extend([t for t in line_tags if t])
            elif line and not line.startswith('#') and not ':' in line:
                # Single tag per line
                tags.append(line)
        
        return tags
    
    def _process_tags(self, tags: List[str]) -> List[str]:
        """Process and validate tags."""
        processed_tags = []
        seen = set()
        
        for tag in tags:
            # Clean tag
            clean_tag = tag.strip().lower()
            
            # Convert to kebab-case
            clean_tag = clean_tag.replace(' ', '-').replace('_', '-')
            
            # Remove special characters except hyphens
            clean_tag = ''.join(c for c in clean_tag if c.isalnum() or c == '-')
            
            # Validate tag
            if clean_tag and len(clean_tag) > 1 and clean_tag not in seen:
                seen.add(clean_tag)
                processed_tags.append(clean_tag)
        
        # Limit to reasonable number
        return processed_tags[:25]
    
    def _build_schema_driven_tags_prompt(self) -> str:
        """Build tags prompt using actual schema structure."""
        subject = self.context.get("subject")
        article_type = self.context.get("article_type")
        
        # Extract schema fields for tag generation
        schema_fields = self._extract_schema_fields()
        
        # Build tag categories from schema
        tag_categories = self._build_tag_categories(schema_fields, subject)
        
        prompt = f"""Generate comprehensive tags for a laser cleaning article about {subject}.

Based on the schema definition, create tags for these categories:

{tag_categories}

REQUIREMENTS:
- Generate 15-25 relevant tags
- Use kebab-case format (lowercase-with-hyphens)
- Include both general and specific tags
- Focus on technical accuracy and searchability
- Include subject-specific variations

Format as a simple list:
- tag-name-1
- tag-name-2
- tag-name-3

Generate the comprehensive tag list now:"""
        
        return prompt
    
    def _extract_schema_fields(self) -> Dict[str, Any]:
        """Extract relevant fields from schema for tag generation."""
        schema_fields = {}
        
        # Get all top-level fields from schema
        for field_name, field_def in self.schema.items():
            if isinstance(field_def, dict):
                schema_fields[field_name] = field_def
        
        return schema_fields
    
    def _build_tag_categories(self, schema_fields: Dict[str, Any], subject: str) -> str:
        """Build tag categories from schema fields."""
        categories = []
        
        # Core subject tags
        categories.append(f"CORE TAGS:\n- {subject.lower()}\n- {subject.lower()}-laser-cleaning\n- laser-cleaning")
        
        # Industry tags from schema
        if "industries" in schema_fields:
            industries = schema_fields["industries"].get("example", [])
            if industries:
                industry_tags = [f"- {industry.lower().replace(' ', '-')}" for industry in industries]
                categories.append(f"INDUSTRY TAGS:\n" + "\n".join(industry_tags))
        
        # Keywords from schema
        if "keywords" in schema_fields:
            keywords = schema_fields["keywords"].get("example", [])
            if keywords:
                keyword_tags = [f"- {kw.lower().replace(' ', '-')}" for kw in keywords if isinstance(kw, str)]
                categories.append(f"KEYWORD TAGS:\n" + "\n".join(keyword_tags))
        
        # Process/outcome tags from schema
        if "outcomes" in schema_fields:
            outcomes = schema_fields["outcomes"].get("example", [])
            if outcomes:
                outcome_tags = []
                for outcome in outcomes[:5]:  # Limit to 5
                    if isinstance(outcome, dict) and "name" in outcome:
                        tag = outcome["name"].lower().replace(' ', '-')
                        outcome_tags.append(f"- {tag}")
                if outcome_tags:
                    categories.append(f"PROCESS TAGS:\n" + "\n".join(outcome_tags))
        
        # Challenge/technical tags from schema
        if "challenges" in schema_fields:
            challenges = schema_fields["challenges"].get("example", [])
            if challenges:
                challenge_tags = []
                for challenge in challenges[:3]:  # Limit to 3
                    if isinstance(challenge, dict) and "name" in challenge:
                        tag = challenge["name"].lower().replace(' ', '-')
                        challenge_tags.append(f"- {tag}")
                if challenge_tags:
                    categories.append(f"TECHNICAL TAGS:\n" + "\n".join(challenge_tags))
        
        # Safety/standards tags from schema
        if "safetyConsiderations" in schema_fields:
            categories.append("SAFETY TAGS:\n- laser-safety\n- operator-safety\n- industrial-standards")
        
        return "\n\n".join(categories)