"""
AssemblyResearcher: Researches related components for complex assembled objects.

When a complex part is specified (like "rocket pump" or "turbine blade"), this
researcher identifies other components typically found assembled with it, including
components made from different materials.

This enables more realistic hero images showing parts in their real-world context
with adjacent/connected components visible.

Usage:
    researcher = AssemblyResearcher()
    result = researcher.get_assembly_context("stainless steel", "high pressure rocket pump")
    # Returns: {
    #     "primary_part": "high pressure rocket pump impeller",
    #     "primary_material": "stainless steel", 
    #     "assembly_components": [
    #         {"part": "shaft seal", "material": "PTFE", "relationship": "seals rotating shaft"},
    #         {"part": "bearing housing", "material": "aluminum", "relationship": "supports shaft"},
    #         {"part": "inlet fitting", "material": "brass", "relationship": "connects to fuel line"}
    #     ],
    #     "assembly_description": "rocket turbopump assembly with visible seals and fittings"
    # }
"""
import os
import json
import hashlib
from typing import Optional, Dict, Any, List
from pathlib import Path

import google.generativeai as genai


class AssemblyResearcher:
    """Research related assembly components for complex parts using Gemini."""
    
    # Cache directory for assembly research results
    CACHE_DIR = Path(__file__).parent.parent.parent.parent / "cache" / "assembly_research"
    
    # Keywords that indicate a complex/assembled part vs simple object
    COMPLEX_PART_INDICATORS = [
        "pump", "engine", "motor", "turbine", "compressor", "actuator",
        "valve", "assembly", "mechanism", "system", "unit", "module",
        "gearbox", "transmission", "drivetrain", "housing", "manifold",
        "exchanger", "reactor", "generator", "alternator", "rotor",
        "impeller", "propeller", "thruster", "injector", "nozzle",
        "bracket", "mount", "fixture", "frame", "chassis", "body"
    ]
    
    def __init__(self):
        """Initialize with Gemini API."""
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model = None
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash')
            except Exception as e:
                print(f"⚠️  Gemini API initialization failed: {e}")
        
        # Ensure cache directory exists
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    def is_complex_part(self, shape_name: str) -> bool:
        """Determine if the given shape/object is complex enough to warrant assembly research."""
        if not shape_name:
            return False
        
        shape_lower = shape_name.lower()
        
        # Check for complex part indicators
        for indicator in self.COMPLEX_PART_INDICATORS:
            if indicator in shape_lower:
                return True
        
        # Multi-word shapes are often more complex
        word_count = len(shape_lower.split())
        if word_count >= 3:
            return True
        
        return False
    
    def get_assembly_context(self, material_name: str, shape_name: str) -> Optional[Dict[str, Any]]:
        """
        Research what other components are typically assembled with this part.
        
        Args:
            material_name: The primary material (e.g., "Stainless Steel")
            shape_name: The object/shape being generated (e.g., "high pressure rocket pump")
            
        Returns:
            Dict with assembly context, or None if not a complex part
        """
        if not self.is_complex_part(shape_name):
            return None
        
        # Check cache first
        cache_key = f"{material_name}_{shape_name}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        # Research assembly components
        result = self._research_assembly(material_name, shape_name)
        
        # Cache the result
        if result:
            self._cache_result(cache_key, result)
        
        return result
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path for a given key."""
        safe_key = hashlib.md5(cache_key.lower().encode()).hexdigest()[:16]
        return self.CACHE_DIR / f"{safe_key}.json"
    
    def _get_cached(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Check cache for existing research result."""
        cache_path = self._get_cache_path(cache_key)
        if cache_path.exists():
            try:
                data = json.loads(cache_path.read_text())
                print(f"   📋 Assembly research loaded from cache")
                return data
            except (json.JSONDecodeError, KeyError):
                pass
        return None
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]) -> None:
        """Save research result to cache."""
        cache_path = self._get_cache_path(cache_key)
        cache_path.write_text(json.dumps({
            "cache_key": cache_key,
            **result
        }, indent=2))
    
    def _research_assembly(self, material_name: str, shape_name: str) -> Dict[str, Any]:
        """Use Gemini to research assembly components for a complex part."""
        if not self.model:
            return self._get_fallback(material_name, shape_name)
        
        prompt = f"""For a {shape_name} made from {material_name}, identify 2-4 OTHER components that would typically be assembled with it or adjacent to it in real-world use.

CRITICAL REQUIREMENTS:
1. Each component must be from a DIFFERENT material than {material_name}
2. Components should be VISIBLE when looking at the assembled part
3. Include the relationship/connection between the component and the main part
4. Focus on components that would appear in a realistic close-up photo

Respond in EXACTLY this JSON format:
{{
    "primary_part": "specific name of main {material_name} part",
    "primary_material": "{material_name}",
    "assembly_components": [
        {{"part": "component name", "material": "material name", "relationship": "how it connects/relates"}},
        {{"part": "component name", "material": "material name", "relationship": "how it connects/relates"}},
        {{"part": "component name", "material": "material name", "relationship": "how it connects/relates"}}
    ],
    "assembly_description": "one sentence describing the assembly for image generation"
}}

Examples:
- Stainless steel rocket pump:
{{
    "primary_part": "turbopump impeller housing",
    "primary_material": "stainless steel",
    "assembly_components": [
        {{"part": "shaft seal ring", "material": "PTFE", "relationship": "seals rotating shaft"}},
        {{"part": "bearing cage", "material": "bronze", "relationship": "supports main shaft bearings"}},
        {{"part": "inlet manifold", "material": "aluminum", "relationship": "connects to propellant feed line"}}
    ],
    "assembly_description": "turbopump assembly showing PTFE seals and bronze bearings around stainless impeller"
}}

- Aluminum aircraft wing spar:
{{
    "primary_part": "wing spar main beam",
    "primary_material": "aluminum",
    "assembly_components": [
        {{"part": "rivets", "material": "titanium", "relationship": "fastens skin panels"}},
        {{"part": "fuel line bracket", "material": "stainless steel", "relationship": "mounts to spar web"}},
        {{"part": "wire harness clamp", "material": "nylon", "relationship": "secures electrical wiring"}}
    ],
    "assembly_description": "aircraft wing spar with titanium rivets and stainless brackets visible"
}}

Main part: {shape_name}
Material: {material_name}
Response:"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.4,  # Slightly creative for variety
                    "max_output_tokens": 400,
                }
            )
            text = response.text.strip()
            
            # Parse JSON response
            try:
                if '{' in text and '}' in text:
                    json_start = text.index('{')
                    json_end = text.rindex('}') + 1
                    json_str = text[json_start:json_end]
                    result = json.loads(json_str)
                    
                    # Validate structure
                    if "assembly_components" in result and len(result.get("assembly_components", [])) > 0:
                        # Ensure primary_material is set
                        result["primary_material"] = material_name
                        return result
                        
            except (json.JSONDecodeError, ValueError) as e:
                print(f"⚠️  JSON parse error in assembly research: {e}")
            
            # Fallback if parsing failed
            return self._get_fallback(material_name, shape_name)
            
        except Exception as e:
            print(f"⚠️  Assembly research API error: {e}")
            return self._get_fallback(material_name, shape_name)
    
    def _get_fallback(self, material_name: str, shape_name: str) -> Dict[str, Any]:
        """
        Provide generic assembly context when API is unavailable.
        Uses common material pairings for industrial equipment.
        """
        # Common adjacent materials by primary material type
        material_pairings = {
            "stainless steel": [
                {"part": "seal ring", "material": "PTFE", "relationship": "provides sealing"},
                {"part": "mounting bracket", "material": "aluminum", "relationship": "supports assembly"},
                {"part": "fasteners", "material": "brass", "relationship": "connects components"}
            ],
            "aluminum": [
                {"part": "bushing", "material": "bronze", "relationship": "bearing surface"},
                {"part": "gasket", "material": "rubber", "relationship": "seals joint"},
                {"part": "hardware", "material": "stainless steel", "relationship": "fastening"}
            ],
            "titanium": [
                {"part": "seal", "material": "PTFE", "relationship": "seals interface"},
                {"part": "bearing", "material": "ceramic", "relationship": "supports rotation"},
                {"part": "connector", "material": "inconel", "relationship": "high-temp interface"}
            ],
            "carbon steel": [
                {"part": "bushing", "material": "bronze", "relationship": "wear surface"},
                {"part": "O-ring", "material": "nitrile rubber", "relationship": "seals shaft"},
                {"part": "shim", "material": "brass", "relationship": "alignment adjustment"}
            ],
            "brass": [
                {"part": "valve seat", "material": "PTFE", "relationship": "sealing surface"},
                {"part": "spring", "material": "stainless steel", "relationship": "provides tension"},
                {"part": "handle", "material": "aluminum", "relationship": "operator interface"}
            ],
            "copper": [
                {"part": "insulation", "material": "PVC", "relationship": "electrical isolation"},
                {"part": "terminal", "material": "brass", "relationship": "connection point"},
                {"part": "clamp", "material": "stainless steel", "relationship": "secures position"}
            ]
        }
        
        # Get pairings for material (case-insensitive lookup)
        material_lower = material_name.lower()
        components = None
        for key, value in material_pairings.items():
            if key in material_lower or material_lower in key:
                components = value
                break
        
        # Default generic pairings
        if not components:
            components = [
                {"part": "seal", "material": "rubber", "relationship": "provides sealing"},
                {"part": "fastener", "material": "steel", "relationship": "secures assembly"},
                {"part": "bracket", "material": "aluminum", "relationship": "mounting support"}
            ]
        
        return {
            "primary_part": shape_name,
            "primary_material": material_name,
            "assembly_components": components,
            "assembly_description": f"{shape_name} assembly with adjacent seals, brackets, and fasteners visible"
        }
    
    def format_for_prompt(self, assembly_context: Dict[str, Any]) -> str:
        """
        Format assembly context into a string for prompt injection.
        
        Returns a description suitable for adding to image generation prompts.
        """
        if not assembly_context:
            return ""
        
        components = assembly_context.get("assembly_components", [])
        if not components:
            return ""
        
        # Build component description
        component_parts = []
        for comp in components[:3]:  # Limit to 3 components
            part = comp.get("part", "")
            material = comp.get("material", "")
            if part and material:
                component_parts.append(f"{material} {part}")
        
        if not component_parts:
            return ""
        
        assembly_desc = assembly_context.get("assembly_description", "")
        if assembly_desc:
            return f"ASSEMBLY CONTEXT: Show {assembly_desc}. Visible adjacent components: {', '.join(component_parts)}."
        else:
            return f"ASSEMBLY CONTEXT: Include visible adjacent components: {', '.join(component_parts)}."
