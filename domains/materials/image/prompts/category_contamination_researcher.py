#!/usr/bin/env python3
"""
Category-Level Contamination Pattern Researcher

Researches contamination patterns at the material category level (metals, ceramics, 
polymers, etc.) with abundant real-world photo references and reusable patterns.

Author: AI Assistant
Date: November 25, 2025
"""

import json
import logging
import os
from typing import Dict, Optional, List
from functools import lru_cache

import google.generativeai as genai

logger = logging.getLogger(__name__)


class CategoryContaminationResearcher:
    """Research category-level contamination patterns with photo-reference accuracy"""
    
    # Material category mappings
    CATEGORY_MAP = {
        # Metals
        "Aluminum": "metals_non_ferrous",
        "Copper": "metals_non_ferrous",
        "Brass": "metals_non_ferrous",
        "Bronze": "metals_non_ferrous",
        "Zinc": "metals_non_ferrous",
        "Titanium": "metals_reactive",
        "Magnesium": "metals_reactive",
        "Steel": "metals_ferrous",
        "Iron": "metals_ferrous",
        "Stainless Steel": "metals_corrosion_resistant",
        "Chrome": "metals_corrosion_resistant",
        
        # Ceramics
        "Porcelain": "ceramics_traditional",
        "Terracotta": "ceramics_traditional",
        "Brick": "ceramics_construction",
        "Concrete": "ceramics_construction",
        "Glass": "ceramics_glass",
        
        # Polymers
        "ABS": "polymers_thermoplastic",
        "Polycarbonate": "polymers_thermoplastic",
        "Nylon": "polymers_engineering",
        "Rubber": "polymers_elastomer",
        
        # Composites
        "Fiberglass": "composites_polymer_matrix",
        "Carbon Fiber": "composites_polymer_matrix",
    }
    
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
        
        logger.info("✅ Category contamination researcher initialized with Gemini Flash 2.0")
    
    def get_category(self, material_name: str) -> str:
        """Get material category for contamination research."""
        # Direct lookup
        if material_name in self.CATEGORY_MAP:
            return self.CATEGORY_MAP[material_name]
        
        # Fuzzy matching for alloys and variations
        material_lower = material_name.lower()
        if "steel" in material_lower or "iron" in material_lower:
            if "stainless" in material_lower:
                return "metals_corrosion_resistant"
            return "metals_ferrous"
        elif any(m in material_lower for m in ["aluminum", "copper", "brass", "bronze", "zinc"]):
            return "metals_non_ferrous"
        elif "titanium" in material_lower or "magnesium" in material_lower:
            return "metals_reactive"
        elif "glass" in material_lower:
            return "ceramics_glass"
        elif any(c in material_lower for c in ["ceramic", "porcelain", "clay"]):
            return "ceramics_traditional"
        elif any(c in material_lower for c in ["concrete", "brick", "cement"]):
            return "ceramics_construction"
        elif any(p in material_lower for p in ["plastic", "polymer", "abs", "pvc"]):
            return "polymers_thermoplastic"
        elif "fiber" in material_lower or "composite" in material_lower:
            return "composites_polymer_matrix"
        
        # Default to generic
        return "generic_industrial_material"
    
    @lru_cache(maxsize=32)
    def research_category_contamination(
        self,
        category: str
    ) -> Dict[str, any]:
        """
        Research contamination patterns for a material category with photo references.
        
        Args:
            category: Material category (e.g., "metals_ferrous", "ceramics_traditional")
            
        Returns:
            Dictionary with comprehensive contamination patterns
        """
        prompt = self._build_category_research_prompt(category)
        
        logger.info(f"🔬 Researching contamination patterns for category: {category}")
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Strip markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif response_text.startswith("```"):
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            data = json.loads(response_text)
            
            logger.info(f"✅ Category research complete: {len(data.get('contamination_patterns', []))} patterns found")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse research response: {e}")
            return self._get_fallback_category_data(category)
        except Exception as e:
            logger.error(f"❌ Research failed: {e}")
            return self._get_fallback_category_data(category)
    
    def _build_category_research_prompt(self, category: str) -> str:
        """Build research prompt for category-level contamination."""
        return f"""Research contamination patterns for the material category: {category}

GOAL: Create a reusable contamination pattern library based on REAL industrial photos and documentation.

RESEARCH FOCUS: Find actual photographs and documented cases of contaminated {category} materials.
Search sources: Industrial cleaning documentation, material science papers, corrosion studies, 
conservation/restoration guides, manufacturing quality control documentation.

CONTAMINATION PATTERNS (3-7 patterns, ordered by prevalence):

For EACH contamination pattern, provide:

1. **Pattern Name**: Descriptive name (e.g., "Industrial Oil Buildup", "Environmental Rust Layer")

2. **Photo Reference Description**: 
   - Describe what you'd see in actual photos of this contamination
   - Reference specific industrial/real-world examples
   - Include lighting characteristics (how light interacts with contamination)

3. **Visual Characteristics**:
   - **Color Range**: Specific color variations (not just "brown" but "orange-brown to dark red-brown")
   - **Texture**: Detailed physical texture (matte, glossy, granular, smooth, rough, flaky)
   - **Thickness Variation**: How thickness varies across surface (edges vs. centers, protected vs. exposed)
   - **Edge Characteristics**: How contamination boundaries appear (gradual fade, sharp edge, irregular)

4. **Distribution Physics**:
   - **Gravity Effects**: How does gravity affect this contamination? (drips, runs, pooling, settling)
   - **Accumulation Zones**: Where does it collect? (bottom, crevices, horizontal surfaces, edges)
   - **Coverage Pattern**: Uniform, patchy, streaked, localized, layered?
   - **Density Variation**: Thick → thin gradient patterns

5. **Layer Interaction**:
   - How does this contamination interact with the base material?
   - How does it interact with other contaminants? (overlaps, mixing, stratification)
   - Does it obscure or enhance surface features?

6. **Lighting Response**:
   - How does light reflect off this contamination? (absorbs, reflects, scatters)
   - Shadow characteristics in/around contamination
   - How does it look under different lighting? (overhead, side, diffuse)

7. **Weathering Progression**:
   - Fresh vs. aged appearance differences
   - Color changes over time
   - Texture evolution (smooth → cracked, uniform → patchy)

8. **Prevalence & Context**:
   - How common is this pattern? (very common, common, occasional, rare)
   - Typical environmental conditions that cause it
   - Time scale for formation (hours, days, months, years)

9. **Realism Red Flags to AVOID**:
   - What artificial patterns should we specifically avoid for this contamination?
   - Common AI-generation mistakes for this pattern
   - Physics violations to watch for

Format as JSON:

{{
    "category": "{category}",
    "contamination_patterns": [
        {{
            "pattern_name": "...",
            "photo_reference": "...",
            "visual_characteristics": {{
                "color_range": "...",
                "texture_detail": "...",
                "thickness_variation": "...",
                "edge_characteristics": "..."
            }},
            "distribution_physics": {{
                "gravity_effects": "...",
                "accumulation_zones": "...",
                "coverage_pattern": "...",
                "density_variation": "..."
            }},
            "layer_interaction": "...",
            "lighting_response": "...",
            "weathering_progression": "...",
            "prevalence": "very common|common|occasional|rare",
            "formation_context": "...",
            "realism_avoid": ["...", "..."]
        }}
    ],
    "base_appearance": {{
        "typical_color_range": "...",
        "surface_characteristics": "...",
        "common_surface_features": "..."
    }},
    "photo_reference_notes": "Notes about documented real-world examples"
}}

CRITICAL: Base ALL descriptions on actual photographs and documented cases. 
Describe what contamination ACTUALLY looks like in industrial settings, not idealized versions."""
    
    def _get_fallback_category_data(self, category: str) -> Dict:
        """Provide basic fallback data if research fails."""
        return {
            "category": category,
            "contamination_patterns": [
                {
                    "pattern_name": "Environmental buildup",
                    "photo_reference": "General industrial contamination",
                    "visual_characteristics": {
                        "color_range": "Gray to dark brown",
                        "texture_detail": "Uneven, matte surface",
                        "thickness_variation": "Heavier in protected areas",
                        "edge_characteristics": "Irregular boundaries"
                    },
                    "distribution_physics": {
                        "gravity_effects": "Drips downward on vertical surfaces",
                        "accumulation_zones": "Bottom edges, crevices, horizontal surfaces",
                        "coverage_pattern": "Patchy and uneven",
                        "density_variation": "Thicker at bottom, thinner at top"
                    },
                    "layer_interaction": "Partially obscures base material",
                    "lighting_response": "Matte, absorbs most light",
                    "weathering_progression": "Darkens and hardens over time",
                    "prevalence": "very common",
                    "formation_context": "Environmental exposure",
                    "realism_avoid": ["uniform coverage", "perfect circles", "floating particles"]
                }
            ],
            "base_appearance": {
                "typical_color_range": "Material-dependent",
                "surface_characteristics": "Varies by processing",
                "common_surface_features": "Machining marks, grain patterns"
            },
            "photo_reference_notes": "Fallback data - research unavailable"
        }
    
    def apply_patterns_to_material(
        self,
        material_name: str,
        category_data: Dict,
        num_patterns: int = 3
    ) -> Dict:
        """
        Apply category-level patterns to specific material for image generation.
        
        Args:
            material_name: Specific material name
            category_data: Category research data
            num_patterns: Number of contamination patterns to apply
            
        Returns:
            Material-specific contamination data for image generation
        """
        patterns = category_data.get('contamination_patterns', [])[:num_patterns]
        
        return {
            "material": material_name,
            "category": category_data.get('category'),
            "selected_patterns": patterns,
            "base_appearance": category_data.get('base_appearance'),
            "photo_reference_notes": category_data.get('photo_reference_notes')
        }
