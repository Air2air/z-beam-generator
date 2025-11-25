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
import time
from typing import Dict, Optional, List
from functools import lru_cache

import google.generativeai as genai

from .persistent_research_cache import PersistentResearchCache
from .payload_monitor import get_payload_monitor

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
        
        # Wood
        "Oak": "wood_hardwood",
        "Maple": "wood_hardwood",
        "Maple Wood": "wood_hardwood",
        "Cherry": "wood_hardwood",
        "Walnut": "wood_hardwood",
        "Mahogany": "wood_hardwood",
        "Pine": "wood_softwood",
        "Cedar": "wood_softwood",
        "Spruce": "wood_softwood",
        "Plywood": "wood_engineered",
        "MDF": "wood_engineered",
    }
    
    def __init__(self, api_key: Optional[str] = None, cache_dir: Optional[str] = None):
        """
        Initialize researcher with Gemini API and persistent cache.
        
        Args:
            api_key: Optional Gemini API key (will use env var if not provided)
            cache_dir: Optional cache directory (default: cache/research/)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment or provided")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Initialize persistent cache
        from pathlib import Path
        cache_path = Path(cache_dir) if cache_dir else None
        self.cache = PersistentResearchCache(cache_dir=cache_path, ttl_days=30)
        
        # Initialize payload monitor for conformity tracking
        self.monitor = get_payload_monitor()
        
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
        elif "wood" in material_lower or any(w in material_lower for w in ["oak", "maple", "pine", "cedar", "cherry", "walnut", "mahogany"]):
            if "plywood" in material_lower or "mdf" in material_lower:
                return "wood_engineered"
            elif any(h in material_lower for h in ["oak", "maple", "cherry", "walnut", "mahogany"]):
                return "wood_hardwood"
            return "wood_softwood"
        
        # Default to generic
        return "generic_industrial_material"
    
    def _clean_json_response(self, json_text: str, attempt: int = 0) -> str:
        """
        Clean JSON response with progressive repair strategies.
        
        Args:
            json_text: Raw JSON text from LLM
            attempt: Retry attempt number (0-2) - determines aggressiveness
            
        Returns:
            Cleaned JSON text ready for parsing
        """
        import re
        
        # Remove any leading/trailing whitespace
        json_text = json_text.strip()
        
        # STRATEGY 1: Light cleaning (attempt 0)
        if attempt == 0:
            # Just strip markdown and trailing commas
            json_text = re.sub(r',\s*}', '}', json_text)
            json_text = re.sub(r',\s*]', ']', json_text)
            return json_text
        
        # STRATEGY 2: Moderate cleaning (attempt 1)
        if attempt == 1:
            # Fix literal newlines inside strings
            parts = json_text.split('"')
            for i in range(1, len(parts), 2):  # Odd indices = inside strings
                parts[i] = parts[i].replace('\n', '\\n').replace('\r', '\\r')
            json_text = '"'.join(parts)
            
            # Trailing commas
            json_text = re.sub(r',\s*}', '}', json_text)
            json_text = re.sub(r',\s*]', ']', json_text)
            return json_text
        
        # STRATEGY 3: Aggressive cleaning (attempt 2+)
        # Find and escape unescaped quotes inside strings
        # This is the nuclear option - walk through char by char
        result = []
        in_string = False
        escape_next = False
        
        for i, char in enumerate(json_text):
            if escape_next:
                result.append(char)
                escape_next = False
                continue
                
            if char == '\\':
                result.append(char)
                escape_next = True
                continue
                
            if char == '"':
                # Check context to determine if this is a string delimiter or internal quote
                if not in_string:
                    # Starting a string
                    in_string = True
                    result.append(char)
                else:
                    # Could be ending string or internal quote
                    # Look ahead: if followed by : or , or } or ], it's likely a delimiter
                    next_meaningful = None
                    for j in range(i + 1, min(i + 5, len(json_text))):
                        if json_text[j] not in ' \t\n\r':
                            next_meaningful = json_text[j]
                            break
                    
                    if next_meaningful in [':', ',', '}', ']', None]:
                        # This is a string delimiter
                        in_string = False
                        result.append(char)
                    else:
                        # This is likely an internal quote - escape it
                        result.append('\\"')
                continue
            
            result.append(char)
        
        json_text = ''.join(result)
        
        # Final cleanup
        json_text = re.sub(r',\s*}', '}', json_text)
        json_text = re.sub(r',\s*]', ']', json_text)
        
        return json_text
    
    def research_category_contamination(
        self,
        category: str,
        max_retries: int = 3
    ) -> Dict[str, any]:
        """
        Research contamination patterns for a material category with persistent cache and retry logic.
        
        Args:
            category: Material category (e.g., "metals_ferrous", "ceramics_traditional")
            max_retries: Maximum retry attempts for JSON parsing failures (default: 3)
            
        Returns:
            Dictionary with comprehensive contamination patterns
        """
        print(f"\n{'='*80}")
        print(f"🔬 CATEGORY RESEARCH: {category}")
        print(f"{'='*80}")
        
        # Check persistent cache first
        cached_data = self.cache.get(category)
        if cached_data is not None:
            print(f"✅ Cache hit - using stored research for {category}")
            print(f"   • Patterns cached: {len(cached_data.get('contamination_patterns', []))}")
            print(f"   • Cache location: {self.cache._get_cache_path(category)}")
            logger.info(f"📬 Using cached research for {category}")
            return cached_data
        
        # Cache miss - research with API
        print(f"📭 Cache miss - researching {category} with Gemini API")
        print(f"   • Building research prompt...")
        logger.info(f"🔬 Researching contamination patterns for category: {category}")
        
        # Get adaptive guidance from monitor based on recent failures
        adaptive_guidance = self.monitor.get_adaptive_prompt_guidance(category)
        
        prompt = self._build_category_research_prompt(category)
        if adaptive_guidance:
            print("   • Adding adaptive JSON guidance based on recent failures...")
            prompt += adaptive_guidance
        
        print(f"   • Prompt built: {len(prompt)} characters")
        
        # Retry loop for JSON parsing failures
        for attempt in range(max_retries):
            try:
                print(f"\n🌐 API Call (attempt {attempt + 1}/{max_retries})")
                print(f"   • Sending request to Gemini Flash 2.0...")
                
                response = self.model.generate_content(prompt)
                response_text = response.text
                
                print(f"   • Response received: {len(response_text)} characters")
                print(f"   • Parsing JSON response...")
                
                # Strip markdown code blocks if present
                if response_text.startswith("```json"):
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                    print(f"   • Stripped markdown wrapper")
                elif response_text.startswith("```"):
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                    print(f"   • Stripped code block wrapper")
                
                # Clean JSON with progressive strategies based on attempt number
                print(f"   • Applying JSON cleaning strategy {attempt + 1}/{max_retries}...")
                response_text = self._clean_json_response(response_text, attempt)
                
                data = json.loads(response_text)
                
                print(f"   ✅ JSON parsed successfully")
                
                # Validate schema conformity
                is_valid, violations = self.monitor.validate_schema(data, category)
                if not is_valid:
                    print(f"   ⚠️  Schema violations detected: {len(violations)}")
                    for violation in violations[:3]:  # Show first 3
                        print(f"      • {violation}")
                else:
                    print(f"   ✅ Schema validation passed")
                
                print(f"   • Patterns found: {len(data.get('contamination_patterns', []))}")
                print(f"   • Base appearance data: {'Yes' if data.get('base_appearance') else 'No'}")
                
                # Record successful parse
                self.monitor.record_parse_attempt(
                    category=category,
                    attempt_num=attempt + 1,
                    success=True,
                    cleaning_strategy=attempt
                )
                
                # Success - cache the result
                print(f"\n💾 Caching research results...")
                self.cache.set(category, data)
                print(f"   ✅ Cached to: {self.cache._get_cache_path(category)}")
                print(f"   • TTL: 30 days")
                
                print(f"\n{'='*80}")
                print(f"✅ RESEARCH COMPLETE: {category}")
                print(f"{'='*80}\n")
                
                logger.info(f"✅ Category research complete: {len(data.get('contamination_patterns', []))} patterns found")
                return data
                
            except json.JSONDecodeError as e:
                # Record failure in monitor
                self.monitor.record_parse_attempt(
                    category=category,
                    attempt_num=attempt + 1,
                    success=False,
                    error=e,
                    raw_json=response_text if attempt == max_retries - 1 else None,
                    cleaning_strategy=attempt
                )
                
                # Show diagnostic info about the failure
                error_line = getattr(e, 'lineno', None)
                error_col = getattr(e, 'colno', None)
                error_pos = getattr(e, 'pos', None)
                
                print(f"\n❌ JSON parsing failed:")
                print(f"   • Error: {e.msg}")
                if error_line and error_col:
                    print(f"   • Location: line {error_line}, column {error_col}")
                if error_pos:
                    # Show context around error position
                    start = max(0, error_pos - 100)
                    end = min(len(response_text), error_pos + 100)
                    context = response_text[start:end]
                    print(f"   • Context: ...{context}...")
                
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    print(f"\n🔄 Retrying with strategy {attempt + 2}/{max_retries} in {wait_time}s...")
                    logger.warning(f"⚠️  JSON parsing failed for {category} (attempt {attempt + 1}/{max_retries}): {e}")
                    logger.info(f"🔄 Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ Failed to parse research response for {category} after {max_retries} attempts: {e}")
                    
                    # Show monitoring report
                    print(self.monitor.get_monitoring_report())
                    
                    raise RuntimeError(f"Failed to parse contamination research for {category}. Invalid JSON response after {max_retries} retries.") from e
            except Exception as e:
                logger.error(f"❌ Research failed for {category}: {e}")
                raise RuntimeError(f"Failed to research contamination patterns for {category}.") from e
        
        # Should never reach here, but for type safety
        raise RuntimeError(f"Unexpected error in research for {category}")
    
    def _build_category_research_prompt(self, category: str) -> str:
        """Build research prompt for category-level contamination."""
        return f"""Research contamination patterns AND aging effects for material category: {category}

GOAL: Create a reusable contamination pattern library based on REAL industrial photos, conservation documentation, and material degradation studies.

CRITICAL: AGING EFFECTS are weighted EQUALLY with traditional contamination. For organics (wood, polymers, natural materials), aging is the PRIMARY contamination concern.

RESEARCH FOCUS: Find actual photographs and documented cases of:
1. Contaminated {category} materials (industrial, environmental, biological)
2. Aged/degraded {category} materials (UV damage, oxidation, biological decay, chemical breakdown)
3. Combined aging + contamination effects

Search sources: Industrial cleaning documentation, material science papers, corrosion studies, 
conservation/restoration guides, manufacturing quality control documentation, museum conservation reports,
weathering studies, accelerated aging research, outdoor exposure trials, archaeological preservation studies.

CONTAMINATION & AGING PATTERNS (5-9 patterns total, ordered by prevalence):

INCLUDE BOTH:
- Traditional contamination patterns (dirt, oils, deposits, stains)
- Aging/degradation patterns (oxidation, UV damage, hydrolysis, biological decay, embrittlement, discoloration)

For EACH pattern (contamination OR aging), provide:

1. **Pattern Name**: Descriptive name
   - Contamination examples: "Industrial Oil Buildup", "Environmental Dust Layer", "Biological Growth"
   - Aging examples: "UV Photodegradation", "Oxidative Discoloration", "Surface Chalking", "Biodegradation", "Stress Cracking"

2. **Photo Reference URLs** (CRITICAL FOR REALISM):
   - Provide 2-4 actual image URLs showing this pattern
   - Sources: Industrial documentation, conservation projects, material science papers, weathering studies
   - Simple format: Just the URL, description in separate field
   - Example URLs (fictitious, for format only):
     * https://example.com/steel-rust-progression.jpg
     * https://example.com/aluminum-oil-buildup.jpg
     * https://example.com/composite-UV-damage.jpg
   - Include search terms used to find these images
   - Note: These URLs anchor the AI to real-world photographic evidence

3. **Photo Reference Description**: 
   - Describe what you'd see in actual photos of this pattern
   - Reference specific industrial/conservation/weathering examples
   - Include micro-scale details visible in close-up photography
   - Lighting characteristics (how light interacts with aged/contaminated surface)

4. **Visual Characteristics**:
   - **Color Range**: Specific color variations with aging progression (e.g., "white → cream → yellow-brown over months")
   - **Texture**: Detailed physical texture evolution (smooth → crazed → cracked → flaked)
   - **Thickness Variation**: How pattern depth varies across surface
   - **Edge Characteristics**: Gradual fade vs. sharp boundary, feathering, undercutting
   - **Surface Topology Changes**: Erosion, pitting, roughening, delamination, fiber exposure

5. **Distribution Physics**:
   - **Gravity Effects**: Drips, runs, pooling, settling patterns
   - **Environmental Exposure Patterns**: UV-facing vs. shaded, wet vs. dry zones, airflow effects
   - **Accumulation Zones**: Where contamination/degradation concentrates (edges, joints, grain, stress points)
   - **Coverage Pattern**: Uniform, patchy, streaked, localized, stratified, gradient-based
   - **Density Variation**: Thick → thin gradients, severity mapping
   - **Substrate Interaction**: How material structure affects distribution (grain following, stress concentration, porosity effects)

6. **Aging Timeline & Progression**:
   - **Formation Rate**: Hours, days, weeks, months, years for visible change
   - **Early Stage (0-25% progression)**: Initial appearance, barely visible changes
   - **Mid Stage (25-75%)**: Pronounced changes, clear visual impact
   - **Advanced Stage (75-100%)**: Severe degradation, structural changes
   - **Color Evolution**: Specific color shift sequence over time
   - **Texture Evolution**: Surface transformation sequence
   - **Reversibility**: Can this be cleaned/restored? Permanent damage?

7. **Layer Interaction & Complexity**:
   - How does this interact with the base material? (penetrates, coats, reacts chemically, breaks down structure)
   - How does it interact with other contaminants/aging? (accelerates, masks, combines with)
   - Synergistic effects (UV + moisture, oil + heat, biological + chemical)
   - Does it obscure or enhance surface features?
   - Stratification patterns (which layers form first, which accumulate on top)

8. **Micro-Scale Distribution Reality**:
   - **Grain Following**: How does pattern follow material grain/structure?
   - **Edge Effects**: Concentration at edges, corners, joints, fasteners
   - **Stress Point Indicators**: Cracks, deformation zones, high-wear areas show different aging
   - **Porosity Effects**: How surface porosity affects contamination/aging distribution
   - **Anisotropic Patterns**: Directional effects (flow marks, extrusion direction, grain orientation)
   - **Boundary Transitions**: How does severity change across zones? (sharp vs. gradual)

9. **Lighting Response & Optical Properties**:
   - How does light reflect off this pattern? (absorbs, reflects, scatters, diffuses)
   - Gloss changes (glossy → satin → matte with aging)
   - Shadow characteristics in/around pattern
   - Appearance under different lighting angles (grazing light reveals texture)
   - Translucency changes (aging may increase/decrease light transmission)
   - Color shift under different illumination (daylight vs. indoor, directional vs. diffuse)

10. **Environmental Context & Formation Conditions**:
   - **Typical Environments**: Indoor/outdoor, industrial/residential, marine/desert/urban
   - **Required Conditions**: Temperature range, humidity, UV exposure, chemical exposure
   - **Accelerating Factors**: Heat, moisture, pollutants, mechanical stress, biological activity
   - **Protective Factors**: Coatings, shading, low humidity, clean environments
   - **Seasonal Variations**: Winter vs. summer appearance differences

11. **Prevalence & Real-World Frequency**:
   - How common is this pattern? (very common, common, occasional, rare)
   - Which industries/applications see this most?
   - Geographic variations (humid climates vs. arid, industrial vs. clean environments)

12. **Material-Specific Structural Damage** (CRITICAL FOR ACCURACY):
   - **Metals ONLY**: Pitting, corrosion cavities, rust holes, galvanic corrosion
   - **Ceramics/Glass**: Crazing, chipping, cracking (NO pitting - ceramics don't pit)
   - **Polymers/Composites**: Delamination, fiber exposure, matrix cracking (NO pitting - polymers don't corrode)
   - **Wood**: Rot, checking, splitting, fiber separation (NO pitting - wood doesn't corrode)
   - **AVOID**: Describing metal-specific damage (pitting, corrosion cavities) for non-metallic materials
   - **Rule**: Match structural damage to material chemistry and failure modes

13. **Realism Red Flags to AVOID**:
   - Artificial patterns that don't occur naturally
   - Common AI-generation mistakes for this pattern
   - Physics violations (e.g., uniform coating where gravity should cause drips)
   - Scale inconsistencies (patterns too small/large for substrate)
   - Impossible color combinations or transitions
   - Missing environmental logic (dry rot in constantly wet conditions)
   - Over-symmetry or perfect geometric patterns in natural aging
   - **CRITICAL**: Material-inappropriate damage (e.g., pitting on polymers/composites, rust on ceramics)

Format as JSON:

{{{{
    "category": "{category}",
    "contamination_patterns": [
        {{{{
            "pattern_name": "...",
            "pattern_type": "contamination|aging|combined",
            "photo_reference_urls": [
                "https://example.com/image1.jpg (description)",
                "https://example.com/image2.jpg (description)"
            ],
            "photo_search_terms": "keywords used to find reference images",
            "photo_reference": "...",
            "visual_characteristics": {{{{
                "color_range": "...",
                "color_evolution": "fresh → intermediate → aged color progression",
                "texture_detail": "...",
                "texture_evolution": "fresh → aged texture transformation",
                "thickness_variation": "...",
                "edge_characteristics": "...",
                "surface_topology_changes": "erosion, pitting, cracking, delamination details"
            }}}},
            "distribution_physics": {{{{
                "gravity_effects": "...",
                "environmental_exposure_patterns": "UV-facing, shaded, wet, dry zone differences",
                "accumulation_zones": "...",
                "coverage_pattern": "...",
                "density_variation": "...",
                "substrate_interaction": "grain following, stress points, porosity effects"
            }}}},
            "aging_timeline": {{{{
                "formation_rate": "hours|days|weeks|months|years",
                "early_stage_0_25_percent": "barely visible changes...",
                "mid_stage_25_75_percent": "pronounced changes...",
                "advanced_stage_75_100_percent": "severe degradation...",
                "reversibility": "fully reversible|partially reversible|permanent damage"
            }}}},
            "layer_interaction": {{{{
                "base_material_interaction": "coats|penetrates|reacts|breaks down structure",
                "contaminant_interaction": "masks|accelerates|combines with other patterns",
                "synergistic_effects": "UV + moisture effects, chemical + biological interactions",
                "stratification": "which layers form first, accumulation sequence"
            }}}},
            "micro_scale_distribution": {{{{
                "grain_following": "how pattern follows material structure",
                "edge_effects": "concentration at boundaries, corners, joints",
                "stress_point_indicators": "cracks, deformation zones",
                "porosity_effects": "...",
                "anisotropic_patterns": "directional effects based on material grain/flow",
                "boundary_transitions": "sharp vs. gradual severity changes"
            }}}},
            "lighting_response": {{{{
                "reflection_characteristics": "absorbs|reflects|scatters|diffuses",
                "gloss_changes": "glossy → satin → matte progression",
                "shadow_characteristics": "...",
                "angle_dependent_appearance": "grazing light effects",
                "translucency_changes": "...",
                "illumination_color_shift": "daylight vs. indoor appearance"
            }}}},
            "environmental_context": {{{{
                "typical_environments": "indoor|outdoor|industrial|marine|urban|rural",
                "required_conditions": "temperature, humidity, UV, chemical exposure needs",
                "accelerating_factors": ["heat", "moisture", "pollutants", "mechanical stress"],
                "protective_factors": ["coatings", "shading", "low humidity"],
                "seasonal_variations": "winter vs. summer differences"
            }}}},
            "prevalence": "very common|common|occasional|rare",
            "industry_applications": "which industries/applications see this most",
            "geographic_variations": "climate-dependent appearance differences",
            "realism_avoid": [
                "artificial pattern X",
                "AI mistake Y",
                "physics violation Z",
                "impossible color transition",
                "missing environmental logic"
            ]
        }}}}
    ],
    "base_appearance": {{{{
        "typical_color_range": "...",
        "fresh_surface_characteristics": "...",
        "common_manufacturing_marks": "...",
        "inherent_variations": "natural color/texture variations in pristine material"
    }}}},
    "aging_priority_notes": "For organics, prioritize aging patterns. For metals, balance corrosion (aging) with deposits. For ceramics, prioritize environmental weathering.",
    "photo_reference_notes": "Documented real-world examples with specific sources",
    "distribution_reality_notes": "Key principles for realistic contamination/aging distribution across this material type"
}}

CRITICAL REQUIREMENTS:
1. **Aging = Contamination**: Treat aging effects as equally important contamination patterns
2. **Organic Materials Priority**: For wood, natural fibers, organics → aging is PRIMARY concern (UV damage, biodegradation, moisture damage)
3. **Metal Aging**: Include oxidation, corrosion, patina formation as aging patterns (not just external deposits)
4. **Polymer Aging**: UV degradation, chalking, crazing, discoloration, embrittlement
5. **Ceramic Aging**: Weathering, efflorescence, biological growth, erosion
6. **Distribution Reality**: Base ALL distribution patterns on actual physics (gravity, environmental exposure gradients, stress concentration)
7. **Photo-Realism**: Every description must reference observable characteristics from real photographs
8. **Micro-Scale Accuracy**: Include grain following, edge effects, porosity interactions
9. **Timeline Specificity**: Provide actual time scales (not vague "over time")
10. **Synergistic Effects**: Document how aging + contamination interact and accelerate each other

Base ALL descriptions on actual photographs, conservation documentation, material science research, and weathering studies. 
Describe what contamination and aging ACTUALLY look like in real-world industrial, outdoor, and conservation settings.

CRITICAL JSON FORMATTING:
- Escape ALL quotes inside string values: Use \\" not "
- Keep URLs simple: No quotes in URL descriptions if possible
- Multi-line strings: Use \\n for line breaks, NOT actual newlines
- Test your JSON structure before responding
- If a value contains quotes, escape them properly
- Example: "description": "Observe \\"aged\\" fiberglass boats" (correct)
- Example: "description": "Observe "aged" fiberglass boats" (WRONG - breaks JSON)"""
    

    
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
