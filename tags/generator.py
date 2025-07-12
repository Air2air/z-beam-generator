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
            # Build comprehensive prompt using full schema
            prompt = self._build_comprehensive_tags_prompt()
            
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
            
            # Remove duplicates and validate
            unique_tags = []
            seen = set()
            
            for tag in tags:
                tag_clean = tag.strip().lower()
                if tag_clean and tag_clean not in seen and len(tag_clean) > 1:
                    seen.add(tag_clean)
                    unique_tags.append(tag.strip())
            
            # Limit to reasonable number (15-25 tags)
            final_tags = unique_tags[:20]
            
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
                # Bullet list format
                tag = line[2:].strip()
                if tag:
                    tags.append(tag)
            elif line.startswith('* '):
                # Asterisk list format
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
    
    def _build_comprehensive_tags_prompt(self) -> str:
        """Build comprehensive tags prompt using schema structure."""
        subject = self.context.get("subject")
        article_type = self.context.get("article_type")
        
        # Extract schema information for richer tagging
        profile_section = None
        for key, value in self.schema.items():
            if "profile" in key.lower() and isinstance(value, dict):
                profile_section = value
                break
        
        # Get schema-based context
        industries = []
        keywords = []
        applications = []
        
        if profile_section:
            industries = profile_section.get("industries", {}).get("example", [])
            keywords = profile_section.get("keywords", {}).get("example", [])
            
            # Extract applications from outcomes or other sections
            outcomes = profile_section.get("outcomes", {}).get("example", [])
            if outcomes:
                applications = [outcome.get("name", "") for outcome in outcomes if outcome.get("name")]
        
        prompt = f"""Generate comprehensive tags for a professional laser cleaning article about {subject}.

Create a diverse set of tags covering all relevant aspects:

ARTICLE CONTEXT:
- Subject: {subject}
- Type: Technical Article
- Industries: {', '.join(industries) if industries else 'Aerospace, Manufacturing, Medical Devices'}
- Target Audience: Materials Engineers, Technicians, Industrial Professionals

REQUIRED TAG CATEGORIES:

CORE MATERIAL TAGS:
- {subject}
- {subject.lower()}
- {subject.lower()}-laser-cleaning
- {subject.lower()}-surface-treatment
- {subject.lower()}-oxide-removal

PROCESS & TECHNIQUE TAGS:
- laser-cleaning
- laser-ablation
- surface-preparation
- precision-cleaning
- contaminant-removal
- surface-treatment
- industrial-cleaning
- non-contact-cleaning
- eco-friendly-cleaning

TECHNICAL PARAMETER TAGS:
- laser-parameters
- pulse-energy
- wavelength-optimization
- scan-speed
- thermal-management
- process-control
- quality-assurance

INDUSTRY APPLICATION TAGS:
- aerospace-cleaning
- manufacturing-processes
- medical-device-cleaning
- electronics-cleaning
- automotive-applications
- defense-applications

MATERIAL PROPERTY TAGS:
- metal-cleaning
- oxide-removal
- corrosion-prevention
- surface-integrity
- material-properties
- substrate-preservation

SAFETY & COMPLIANCE TAGS:
- laser-safety
- environmental-compliance
- industrial-standards
- operator-safety
- regulatory-compliance

COMPARISON & ANALYSIS TAGS:
- traditional-methods-comparison
- cost-effectiveness
- efficiency-analysis
- performance-metrics
- quality-improvement

TECHNICAL SPECIFICATIONS:
- equipment-specifications
- system-requirements
- operational-parameters
- maintenance-procedures

GENERATE 15-20 RELEVANT TAGS:
Create a focused list of the most relevant tags for this {subject} laser cleaning article.
Focus on tags that would be useful for:
- SEO optimization
- Content categorization
- Technical search
- Industry-specific filtering

Format as a simple list, one tag per line:
- tag-name-1
- tag-name-2
- tag-name-3

CRITICAL REQUIREMENTS:
- Use kebab-case (lowercase with hyphens)
- No special characters except hyphens
- Each tag should be 2-4 words maximum
- Include both general and specific tags
- Focus on technical accuracy
- Ensure tags are searchable and meaningful

Generate the comprehensive tag list now:"""
        
        return prompt