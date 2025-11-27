#!/usr/bin/env python3
"""
Visual Appearance Researcher

Uses Gemini API to research detailed visual descriptions of how
contaminants appear on specific materials for realistic image generation.

Gathers information from:
- Scientific literature
- Industrial documentation
- Photo references
- Material science databases

Author: AI Assistant
Date: November 26, 2025
"""

import os
import logging
from typing import Dict, Optional, List
from functools import lru_cache
import json

import google.generativeai as genai

logger = logging.getLogger(__name__)


class VisualAppearanceResearcher:
    """
    Research visual appearance of contaminants on specific materials.
    
    Provides detailed descriptions needed for photo-realistic AI image generation,
    including color variations, texture details, distribution patterns, and
    aging effects specific to each material-contaminant combination.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize researcher with Gemini API.
        
        Args:
            api_key: Optional Gemini API key (uses GEMINI_API_KEY env var if not provided)
        
        Raises:
            ValueError: If no API key available
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment or provided")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        logger.info("✅ Visual appearance researcher initialized with Gemini Flash 2.0")
    
    @lru_cache(maxsize=256)
    def research_appearance_on_material(
        self,
        contaminant_id: str,
        contaminant_name: str,
        material_name: str,
        material_properties: Optional[Dict] = None,
        chemical_composition: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Research how contaminant appears on specific material.
        
        Args:
            contaminant_id: Unique ID (e.g., "rust-oxidation")
            contaminant_name: Human-readable name (e.g., "Rust / Iron Oxide")
            material_name: Material name (e.g., "Steel", "Aluminum")
            material_properties: Optional material properties dict
            chemical_composition: Optional chemical formula/composition
        
        Returns:
            Dictionary with detailed visual descriptions:
            {
                "description": "Overall visual appearance on this material",
                "common_patterns": "Distribution and accumulation patterns",
                "aged_appearance": "How it looks after aging/weathering",
                "lighting_effects": "Appearance under different lighting",
                "texture_details": "Fine-grained texture information",
                "color_variations": "Specific color range on this material",
                "thickness_range": "Typical thickness range",
                "distribution_factors": "What affects where it accumulates"
            }
        """
        print(f"\n🔬 Researching visual appearance: {contaminant_name} on {material_name}")
        
        # Build research prompt
        prompt = self._build_research_prompt(
            contaminant_id=contaminant_id,
            contaminant_name=contaminant_name,
            material_name=material_name,
            material_properties=material_properties,
            chemical_composition=chemical_composition
        )
        
        # Call Gemini API
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.3,  # Lower for factual accuracy
                    'top_p': 0.8,
                    'top_k': 40,
                    'max_output_tokens': 2048,
                }
            )
            
            # Parse response
            result = self._parse_response(response.text)
            
            print(f"   ✅ Research complete: {len(result)} visual aspects documented")
            return result
            
        except Exception as e:
            logger.error(f"Research failed for {contaminant_name} on {material_name}: {e}")
            print(f"   ❌ Research failed: {e}")
            raise
    
    def _build_research_prompt(
        self,
        contaminant_id: str,
        contaminant_name: str,
        material_name: str,
        material_properties: Optional[Dict],
        chemical_composition: Optional[str]
    ) -> str:
        """Build detailed research prompt for Gemini."""
        
        # Base prompt
        prompt = f"""You are a materials science and industrial contamination expert. Research the visual appearance of {contaminant_name} on {material_name} surfaces.

MATERIAL: {material_name}
"""
        
        # Add material properties if available
        if material_properties:
            prompt += f"\nMaterial Properties:\n"
            for key, value in material_properties.items():
                prompt += f"  - {key}: {value}\n"
        
        # Add chemical info if available
        if chemical_composition:
            prompt += f"\nContaminant Composition: {chemical_composition}\n"
        
        prompt += f"""
TASK: Provide detailed visual descriptions needed for AI image generation. Focus on photo-realistic details that would be visible in industrial/technical photography.

Provide information in the following structure (use JSON format):

{{
  "description": "2-3 sentence overall description of how {contaminant_name} appears on {material_name}. Include dominant colors, general texture, and typical coverage patterns.",
  
  "color_variations": "Detailed color range specific to this material. List 3-5 specific colors/shades from fresh to aged. Be precise (e.g., 'rust-orange with brown edges' not just 'orange').",
  
  "texture_details": "Detailed texture description. How does it feel to touch? Is it smooth, rough, crystalline, powdery, sticky, crusty? Include any grain, pattern, or structure visible at close range.",
  
  "common_patterns": "How does it distribute on {material_name}? Does it form uniform coating, localized spots, streaks, drip marks? Where does it accumulate first (edges, crevices, flat surfaces)?",
  
  "aged_appearance": "How does appearance change over time? Compare fresh contamination (hours/days old) to aged contamination (months/years old). Include color changes, texture evolution, thickness buildup.",
  
  "lighting_effects": "How does it look under different lighting? Direct sunlight vs indoor fluorescent? Any sheen, gloss, matte finish, iridescence, or rainbow effects?",
  
  "thickness_range": "Typical thickness from thin film to heavy buildup. Use measurements (micrometers, millimeters) or comparisons (paper-thin, coin-thick).",
  
  "distribution_patterns": "What are the typical distribution patterns on {material_name}? Describe specific types: uniform coating, edge accumulation, point source spreading, gradient from source, patchy/spotty, streaky/linear, localized concentrations, radial patterns, etc. Be specific about which patterns are most common.",
  
  "uniformity_assessment": "How uniform is the distribution on {material_name}? Rate and describe: perfectly uniform across surface, mostly uniform with minor variations, moderately patchy, highly variable/irregular, concentrated in specific areas. Explain what causes the uniformity level.",
  
  "concentration_variations": "Where does concentration vary on {material_name}? Which areas tend to be heavy vs light? Consider: edges vs center, top vs bottom, corners, crevices, flat surfaces, vertical walls, horizontal surfaces, exposed areas, sheltered areas. Describe the gradient patterns.",
  
  "typical_formations": "What physical formations does {contaminant_name} create on {material_name}? Describe specific formations: drip marks, runs/streaks, pools/puddles, thin films, thick crusts, discrete patches, spots/dots, stains, uniform coatings, buildups, crystalline structures, etc. Be detailed about formation mechanisms.",
  
  "geometry_effects": "How does surface geometry affect distribution on {material_name}? Describe behavior: accumulates in corners, builds up in crevices, pools on flat areas, drips on vertical surfaces, collects at edges, follows contours, bridges gaps, fills depressions. Explain the physical reasons.",
  
  "gravity_influence": "How does gravity affect the distribution pattern on {material_name}? Describe: downward flow behavior, pooling at bottom edges, drip marks from top to bottom, vertical streaking, settling on horizontal surfaces, runs down slopes, hangs from overhead surfaces. Quantify if possible.",
  
  "coverage_ranges": "What are typical coverage percentages for different contamination levels on {material_name}? Define and describe: sparse (<10% coverage), light (10-30%), moderate (30-60%), heavy (60-85%), extreme (>85%). For each level, describe visual appearance and typical thickness.",
  
  "edge_center_behavior": "Does {contaminant_name} prefer edges, center, or distribute uniformly on {material_name}? Describe: preferentially accumulates at edges, concentrates in center areas, distributes uniformly, avoids edges, follows perimeter, random distribution. Explain the mechanism causing this behavior.",
  
  "buildup_progression": "How does {contaminant_name} build up over time on {material_name}? Describe progression: starts as thin film then thickens, begins at contact points then spreads, starts at edges then moves inward, uniform gradual accumulation, point sources that expand outward, layering effects, seasonal variations. Include timeframes (hours, days, months)."
}}

CRITICAL: Return ONLY the JSON object. No additional text before or after. Base answers on real-world industrial experience and scientific accuracy. Give EQUAL detail to both visual characteristics AND distribution patterns.
"""
        
        return prompt
    
    def _parse_response(self, response_text: str) -> Dict[str, str]:
        """Parse Gemini response into structured data."""
        
        # Clean response - remove markdown code blocks if present
        text = response_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        try:
            # Parse JSON
            data = json.loads(text)
            
            # Validate required fields
            required_fields = [
                # Visual characteristics (7 fields)
                'description', 'color_variations', 'texture_details',
                'common_patterns', 'aged_appearance', 'lighting_effects',
                'thickness_range',
                # Distribution characteristics (8 fields - equal detail)
                'distribution_patterns', 'uniformity_assessment', 'concentration_variations',
                'typical_formations', 'geometry_effects', 'gravity_influence',
                'coverage_ranges', 'edge_center_behavior', 'buildup_progression'
            ]
            
            for field in required_fields:
                if field not in data:
                    logger.warning(f"Missing field in response: {field}")
                    data[field] = "Not researched"
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {text[:500]}")
            
            # Return basic structure with raw text
            return {
                # Visual characteristics
                'description': text[:500],
                'color_variations': 'Parse failed - see description',
                'texture_details': 'Parse failed - see description',
                'common_patterns': 'Parse failed - see description',
                'aged_appearance': 'Parse failed - see description',
                'lighting_effects': 'Parse failed - see description',
                'thickness_range': 'Parse failed - see description',
                # Distribution characteristics
                'distribution_patterns': 'Parse failed - see description',
                'uniformity_assessment': 'Parse failed - see description',
                'concentration_variations': 'Parse failed - see description',
                'typical_formations': 'Parse failed - see description',
                'geometry_effects': 'Parse failed - see description',
                'gravity_influence': 'Parse failed - see description',
                'coverage_ranges': 'Parse failed - see description',
                'edge_center_behavior': 'Parse failed - see description',
                'buildup_progression': 'Parse failed - see description'
            }
    
    def research_multiple_materials(
        self,
        contaminant_id: str,
        contaminant_name: str,
        material_names: List[str],
        chemical_composition: Optional[str] = None
    ) -> Dict[str, Dict[str, str]]:
        """
        Research appearance on multiple materials.
        
        Args:
            contaminant_id: Contaminant ID
            contaminant_name: Human-readable name
            material_names: List of material names
            chemical_composition: Optional chemical composition
        
        Returns:
            Dict mapping material names to appearance data
        """
        results = {}
        
        print(f"\n📊 Batch research: {contaminant_name} on {len(material_names)} materials")
        
        for i, material_name in enumerate(material_names, 1):
            print(f"\n[{i}/{len(material_names)}] {material_name}")
            
            try:
                appearance = self.research_appearance_on_material(
                    contaminant_id=contaminant_id,
                    contaminant_name=contaminant_name,
                    material_name=material_name,
                    chemical_composition=chemical_composition
                )
                
                results[material_name.lower()] = appearance
                
            except Exception as e:
                logger.error(f"Failed to research {material_name}: {e}")
                print(f"   ⚠️  Skipping {material_name} due to error")
                continue
        
        print(f"\n✅ Batch research complete: {len(results)}/{len(material_names)} successful")
        return results
    
    def research_appearance_on_category(
        self,
        contaminant_id: str,
        contaminant_name: str,
        category_name: str,
        chemical_composition: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Research how contaminant appears on an entire material category.
        More efficient than per-material research - generates one comprehensive
        description applicable to all materials in the category.
        
        Args:
            contaminant_id: Unique ID (e.g., "rust-oxidation")
            contaminant_name: Human-readable name (e.g., "Rust / Iron Oxide")
            category_name: Category name (e.g., "metal", "ceramic", "glass")
            chemical_composition: Optional chemical formula/composition
        
        Returns:
            Dictionary with detailed visual descriptions applicable to entire category
        """
        print(f"\n🔬 Researching visual appearance: {contaminant_name} on {category_name.upper()} category")
        
        # Build category-level research prompt
        prompt = self._build_category_research_prompt(
            contaminant_id=contaminant_id,
            contaminant_name=contaminant_name,
            category_name=category_name,
            chemical_composition=chemical_composition
        )
        
        try:
            # Query Gemini
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.3,
                    'top_p': 0.95,
                    'top_k': 40,
                    'max_output_tokens': 8192
                }
            )
            
            # Parse response
            result = self._parse_response(response.text)
            
            print(f"   ✅ Research complete: {len(result)} visual aspects documented")
            return result
            
        except Exception as e:
            logger.error(f"Research failed for {contaminant_name} on {category_name}: {e}")
            print(f"   ❌ Research failed: {e}")
            raise
    
    def _build_category_research_prompt(
        self,
        contaminant_id: str,
        contaminant_name: str,
        category_name: str,
        chemical_composition: Optional[str] = None
    ) -> str:
        """Build detailed research prompt for category-level research."""
        
        # Base prompt
        prompt = f"""You are a materials science and industrial contamination expert. Research the visual appearance of {contaminant_name} on {category_name.upper()} surfaces in general.

MATERIAL CATEGORY: {category_name.upper()} (covers all {category_name} materials: metals like steel/aluminum/copper, ceramics like alumina/silicon carbide, etc.)
"""
        
        # Add chemical info if available
        if chemical_composition:
            prompt += f"\nContaminant Composition: {chemical_composition}\n"
        
        prompt += f"""
TASK: Provide detailed visual descriptions applicable to ALL materials in the {category_name} category. Focus on photo-realistic details that would be visible in industrial/technical photography. Describe characteristics common across {category_name} surfaces.

Provide information in the following structure (use JSON format):

{{
  "description": "2-3 sentence overall description of how {contaminant_name} appears on {category_name} surfaces. Include dominant colors, general texture, and typical coverage patterns common across this material category.",
  
  "color_variations": "Detailed color range specific to {category_name} materials. List 3-5 specific colors/shades from fresh to aged. Be precise (e.g., 'rust-orange with brown edges' not just 'orange').",
  
  "texture_details": "Detailed texture description on {category_name} surfaces. How does it feel to touch? Is it smooth, rough, crystalline, powdery, sticky, crusty? Include any grain, pattern, or structure visible at close range.",
  
  "common_patterns": "How does it distribute on {category_name} surfaces? Does it form uniform coating, localized spots, streaks, drip marks? Where does it accumulate first (edges, crevices, flat surfaces)?",
  
  "aged_appearance": "How does appearance change over time on {category_name}? Compare fresh contamination (hours/days old) to aged contamination (months/years old). Include color changes, texture evolution, thickness buildup.",
  
  "lighting_effects": "How does it look under different lighting on {category_name}? Direct sunlight vs indoor fluorescent? Any sheen, gloss, matte finish, iridescence, or rainbow effects?",
  
  "thickness_range": "Typical thickness on {category_name} from thin film to heavy buildup. Use measurements (micrometers, millimeters) or comparisons (paper-thin, coin-thick).",
  
  "distribution_patterns": "What are the typical distribution patterns on {category_name} surfaces? Describe specific types: uniform coating, edge accumulation, point source spreading, gradient from source, patchy/spotty, streaky/linear, localized concentrations, radial patterns, etc. Be specific about which patterns are most common on this material category.",
  
  "uniformity_assessment": "How uniform is the distribution on {category_name} surfaces? Rate and describe: perfectly uniform across surface, mostly uniform with minor variations, moderately patchy, highly variable/irregular, concentrated in specific areas. Explain what causes the uniformity level on this material type.",
  
  "concentration_variations": "Where does concentration vary on {category_name} surfaces? Which areas tend to be heavy vs light? Consider: edges vs center, top vs bottom, corners, crevices, flat surfaces, vertical walls, horizontal surfaces, exposed areas, sheltered areas. Describe the gradient patterns typical for this material category.",
  
  "typical_formations": "What physical formations does {contaminant_name} create on {category_name} surfaces? Describe specific formations: drip marks, runs/streaks, pools/puddles, thin films, thick crusts, discrete patches, spots/dots, stains, uniform coatings, buildups, crystalline structures, etc. Be detailed about formation mechanisms on this material type.",
  
  "geometry_effects": "How does surface geometry affect distribution on {category_name}? Describe behavior: accumulates in corners, builds up in crevices, pools on flat areas, drips on vertical surfaces, collects at edges, follows contours, bridges gaps, fills depressions. Explain the physical reasons specific to this material category.",
  
  "gravity_influence": "How does gravity affect the distribution pattern on {category_name} surfaces? Describe: downward flow behavior, pooling at bottom edges, drip marks from top to bottom, vertical streaking, settling on horizontal surfaces, runs down slopes, hangs from overhead surfaces. Quantify if possible for this material type.",
  
  "coverage_ranges": "What are typical coverage percentages for different contamination levels on {category_name}? Define and describe: sparse (<10% coverage), light (10-30%), moderate (30-60%), heavy (60-85%), extreme (>85%). For each level, describe visual appearance and typical thickness on this material category.",
  
  "edge_center_behavior": "Does {contaminant_name} prefer edges, center, or distribute uniformly on {category_name} surfaces? Describe: preferentially accumulates at edges, concentrates in center areas, distributes uniformly, avoids edges, follows perimeter, random distribution. Explain the mechanism causing this behavior on this material type.",
  
  "buildup_progression": "How does {contaminant_name} build up over time on {category_name} surfaces? Describe progression: starts as thin film then thickens, begins at contact points then spreads, starts at edges then moves inward, uniform gradual accumulation, point sources that expand outward, layering effects, seasonal variations. Include timeframes (hours, days, months) typical for this material category."
}}

CRITICAL: Return ONLY the JSON object. No additional text before or after. Base answers on real-world industrial experience and scientific accuracy. Focus on characteristics COMMON ACROSS ALL {category_name.upper()} MATERIALS. Give EQUAL detail to both visual characteristics AND distribution patterns.
"""
        
        return prompt
    
    def format_for_yaml(self, appearance_data: Dict[str, str]) -> Dict[str, str]:
        """
        Format appearance data for insertion into Contaminants.yaml.
        
        Args:
            appearance_data: Raw research results
        
        Returns:
            Formatted dict ready for YAML insertion (15 fields total)
        """
        return {
            # Visual characteristics (7 fields)
            'description': appearance_data.get('description', ''),
            'color_variations': appearance_data.get('color_variations', ''),
            'texture_details': appearance_data.get('texture_details', ''),
            'common_patterns': appearance_data.get('common_patterns', ''),
            'aged_appearance': appearance_data.get('aged_appearance', ''),
            'lighting_effects': appearance_data.get('lighting_effects', ''),
            'thickness_range': appearance_data.get('thickness_range', ''),
            # Distribution characteristics (8 fields - equal detail)
            'distribution_patterns': appearance_data.get('distribution_patterns', ''),
            'uniformity_assessment': appearance_data.get('uniformity_assessment', ''),
            'concentration_variations': appearance_data.get('concentration_variations', ''),
            'typical_formations': appearance_data.get('typical_formations', ''),
            'geometry_effects': appearance_data.get('geometry_effects', ''),
            'gravity_influence': appearance_data.get('gravity_influence', ''),
            'coverage_ranges': appearance_data.get('coverage_ranges', ''),
            'edge_center_behavior': appearance_data.get('edge_center_behavior', ''),
            'buildup_progression': appearance_data.get('buildup_progression', '')
        }


def create_researcher(api_key: Optional[str] = None) -> VisualAppearanceResearcher:
    """
    Factory function to create researcher instance.
    
    Args:
        api_key: Optional API key (uses environment variable if not provided)
    
    Returns:
        VisualAppearanceResearcher instance
    """
    return VisualAppearanceResearcher(api_key=api_key)
