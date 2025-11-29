"""
MaterialShapeResearcher: Researches real-world objects and forms made from materials.

Uses AI to find the most common, recognizable real-world object for each material,
including context information (standalone object vs structural/architectural).

Caches results to avoid repeated API calls.

Usage:
    researcher = MaterialShapeResearcher()
    result = researcher.get_common_shape("Dolomite")
    # Returns: {"object": "building facade panel", "context": "architectural", "setting": "exterior wall section"}
    
    # For standalone objects:
    result = researcher.get_common_shape("Bismuth")
    # Returns: {"object": "pharmaceutical tablet mold", "context": "standalone", "setting": "workshop bench"}
"""
import os
import json
import hashlib
from typing import Optional, Dict, Any
from pathlib import Path

import google.generativeai as genai


class MaterialShapeResearcher:
    """Research real-world objects made from materials using Gemini."""
    
    # Cache directory for research results
    CACHE_DIR = Path(__file__).parent.parent.parent.parent / "cache" / "shape_research"
    
    # Fallback lookup for when API is unavailable
    # Format: {"object": str, "context": "standalone"|"architectural"|"industrial", "setting": str}
    FALLBACK_SHAPES = {
        # Standalone objects (workshop bench setting)
        "Aluminum": {"object": "beverage can", "context": "standalone", "setting": "workshop bench"},
        "Copper": {"object": "electrical wire spool", "context": "standalone", "setting": "workshop bench"},
        "Bismuth": {"object": "pharmaceutical tablet mold", "context": "standalone", "setting": "workshop bench"},
        "Brass": {"object": "door handle", "context": "standalone", "setting": "workshop bench"},
        "Stainless Steel": {"object": "kitchen sink", "context": "standalone", "setting": "workshop bench"},
        "Titanium": {"object": "hip implant", "context": "standalone", "setting": "workshop bench"},
        "Polymer": {"object": "water bottle", "context": "standalone", "setting": "workshop bench"},
        "Wood": {"object": "cutting board", "context": "standalone", "setting": "workshop bench"},
        "Cast Iron": {"object": "skillet", "context": "standalone", "setting": "workshop bench"},
        "Bronze": {"object": "bell", "context": "standalone", "setting": "workshop bench"},
        "Nickel": {"object": "coin", "context": "standalone", "setting": "workshop bench"},
        "Zinc": {"object": "galvanized bolt", "context": "standalone", "setting": "workshop bench"},
        "Lead": {"object": "fishing sinker", "context": "standalone", "setting": "workshop bench"},
        "Tin": {"object": "food can", "context": "standalone", "setting": "workshop bench"},
        "Magnesium": {"object": "laptop case", "context": "standalone", "setting": "workshop bench"},
        "Chrome": {"object": "faucet", "context": "standalone", "setting": "workshop bench"},
        "Carbon Fiber": {"object": "bicycle frame", "context": "standalone", "setting": "workshop bench"},
        "Rubber": {"object": "tire", "context": "standalone", "setting": "workshop bench"},
        "Leather": {"object": "belt", "context": "standalone", "setting": "workshop bench"},
        "Fabric": {"object": "upholstery panel", "context": "standalone", "setting": "workshop bench"},
        
        # Architectural/structural materials (in-situ settings)
        "Steel": {"object": "I-beam", "context": "architectural", "setting": "construction site with beam installed in building frame"},
        "Concrete": {"object": "wall section", "context": "architectural", "setting": "building exterior showing concrete wall panel"},
        "Brick": {"object": "wall section", "context": "architectural", "setting": "building exterior showing brick wall"},
        "Stone": {"object": "facade panel", "context": "architectural", "setting": "building exterior wall"},
        "Marble": {"object": "floor tile section", "context": "architectural", "setting": "interior floor or wall installation"},
        "Granite": {"object": "countertop section", "context": "architectural", "setting": "kitchen or bathroom installation"},
        "Limestone": {"object": "building block", "context": "architectural", "setting": "historic building facade"},
        "Sandstone": {"object": "wall cladding", "context": "architectural", "setting": "building exterior"},
        "Dolomite": {"object": "polished countertop section", "context": "architectural", "setting": "kitchen installation"},
        "Slate": {"object": "roof tiles", "context": "architectural", "setting": "rooftop installation"},
        "Terracotta": {"object": "roof tiles", "context": "architectural", "setting": "Mediterranean-style rooftop"},
        "Glass": {"object": "window pane", "context": "architectural", "setting": "building window frame"},
        "Ceramic": {"object": "floor tile section", "context": "architectural", "setting": "interior floor installation"},
        
        # Industrial in-situ
        "Rebar": {"object": "reinforcement grid", "context": "industrial", "setting": "concrete formwork on construction site"},
    }
    
    def __init__(self):
        """Initialize with Gemini API."""
        self.model = None
        self._init_gemini()
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    def _init_gemini(self):
        """Initialize Gemini model."""
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
    
    def _get_cache_path(self, material_name: str) -> Path:
        """Get cache file path for a material."""
        safe_name = hashlib.md5(material_name.lower().encode()).hexdigest()[:12]
        return self.CACHE_DIR / f"{safe_name}.json"
    
    def _load_from_cache(self, material_name: str) -> Optional[Dict[str, str]]:
        """Load cached research result."""
        cache_path = self._get_cache_path(material_name)
        if cache_path.exists():
            try:
                data = json.loads(cache_path.read_text())
                # Handle both old format (just "shape") and new format (full dict)
                if "object" in data:
                    return data
                elif "shape" in data:
                    # Migrate old format
                    return {
                        "object": data["shape"],
                        "context": "standalone",
                        "setting": "workshop bench"
                    }
            except (json.JSONDecodeError, KeyError):
                pass
        return None
    
    def _save_to_cache(self, material_name: str, result: Dict[str, str]):
        """Save research result to cache."""
        cache_path = self._get_cache_path(material_name)
        cache_path.write_text(json.dumps({
            "material": material_name,
            **result
        }))
    
    def _research_shape(self, material_name: str) -> Dict[str, str]:
        """Use Gemini to research the most common real-world object and context for this material."""
        if not self.model:
            return self._get_fallback(material_name)
        
        prompt = f"""For the material "{material_name}", identify:
1. The most common FINISHED/MANUFACTURED product made from it
2. Whether it's typically a standalone object OR part of a building/structure
3. The appropriate setting to photograph it

CRITICAL REQUIREMENTS:
- Must be a FABRICATED/MANUFACTURED object (NOT raw material, NOT aggregate, NOT crushed/broken form)
- Must be visually RECOGNIZABLE by a general audience
- For construction aggregates/minerals: show the FINAL PRODUCT (concrete block, tile, building panel, paving stone)
- For building materials: show INSTALLED architectural features
- AVOID these raw material terms: "aggregate", "crushed", "raw", "sample", "chunk", "piece", "ore", "gravel", "powder"

Respond in EXACTLY this JSON format, nothing else:
{{"object": "specific manufactured object name", "context": "standalone|architectural|industrial", "setting": "brief setting description"}}

Examples:
- Dolomite: {{"object": "terrazzo floor tile", "context": "architectural", "setting": "interior floor installation"}}
- Steel: {{"object": "I-beam", "context": "architectural", "setting": "construction site with beam in building frame"}}
- Copper: {{"object": "electrical wire spool", "context": "standalone", "setting": "workshop bench"}}
- Concrete: {{"object": "precast wall panel", "context": "architectural", "setting": "building exterior wall"}}
- Limestone: {{"object": "carved building ornament", "context": "architectural", "setting": "historic building facade"}}
- Marble: {{"object": "polished floor tile", "context": "architectural", "setting": "interior floor installation"}}

Material: {material_name}
Response:"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 150,
                }
            )
            text = response.text.strip()
            
            # Try to parse JSON response
            try:
                # Clean up response - find JSON
                if '{' in text and '}' in text:
                    json_start = text.index('{')
                    json_end = text.rindex('}') + 1
                    json_str = text[json_start:json_end]
                    result = json.loads(json_str)
                    
                    # Validate required fields
                    if "object" in result and "context" in result:
                        obj_name = result.get("object", "").lower()
                        
                        # REJECT raw material forms - use fallback instead
                        raw_material_terms = ["aggregate", "crushed", "raw", "sample", "chunk", 
                                              "piece", "ore", "gravel", "powder", "rock", "stone ",
                                              "pellet", "granule", "bead", "particle", "sand"]
                        if any(term in obj_name for term in raw_material_terms):
                            print(f"⚠️  Rejecting unsuitable form '{obj_name}', using fallback")
                            return self._get_fallback(material_name)
                        
                        return {
                            "object": obj_name,
                            "context": result.get("context", "standalone").lower(),
                            "setting": result.get("setting", "workshop bench")
                        }
            except (json.JSONDecodeError, ValueError):
                pass
            
            # Fallback: just use first line as object name
            return {
                "object": text.split('\n')[0].lower()[:50],
                "context": "standalone",
                "setting": "workshop bench"
            }
            
        except Exception as e:
            print(f"⚠️  Shape research API error for {material_name}: {e}")
            return self._get_fallback(material_name)
    
    def _get_fallback(self, material_name: str) -> Dict[str, str]:
        """Get fallback shape from lookup table."""
        key = material_name.strip().title()
        fallback = self.FALLBACK_SHAPES.get(key)
        if fallback:
            return fallback
        return {
            "object": f"{material_name} sample",
            "context": "standalone",
            "setting": "workshop bench"
        }
    
    def get_common_shape(self, material_name: str) -> Dict[str, str]:
        """
        Returns the most common real-world object and context for this material.
        
        Uses cached results if available, otherwise researches via Gemini.
        
        Args:
            material_name: Name of the material (e.g., "Bismuth", "Steel", "Dolomite")
            
        Returns:
            Dict with:
                - object: Specific object name (e.g., "I-beam", "facade panel")
                - context: "standalone" | "architectural" | "industrial"
                - setting: Setting description (e.g., "workshop bench", "building exterior")
        """
        # Check cache first
        cached = self._load_from_cache(material_name)
        if cached:
            print(f"📬 Shape cache hit: {material_name} → {cached['object']} ({cached['context']})")
            return cached
        
        # Research via API
        print(f"🔬 Researching common shape for {material_name}...")
        result = self._research_shape(material_name)
        
        # Cache the result
        self._save_to_cache(material_name, result)
        print(f"✅ Shape researched: {material_name} → {result['object']} ({result['context']}: {result['setting']})")
        
        return result
    
    def get_object_name(self, material_name: str) -> str:
        """Convenience method to get just the object name (backward compatible)."""
        result = self.get_common_shape(material_name)
        return result["object"]
    
    def clear_cache(self, material_name: Optional[str] = None):
        """Clear cache for a specific material or all materials."""
        if material_name:
            cache_path = self._get_cache_path(material_name)
            if cache_path.exists():
                cache_path.unlink()
        else:
            for cache_file in self.CACHE_DIR.glob("*.json"):
                cache_file.unlink()
