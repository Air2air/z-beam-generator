#!/usr/bin/env python3
"""
Material Contamination Researcher

Uses Gemini API to research material properties, common objects, typical environments,
and scientifically accurate contamination for laser cleaning image generation.

Author: AI Assistant
Date: November 24, 2025
"""

import json
import logging
import os
from typing import Dict, Optional, List
from functools import lru_cache

import google.generativeai as genai

logger = logging.getLogger(__name__)


class MaterialContaminationResearcher:
    """Research material properties and contamination for before/after image generation"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize researcher with Gemini API.
        
        Args:
            api_key: Optional Gemini API key (will use env var if not provided)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment or provided")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        logger.info("✅ Material contamination researcher initialized with Gemini Flash 2.0")
    
    @lru_cache(maxsize=128)
    def research_material_contamination(
        self,
        material_name: str,
        material_properties: Optional[Dict] = None
    ) -> Dict[str, any]:
        """
        Research comprehensive contamination data for a material.
        
        Args:
            material_name: Name of the material (e.g., "Aluminum", "Stainless Steel")
            material_properties: Optional material properties from Materials.yaml
            
        Returns:
            Dictionary with complete research data:
            {
                "common_object": str,
                "object_description": str,
                "typical_size": str,
                "typical_environment": str,
                "environment_description": str,
                "contaminants": [
                    {
                        "name": str,
                        "chemical_formula": str,
                        "cause": str,
                        "appearance": {
                            "color": str,
                            "texture": str,
                            "pattern": str,
                            "thickness": str
                        },
                        "prevalence": str
                    }
                ],
                "base_material_appearance": {
                    "clean_color": str,
                    "clean_texture": str,
                    "clean_sheen": str,
                    "natural_features": str
                }
            }
        """
        logger.info(f"🔍 Researching contamination for {material_name}")
        
        # Build comprehensive research prompt
        prompt = self._build_research_prompt(material_name, material_properties)
        
        try:
            # Generate research response
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            try:
                data = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Raw response: {response_text}")
                raise
            
            # Log research summary
            logger.info(f"✅ Common object: {data.get('common_object', 'N/A')}")
            logger.info(f"📏 Size: {data.get('typical_size', 'N/A')}")
            logger.info(f"🌍 Environment: {data.get('typical_environment', 'N/A')}")
            logger.info(f"🧪 Contaminants researched: {len(data.get('contaminants', []))}")
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Material contamination research failed: {e}")
            raise
    
    def _build_research_prompt(
        self,
        material_name: str,
        material_properties: Optional[Dict] = None
    ) -> str:
        """Build comprehensive research prompt for Gemini."""
        
        # Add material properties context if available
        properties_context = ""
        if material_properties:
            props = []
            if 'category' in material_properties:
                props.append(f"Category: {material_properties['category']}")
            if 'density' in material_properties:
                props.append(f"Density: {material_properties['density']}")
            if 'applications' in material_properties:
                apps = material_properties['applications'][:3]  # First 3 applications
                props.append(f"Common applications: {', '.join(apps)}")
            
            if props:
                properties_context = f"\n\nMaterial properties for context:\n{chr(10).join(f'- {p}' for p in props)}"
        
        return f"""Research comprehensive contamination data for {material_name} to generate scientifically accurate before/after laser cleaning images.
{properties_context}

RESEARCH REQUIREMENTS (MANDATORY - Use scientific/technical sources):

1. MOST COMMON OBJECT:
   - What is the #1 most manufactured/used object made from {material_name}?
   - Consider: Industrial use, consumer products, historical prevalence
   - Provide brief description (2-3 sentences) of this object

2. TYPICAL SIZE & DIMENSIONS:
   - What is the standard size/dimensions of this common object?
   - Use specific measurements (e.g., "12 inches diameter, 3mm thick")

3. TYPICAL ENVIRONMENT:
   - Where is this object most commonly found/used?
   - What environmental factors affect it? (moisture, temperature, chemicals, etc.)
   - Provide 2-3 sentence description of the environment

4. SCIENTIFICALLY ACCURATE CONTAMINANTS:
   Research 3-5 specific contaminants that ACTUALLY occur on {material_name} in this environment:
   
   For EACH contaminant, provide:
   - Exact name (e.g., "Iron oxide rust", "Copper carbonate patina")
   - Chemical formula if applicable (e.g., "Fe₂O₃", "Cu₂CO₃(OH)₂")
   - Environmental cause (what causes this contamination)
   - DETAILED appearance on {material_name}:
     * Exact color (e.g., "orange-brown", "blue-green", not just "rust colored")
     * Texture (powdery, crusted, flaky, smooth, rough, granular)
     * Pattern (uniform, patchy, streaked, localized, layered)
     * Typical thickness (surface film, 1-3mm, heavy buildup, etc.)
   - Prevalence (very common, common, occasional, rare)

5. BASE MATERIAL APPEARANCE (CLEAN STATE):
   - Exact color when clean (e.g., "bright silvery-gray", "copper-orange")
   - Surface texture (smooth, brushed, cast, forged, polished)
   - Sheen/finish (matte, satin, glossy, metallic)
   - Natural features (grain pattern, surface variations, typical imperfections)

CRITICAL: Base answers on actual material science data, corrosion studies, industrial cleaning documentation, and real-world observations. Reference specific environmental conditions that cause each type of contamination.

Format your response as JSON (use plain text, no special characters in formulas):

{{
    "common_object": "<most common object made from {material_name}>",
    "object_description": "<2-3 sentence description>",
    "typical_size": "<specific dimensions>",
    "typical_environment": "<environment name>",
    "environment_description": "<2-3 sentences about environment and conditions>",
    "contaminants": [
        {{
            "name": "<exact contamination name>",
            "chemical_formula": "<formula if applicable>",
            "cause": "<what environmental factor causes this>",
            "appearance": {{
                "color": "<exact color description>",
                "texture": "<detailed texture>",
                "pattern": "<distribution pattern>",
                "thickness": "<typical thickness/depth>"
            }},
            "prevalence": "<very common|common|occasional|rare>"
        }}
    ],
    "base_material_appearance": {{
        "clean_color": "<exact color when clean>",
        "clean_texture": "<surface texture>",
        "clean_sheen": "<matte|satin|glossy|metallic>",
        "natural_features": "<grain, variations, typical minor imperfections>"
    }},
    "research_notes": "<brief note about sources or key considerations>"
}}

Provide comprehensive, scientifically accurate data based on real-world material behavior."""
    
    def get_contamination_summary(self, research_data: Dict) -> str:
        """Generate human-readable summary of research data."""
        lines = []
        lines.append(f"Material: {research_data.get('common_object', 'Unknown')}")
        lines.append(f"Size: {research_data.get('typical_size', 'Unknown')}")
        lines.append(f"Environment: {research_data.get('typical_environment', 'Unknown')}")
        lines.append(f"\nContaminants ({len(research_data.get('contaminants', []))}):")
        
        for i, contam in enumerate(research_data.get('contaminants', []), 1):
            lines.append(f"  {i}. {contam['name']}")
            if contam.get('chemical_formula'):
                lines.append(f"     Formula: {contam['chemical_formula']}")
            lines.append(f"     Appearance: {contam['appearance']['color']}, {contam['appearance']['texture']}")
            lines.append(f"     Prevalence: {contam['prevalence']}")
        
        return "\n".join(lines)
