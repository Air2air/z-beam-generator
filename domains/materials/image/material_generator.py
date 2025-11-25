#!/usr/bin/env python3
"""
Material Before/After Image Generator

Generator for material laser cleaning before/after images with scientifically
accurate contamination research.

Author: AI Assistant
Date: November 24, 2025
"""

import logging
from typing import Dict, Any, Optional

from domains.materials.image.prompts.material_researcher import MaterialContaminationResearcher
from domains.materials.image.prompts.category_contamination_researcher import CategoryContaminationResearcher
from domains.materials.image.prompts.material_prompts import build_material_cleaning_prompt
from domains.materials.image.material_config import MaterialImageConfig

logger = logging.getLogger(__name__)


class MaterialImageGenerator:
    """
    Generator for material before/after laser cleaning images.
    
    Uses category-level contamination research for photo-realistic patterns
    with abundant real-world references.
    """
    
    def __init__(self, gemini_api_key: Optional[str] = None, use_category_research: bool = True):
        """
        Initialize material image generator.
        
        Args:
            gemini_api_key: Optional Gemini API key for contamination research
            use_category_research: Use category-level research (more realistic, reusable)
        """
        self.material_researcher = None
        self.category_researcher = None
        self.use_category_research = use_category_research
        
        if gemini_api_key:
            try:
                if use_category_research:
                    self.category_researcher = CategoryContaminationResearcher(api_key=gemini_api_key)
                    logger.info("✅ Category-level contamination research enabled")
                else:
                    self.material_researcher = MaterialContaminationResearcher(api_key=gemini_api_key)
                    logger.info("✅ Material-specific contamination research enabled")
            except Exception as e:
                logger.warning(f"⚠️  Contamination research disabled: {e}")
    
    def generate_prompt(
        self,
        material_name: str,
        material_properties: Optional[Dict] = None,
        config: Optional[MaterialImageConfig] = None,
        research_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate before/after image prompt for a material.
        
        Args:
            material_name: Name of the material (e.g., "Aluminum", "Stainless Steel")
            material_properties: Optional material properties from Materials.yaml
            config: Optional MaterialImageConfig for contamination control
            research_data: Optional pre-fetched research data (avoids duplicate calls)
            
        Returns:
            Image prompt string optimized for Imagen 4
        """
        # Use default config if not provided
        if config is None:
            config = MaterialImageConfig(material=material_name)
        
        # Get contamination research data if not provided
        if research_data is None:
            if self.use_category_research and self.category_researcher:
                try:
                    # Get category for this material
                    category = self.category_researcher.get_category(material_name)
                    logger.info(f"📂 Material category: {category}")
                    
                    # Research category patterns
                    category_data = self.category_researcher.research_category_contamination(category)
                    
                    # Apply patterns to this material
                    research_data = self.category_researcher.apply_patterns_to_material(
                        material_name, category_data, config.contamination_uniformity
                    )
                    logger.info(f"🔬 Applied {len(research_data.get('selected_patterns', []))} category patterns to {material_name}")
                except Exception as e:
                    logger.warning(f"⚠️  Category research failed for {material_name}: {e}")
                    research_data = self._get_fallback_research(material_name)
            elif self.material_researcher:
                try:
                    research_data = self.material_researcher.research_material_contamination(
                        material_name, material_properties
                    )
                    logger.info(f"🔬 Researched contamination for {material_name}")
                except Exception as e:
                    logger.warning(f"⚠️  Research failed for {material_name}: {e}")
                    research_data = self._get_fallback_research(material_name)
            else:
                # No researcher available - use fallback
                research_data = self._get_fallback_research(material_name)
        elif research_data is None:
            # No researcher and no data provided - use fallback
            research_data = self._get_fallback_research(material_name)
        
        # Build complete prompt with research data
        prompt = build_material_cleaning_prompt(
            material_name=material_name,
            research_data=research_data,
            contamination_level=config.contamination_level,
            contamination_uniformity=config.contamination_uniformity,
            view_mode=config.view_mode,
            environment_wear=config.environment_wear
        )
        
        return prompt
    
    def get_negative_prompt(
        self,
        material_name: str,
        config: Optional[MaterialImageConfig] = None
    ) -> str:
        """
        Get comprehensive negative prompt for before/after image accuracy.
        
        Includes:
        - Contamination accuracy (no unnatural contamination)
        - Material appearance accuracy
        - Split composition control
        - Lighting consistency
        - Viewpoint consistency
        - Text/label exclusions
        
        Args:
            material_name: Name of the material
            config: Optional MaterialImageConfig
        
        Returns:
            Comprehensive negative prompt string
        """
        # Base negative prompt for all material images
        base_negative = [
            # Contamination realism (CRITICAL)
            "unnatural contamination", "fake-looking dirt", "painted-on grime",
            "uniform contamination", "perfectly even dirt", "artificially applied contamination",
            "contamination that defies physics", "contamination in impossible locations",
            "white powder overlay", "uniform powder coating", "flat contamination layer",
            "contamination defying gravity", "floating contamination particles",
            "no texture variation in contamination", "perfectly smooth contamination",
            "contamination with no shadows", "contamination with uniform reflectance",
            "digital overlay appearance", "copy-pasted contamination pattern",
            "contamination without layer interaction", "flat stacked contaminants",
            
            # Material appearance
            f"incorrect {material_name} appearance", "wrong material color",
            "impossible material texture", "fake material surface",
            
            # Split composition issues
            "no clear split", "blurred division", "merged halves",
            "asymmetric split", "unequal sides", "different objects on each side",
            "completely different items", "unrelated objects",
            
            # Lighting consistency
            "different lighting on each side", "mismatched shadows",
            "inconsistent light direction", "different time of day",
            
            # Viewpoint consistency
            "completely different angle", "different perspective",
            "rotated object", "flipped orientation", "different size",
            
            # Quality issues
            "blurry", "low resolution", "pixelated", "artifacts",
            "watermarks", "text", "labels", "captions", "logos",
            
            # Unrealistic elements
            "cartoon", "illustration", "drawing", "CGI", "3D render",
            "unrealistic", "impossible physics", "floating objects"
        ]
        
        # Add view mode specific exclusions
        if config and config.view_mode == "Contextual":
            base_negative.extend([
                "flat perspective", "orthographic view", "top-down only",
                "no depth", "2D appearance", "studio background",
                "isolated object", "floating in space"
            ])
        elif config and config.view_mode == "Isolated":
            base_negative.extend([
                "busy background", "cluttered environment",
                "visible surroundings", "context objects",
                "natural environment", "realistic setting"
            ])
        
        return ", ".join(base_negative)
    
    def get_generation_params(
        self,
        config: Optional[MaterialImageConfig] = None
    ) -> Dict[str, Any]:
        """
        Get generation parameters for Imagen 4.
        
        Args:
            config: Optional MaterialImageConfig
        
        Returns:
            Dictionary with aspect_ratio, guidance_scale, safety_filter_level
        """
        # Higher guidance scale for technical accuracy
        guidance_scale = 15.0  # Elevated for accurate contamination representation
        
        # Contextual view may need slightly lower guidance for natural composition
        if config and config.view_mode == "Contextual":
            guidance_scale = 13.0
        
        return {
            "aspect_ratio": "16:9",  # Side-by-side format
            "guidance_scale": guidance_scale,
            "safety_filter_level": "block_few"
        }
    
    def generate_complete(
        self,
        material_name: str,
        material_properties: Optional[Dict] = None,
        config: Optional[MaterialImageConfig] = None
    ) -> Dict[str, Any]:
        """
        Generate complete prompt package for image generation.
        
        Args:
            material_name: Name of the material
            material_properties: Optional material properties from Materials.yaml
            config: Optional MaterialImageConfig for contamination control
            
        Returns:
            Dictionary with prompt, negative_prompt, and generation_params:
            {
                "prompt": str,
                "negative_prompt": str,
                "research_data": Dict,
                "aspect_ratio": str,
                "guidance_scale": float,
                "safety_filter_level": str
            }
        """
        # Use default config if not provided
        if config is None:
            config = MaterialImageConfig(material=material_name)
        
        # Get contamination research data (single call)
        research_data = None
        if self.researcher:
            try:
                research_data = self.researcher.research_material_contamination(
                    material_name, material_properties
                )
                common_obj = research_data.get('common_object', material_name)
                contam_count = len(research_data.get('contaminants', []))
                logger.info(f"🔬 {material_name}: {common_obj} with {contam_count} contaminants researched")
            except Exception as e:
                logger.warning(f"⚠️  Research failed for {material_name}: {e}")
                research_data = self._get_fallback_research(material_name)
        else:
            research_data = self._get_fallback_research(material_name)
        
        # Generate prompt with research data (pass data to avoid duplicate research)
        prompt = self.generate_prompt(
            material_name, material_properties, config, research_data
        )
        
        # Generate negative prompt
        negative_prompt = self.get_negative_prompt(material_name, config)
        
        # Get generation params
        params = self.get_generation_params(config)
        
        # Log configuration
        logger.info(
            f"📊 Config: {config.contamination_intensity_label} contamination, "
            f"{config.uniformity_label}, {config.view_mode} view"
        )
        
        return {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "research_data": research_data,
            "config": config.to_dict(),
            **params
        }
    
    def _get_fallback_research(self, material_name: str) -> Dict[str, Any]:
        """Get minimal fallback research data when API unavailable."""
        logger.warning(f"Using fallback research for {material_name}")
        return {
            "common_object": f"{material_name} object",
            "object_description": f"Common {material_name} item",
            "typical_size": "standard size",
            "typical_environment": "typical working environment",
            "environment_description": "Normal usage environment",
            "contaminants": [
                {
                    "name": "Surface dirt",
                    "chemical_formula": "",
                    "cause": "Environmental exposure",
                    "appearance": {
                        "color": "Dark gray to black",
                        "texture": "Matte, dusty",
                        "pattern": "Uneven, accumulated in crevices",
                        "thickness": "Thin to moderate layer"
                    },
                    "prevalence": "Very common"
                }
            ],
            "base_material_appearance": {
                "clean_color": f"Natural {material_name} color",
                "clean_texture": f"Natural {material_name} texture",
                "clean_sheen": "Natural sheen",
                "natural_features": "Typical surface features"
            }
        }
