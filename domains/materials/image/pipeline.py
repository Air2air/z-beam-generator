#!/usr/bin/env python3
"""
Material Image Generation Pipeline

Core pipeline logic for image generation - separated from CLI concerns.
Handles: research, prompt generation, image generation, validation, learning.

This module owns the generation flow. CLI (cli.py) handles user interface.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import yaml

from domains.materials.image.material_generator import MaterialImageGenerator
from domains.materials.image.material_config import MaterialImageConfig
from shared.api.gemini_image_client import GeminiImageClient
from shared.api.gemini_flash_image_client import GeminiFlashImageClient
from shared.image.learning import create_logger

logger = logging.getLogger(__name__)

# Path to config files
CONFIG_PATH = Path(__file__).parent / "config.yaml"
MATERIALS_YAML_PATH = Path(__file__).parent.parent.parent.parent / "data" / "materials" / "Materials.yaml"


@dataclass
class GenerationResult:
    """Result of image generation pipeline."""
    passed: bool
    output_path: Optional[Path]
    validation_result: Optional[Any]
    prompt_package: Optional[Dict[str, Any]]
    file_size: int = 0
    skipped_validation: bool = False


def load_image_config() -> Dict[str, Any]:
    """
    Load image generation config from config.yaml.
    FAIL-FAST: Raises if config missing or invalid.
    """
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"FAIL-FAST: Image config not found at {CONFIG_PATH}. "
            f"This file is required for image generation."
        )
    
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
    
    # FAIL-FAST: Require quality settings
    if 'quality' not in config:
        raise ValueError(
            f"FAIL-FAST: 'quality' section missing from {CONFIG_PATH}. "
            f"Required keys: pass_threshold, guidance_scale_default"
        )
    
    quality = config['quality']
    if 'pass_threshold' not in quality:
        raise ValueError(f"FAIL-FAST: 'quality.pass_threshold' missing from {CONFIG_PATH}")
    if 'guidance_scale_default' not in quality:
        raise ValueError(f"FAIL-FAST: 'quality.guidance_scale_default' missing from {CONFIG_PATH}")
    
    return config


# Load config at module level - FAIL-FAST if missing
_IMAGE_CONFIG = load_image_config()
PASS_THRESHOLD = _IMAGE_CONFIG['quality']['pass_threshold']
GUIDANCE_SCALE_DEFAULT = _IMAGE_CONFIG['quality']['guidance_scale_default']


def load_material_properties(material_name: str) -> Optional[Dict[str, Any]]:
    """
    Load material properties from Materials.yaml.
    
    Returns:
        Dictionary with material properties, or None if not found
    """
    if not MATERIALS_YAML_PATH.exists():
        logger.warning(f"⚠️  Materials.yaml not found at {MATERIALS_YAML_PATH}")
        return None
    
    try:
        with open(MATERIALS_YAML_PATH, 'r') as f:
            data = yaml.safe_load(f)
        
        materials = data.get('materials', {})
        material_data = materials.get(material_name)
        
        if not material_data:
            logger.warning(f"⚠️  Material '{material_name}' not found in Materials.yaml")
            return None
        
        # Extract relevant properties
        material_props = material_data.get('properties', {})
        characteristics = material_props.get('material_characteristics', {})
        laser_interaction = material_props.get('laser_material_interaction', {})
        
        # Helper to extract value from property dict
        def get_value(prop_dict, default=None):
            if isinstance(prop_dict, dict):
                return prop_dict.get('value', default)
            return prop_dict if prop_dict else default
        
        properties = {
            'name': material_data.get('name', material_name),
            'category': material_data.get('category'),
            'subcategory': material_data.get('subcategory'),
            'density': get_value(characteristics.get('density')),
            'porosity': get_value(characteristics.get('porosity')),
            'surface_roughness': get_value(characteristics.get('surfaceRoughness')),
            'hardness': get_value(characteristics.get('hardness')),
            'reflectivity': get_value(characteristics.get('reflectivity')),
            'absorptivity': get_value(characteristics.get('absorptivity')),
            'color': get_value(characteristics.get('color')),
            'corrosion_resistance': get_value(characteristics.get('corrosionResistance')),
            'oxidation_resistance': get_value(characteristics.get('oxidationResistance')),
            'laser_reflectivity': get_value(laser_interaction.get('laserReflectivity')),
            'absorption_coefficient': get_value(laser_interaction.get('absorptionCoefficient')),
            'thermal_conductivity': get_value(laser_interaction.get('thermalConductivity')),
            'contamination_valid': material_data.get('contamination', {}).get('valid', []),
            'contamination_prohibited': material_data.get('contamination', {}).get('prohibited', []),
            'material_characteristics': characteristics,
            'laser_interaction': laser_interaction,
        }
        
        # Log what was loaded
        loaded_visual = sum(1 for k in ['reflectivity', 'absorptivity', 'color'] if properties.get(k))
        loaded_resistance = sum(1 for k in ['corrosion_resistance', 'oxidation_resistance'] if properties.get(k))
        logger.info(f"📋 Loaded material properties for {material_name}")
        logger.info(f"   • Visual properties: {loaded_visual}/3 loaded")
        logger.info(f"   • Resistance properties: {loaded_resistance}/2 loaded")
        
        return properties
        
    except Exception as e:
        logger.warning(f"⚠️  Failed to load material properties: {e}")
        return None


def build_feedback_text(validation_result) -> Tuple[Optional[str], Optional[str]]:
    """Build comprehensive feedback text from validation result."""
    feedback_parts = []
    feedback_category = None
    
    if validation_result.overall_assessment:
        feedback_parts.append(validation_result.overall_assessment)
    
    if validation_result.physics_issues:
        feedback_parts.append("Physics Issues: " + "; ".join(validation_result.physics_issues[:3]))
    
    if validation_result.distribution_issues:
        feedback_parts.append("Distribution Issues: " + "; ".join(validation_result.distribution_issues[:3]))
    
    if validation_result.recommendations:
        feedback_parts.append("Recommendations: " + "; ".join(validation_result.recommendations[:5]))
    
    if feedback_parts:
        feedback_text = "\n".join(feedback_parts)
        
        if validation_result.physics_issues and len(validation_result.physics_issues) > 0:
            feedback_category = 'physics'
        elif feedback_text and ('text label' in feedback_text.lower() or 'no visible difference' in feedback_text.lower()):
            feedback_category = 'aesthetics'
        elif validation_result.passed:
            feedback_category = 'success'
        else:
            feedback_category = 'quality'
        
        return feedback_text, feedback_category
    
    return None, None


class ImageGenerationPipeline:
    """
    Core pipeline for material image generation.
    
    Responsibilities:
    - Research: Load material properties and contamination data
    - Generate: Create prompt and generate image via Imagen or Gemini Flash
    - Validate: Check image quality via Gemini Vision
    - Learn: Log results to learning database
    """
    
    def __init__(self, gemini_api_key: str, use_flash: bool = False):
        """Initialize pipeline with API key.
        
        Args:
            gemini_api_key: API key for Gemini services
            use_flash: If True, use Gemini 2.0 Flash for generation (faster, more available)
        """
        self.gemini_api_key = gemini_api_key
        self.use_flash = use_flash
        self.generator = MaterialImageGenerator(gemini_api_key=gemini_api_key)
        
        # Select image generation client
        if use_flash:
            self.image_client = GeminiFlashImageClient()
        else:
            self.image_client = GeminiImageClient(api_key=gemini_api_key)
        
        self.learning_logger = create_logger()
    
    def get_material_category(self, material: str) -> Optional[str]:
        """Get category for a material from pattern selector."""
        if self.generator.pattern_selector:
            result = self.generator.pattern_selector.get_patterns_for_image_gen(material, num_patterns=1)
            return result.get('category')
        return None
    
    def generate(
        self,
        material: str,
        config: MaterialImageConfig,
        output_path: Path,
        shape_override: Optional[str] = None,
        show_prompt: bool = False,
        dry_run: bool = False,
        skip_validation: bool = False
    ) -> GenerationResult:
        """
        Run the full image generation pipeline.
        
        Args:
            material: Material name
            config: MaterialImageConfig instance
            output_path: Path to save generated image
            shape_override: Optional shape/object override
            show_prompt: If True, display prompt before generation
            dry_run: If True, generate prompt but don't create image
            skip_validation: If True, skip Gemini vision validation
            
        Returns:
            GenerationResult with outcome details
        """
        # Run early validation if available
        self._run_early_validation(material, config)
        
        # Load material properties
        material_properties = load_material_properties(material)
        
        # Generate prompt package
        logger.info("🔬 Researching contamination data...")
        prompt_package = self.generator.generate_complete(
            material_name=material,
            material_properties=material_properties,
            config=config,
            shape_override=shape_override
        )
        
        # Run prompt validation
        self._run_prompt_validation(material, prompt_package)
        
        # Show prompt if requested
        if show_prompt:
            self._display_prompt(prompt_package)
        
        # Exit early if dry run
        if dry_run:
            logger.info("✅ Dry run complete - no image generated")
            return GenerationResult(
                passed=True,
                output_path=None,
                validation_result=None,
                prompt_package=prompt_package
            )
        
        # Generate and validate image
        return self._generate_and_validate(
            material=material,
            config=config,
            prompt_package=prompt_package,
            output_path=output_path,
            shape_override=shape_override,
            skip_validation=skip_validation
        )
    
    def _run_early_validation(self, material: str, config: MaterialImageConfig):
        """Run early validation (pre-research)."""
        try:
            from shared.validation import UnifiedValidator, ValidationStatus
            
            prompts_dir = Path(__file__).parent / "prompts" / "shared"
            validator = UnifiedValidator(prompts_dir=prompts_dir)
            
            report = validator.validate_early(
                material=material,
                config={
                    'category': config.category,
                    'contamination_uniformity': config.contamination_uniformity,
                    'view_mode': config.view_mode
                }
            )
            
            if report.status == ValidationStatus.CRITICAL:
                logger.error("🚨 Early validation FAILED (critical):")
                logger.error(report.fix_instructions)
                raise ValueError(f"Early validation failed: {report.fix_instructions}")
            elif report.status == ValidationStatus.FAIL:
                logger.warning("⚠️  Early validation issues found:")
                logger.warning(report.fix_instructions)
            else:
                logger.info("✅ Early validation passed")
                
        except ImportError as e:
            logger.debug(f"Unified validator not available: {e}")
    
    def _run_prompt_validation(self, material: str, prompt_package: Dict[str, Any]):
        """Run prompt validation (pre-generation)."""
        try:
            from shared.validation import UnifiedValidator, ValidationStatus
            
            prompts_dir = Path(__file__).parent / "prompts" / "shared"
            validator = UnifiedValidator(prompts_dir=prompts_dir)
            
            report = validator.validate_prompt(
                prompt=prompt_package["prompt"],
                negative_prompt=prompt_package["negative_prompt"],
                material=material
            )
            
            if report.status == ValidationStatus.CRITICAL:
                logger.error("🚨 Prompt validation FAILED (critical):")
                logger.error(report.fix_instructions)
                raise ValueError(f"Prompt validation failed: {report.fix_instructions}")
            elif report.status == ValidationStatus.FAIL:
                # Try auto-fix
                if report.fix_actions:
                    original_len = len(prompt_package["prompt"])
                    prompt_package["prompt"] = report.apply_auto_fixes(prompt_package["prompt"])
                    logger.info(f"🔧 Applied auto-fixes: {original_len} → {len(prompt_package['prompt'])} chars")
                else:
                    logger.warning("⚠️  Prompt validation issues (no auto-fix available):")
                    logger.warning(report.fix_instructions)
            else:
                logger.info(f"✅ Prompt validation passed ({report.prompt_length} chars)")
                
        except ImportError as e:
            logger.debug(f"Unified validator not available: {e}")
    
    def _display_prompt(self, prompt_package: Dict[str, Any]):
        """Display prompt for user review."""
        logger.info("\n" + "="*80)
        logger.info("📝 GENERATED PROMPT")
        logger.info("="*80)
        logger.info(prompt_package["prompt"])
        logger.info("\n" + "="*80)
        logger.info("🚫 NEGATIVE PROMPT")
        logger.info("="*80)
        logger.info(prompt_package["negative_prompt"])
        logger.info("")
    
    def _generate_and_validate(
        self,
        material: str,
        config: MaterialImageConfig,
        prompt_package: Dict[str, Any],
        output_path: Path,
        shape_override: Optional[str] = None,
        skip_validation: bool = False
    ) -> GenerationResult:
        """Generate image and run validation."""
        
        logger.info(f"\n{'='*80}")
        logger.info(f"🎨 GENERATING IMAGE")
        logger.info(f"{'='*80}")
        logger.info(f"   • Aspect ratio: {prompt_package['aspect_ratio']}")
        logger.info(f"   • Guidance scale: {prompt_package['guidance_scale']}")
        
        # Generate image
        image = self.image_client.generate_image(
            prompt=prompt_package["prompt"],
            negative_prompt=prompt_package["negative_prompt"],
            aspect_ratio=prompt_package["aspect_ratio"],
            guidance_scale=prompt_package["guidance_scale"]
        )
        
        # Save image
        image.save(output_path)
        file_size = output_path.stat().st_size
        
        logger.info(f"✅ Image saved to: {output_path}")
        logger.info(f"   • Size: {file_size / 1024:.1f} KB")
        
        # Skip validation if disabled or explicitly skipped
        if not config.validate or skip_validation:
            if skip_validation:
                logger.info("\n⏭️  Validation skipped (--skip-validation)")
            return GenerationResult(
                passed=True,
                output_path=output_path,
                validation_result=None,
                prompt_package=prompt_package,
                file_size=file_size
            )
        
        # Validate image
        logger.info("\n🔍 Validating image with Gemini Vision...")
        
        from domains.materials.image.validator import MaterialImageValidator
        validator = MaterialImageValidator(self.gemini_api_key)
        
        try:
            validation_result = validator.validate_material_image(
                image_path=output_path,
                material_name=material,
                research_data=prompt_package["research_data"],
                config=config.to_dict(),
                original_prompt=prompt_package["prompt"],
                validation_result=prompt_package.get("validation_result")
            )
        except Exception as val_error:
            error_str = str(val_error)
            if "429" in error_str or "quota" in error_str.lower():
                logger.warning("\n⚠️  Validation API quota exceeded - skipping validation")
                return GenerationResult(
                    passed=True,
                    output_path=output_path,
                    validation_result=None,
                    prompt_package=prompt_package,
                    file_size=file_size,
                    skipped_validation=True
                )
            raise
        
        # Display validation results
        self._display_validation_results(validation_result)
        
        # Log to learning database
        feedback_text, feedback_category = build_feedback_text(validation_result)
        self._log_to_learning(
            material=material,
            config=config,
            prompt_package=prompt_package,
            validation_result=validation_result,
            output_path=output_path,
            file_size=file_size,
            feedback_text=feedback_text,
            feedback_category=feedback_category,
            shape_override=shape_override
        )
        
        return GenerationResult(
            passed=validation_result.passed,
            output_path=output_path,
            validation_result=validation_result,
            prompt_package=prompt_package,
            file_size=file_size
        )
    
    def _display_validation_results(self, validation_result):
        """Display validation results to user."""
        logger.info("\n📊 VALIDATION RESULTS:")
        logger.info(f"   • Realism Score: {validation_result.realism_score:.1f}/100")
        logger.info(f"   • Pass Threshold: {PASS_THRESHOLD}/100")
        
        if validation_result.text_labels_present:
            logger.info(f"   • Text/Labels: ❌ DETECTED (automatic fail)")
            if validation_result.text_label_details:
                for detail in validation_result.text_label_details:
                    logger.info(f"      → {detail}")
        else:
            logger.info(f"   • Text/Labels: ✅ None detected")
        
        if validation_result.position_shift_appropriate is not None:
            shift_status = "✅ Appropriate" if validation_result.position_shift_appropriate else "❌ Identical/Wrong"
            logger.info(f"   • Position Shift: {shift_status}")
        
        logger.info(f"   • Status: {'✅ PASSED' if validation_result.passed else '❌ FAILED'}")
        
        if validation_result.overall_assessment:
            logger.info(f"\n   Assessment: {validation_result.overall_assessment}")
        
        if validation_result.physics_issues:
            logger.info(f"\n   Physics Issues:")
            for issue in validation_result.physics_issues[:5]:
                logger.info(f"      • {issue}")
        
        if validation_result.recommendations:
            logger.info(f"\n   Recommendations:")
            for rec in validation_result.recommendations[:5]:
                logger.info(f"      • {rec}")
    
    def _log_to_learning(
        self,
        material: str,
        config: MaterialImageConfig,
        prompt_package: Dict[str, Any],
        validation_result,
        output_path: Path,
        file_size: int,
        feedback_text: Optional[str],
        feedback_category: Optional[str],
        shape_override: Optional[str] = None
    ):
        """Log attempt to learning database."""
        try:
            research_data = prompt_package.get('research_data', {})
            context_data = research_data.get('context_settings', {})
            
            self.learning_logger.log_attempt(
                material=material,
                category=config.category,
                generation_params={
                    'prompt_length': len(prompt_package['prompt']),
                    'guidance_scale': prompt_package['guidance_scale'],
                    'contamination_uniformity': config.contamination_uniformity,
                    'view_mode': config.view_mode,
                    'severity': config.severity,
                    'shape_override': shape_override,
                    'patterns_used': [p.get('pattern_name', p.get('name', 'Unknown')) 
                                    for p in research_data.get('selected_patterns', 
                                    research_data.get('contaminants', []))[:3]],
                    'feedback_text': feedback_text,
                    'feedback_category': feedback_category,
                    'context': config.context,
                    'aging_weight': context_data.get('aging_weight'),
                    'contamination_weight': context_data.get('contamination_weight'),
                },
                validation_results={
                    'realism_score': int(validation_result.realism_score) if validation_result.realism_score else 0,
                    'passed': validation_result.passed,
                    'physics_issues': validation_result.physics_issues or [],
                },
                outcome={
                    'failure_category': feedback_category if not validation_result.passed else None,
                    'final_success': validation_result.passed
                },
                image_metadata={
                    'path': str(output_path),
                    'size_kb': file_size / 1024
                }
            )
            
            # Update pattern effectiveness
            patterns_used = [p.get('pattern_name', p.get('name', 'Unknown')) 
                            for p in research_data.get('selected_patterns', 
                            research_data.get('contaminants', []))[:3]]
            
            self.learning_logger.update_pattern_effectiveness(
                patterns_used=patterns_used,
                category=config.category,
                context=config.context,
                passed=validation_result.passed,
                realism_score=validation_result.realism_score or 0
            )
            
            # Update learned defaults if successful
            if validation_result.passed:
                self.learning_logger.update_learned_defaults_from_success(
                    category=config.category,
                    context=config.context,
                    guidance_scale=prompt_package.get('guidance_scale') or GUIDANCE_SCALE_DEFAULT,
                    realism_score=validation_result.realism_score or 0,
                    aging_weight=context_data.get('aging_weight'),
                    contamination_weight=context_data.get('contamination_weight')
                )
                
        except Exception as log_error:
            logger.debug(f"Failed to log to learning database: {log_error}")
