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
            # Build comprehensive prompt using full schema
            prompt = self._build_comprehensive_jsonld_prompt()
            
            # Generate using API with more tokens
            response = self.api_client.generate(prompt, max_tokens=2500)
            
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
                logger.error(f"Response: {repr(response)}")
                return None
                
        except Exception as e:
            logger.error(f"JSON-LD generation failed: {e}", exc_info=True)
            return None
    
    def _build_comprehensive_jsonld_prompt(self) -> str:
        """Build comprehensive JSON-LD prompt using schema structure."""
        subject = self.context.get("subject")
        article_type = self.context.get("article_type")
        
        prompt = f"""Generate comprehensive JSON-LD structured data for a professional laser cleaning article about {subject}.

Create detailed Schema.org structured data following these requirements:

ARTICLE INFORMATION:
- Subject: {subject}
- Type: Technical Article
- Audience: Materials Engineers, Industrial Professionals

REQUIRED JSON-LD STRUCTURE:

{{
  "@context": "https://schema.org",
  "@type": "TechArticle",
  "headline": "{subject} Laser Cleaning: Complete Technical Guide",
  "description": "Comprehensive guide to laser cleaning {subject} surfaces, including optimal parameters, techniques, safety considerations, and industrial applications for aerospace, manufacturing, and medical device industries",
  "keywords": [
    "{subject.lower()}",
    "laser cleaning",
    "surface preparation",
    "industrial cleaning",
    "{subject.lower()} oxide removal",
    "laser ablation",
    "precision cleaning",
    "contaminant removal",
    "surface treatment"
  ],
  "author": {{
    "@type": "Person",
    "name": "Dr. Sarah Chen",
    "jobTitle": "Senior Materials Engineer",
    "worksFor": {{
      "@type": "Organization",
      "name": "Z-Beam Technologies",
      "specialization": "Laser Surface Processing"
    }}
  }},
  "publisher": {{
    "@type": "Organization",
    "name": "Z-Beam Technologies",
    "url": "https://z-beam.com"
  }},
  "datePublished": "{self.context.get('publishedAt', '2024-01-01')}",
  "dateModified": "{self.context.get('lastUpdated', '2024-01-01')}",
  "url": "https://z-beam.com/materials/{subject.lower().replace(' ', '-')}",
  "image": "https://z-beam.com/images/materials/{subject.lower().replace(' ', '-')}-laser-cleaning.jpg",
  "articleSection": "Materials",
  "about": {{
    "@type": "Thing",
    "name": "{subject} Laser Cleaning",
    "description": "Industrial laser cleaning process for {subject} surfaces"
  }},
  "mentions": [
    {{
      "@type": "Thing",
      "name": "Laser Ablation",
      "description": "Physical process of removing material using laser energy"
    }},
    {{
      "@type": "Thing", 
      "name": "Surface Preparation",
      "description": "Process of cleaning and preparing surfaces for coating or bonding"
    }},
    {{
      "@type": "Thing",
      "name": "{subject} Oxide Removal",
      "description": "Specific application of laser cleaning for removing oxides from {subject}"
    }}
  ],
  "audience": {{
    "@type": "Audience",
    "audienceType": "Professional",
    "name": "Materials Engineers and Technicians"
  }},
  "educationalLevel": "Intermediate",
  "learningResourceType": "Technical Guide",
  "applicationCategory": [
    "Aerospace",
    "Manufacturing",
    "Medical Devices",
    "Electronics",
    "Automotive"
  ],
  "mainEntity": {{
    "@type": "Product",
    "name": "{subject}",
    "description": "Metal material commonly used in aerospace and manufacturing applications",
    "category": "Industrial Material",
    "material": "{subject}",
    "applicationCategory": "Surface Cleaning"
  }},
  "potentialAction": {{
    "@type": "ReadAction",
    "target": "https://z-beam.com/materials/{subject.lower().replace(' ', '-')}"
  }}
}}

CRITICAL REQUIREMENTS:
- Return ONLY valid JSON format
- No explanations, no markdown formatting
- Use "{subject}" throughout all relevant fields
- Follow Schema.org standards exactly
- Include ALL fields shown above
- Use professional, technical language
- Ensure all URLs and references are realistic

Generate the comprehensive JSON-LD now:"""
        
        return prompt