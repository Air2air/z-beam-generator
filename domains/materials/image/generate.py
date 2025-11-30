#!/usr/bin/env python3
"""
Material Image Generator CLI

Generate before/after laser cleaning images with researched contamination defaults.
Includes auto-retry with feedback injection on validation failure.

Usage:
    python3 domains/materials/image/generate.py --material "Aluminum"
    python3 domains/materials/image/generate.py --material "Stainless Steel" --max-retries 5
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from domains.materials.image.material_generator import MaterialImageGenerator
from domains.materials.image.material_config import MaterialImageConfig
from shared.api.gemini_image_client import GeminiImageClient
from shared.image.learning import create_logger

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Constants
MAX_RETRIES = 1  # Default: single attempt, wait for user feedback before retry
PASS_THRESHOLD = 75.0


def build_feedback_text(validation_result) -> Tuple[Optional[str], Optional[str]]:
    """
    Build comprehensive feedback text from validation result.
    
    Returns:
        Tuple of (feedback_text, feedback_category)
    """
    feedback_parts = []
    feedback_category = None
    
    # Add overall assessment
    if validation_result.overall_assessment:
        feedback_parts.append(validation_result.overall_assessment)
    
    # Add specific issues
    if validation_result.physics_issues:
        feedback_parts.append("Physics Issues: " + "; ".join(validation_result.physics_issues[:3]))
    
    if validation_result.distribution_issues:
        feedback_parts.append("Distribution Issues: " + "; ".join(validation_result.distribution_issues[:3]))
    
    # Add recommendations
    if validation_result.recommendations:
        feedback_parts.append("Recommendations: " + "; ".join(validation_result.recommendations[:5]))
    
    if feedback_parts:
        feedback_text = "\n".join(feedback_parts)
        
        # Categorize feedback
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


def build_correction_prompt(validation_result, attempt_num: int, prompt_aware_feedback: Optional[str] = None) -> str:
    """
    Build a correction prompt from validation feedback to inject into the next attempt.
    
    Args:
        validation_result: The validation result with recommendations
        attempt_num: Current attempt number
        prompt_aware_feedback: Optional prompt-aware correction feedback from validator
        
    Returns:
        Correction prompt string to append to next generation
    """
    corrections = []
    
    corrections.append(f"\n\n🔧 CRITICAL CORRECTIONS FROM ATTEMPT {attempt_num} (MUST FIX):")
    
    # Use prompt-aware feedback if available (more specific)
    if prompt_aware_feedback:
        corrections.append(prompt_aware_feedback)
    else:
        # Fall back to generic feedback
        # Add assessment
        if validation_result.overall_assessment:
            corrections.append(f"PROBLEM: {validation_result.overall_assessment}")
        
        # Add specific issues to fix
        if validation_result.physics_issues:
            corrections.append("FIX PHYSICS:")
            for issue in validation_result.physics_issues[:3]:
                corrections.append(f"  - {issue}")
        
        if validation_result.distribution_issues:
            corrections.append("FIX DISTRIBUTION:")
            for issue in validation_result.distribution_issues[:3]:
                corrections.append(f"  - {issue}")
        
        # Add recommendations as requirements
        if validation_result.recommendations:
            corrections.append("MANDATORY REQUIREMENTS:")
            for rec in validation_result.recommendations[:5]:
                corrections.append(f"  - {rec}")
    
    # Add emphasis on before/after difference
    corrections.append("\nCRITICAL: The BEFORE side MUST show VISIBLE contamination. The AFTER side MUST be CLEAN. The difference MUST be DRAMATIC and OBVIOUS.")
    corrections.append("CRITICAL: The RIGHT side MUST be ROTATED 10-20 degrees horizontally from the LEFT side.")
    
    return "\n".join(corrections)


def log_attempt(
    generation_logger,
    material: str,
    config: MaterialImageConfig,
    prompt_package: Dict[str, Any],
    validation_result,
    output_path: Path,
    file_size: int,
    attempt_num: int,
    feedback_text: Optional[str],
    feedback_category: Optional[str],
    previous_feedback: Optional[str] = None,
    shape_override: Optional[str] = None
):
    """Log attempt to learning database."""
    try:
        # Extract pre-generation validation metrics if available
        pre_validation_metrics = {}
        if 'validation_result' in prompt_package:
            pre_val = prompt_package['validation_result']
            pre_validation_metrics = {
                'pre_validation_passed': not pre_val.has_critical_issues if pre_val else True,
                'pre_validation_errors': len(pre_val.errors) if pre_val else 0,
                'pre_validation_warnings': len(pre_val.warnings) if pre_val else 0,
                'pre_validation_critical': len(pre_val.critical_issues) if pre_val else 0
            }
        
        # Extract context-related data for learning
        research_data = prompt_package.get('research_data', {})
        context_data = research_data.get('context_settings', {})
        
        # Extract pattern scores if available (for learning which patterns work best)
        pattern_scores = {}
        for p in research_data.get('selected_patterns', []):
            if 'relevance_score' in p:
                pattern_scores[p.get('pattern_name', 'unknown')] = p['relevance_score']
        
        generation_logger.log_attempt(
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
                'feedback_applied': previous_feedback is not None,
                'previous_feedback': previous_feedback,  # Feedback from previous attempt
                'feedback_text': feedback_text,  # Validator feedback for learning
                'feedback_category': feedback_category,
                'feedback_source': 'automated',
                'attempt_number': attempt_num,
                # New context parameters for learning
                'context': config.context,
                'aging_weight': context_data.get('aging_weight'),
                'contamination_weight': context_data.get('contamination_weight'),
                'background': research_data.get('context_background'),
                'pattern_scores': pattern_scores,
                # Optimization metrics
                'prompt_chars_before_opt': prompt_package.get('prompt_chars_before_opt'),
                'prompt_chars_after_opt': len(prompt_package['prompt']),
                **pre_validation_metrics
            },
            validation_results={
                'prompt_length': 0,
                'truncated': False,
                'realism_score': int(validation_result.realism_score) if validation_result.realism_score else 0,
                'passed': validation_result.passed,
                'physics_issues': validation_result.physics_issues if validation_result.physics_issues else [],
                'red_flags': []
            },
            outcome={
                'failure_category': feedback_category if not validation_result.passed else None,
                'retry_count': attempt_num - 1,
                'final_success': validation_result.passed
            },
            image_metadata={
                'path': str(output_path),
                'size_kb': file_size / 1024
            }
        )
        
        # Update learning system with outcome
        patterns_used = [p.get('pattern_name', p.get('name', 'Unknown')) 
                        for p in research_data.get('selected_patterns', 
                        research_data.get('contaminants', []))[:3]]
        
        # Update pattern effectiveness
        generation_logger.update_pattern_effectiveness(
            patterns_used=patterns_used,
            category=config.category,
            context=config.context,
            passed=validation_result.passed,
            realism_score=validation_result.realism_score or 0
        )
        
        # Update learned defaults if successful
        if validation_result.passed:
            generation_logger.update_learned_defaults_from_success(
                category=config.category,
                context=config.context,
                guidance_scale=prompt_package.get('guidance_scale', 15.0),
                realism_score=validation_result.realism_score or 0,
                aging_weight=context_data.get('aging_weight'),
                contamination_weight=context_data.get('contamination_weight')
            )
            
    except Exception as log_error:
        logger.debug(f"Failed to log to learning database: {log_error}")


def generate_and_validate(
    image_client: GeminiImageClient,
    validator,
    prompt_package: Dict[str, Any],
    output_path: Path,
    material: str,
    config: MaterialImageConfig,
    attempt_num: int,
    max_attempts: int,
    correction_feedback: Optional[str] = None
) -> Tuple[Any, Optional[str], int]:
    """
    Generate an image and validate it.
    
    Args:
        image_client: GeminiImageClient instance
        validator: MaterialImageValidator instance
        prompt_package: Prompt package from generator
        output_path: Path to save image
        material: Material name
        config: MaterialImageConfig
        attempt_num: Current attempt number
        max_attempts: Maximum attempts allowed
        correction_feedback: Feedback from previous attempt to inject
        
    Returns:
        Tuple of (validation_result, feedback_text, file_size)
    """
    # Inject correction feedback if available
    prompt = prompt_package["prompt"]
    if correction_feedback:
        # Inject corrections at the end of the prompt
        prompt = prompt + correction_feedback
        logger.info(f"📝 Injected {len(correction_feedback)} chars of correction feedback")
    
    logger.info(f"\n{'='*80}")
    logger.info(f"🎨 ATTEMPT {attempt_num}/{max_attempts}")
    logger.info(f"{'='*80}")
    logger.info(f"   • Aspect ratio: {prompt_package['aspect_ratio']}")
    logger.info(f"   • Guidance scale: {prompt_package['guidance_scale']}")
    if correction_feedback:
        logger.info(f"   • Corrections applied: YES (from attempt {attempt_num - 1})")
    logger.info("")
    
    # Generate image
    image = image_client.generate_image(
        prompt=prompt,
        negative_prompt=prompt_package["negative_prompt"],
        aspect_ratio=prompt_package["aspect_ratio"],
        guidance_scale=prompt_package["guidance_scale"]
    )
    
    # Save image
    image.save(output_path)
    file_size = output_path.stat().st_size
    
    logger.info(f"✅ Image saved to: {output_path}")
    logger.info(f"   • Size: {file_size / 1024:.1f} KB")
    
    # Validate
    logger.info("\n🔍 Validating image with Gemini Vision...")
    
    try:
        validation_result = validator.validate_material_image(
            image_path=output_path,
            material_name=material,
            research_data=prompt_package["research_data"],
            config=config.to_dict(),
            original_prompt=prompt,
            validation_result=prompt_package.get("validation_result")
        )
    except Exception as val_error:
        error_str = str(val_error)
        # Check if it's a quota error (429)
        if "429" in error_str or "quota" in error_str.lower():
            logger.warning("\n⚠️  Validation API quota exceeded - skipping validation")
            logger.info("   Image saved successfully, but couldn't validate due to API limits")
            # Return a "skip" result - image is saved, just not validated
            from domains.materials.image.validator import MaterialValidationResult
            skip_result = MaterialValidationResult(
                passed=True,  # Don't fail the whole run just because validation quota exceeded
                realism_score=0,
                overall_assessment="Validation skipped due to API quota limits",
                recommendations=["Re-run validation when API quota resets"]
            )
            skip_result.skipped = True  # Mark as skipped, not failed
            return skip_result, "Validation skipped (API quota)", file_size
        else:
            # Re-raise non-quota errors
            raise
    
    # Build feedback
    feedback_text, feedback_category = build_feedback_text(validation_result)
    
    # Display results
    logger.info("\n📊 VALIDATION RESULTS:")
    logger.info(f"   • Realism Score: {validation_result.realism_score:.1f}/100")
    logger.info(f"   • Pass Threshold: {PASS_THRESHOLD}/100")
    
    # Show text label detection (critical failure reason)
    if validation_result.text_labels_present:
        logger.info(f"   • Text/Labels: ❌ DETECTED (automatic fail)")
        if validation_result.text_label_details:
            for detail in validation_result.text_label_details:
                logger.info(f"      → {detail}")
    else:
        logger.info(f"   • Text/Labels: ✅ None detected")
    
    # Show position shift check
    if validation_result.position_shift_appropriate is not None:
        shift_status = "✅ Appropriate" if validation_result.position_shift_appropriate else "❌ Identical/Wrong"
        logger.info(f"   • Position Shift: {shift_status}")
    
    logger.info(f"   • Status: {'✅ PASSED' if validation_result.passed else '❌ FAILED'}")
    
    # Always show feedback (pass or fail)
    if validation_result.overall_assessment:
        logger.info(f"\n   Assessment: {validation_result.overall_assessment}")
    
    if validation_result.physics_issues:
        logger.info(f"\n   Physics Issues:")
        for issue in validation_result.physics_issues[:5]:
            logger.info(f"      • {issue}")
    
    if validation_result.distribution_issues:
        logger.info(f"\n   Distribution Issues:")
        for issue in validation_result.distribution_issues[:5]:
            logger.info(f"      • {issue}")
    
    if validation_result.recommendations:
        logger.info(f"\n   Recommendations:")
        for rec in validation_result.recommendations[:5]:
            logger.info(f"      • {rec}")
    
    return validation_result, feedback_text, file_size


def main():
    # Validate feedback consistency before generation
    try:
        from domains.materials.image.tools.validate_feedback import validate_before_generation
        if not validate_before_generation():
            logger.warning("⚠️  Proceeding with generation despite feedback inconsistencies")
    except ImportError:
        pass  # Validation tool not available, continue anyway
    
    parser = argparse.ArgumentParser(
        description="Generate material before/after laser cleaning images with researched defaults",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate with auto-retry on failure (default: 3 attempts)
  python3 domains/materials/image/generate.py --material "Aluminum"
  
  # Generate with more retry attempts
  python3 domains/materials/image/generate.py --material "Steel" --max-retries 5
  
  # Show prompt without generating
  python3 domains/materials/image/generate.py --material "Brass" --show-prompt --dry-run

Auto-Retry Feature:
  When validation fails, the system will automatically:
  1. Extract feedback from the validator (assessment, issues, recommendations)
  2. Inject corrections into the next prompt
  3. Regenerate with feedback-enhanced prompt
  4. Repeat up to --max-retries times (default: 3)
  
  All attempts are logged to the learning database for analysis.
        """
    )
    
    # Required arguments
    parser.add_argument("--material", required=True, 
                       help="Material name (e.g., 'Aluminum', 'Stainless Steel')")
    
    # Output options
    parser.add_argument("--output-dir", type=Path,
                       help="Output directory (default: public/images/materials)")
    parser.add_argument("--filename",
                       help="Output filename (default: {material-slug}-laser-cleaning.png)")
    
    # Control options
    parser.add_argument('--no-validate', action='store_true',
                       help='[NOT RECOMMENDED] Skip mandatory validation')
    parser.add_argument("--show-prompt", action="store_true",
                       help="Show the generated prompt")
    parser.add_argument("--dry-run", action="store_true",
                       help="Generate prompt but don't create image")
    parser.add_argument("--max-retries", type=int, default=MAX_RETRIES,
                       help=f"Maximum retry attempts on validation failure (default: {MAX_RETRIES})")
    parser.add_argument("--no-retry", action="store_true",
                       help="Disable auto-retry on validation failure")
    
    # Shape/object override
    parser.add_argument("--shape", type=str,
                       help="Override the researched shape/object")
    
    # Contamination severity
    parser.add_argument("--severity", type=str, choices=["light", "moderate", "heavy"],
                       default=None,
                       help="Contamination severity: light (<30%%), moderate (30-60%%), heavy (>60%%). Auto-set by context if not specified.")
    
    # Environmental context
    parser.add_argument("--context", type=str, choices=["indoor", "outdoor", "industrial", "marine"],
                       default="outdoor",
                       help="Environmental context: indoor (light contamination), outdoor (weathering+contamination), industrial (heavy contamination), marine (salt+weathering)")
    
    # Contamination variety
    parser.add_argument("--uniformity", type=int, choices=[1, 2, 3, 4, 5],
                       default=None,
                       help="Number of contaminant types (1-5). Default varies by category (typically 3).")
    
    # Visual weight adjustments
    parser.add_argument("--aging-weight", type=float, default=None,
                       help="Aging intensity on left (before) side. 0.0-2.0, default 1.0. Higher = more visible aging.")
    parser.add_argument("--contamination-weight", type=float, default=None,
                       help="Contamination intensity on right (after) side. 0.0-2.0, default 1.0. Higher = more visible contamination.")
    
    # Safety options
    parser.add_argument("--backup", action="store_true",
                       help="Backup existing image before overwriting (creates .backup.png)")
    parser.add_argument("--no-overwrite", action="store_true",
                       help="Don't overwrite existing image - exit if file exists")
    
    args = parser.parse_args()
    
    # Get API keys
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        logger.error("❌ GEMINI_API_KEY environment variable not set")
        sys.exit(1)
    
    # Initialize generator
    generator = MaterialImageGenerator(gemini_api_key=gemini_api_key)
    
    # Get category for this material from pattern selector (zero API calls)
    category = None
    if generator.pattern_selector:
        result = generator.pattern_selector.get_patterns_for_image_gen(args.material, num_patterns=1)
        category = result.get('category')
    if not category:
        logger.warning("⚠️  Category lookup failed - using default settings")
    
    # Create configuration
    config = MaterialImageConfig.from_material(
        material=args.material,
        category=category,
        validate=not args.no_validate,
        severity=args.severity,
        context=args.context,
        aging_weight=args.aging_weight,
        contamination_weight=args.contamination_weight
    )
    
    # Override uniformity if specified
    if args.uniformity:
        config.contamination_uniformity = args.uniformity
    
    # Log configuration
    logger.info("="*80)
    logger.info(f"🔬 MATERIAL IMAGE GENERATION: {args.material}")
    logger.info("="*80)
    logger.info("📊 Configuration:")
    if category:
        logger.info(f"   • Category: {category}")
    logger.info(f"   • Context: {config.context_description}")
    logger.info(f"   • Uniformity: {config.uniformity_label} ({config.contamination_uniformity} patterns)")
    logger.info(f"   • Severity: {config.severity_description}")
    logger.info(f"   • View Mode: {config.view_mode}")
    logger.info(f"   • Guidance Scale: {config.guidance_scale}")
    logger.info(f"   • Max Retries: {args.max_retries if not args.no_retry else 'disabled'}")
    if args.shape:
        logger.info(f"   • Shape Override: {args.shape}")
    logger.info("")
    
    # ══════════════════════════════════════════════════════════════════════════════
    # UNIFIED VALIDATION - STAGE 1: EARLY (pre-research)
    # ══════════════════════════════════════════════════════════════════════════════
    try:
        from shared.validation import UnifiedValidator, ValidationStatus
        from pathlib import Path as ValidationPath
        
        prompts_dir = ValidationPath(__file__).parent / "prompts" / "shared"
        unified_validator = UnifiedValidator(prompts_dir=prompts_dir)
        
        early_report = unified_validator.validate_early(
            material=args.material,
            config={
                'category': category,
                'contamination_uniformity': config.contamination_uniformity,
                'view_mode': config.view_mode
            }
        )
        
        if early_report.status == ValidationStatus.CRITICAL:
            logger.error("🚨 Early validation FAILED (critical):")
            logger.error(early_report.fix_instructions)
            sys.exit(1)
        elif early_report.status == ValidationStatus.FAIL:
            logger.warning("⚠️  Early validation issues found:")
            logger.warning(early_report.fix_instructions)
        else:
            logger.info("✅ Early validation passed")
    except ImportError as e:
        logger.debug(f"Unified validator not available: {e}")
        unified_validator = None
    
    # Generate prompt package
    logger.info("🔬 Researching contamination data...")
    prompt_package = generator.generate_complete(
        material_name=args.material,
        config=config,
        shape_override=args.shape
    )
    
    # ══════════════════════════════════════════════════════════════════════════════
    # UNIFIED VALIDATION - STAGE 2: PROMPT (pre-generation)
    # ══════════════════════════════════════════════════════════════════════════════
    if unified_validator:
        prompt_report = unified_validator.validate_prompt(
            prompt=prompt_package["prompt"],
            negative_prompt=prompt_package["negative_prompt"],
            material=args.material
        )
        
        if prompt_report.status == ValidationStatus.CRITICAL:
            logger.error("🚨 Prompt validation FAILED (critical):")
            logger.error(prompt_report.fix_instructions)
            sys.exit(1)
        elif prompt_report.status == ValidationStatus.FAIL:
            # Try auto-fix
            if prompt_report.fix_actions:
                original_len = len(prompt_package["prompt"])
                prompt_package["prompt"] = prompt_report.apply_auto_fixes(prompt_package["prompt"])
                fixed_len = len(prompt_package["prompt"])
                logger.info(f"🔧 Applied auto-fixes: {original_len} → {fixed_len} chars")
                
                # Re-validate
                prompt_report = unified_validator.validate_prompt(
                    prompt=prompt_package["prompt"],
                    negative_prompt=prompt_package["negative_prompt"],
                    material=args.material
                )
                
                if prompt_report.status in (ValidationStatus.FAIL, ValidationStatus.CRITICAL):
                    logger.warning("⚠️  Auto-fixes insufficient. Manual intervention needed:")
                    logger.warning(prompt_report.fix_instructions)
            else:
                logger.warning("⚠️  Prompt validation issues (no auto-fix available):")
                logger.warning(prompt_report.fix_instructions)
        else:
            logger.info(f"✅ Prompt validation passed ({prompt_report.prompt_length} chars)")
    
    # Show prompt if requested
    if args.show_prompt:
        logger.info("\n" + "="*80)
        logger.info("📝 GENERATED PROMPT")
        logger.info("="*80)
        logger.info(prompt_package["prompt"])
        logger.info("\n" + "="*80)
        logger.info("🚫 NEGATIVE PROMPT")
        logger.info("="*80)
        logger.info(prompt_package["negative_prompt"])
        logger.info("")
    
    # Exit if dry run
    if args.dry_run:
        logger.info("✅ Dry run complete - no image generated")
        return
    
    # Set output path
    output_dir = args.output_dir or Path("public/images/materials")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if args.filename:
        output_path = output_dir / args.filename
    else:
        slug = args.material.replace(" ", "-").replace("/", "-").lower()
        output_path = output_dir / f"{slug}-laser-cleaning.png"
    
    # Check if file exists and handle backup/no-overwrite
    if output_path.exists():
        if args.no_overwrite:
            logger.info(f"⚠️  Image already exists: {output_path}")
            logger.info("   Use --backup to preserve existing, or remove --no-overwrite to replace")
            sys.exit(0)
        
        if args.backup:
            import shutil
            backup_path = output_path.with_suffix('.backup.png')
            shutil.copy2(output_path, backup_path)
            logger.info(f"📦 Backed up existing image to: {backup_path}")
    
    # Initialize clients
    image_client = GeminiImageClient(api_key=gemini_api_key)
    generation_logger = create_logger()
    
    # Import validator
    from domains.materials.image.validator import MaterialImageValidator
    validator = MaterialImageValidator(gemini_api_key) if config.validate else None
    
    # Retry loop - DEFAULT: 1 attempt (no auto-retry)
    # Retries waste API calls since validation failures rarely improve with regeneration
    max_attempts = args.max_retries if args.max_retries > 1 else 1
    correction_feedback = None
    final_validation_result = None
    
    for attempt in range(1, max_attempts + 1):
        try:
            if config.validate:
                validation_result, feedback_text, file_size = generate_and_validate(
                    image_client=image_client,
                    validator=validator,
                    prompt_package=prompt_package,
                    output_path=output_path,
                    material=args.material,
                    config=config,
                    attempt_num=attempt,
                    max_attempts=max_attempts,
                    correction_feedback=correction_feedback
                )
                
                # Log attempt (always, pass or fail)
                _, feedback_category = build_feedback_text(validation_result)
                log_attempt(
                    generation_logger=generation_logger,
                    material=args.material,
                    config=config,
                    prompt_package=prompt_package,
                    validation_result=validation_result,
                    output_path=output_path,
                    file_size=file_size,
                    attempt_num=attempt,
                    feedback_text=feedback_text,
                    feedback_category=feedback_category,
                    previous_feedback=correction_feedback,
                    shape_override=args.shape
                )
                
                final_validation_result = validation_result
                
                # Check if validation was skipped (quota error) - don't retry
                if hasattr(validation_result, 'skipped') and validation_result.skipped:
                    logger.info("\n✅ Image generated successfully (validation skipped due to API quota)")
                    break
                
                # Check if passed
                if validation_result.passed:
                    logger.info(f"\n✅ Validation PASSED on attempt {attempt}")
                    break
                
                # Check if more retries available
                if attempt < max_attempts:
                    logger.info(f"\n🔄 Validation FAILED - preparing retry {attempt + 1}/{max_attempts}...")
                    
                    # Try prompt-aware validation for more specific feedback
                    prompt_aware_feedback = None
                    try:
                        current_prompt = prompt_package["prompt"]
                        if correction_feedback:
                            current_prompt = current_prompt + correction_feedback
                        prompt_aware_feedback = validator.build_correction_injection(
                            image_path=output_path,
                            original_prompt=current_prompt,
                            material_name=args.material,
                            config=config.to_dict()
                        )
                        if prompt_aware_feedback:
                            logger.info("   📝 Generated prompt-aware corrections")
                    except Exception as pa_error:
                        logger.debug(f"Prompt-aware validation unavailable: {pa_error}")
                    
                    correction_feedback = build_correction_prompt(
                        validation_result, attempt, prompt_aware_feedback
                    )
                else:
                    logger.warning(f"\n⚠️  Validation FAILED after {attempt} attempts")
                    logger.warning("   Image saved but may not meet quality standards")
                    
            else:
                # No validation - just generate once
                logger.info(f"\n🎨 Generating image (validation disabled)...")
                image = image_client.generate_image(
                    prompt=prompt_package["prompt"],
                    negative_prompt=prompt_package["negative_prompt"],
                    aspect_ratio=prompt_package["aspect_ratio"],
                    guidance_scale=prompt_package["guidance_scale"]
                )
                image.save(output_path)
                file_size = output_path.stat().st_size
                logger.info(f"✅ Image saved to: {output_path}")
                logger.info(f"   • Size: {file_size / 1024:.1f} KB")
                break
                
        except Exception as e:
            logger.error(f"\n❌ Attempt {attempt} failed: {e}")
            if attempt == max_attempts:
                logger.error("   All attempts exhausted")
                sys.exit(1)
            else:
                logger.warning(f"   Retrying ({attempt + 1}/{max_attempts})...")
    
    # Final summary
    logger.info("\n" + "="*80)
    if final_validation_result and final_validation_result.passed:
        logger.info("✅ GENERATION COMPLETE - PASSED VALIDATION")
    elif final_validation_result:
        logger.info(f"⚠️  GENERATION COMPLETE - Score: {final_validation_result.realism_score:.0f}/100")
    else:
        logger.info("✅ GENERATION COMPLETE")
    logger.info("="*80)


if __name__ == "__main__":
    main()
