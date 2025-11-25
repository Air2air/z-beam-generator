#!/usr/bin/env python3
"""
Material Image Generator CLI

Generate before/after laser cleaning images with contamination research.

Usage:
    python3 domains/materials/image/generate.py --material "Aluminum"
    python3 domains/materials/image/generate.py --material "Stainless Steel" --contamination-level 4 --uniformity 3
    python3 domains/materials/image/generate.py --material "Copper" --view-mode Isolated --validate
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
from domains.materials.image.contamination_levels import (
    CONTAMINATION_LEVELS, UNIFORMITY_LEVELS, VIEW_MODES
)
from shared.api.gemini_image_client import GeminiImageClient

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Generate material before/after laser cleaning images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic generation with defaults (Level 3, Uniformity 3, Contextual view)
  python3 domains/materials/image/generate.py --material "Aluminum"
  
  # Heavy contamination with diverse types
  python3 domains/materials/image/generate.py --material "Steel" --contamination-level 4 --uniformity 5
  
  # Light contamination, isolated technical view
  python3 domains/materials/image/generate.py --material "Copper" --contamination-level 2 --uniformity 2 --view-mode Isolated
  
  # With validation
  python3 domains/materials/image/generate.py --material "Titanium" --validate
  
  # Show prompt without generating
  python3 domains/materials/image/generate.py --material "Brass" --show-prompt --dry-run

Contamination Levels (1-5):
  1 = Minimal (light dust, <20% coverage)
  2 = Light (20-40% coverage)
  3 = Moderate (40-60% coverage, typical real-world)
  4 = Heavy (60-80% coverage)
  5 = Severe (80-95% coverage)

Uniformity Levels (1-5):
  1 = Single contaminant type
  2 = Two types
  3 = Three types
  4 = Four types
  5 = Diverse (4+ types)

View Modes:
  Contextual = 3D perspective in realistic environment (default)
  Isolated = 2D technical documentation view
        """
    )
    
    # Required arguments
    parser.add_argument("--material", required=True, 
                       help="Material name (e.g., 'Aluminum', 'Stainless Steel')")
    
    # Configuration options
    parser.add_argument("--contamination-level", type=int, choices=[1,2,3,4,5], default=3,
                       help="Contamination intensity 1-5 (default: 3)")
    parser.add_argument("--uniformity", type=int, choices=[1,2,3,4,5], default=3,
                       help="Contamination variety 1-5 (default: 3)")
    parser.add_argument("--view-mode", choices=["Contextual", "Isolated"], default="Contextual",
                       help="View mode (default: Contextual)")
    parser.add_argument("--environment-wear", type=int, choices=[1,2,3,4,5], default=3,
                       help="Background aging 1-5 (default: 3)")
    
    # Output options
    parser.add_argument("--output-dir", type=Path,
                       help="Output directory (default: public/images/materials)")
    parser.add_argument("--filename",
                       help="Output filename (default: {material-slug}-laser-cleaning.png)")
    
    # Control options
    parser.add_argument("--validate", action="store_true",
                       help="Validate generated image with Gemini Vision")
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
    
    # Create configuration
    config = MaterialImageConfig(
        material=args.material,
        contamination_level=args.contamination_level,
        contamination_uniformity=args.uniformity,
        view_mode=args.view_mode,
        environment_wear=args.environment_wear,
        validate=args.validate
    )
    
    # Log configuration
    logger.info("="*80)
    logger.info(f"🔬 MATERIAL IMAGE GENERATION: {args.material}")
    logger.info("="*80)
    logger.info(f"📊 Configuration:")
    logger.info(f"   • Contamination: {config.contamination_intensity_label} (Level {config.contamination_level})")
    logger.info(f"   • Uniformity: {config.uniformity_label} (Level {config.contamination_uniformity})")
    logger.info(f"   • View Mode: {config.view_mode}")
    logger.info(f"   • Environment Wear: {config.environment_wear}/5")
    logger.info("")
    
    # Initialize generator
    generator = MaterialImageGenerator(gemini_api_key=gemini_api_key)
    
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
        
        # Validate if requested
        if args.validate:
            logger.info("\n🔍 Validating image with Gemini Vision...")
            # TODO: Implement validation with validator.py
            logger.info("⚠️  Validation not yet implemented")
        
        logger.info("\n" + "="*80)
        logger.info("✅ GENERATION COMPLETE")
        logger.info("="*80)
        
    except Exception as e:
        logger.error(f"\n❌ Generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
