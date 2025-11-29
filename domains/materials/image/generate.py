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
from domains.materials.image.learning import create_logger

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Constants
MAX_RETRIES = 3
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
    previous_feedback: Optional[str] = None
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
        
        generation_logger.log_attempt(
            material=material,
            category=config.category,
            generation_params={
                'prompt_length': len(prompt_package['prompt']),
                'guidance_scale': prompt_package['guidance_scale'],
                'contamination_uniformity': config.contamination_uniformity,
                'view_mode': config.view_mode,
                'patterns_used': [p.get('pattern_name', p.get('name', 'Unknown')) 
                                for p in prompt_package['research_data'].get('selected_patterns', 
                                prompt_package['research_data'].get('contaminants', []))[:3]],
                'feedback_applied': previous_feedback is not None,
                'previous_feedback': previous_feedback,  # Feedback from previous attempt
                'feedback_text': feedback_text,  # Validator feedback for learning
                'feedback_category': feedback_category,
                'feedback_source': 'automated',
                'attempt_number': attempt_num,
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
    
    validation_result = validator.validate_material_image(
        image_path=output_path,
        material_name=material,
        research_data=prompt_package["research_data"],
        config=config.to_dict(),
        original_prompt=prompt,
        validation_result=prompt_package.get("validation_result")
    )
    
    # Build feedback
    feedback_text, feedback_category = build_feedback_text(validation_result)
    
    # Display results
    logger.info("\n📊 VALIDATION RESULTS:")
    logger.info(f"   • Realism Score: {validation_result.realism_score:.1f}/100")
    logger.info(f"   • Pass Threshold: {PASS_THRESHOLD}/100")
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
    
    args = parser.parse_args()
    
    # Get API keys
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        logger.error("❌ GEMINI_API_KEY environment variable not set")
        sys.exit(1)
    
    # Initialize generator
    generator = MaterialImageGenerator(gemini_api_key=gemini_api_key)
    
    # Get category for this material
    category = None
    if generator.category_researcher:
        category = generator.category_researcher.get_category(args.material)
    else:
        logger.warning("⚠️  Category research unavailable - using default settings")
    
    # Create configuration
    config = MaterialImageConfig.from_material(
        material=args.material,
        category=category,
        validate=not args.no_validate
    )
    
    # Log configuration
    logger.info("="*80)
    logger.info(f"🔬 MATERIAL IMAGE GENERATION: {args.material}")
    logger.info("="*80)
    logger.info("📊 Configuration:")
    if category:
        logger.info(f"   • Category: {category}")
    logger.info(f"   • Uniformity: {config.uniformity_label} ({config.contamination_uniformity} patterns)")
    logger.info(f"   • View Mode: {config.view_mode}")
    logger.info(f"   • Guidance Scale: {config.guidance_scale}")
    logger.info(f"   • Max Retries: {args.max_retries if not args.no_retry else 'disabled'}")
    if args.shape:
        logger.info(f"   • Shape Override: {args.shape}")
    logger.info("")
    
    # Generate prompt package
    logger.info("🔬 Researching contamination data...")
    prompt_package = generator.generate_complete(
        material_name=args.material,
        config=config,
        shape_override=args.shape
    )
    
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
    
    # Initialize clients
    image_client = GeminiImageClient(api_key=gemini_api_key)
    generation_logger = create_logger()
    
    # Import validator
    from domains.materials.image.validator import MaterialImageValidator
    validator = MaterialImageValidator(gemini_api_key) if config.validate else None
    
    # Retry loop
    max_attempts = 1 if args.no_retry or not config.validate else args.max_retries
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
                    previous_feedback=correction_feedback
                )
                
                final_validation_result = validation_result
                
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
