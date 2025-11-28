#!/usr/bin/env python3
"""
Material Before/After Image Generator

Generator for material laser cleaning before/after images with scientifically
accurate contamination research.

Author: AI Assistant
Date: November 24, 2025
"""

import json
import logging
from typing import Dict, Any, Optional

from domains.materials.image.research.material_researcher import MaterialContaminationResearcher
from domains.materials.image.research.category_contamination_researcher import CategoryContaminationResearcher
from shared.image.utils.prompt_builder import SharedPromptBuilder
from shared.image.orchestrator import ImagePromptOrchestrator  # ✅ NEW: Orchestrated validation
from domains.materials.image.material_config import MaterialImageConfig
from shared.image.utils.image_pipeline_monitor import (
    get_pipeline_monitor, FailureStage, FailureType
)
# ✅ FIXED (Nov 26, 2025): Use shared types to avoid cross-domain imports
from shared.types.contamination import ContaminationContext
from shared.validation.contamination_validator import ContaminationValidator

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
        
        # Initialize prompt builder with correct path
        from pathlib import Path
        prompts_dir = Path(__file__).parent / "prompts" / "shared"
        self.prompt_builder = SharedPromptBuilder(prompts_dir=prompts_dir)
        
        # ✅ NEW: Initialize orchestrator for validated prompt generation
        self.orchestrator = ImagePromptOrchestrator(domain='materials')
        
        self.pipeline_monitor = get_pipeline_monitor()
        self.contamination_validator = ContaminationValidator()
        
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
        # Require explicit config
        if config is None:
            raise ValueError(f"MaterialImageConfig is required for {material_name}. Cannot use default configuration.")
        
        # Get contamination research data if not provided
        if research_data is None:
            if self.use_category_research and self.category_researcher:
                try:
                    # Get category for this material
                    print(f"\n📂 Determining material category for: {material_name}")
                    category = self.category_researcher.get_category(material_name)
                    print(f"   ✅ Category: {category}")
                    logger.info(f"📂 Material category: {category}")
                    
                    # Research category patterns (with built-in terminal logging)
                    category_data = self.category_researcher.research_category_contamination(category)
                    
                    # Apply patterns to this material
                    print(f"\n🎨 Applying patterns to {material_name}")
                    print(f"   • Selecting {config.contamination_uniformity} pattern(s) from research")
                    research_data = self.category_researcher.apply_patterns_to_material(
                        material_name, category_data, config.contamination_uniformity
                    )
                    print(f"   ✅ Applied {len(research_data.get('selected_patterns', []))} contamination patterns")
                    logger.info(f"🔬 Applied {len(research_data.get('selected_patterns', []))} category patterns")
                    
                    # 🔥 NEW: Validate contamination patterns against material properties
                    print(f"\n🔬 Validating contamination patterns for {material_name}...")
                    validation_result = self.contamination_validator.validate_generation_config(
                        material_name=material_name,
                        research_data=research_data,
                        context=ContaminationContext(usage="laser_cleaning", environment="industrial")
                    )
                    
                    if not validation_result.is_valid:
                        # Log validation errors
                        print(f"\n⚠️  Contamination validation found issues:")
                        for error in validation_result.get_errors():
                            print(f"   ❌ {error.message}")
                            print(f"      {error.explanation}")
                            if error.suggestion:
                                print(f"      💡 {error.suggestion}")
                            logger.error(f"Contamination validation error: {error.message}")
                        
                        # Filter out incompatible patterns
                        original_count = len(research_data.get('selected_patterns', []))
                        valid_patterns = []
                        for pattern in research_data.get('selected_patterns', []):
                            pattern_name = pattern.get('pattern_name', '')
                            single_result = self.contamination_validator.validate_patterns_for_material(
                                material_name=material_name,
                                pattern_names=[pattern_name]
                            )
                            if single_result.is_valid:
                                valid_patterns.append(pattern)
                            else:
                                print(f"   🚫 Filtered out: {pattern_name}")
                        
                        research_data['selected_patterns'] = valid_patterns
                        filtered_count = original_count - len(valid_patterns)
                        print(f"\n✅ Filtered {filtered_count} incompatible patterns ({len(valid_patterns)} remain)")
                        logger.info(f"🔬 Filtered {filtered_count} incompatible contamination patterns")
                        
                        # If no valid patterns remain, fail
                        if not valid_patterns:
                            error_msg = f"No valid contamination patterns for {material_name}. All researched patterns were incompatible."
                            logger.error(f"❌ {error_msg}")
                            raise RuntimeError(error_msg)
                    else:
                        print(f"   ✅ All contamination patterns validated successfully")
                        logger.info(f"✅ Contamination validation passed for {material_name}")
                    
                except json.JSONDecodeError as e:
                    # JSON parsing failure - already handled by category researcher monitor
                    logger.error(f"❌ JSON parsing failed for {material_name}: {e}")
                    raise RuntimeError(f"Failed to parse contamination research for {material_name}.") from e
                except Exception as e:
                    # General research failure
                    from shared.image.utils.image_pipeline_monitor import FailureStage, FailureType
                    self.pipeline_monitor.record_failure(
                        material=material_name,
                        stage=FailureStage.RESEARCH,
                        failure_type=FailureType.GENERATION_ERROR,
                        severity="high",
                        details={'error': str(e), 'category': category if 'category' in locals() else 'unknown'}
                    )
                    logger.error(f"❌ Category research failed for {material_name}: {e}")
                    raise RuntimeError(f"Failed to research contamination patterns for {material_name}. Category research is required.") from e
            elif self.material_researcher:
                try:
                    research_data = self.material_researcher.research_material_contamination(
                        material_name, material_properties
                    )
                    logger.info(f"🔬 Researched contamination for {material_name}")
                except Exception as e:
                    logger.error(f"❌ Research failed for {material_name}: {e}")
                    raise RuntimeError(f"Failed to research contamination for {material_name}. Research is required.") from e
            else:
                raise RuntimeError(f"No contamination researcher configured. Cannot generate prompt for {material_name}.")
        elif research_data is None:
            raise RuntimeError(f"No research data provided for {material_name}. Research is required for image generation.")
        
        # Get learned feedback for this category
        learned_feedback = None
        try:
            from domains.materials.image.learning import create_logger
            learning_logger = create_logger()
            learned_feedback = learning_logger.get_category_feedback(
                material_category=config.category,
                limit=5  # Top 5 most common issues
            )
            if learned_feedback:
                logger.info(f"🧠 Loaded {len(learned_feedback.split(chr(10)))-1} learned feedback items for {config.category}")
        except Exception as e:
            logger.debug(f"Could not load learned feedback: {e}")
        
        # Build complete prompt with research data using SharedPromptBuilder
        prompt = self.prompt_builder.build_generation_prompt(
            material_name=material_name,
            research_data=research_data,
            contamination_uniformity=config.contamination_uniformity,
            view_mode=config.view_mode,
            material_category=config.category,
            learned_feedback=learned_feedback
        )
        
        return prompt
    
    def generate_validated_prompt_package(
        self,
        material_name: str,
        config: Optional[MaterialImageConfig] = None
    ) -> Dict[str, Any]:
        """
        Generate orchestrated prompt with validation for image generation.
        
        Uses ImagePromptOrchestrator to build prompt through multi-stage chain
        (Research → Visual → Composition → Refinement → Assembly → Validation).
        
        Returns validated prompt package with validation results for:
        - Pre-generation quality control
        - Post-generation reference for image validator
        - Learning data storage
        
        Args:
            material_name: Name of the material
            config: Optional MaterialImageConfig
        
        Returns:
            Dict containing:
                - prompt: str - Validated final prompt
                - validation_result: PromptValidationResult - Pre-generation validation
                - stage_outputs: Dict - All stage outputs from orchestrator
                - metadata: Dict - Additional context
        
        Raises:
            ValidationError: If prompt has critical validation issues
        """
        config = config or MaterialImageConfig(material_name=material_name)
        
        # Use orchestrator with generic parameters (domain-agnostic)
        # Orchestrator expects: identifier + **kwargs
        chained_result = self.orchestrator.generate_hero_prompt(
            identifier=material_name,
            category=config.category,
            api='imagen'
        )
        
        # Extract validation result from stage outputs
        validation_result = chained_result.stage_outputs.get('validation')
        
        return {
            'prompt': chained_result.prompt,
            'validation_result': validation_result,
            'stage_outputs': chained_result.stage_outputs,
            'metadata': chained_result.metadata
        }
    
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
            # Split-screen composition (CRITICAL)
            "single object only", "no comparison", "one state only",
            "just contaminated", "just clean", "no split",
            "no before and after", "missing half", "incomplete composite",
            "single photo", "not a comparison", "no transformation shown",
            "mirror image", "mirror reflection", "horizontally flipped",
            "reflected version", "same state both sides", "no transformation",
            "both sides dirty", "both sides clean", "symmetrical contamination",
            
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
            
            # Text and labels (CRITICAL - ABSOLUTE PROHIBITION)
            "text", "words", "letters", "numbers", "digits",
            "labels", "captions", "annotations", "titles",
            "watermarks", "logos", "branding", "stamps",
            "writing", "script", "typography", "font",
            "signage", "markings", "inscriptions",
            "before label", "after label", "before text", "after text",
            "any visible characters", "any readable text",
            "any written language", "any textual elements",
            
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
        # Get guidance scale from config (already validated and auto-adjusted)
        guidance_scale = config.guidance_scale if config else 15.0
        
        return {
            "aspect_ratio": "16:9",  # Side-by-side format
            "guidance_scale": guidance_scale,
            "safety_filter_level": "block_few"
        }
    
    def generate_complete(
        self,
        material_name: str,
        material_properties: Optional[Dict] = None,
        config: Optional[MaterialImageConfig] = None,
        use_validation: bool = True
    ) -> Dict[str, Any]:
        """
        Generate complete prompt package for image generation.
        
        Args:
            material_name: Name of the material
            material_properties: Optional material properties from Materials.yaml
            config: Optional MaterialImageConfig for contamination control
            use_validation: If True, use orchestrator with pre-generation validation
            
        Returns:
            Dictionary with prompt, negative_prompt, and generation_params:
            {
                "prompt": str,
                "negative_prompt": str,
                "research_data": Dict,
                "aspect_ratio": str,
                "guidance_scale": float,
                "safety_filter_level": str,
                "validation_result": PromptValidationResult (if use_validation=True)
            }
        """
        # Require explicit config
        if config is None:
            raise ValueError(f"MaterialImageConfig is required for {material_name}. Cannot use default configuration.")
        
        # Get contamination research data (single call)
        research_data = None
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
                logger.error(f"❌ Category research failed for {material_name}: {e}")
                raise RuntimeError(f"Failed to research contamination patterns for {material_name}.") from e
        elif self.material_researcher:
            try:
                research_data = self.material_researcher.research_material_contamination(
                    material_name, material_properties
                )
                common_obj = research_data.get('common_object', material_name)
                contam_count = len(research_data.get('contaminants', []))
                logger.info(f"🔬 {material_name}: {common_obj} with {contam_count} contaminants researched")
            except Exception as e:
                logger.error(f"❌ Research failed for {material_name}: {e}")
                raise RuntimeError(f"Failed to research contamination for {material_name}.") from e
        else:
                raise RuntimeError(f"No contamination researcher configured for {material_name}.")
        
        # Generate prompt with optional validation
        validation_result = None
        if use_validation:
            # Use orchestrator with validation
            try:
                validated_package = self.generate_validated_prompt_package(material_name, config)
                prompt = validated_package['prompt']
                validation_result = validated_package['validation_result']
                
                # Log validation results
                if validation_result:
                    if validation_result.has_critical_issues:
                        logger.error(f"❌ Prompt validation FAILED with {len(validation_result.critical_issues)} critical issues")
                        for issue in validation_result.critical_issues:
                            logger.error(f"   • {issue.message}")
                        raise RuntimeError("Prompt validation failed with critical issues")
                    elif validation_result.errors:
                        logger.warning(f"⚠️  Prompt has {len(validation_result.errors)} errors")
                    else:
                        logger.info(f"✅ Prompt validation passed")
                        
            except Exception as e:
                logger.warning(f"⚠️  Orchestrator validation failed, falling back to SharedPromptBuilder: {e}")
                # Fallback to standard prompt generation
                prompt = self.generate_prompt(
                    material_name, material_properties, config, research_data
                )
        else:
            # Standard prompt generation without validation
            prompt = self.generate_prompt(
                material_name, material_properties, config, research_data
            )
        
        # Generate negative prompt
        negative_prompt = self.get_negative_prompt(material_name, config)
        
        # Get generation params
        params = self.get_generation_params(config)
        
        # Log configuration
        logger.info(
            f"📊 Config: {config.uniformity_label}, {config.view_mode} view, "
            f"guidance scale {config.guidance_scale}"
        )
        
        result = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "research_data": research_data,
            "config": config.to_dict(),
            **params
        }
        
        # Add validation result if available
        if validation_result:
            result['validation_result'] = validation_result
            
        return result
    

