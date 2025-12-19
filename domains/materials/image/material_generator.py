#!/usr/bin/env python3
"""
Material Before/After Image Generator

Generator for material laser cleaning before/after images with scientifically
accurate contamination data from Contaminants.yaml.

SIMPLIFIED ARCHITECTURE (Nov 29, 2025):
- Contamination data: Reads from Contaminants.yaml (NO API calls)
- Shape research: Optional Gemini API call (the only external research)
- Zero API calls for contamination patterns - uses pre-populated data

Author: AI Assistant
Date: November 24, 2025 (Simplified: November 29, 2025)
"""

import logging
from typing import Any, Dict, Optional

from domains.materials.image.material_config import MaterialImageConfig

# Simplified architecture: Use YAML-based pattern selector (no API calls for contamination)
from domains.materials.image.research.contamination_pattern_selector import (
    ContaminationPatternSelector,
)
from shared.image.orchestrator import ImagePromptOrchestrator
from shared.image.utils.image_pipeline_monitor import get_pipeline_monitor
from shared.image.utils.prompt_builder import SharedPromptBuilder

# Centralized metal classification for accurate rust prevention
from shared.utils.metal_classifier import get_classifier
from shared.validation.contamination_validator import ContaminationValidator

logger = logging.getLogger(__name__)


class MaterialImageGenerator:
    """
    Generator for material before/after laser cleaning images.
    
    SIMPLIFIED ARCHITECTURE (Nov 29, 2025):
    - Contamination patterns: From Contaminants.yaml (ZERO API calls)
    - Shape research: Optional Gemini API call (only external call)
    - Deterministic, fast, no cache dependencies
    """
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """
        Initialize material image generator.
        
        Args:
            gemini_api_key: Optional Gemini API key for shape research ONLY
                           (contamination data comes from Contaminants.yaml)
        """
        # Simplified: Pattern selector reads from YAML (no API)
        self.pattern_selector = ContaminationPatternSelector()
        self.gemini_api_key = gemini_api_key  # Only used for shape research
        
        # Initialize prompt builder
        from pathlib import Path
        prompts_dir = Path(__file__).parent / "prompts" / "shared"
        self.prompt_builder = SharedPromptBuilder(prompts_dir=prompts_dir)
        
        # Orchestrator for validated prompt generation - WITH SharedPromptBuilder
        # This ensures 6-stage chain uses comprehensive prompt building
        self.orchestrator = ImagePromptOrchestrator(
            domain='materials',
            prompt_builder=self.prompt_builder  # Assembly stage uses SharedPromptBuilder
        )
        
        self.pipeline_monitor = get_pipeline_monitor()
        self.contamination_validator = ContaminationValidator()
        
        logger.info("✅ MaterialImageGenerator initialized (zero API calls for contamination)")
        logger.info("   • Orchestrator integrated with SharedPromptBuilder")
        if gemini_api_key:
            logger.info("   • Shape research enabled (Gemini API available)")
    
    def generate_prompt(
        self,
        material_name: str,
        material_properties: Optional[Dict] = None,
        config: Optional[MaterialImageConfig] = None,
        research_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate before/after image prompt for a material.
        
        SIMPLIFIED: Uses Contaminants.yaml for patterns (ZERO API calls).
        
        Args:
            material_name: Name of the material (e.g., "Aluminum", "Stainless Steel")
            material_properties: Optional material properties from Materials.yaml
            config: Optional MaterialImageConfig for contamination control
            research_data: Optional pre-fetched research data
            
        Returns:
            Image prompt string optimized for Imagen 4
        """
        # Require explicit config
        if config is None:
            raise ValueError(f"MaterialImageConfig is required for {material_name}. Cannot use default configuration.")
        
        # Get contamination data from YAML (ZERO API calls)
        if research_data is None:
            print("\n📦 Loading contamination patterns from Contaminants.yaml...")
            research_data = self.pattern_selector.get_patterns_for_image_gen(
                material_name=material_name,
                num_patterns=config.contamination_uniformity,
                context=config.context
            )
            
            patterns = research_data.get('selected_patterns', [])
            rich_count = sum(1 for p in patterns if p.get('has_rich_appearance_data'))
            
            print(f"   ✅ Selected {len(patterns)} patterns for {material_name}")
            print(f"   📊 {rich_count}/{len(patterns)} have rich material-specific appearance data")
            for p in patterns:
                marker = "✨" if p.get('has_rich_appearance_data') else "📄"
                print(f"   {marker} {p['pattern_name']}")
            
            logger.info(f"📋 {material_name}: {len(patterns)} patterns from YAML, {rich_count} with rich data")
        
        # Get learned feedback for this category
        learned_feedback = None
        try:
            from shared.image.learning import create_logger
            learning_logger = create_logger()
            learned_feedback = learning_logger.get_category_feedback(
                material_category=config.category,
                limit=5
            )
            if learned_feedback:
                logger.info(f"🧠 Loaded learned feedback for {config.category}")
        except Exception as e:
            logger.debug(f"Could not load learned feedback: {e}")
        
        # Build complete prompt with research data
        prompt = self.prompt_builder.build_generation_prompt(
            material_name=material_name,
            research_data=research_data,
            contamination_uniformity=config.contamination_uniformity,
            view_mode=config.view_mode,
            material_category=config.category,
            learned_feedback=learned_feedback,
            severity=config.severity,
            aging_weight=getattr(config, 'aging_weight', None),
            contamination_weight=getattr(config, 'contamination_weight', None)
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
        # Base negative prompt - PRIORITY ORDER (most critical FIRST)
        base_negative = [
            # ═══════════════════════════════════════════════════════════════
            # PRIORITY 1: TEXT/LABELS (ABSOLUTE PROHIBITION - FIRST POSITION)
            # ═══════════════════════════════════════════════════════════════
            "text", "words", "letters", "numbers", "writing",
            "labels", "micros", "before", "after", "watermarks",
            "any text whatsoever", "any labels", "any writing",
            "text overlays", "caption text", "title text",
            
            # ═══════════════════════════════════════════════════════════════
            # PRIORITY 2: WRONG OBJECT SHAPE (CRITICAL - SECOND POSITION)
            # ═══════════════════════════════════════════════════════════════
            "crystal", "crystals", "crystal formation", "crystalline structure",
            "raw ore", "ore chunk", "mineral specimen", "geode",
            "random chunk", "irregular chunk", "raw material chunk",
            "wrong shape", "wrong form", "wrong object",
            "not an ingot", "not a sheet", "not a wire", "not a pipe",
            "abstract shape", "unidentifiable shape", "generic blob",
            "decorative object", "art piece", "sculpture",
            
            # ═══════════════════════════════════════════════════════════════
            # PRIORITY 3: SPLIT COMPOSITION (CRITICAL)
            # ═══════════════════════════════════════════════════════════════
            "single object only", "no comparison", "one state only",
            "just contaminated", "just clean", "no split",
            "no before and after", "missing half", "incomplete composite",
            "mirror image", "mirror reflection", "same state both sides",
            
            # ═══════════════════════════════════════════════════════════════
            # PRIORITY 4: POSITION/ANGLE/ROTATION VIOLATIONS (CRITICAL)
            # ═══════════════════════════════════════════════════════════════
            "identical positions", "mirror copy", "exact duplicate",
            "same angle both sides", "no rotation", "same rotation",
            "identical orientation", "no horizontal rotation",
            "tilted up", "tilted down", "vertical tilt", "angled up", "angled down",
            "same shadows both sides", "no position shift", "static",
            "perfectly aligned", "symmetrical placement",
            
            # ═══════════════════════════════════════════════════════════════
            # PRIORITY 5: BACKGROUND VIOLATIONS (HIGH)
            # ═══════════════════════════════════════════════════════════════
            "outdoor", "nature", "sky", "grass", "trees", "landscape",
            "white background", "studio backdrop", "abstract background",
            "plain background", "gradient background",
            
            # ═══════════════════════════════════════════════════════════════
            # STANDARD: CONTAMINATION REALISM
            # ═══════════════════════════════════════════════════════════════
            "dirt", "soil", "mud", "generic dirt", "brown dirt",
            "drips", "drops", "dripping", "pooling", "liquid drips",
            "unnatural contamination", "fake-looking dirt", "painted-on grime",
            "uniform contamination", "perfectly even dirt",
            "contamination defying gravity", "floating particles",
            "digital overlay", "copy-pasted pattern",
            
            # ═══════════════════════════════════════════════════════════════
            # STANDARD: MATERIAL APPEARANCE
            # ═══════════════════════════════════════════════════════════════
            f"incorrect {material_name} appearance", "wrong material color",
            "impossible material texture", "fake material surface",
            
            # ═══════════════════════════════════════════════════════════════
            # STANDARD: QUALITY/UNREALISTIC
            # ═══════════════════════════════════════════════════════════════
            "blurry", "low resolution", "pixelated", "artifacts",
            "cartoon", "illustration", "CGI", "3D render"
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
        
        # Add material-specific exclusions for corrosion-resistant materials
        # Use centralized MetalClassifier - non-ferrous metals cannot rust
        classifier = get_classifier()
        if not classifier.can_rust(material_name):
            # This material is non-ferrous or non-metallic - exclude rust terms
            base_negative.extend([
                "rust", "rusty", "rust spots", "orange rust", "red rust",
                "iron oxide", "rust streaks", "rust stains", "corroded rust"
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
        shape_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate complete prompt package for image generation via orchestrator.
        
        USES 6-STAGE ORCHESTRATOR CHAIN:
        1. Research → Extract/use provided research data
        2. Visual → Generate appearance description
        3. Composition → Layout before/after
        4. Refinement → Technical accuracy
        5. Assembly → SharedPromptBuilder (comprehensive prompt)
        6. Validation → Pre-generation quality check
        
        SIMPLIFIED (Nov 29, 2025):
        - Contamination data: From Contaminants.yaml (ZERO API calls)
        - Shape research: Optional Gemini API call (only if API key provided)
        
        Args:
            material_name: Name of the material
            material_properties: Optional material properties from Materials.yaml
            config: Optional MaterialImageConfig for contamination control
            shape_override: Optional override for shape/object (e.g., "I-beam in a building structure")
            
        Returns:
            Dictionary with prompt, negative_prompt, stage_outputs, and generation_params
        """
        # Require explicit config
        if config is None:
            raise ValueError(f"MaterialImageConfig is required for {material_name}. Cannot use default configuration.")
        
        # === CONTAMINATION DATA (from YAML - ZERO API calls) ===
        print("\n📦 Loading contamination patterns from Contaminants.yaml...")
        research_data = self.pattern_selector.get_patterns_for_image_gen(
            material_name=material_name,
            num_patterns=config.contamination_uniformity,
            context=config.context
        )
        
        patterns = research_data.get('selected_patterns', [])
        rich_count = sum(1 for p in patterns if p.get('has_rich_appearance_data'))
        
        # === MANDATORY TERMINAL OUTPUT: All Associated Contaminants ===
        # Per policy: List ALL contaminants selected for image generation
        print(f"\n{'='*70}")
        print(f"🧪 CONTAMINATION PATTERNS FOR: {material_name}")
        print(f"{'='*70}")
        print(f"   Context: {config.context}")
        print(f"   Patterns requested: {config.contamination_uniformity}")
        print(f"   Patterns selected: {len(patterns)}")
        print(f"   Rich appearance data: {rich_count}/{len(patterns)}")
        print(f"\n   📋 SELECTED CONTAMINATION PATTERNS:")
        for i, p in enumerate(patterns, 1):
            pattern_id = p.get('pattern_id', 'unknown')
            pattern_name = p.get('pattern_name', pattern_id)
            has_rich = '✅' if p.get('has_rich_appearance_data') else '⚠️'
            category = p.get('category', 'contamination')
            
            # Get visual characteristics summary
            visual = p.get('visual_characteristics', {})
            colors = visual.get('color_range', 'N/A')
            texture = visual.get('texture_detail', 'N/A')[:50] if visual.get('texture_detail') else 'N/A'
            
            print(f"\n   {i}. {pattern_name} ({pattern_id})")
            print(f"      {has_rich} Rich data | Category: {category}")
            print(f"      Colors: {colors}")
            print(f"      Texture: {texture}...")
            
            # Show realism notes if available
            realism = p.get('realism_notes', '')
            if realism:
                print(f"      Realism: {realism[:60]}...")
        
        print(f"\n{'='*70}")
        print(f"   ✅ Selected {len(patterns)} patterns (ZERO API calls)")
        print(f"   📊 {rich_count}/{len(patterns)} have rich appearance data")
        
        category = research_data.get('category', 'metal')
        
        # Add context-specific background to research_data
        research_data['context_background'] = config.context_background
        
        # === SHAPE RESEARCH (optional API call) ===
        if shape_override:
            # User provided explicit shape override
            if ' in ' in shape_override.lower() or ' on ' in shape_override.lower():
                research_data['common_shape'] = shape_override
                research_data['common_object'] = shape_override
                research_data['shape_context'] = 'architectural/structural'
                research_data['setting'] = 'its installed location'
            else:
                research_data['common_shape'] = shape_override
                research_data['common_object'] = shape_override
                research_data['shape_context'] = 'standalone'
                research_data['setting'] = 'a workshop bench'
            print(f"   🎯 Shape override: {shape_override}")
        elif self.gemini_api_key:
            # Research most common shape/item (only API call)
            try:
                from domains.materials.image.research.shape_researcher import (
                    MaterialShapeResearcher,
                )
                shape_researcher = MaterialShapeResearcher()
                print(f"\n🔎 Researching common {material_name} object (API call)...")
                shape_result = shape_researcher.get_common_shape(material_name, category)
                research_data['common_shape'] = shape_result['object']
                research_data['common_object'] = shape_result['object']
                research_data['shape_context'] = shape_result['context']
                research_data['setting'] = shape_result['setting']
                print(f"   ✅ Shape: {shape_result['object']} ({shape_result['context']})")
            except Exception as e:
                logger.warning(f"⚠️  Shape research unavailable: {e}")
                # Default to generic object
                research_data['common_object'] = f"{material_name} component"
                research_data['setting'] = 'a workshop bench'
        else:
            # No API key - use generic shape
            research_data['common_object'] = f"{material_name} component"
            research_data['setting'] = 'a workshop bench'
            print("   📋 No shape research (no API key) - using generic")
        
        # === ASSEMBLY RESEARCH (for complex parts) ===
        shape_name = research_data.get('common_object', research_data.get('common_shape', ''))
        if self.gemini_api_key and shape_name:
            try:
                from domains.materials.image.research.assembly_researcher import (
                    AssemblyResearcher,
                )
                assembly_researcher = AssemblyResearcher()
                
                # Only research if it's a complex part
                if assembly_researcher.is_complex_part(shape_name):
                    print("\n🔧 Researching assembly components for complex part...")
                    assembly_context = assembly_researcher.get_assembly_context(material_name, shape_name)
                    
                    if assembly_context:
                        research_data['assembly_context'] = assembly_context
                        research_data['assembly_description'] = assembly_researcher.format_for_prompt(assembly_context)
                        
                        # Log assembly components
                        components = assembly_context.get('assembly_components', [])
                        print(f"   ✅ Found {len(components)} assembly components:")
                        for comp in components:
                            print(f"      • {comp['material']} {comp['part']} ({comp['relationship']})")
            except Exception as e:
                logger.debug(f"Assembly research skipped: {e}")
        
        # === PROMPT GENERATION VIA ORCHESTRATOR ===
        # Use orchestrator as PRIMARY path - it now uses SharedPromptBuilder in assembly stage
        # This ensures 6-stage chain with comprehensive prompt building and validation
        
        validation_result = None
        prompt = None
        stage_outputs = {}
        
        print("\n" + "=" * 60)
        print("🎭 ORCHESTRATOR: 6-Stage Prompt Generation Chain")
        print("=" * 60)
        
        try:
            # Use orchestrator with SharedPromptBuilder integration
            chained_result = self.orchestrator.generate_hero_prompt(
                identifier=material_name,
                research_data=research_data,
                material_properties=material_properties,
                config=config,
                category=config.category,
                api='imagen'
            )
            
            prompt = chained_result.prompt
            stage_outputs = chained_result.stage_outputs
            validation_result = stage_outputs.get('validation')
            
            print("\n" + "=" * 60)
            print(f"✅ ORCHESTRATOR COMPLETE: {len(prompt)} char prompt generated")
            print("=" * 60)
            
            # Check validation result
            if validation_result:
                if hasattr(validation_result, 'has_critical_issues') and validation_result.has_critical_issues:
                    logger.error("❌ Prompt validation FAILED with critical issues")
                    # Raise to prevent bad prompt from proceeding
                    raise ValueError(f"Prompt validation failed: {validation_result.format_report()}")
                elif hasattr(validation_result, 'errors') and validation_result.errors:
                    logger.warning(f"⚠️  Prompt has {len(validation_result.errors)} non-critical errors")
                else:
                    logger.info("✅ Prompt validation passed")
                    
        except Exception as e:
            # FAIL-FAST: Do not silently fall back - raise the error
            # Per copilot-instructions.md: NO fallbacks in production code
            logger.error(f"❌ Orchestrator failed: {e}")
            print(f"\n❌ FAIL-FAST: Orchestrator error - {e}")
            raise RuntimeError(
                f"FAIL-FAST: Orchestrator failed for {material_name}. "
                f"Error: {e}. "
                f"Fix the orchestrator issue instead of using fallback."
            ) from e
        
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
            "stage_outputs": stage_outputs,  # Include orchestrator stage outputs
            **params
        }
        
        # Add validation result if available
        if validation_result:
            result['validation_result'] = validation_result
            
        return result
    

