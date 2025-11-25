#!/usr/bin/env python3
"""
Material Image Generator CLI

Generate before/after laser cleaning images with researched contamination defaults.

Usage:
    python3 domains/materials/image/generate.py --material "Aluminum"
    python3 domains/materials/image/generate.py --material "Stainless Steel" --validate
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from domains.materials.image.material_generator import MaterialImageGenerator
from domains.materials.image.material_config import MaterialImageConfig
from shared.api.gemini_image_client import GeminiImageClient
from domains.materials.image.learning import create_logger

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Generate material before/after laser cleaning images with researched defaults",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate with researched defaults (automatic category detection)
  python3 domains/materials/image/generate.py --material "Aluminum"
  
  # Generate with validation
  python3 domains/materials/image/generate.py --material "Steel" --validate
  
  # Show prompt without generating
  python3 domains/materials/image/generate.py --material "Brass" --show-prompt --dry-run

Researched Defaults:
  All contamination settings are automatically determined based on material category.
  - Metals (ferrous): 3 pattern types (rust, oil, dirt)
  - Metals (non-ferrous): 3 pattern types (oxidation, grime, fingerprints)
  - Ceramics: 2-4 pattern types based on material
  - Polymers: 2-3 pattern types (residue, oils, dirt)
  - Wood: 3 pattern types (dirt, oils, mold)
  - Composites: 3 pattern types (resin, dust, oils)
  
  All images use Contextual view (3D perspective in realistic environment).
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
                       help='[NOT RECOMMENDED] Skip mandatory validation (validation is required by default)')
    parser.add_argument("--show-prompt", action="store_true",
                       help="Show the generated prompt")
    parser.add_argument("--dry-run", action="store_true",
                       help="Generate prompt but don't create image")
    
    args = parser.parse_args()
    
    # Get API keys
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        logger.error("❌ GEMINI_API_KEY environment variable not set")
        sys.exit(1)
    
    # Initialize generator to get category
    generator = MaterialImageGenerator(gemini_api_key=gemini_api_key)
    
    # Get category for this material
    if generator.category_researcher:
        category = generator.category_researcher.get_category(args.material)
    else:
        category = None
        logger.warning("⚠️  Category research unavailable - using default settings")
    
    # Create configuration with researched defaults
    # Validation is MANDATORY by default (use --no-validate to disable)
    config = MaterialImageConfig.from_material(
        material=args.material,
        category=category,
        validate=not args.no_validate  # Inverted: True unless explicitly disabled
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
    logger.info("")
    
    # Generate complete prompt package
    logger.info("🔬 Researching contamination data...")
    prompt_package = generator.generate_complete(
        material_name=args.material,
        config=config
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
    if args.output_dir:
        output_dir = args.output_dir
    else:
        # Use public/images/materials directory (not material-specific subdirs)
        output_dir = Path("public/images/materials")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if args.filename:
        output_path = output_dir / args.filename
    else:
        # Use same naming as frontmatter: {material-slug}-laser-cleaning.png
        slug = args.material.replace(" ", "-").replace("/", "-").lower()
        output_path = output_dir / f"{slug}-laser-cleaning.png"
    
    # Generate image
    logger.info(f"🎨 Generating image with Imagen 4...")
    logger.info(f"   • Aspect ratio: {prompt_package['aspect_ratio']}")
    logger.info(f"   • Guidance scale: {prompt_package['guidance_scale']}")
    logger.info("")
    
    # Initialize Gemini Image client
    image_client = GeminiImageClient(api_key=gemini_api_key)
    
    try:
        # Generate image (returns PIL Image object)
        image = image_client.generate_image(
            prompt=prompt_package["prompt"],
            negative_prompt=prompt_package["negative_prompt"],
            aspect_ratio=prompt_package["aspect_ratio"],
            guidance_scale=prompt_package["guidance_scale"]
        )
        
        # Save PIL Image directly
        image.save(output_path)
        
        # Get file size for reporting
        from pathlib import Path as PathLib
        file_size = PathLib(output_path).stat().st_size
        
        logger.info(f"✅ Image saved to: {output_path}")
        logger.info(f"   • Size: {file_size / 1024:.1f} KB")
        
        # Validate if enabled (mandatory by default)
        if config.validate:
            logger.info("\n🔍 Validating image with Gemini Vision...")
            
            try:
                from domains.materials.image.validator import MaterialImageValidator
                
                validator = MaterialImageValidator(gemini_api_key)
                validation_result = validator.validate_material_image(
                    image_path=output_path,
                    material_name=args.material,
                    research_data=prompt_package["research_data"],
                    config=config.to_dict()
                )
                
                logger.info("\n📊 VALIDATION RESULTS:")
                logger.info(f"   • Realism Score: {validation_result.realism_score:.1f}/100")
                logger.info("   • Pass Threshold: 75.0/100")
                logger.info(f"   • Status: {'✅ PASSED' if validation_result.passed else '❌ FAILED'}")
                
                # Log to learning database
                try:
                    generation_logger = create_logger()
                    generation_logger.log_attempt(
                        material=args.material,
                        category=config.category,
                        generation_params={
                            'prompt_length': len(prompt_package['prompt']),
                            'guidance_scale': prompt_package['guidance_scale'],
                            'contamination_uniformity': config.contamination_uniformity,
                            'view_mode': config.view_mode,
                            'patterns_used': [p.get('pattern_name', p.get('name', 'Unknown')) 
                                            for p in prompt_package['research_data'].get('selected_patterns', 
                                            prompt_package['research_data'].get('contaminants', []))[:3]],
                            'feedback_applied': True  # Always true now since feedback is always loaded
                        },
                        validation_results={
                            'prompt_length': 0,  # Validation prompt length tracking added separately
                            'truncated': False,  # Emergency truncation tracking
                            'realism_score': int(validation_result.realism_score) if validation_result.realism_score else 0,
                            'passed': validation_result.passed,
                            'physics_issues': validation_result.physics_issues if validation_result.physics_issues else [],
                            'red_flags': []  # Red flags tracked in future enhancement
                        },
                        outcome={
                            'failure_category': 'physics' if (validation_result.physics_issues and len(validation_result.physics_issues) > 0) else None,
                            'retry_count': 0,
                            'final_success': validation_result.passed
                        },
                        image_metadata={
                            'path': str(output_path),
                            'size_kb': file_size / 1024
                        }
                    )
                except Exception as log_error:
                    logger.debug(f"Failed to log to learning database: {log_error}")
                
                if not validation_result.passed:
                    logger.warning("\n⚠️  Image failed validation:")
                    if validation_result.physics_issues:
                        logger.warning(f"   • Physics issues: {', '.join(validation_result.physics_issues[:3])}")
                    if validation_result.distribution_issues:
                        logger.warning(f"   • Distribution issues: {', '.join(validation_result.distribution_issues[:3])}")
                    logger.warning("\n   Consider regenerating with adjusted parameters.")
            except Exception as validation_error:
                logger.error(f"\n❌ Validation failed: {validation_error}")
                logger.warning("   Image was generated but validation could not be completed")
                logger.warning("   Use --no-validate flag to skip validation if needed")
        
        logger.info("\n" + "="*80)
        logger.info("✅ GENERATION COMPLETE")
        logger.info("="*80)
        
    except Exception as e:
        logger.error(f"\n❌ Generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
