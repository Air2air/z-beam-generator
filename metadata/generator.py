"""Metadata generator for schema-driven article metadata."""

import logging
import json
import re
from typing import Dict, Any, Optional
from api_client import APIClient

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
            # Build comprehensive prompt using full schema
            prompt = self._build_comprehensive_prompt()
            
            # Generate using API with more tokens for complex content
            response = self.api_client.generate(prompt, max_tokens=3000)
            
            if not response:
                logger.error("Failed to generate metadata")
                return None
            
            # Validate response before processing
            if not self._validate_response(response):
                logger.error("Response validation failed")
                return None
            
            # Clean and parse response
            cleaned_response = self._clean_response(response)
            
            # Parse YAML response
            import yaml
            try:
                metadata = yaml.safe_load(cleaned_response)
                if not metadata:
                    logger.error("Empty metadata response")
                    return None
                    
                logger.info("Successfully generated and parsed metadata")
                return metadata
                
            except yaml.YAMLError as e:
                logger.error(f"Failed to parse metadata YAML: {e}")
                logger.error(f"Cleaned response: {repr(cleaned_response)}")
                return None
                
        except Exception as e:
            logger.error(f"Metadata generation failed: {e}", exc_info=True)
            return None
    
    def _validate_response(self, response: str) -> bool:
        """Validate AI response before parsing."""
        if not response or len(response.strip()) < 50:
            logger.error("Response too short")
            return False
        
        if response.strip().startswith('{'):
            logger.error("AI returned JSON instead of YAML")
            return False
        
        if '"type": "string"' in response:
            logger.error("AI returned schema definition instead of actual data")
            return False
        
        if not ':' in response:
            logger.error("Response doesn't appear to be YAML")
            return False
        
        return True
    
    def _clean_response(self, response: str) -> str:
        """Clean API response to extract valid YAML."""
        cleaned = response.strip()
        
        # Remove markdown code blocks
        if cleaned.startswith("```yaml") or cleaned.startswith("```yml"):
            cleaned = cleaned.split('\n', 1)[1]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        return cleaned.strip()
    
    def _build_comprehensive_prompt(self) -> str:
        """Build comprehensive prompt using full schema structure."""
        subject = self.context.get("subject")
        article_type = self.context.get("article_type")
        
        # Find the materialProfile section in schema
        profile_section = None
        for key, value in self.schema.items():
            if "profile" in key.lower() and isinstance(value, dict):
                profile_section = value
                break
        
        if not profile_section:
            # Fallback to simple prompt if no profile section found
            return self._build_simple_prompt()
        
        # Extract key schema elements for comprehensive generation
        industries = profile_section.get("industries", {}).get("example", [])
        keywords_example = profile_section.get("keywords", {}).get("example", [])
        outcomes_example = profile_section.get("outcomes", {}).get("example", [])
        challenges_example = profile_section.get("challenges", {}).get("example", [])
        
        prompt = f"""Generate comprehensive YAML metadata for a professional laser cleaning article about {subject}.

Create detailed, technical metadata based on this structure:

BASIC INFORMATION:
- Subject: {subject}
- Article Type: {article_type}
- Target Audience: Materials Engineers, Technicians, Industrial Professionals

REQUIRED COMPREHENSIVE FIELDS:

title: "{subject} Laser Cleaning: Complete Technical Guide"
description: "Comprehensive guide to laser cleaning {subject} surfaces, including optimal parameters, techniques, safety considerations, and industrial applications"
category: "Materials"
type: "material-profile"
difficulty: "intermediate"
class: "Metal"
primaryAudience: "Materials Engineers"
secondaryAudience: "Technicians"
schemaOrgType: "TechArticle"

keywords:
  - "{subject.lower()}"
  - "laser cleaning"
  - "surface preparation"
  - "industrial cleaning"
  - "{subject.lower()} oxide removal"
  - "surface treatment"
  - "laser ablation"
  - "contaminant removal"
  - "precision cleaning"

industries:
  - "Aerospace"
  - "Manufacturing"
  - "Medical Devices"
  - "Electronics"
  - "Automotive"
  - "Defense"

outcomes:
  - name: "Effective Contaminant Removal"
    description: "Achieves 98% removal of oxides and residues from {subject}, ensuring consistency and quality"
  - name: "Substrate Integrity"
    description: "Preserves {subject} surface hardness and material properties critical for industrial applications"
  - name: "Eco-Friendly Process"
    description: "Eliminates chemical solvents, reducing environmental footprint for {subject} cleaning operations"

challenges:
  - name: "Oxide Layer Tenacity"
    description: "{subject} oxide films resist removal, requiring optimized pulse energies and precise wavelengths"
  - name: "Thermal Sensitivity"
    description: "Excessive heat risks microcracking in {subject}, mitigated by real-time thermal monitoring"
  - name: "Process Optimization"
    description: "Laser parameter calibration requires expertise for optimal {subject} cleaning results"

substrates:
  - name: "Pure {subject}"
    properties:
      - "High thermal conductivity"
      - "Excellent corrosion resistance"
      - "Lightweight structure"
    cleaningConsiderations: "Use moderate pulse energies to prevent thermal damage"
  - name: "{subject} Alloys"
    properties:
      - "Enhanced strength"
      - "Improved durability"
      - "Specialized compositions"
    cleaningConsiderations: "Adjust wavelength for specific alloy absorption characteristics"

performanceMetrics:
  description: "Performance metrics for {subject} laser cleaning ensure efficient processing with minimal thermal impact"
  metrics:
    - name: "Removal Rate"
      value: "8-15 m²/hour"
      consideration: "Varies with contamination thickness and type"
    - name: "Pulse Energy"
      value: "0.5-2.0 mJ"
      consideration: "Lower for thin coatings, higher for thick oxides"
    - name: "Wavelength"
      value: "1064 nm"
      consideration: "Optimal for {subject} absorption characteristics"
    - name: "Scan Speed"
      value: "5-12 mm/s"
      consideration: "Adjust based on component geometry and requirements"

url: "https://z-beam.com/materials/{subject.lower().replace(' ', '-')}"
publishedAt: "{self.context.get('publishedAt', '2024-01-01')}"
lastUpdated: "{self.context.get('lastUpdated', '2024-01-01')}"

author:
  name: "Dr. Sarah Chen"
  title: "Senior Materials Engineer"
  organization: "Z-Beam Technologies"
  specialization: "Laser Surface Processing"

contentManagement:
  articleType: "material-profile"
  generationTimestamp: "{self.context.get('generation_timestamp', '')}"
  modelUsed: "{self.context.get('model_used', '')}"

CRITICAL REQUIREMENTS:
- Return ONLY valid YAML format
- No explanations, no JSON, no markdown formatting
- Use "{subject}" throughout all relevant fields
- Every field must contain meaningful, professional content
- Include ALL fields shown above
- Use technical language appropriate for engineering audience
- Ensure all values are realistic and industry-appropriate

Generate the comprehensive YAML metadata now:"""
        
        return prompt
    
    def _build_simple_prompt(self) -> str:
        """Fallback to simple prompt if schema parsing fails."""
        subject = self.context.get("subject")
        
        prompt = f"""Generate YAML metadata for a laser cleaning article about {subject}.

title: "{subject} Laser Cleaning: Complete Technical Guide"
description: "Comprehensive guide to laser cleaning {subject} surfaces including techniques, parameters, and best practices"
category: "Materials"
type: "material-profile"
difficulty: "intermediate"
keywords:
  - "{subject.lower()}"
  - "laser cleaning"
  - "surface preparation"
industries:
  - "Aerospace"
  - "Manufacturing"
class: "Metal"
primaryAudience: "Materials Engineers"
secondaryAudience: "Technicians"
schemaOrgType: "TechArticle"
url: "https://z-beam.com/materials/{subject.lower()}"
publishedAt: "{self.context.get('publishedAt', '2024-01-01')}"
lastUpdated: "{self.context.get('lastUpdated', '2024-01-01')}"

Generate the YAML now:"""
        
        return prompt