#!/usr/bin/env python3
"""
Material Image Generator CLI

Command-line interface for material image generation.
Thin wrapper around pipeline.py - handles arguments and output formatting.

Usage:
    python3 domains/materials/image/cli.py --material "Aluminum"
    python3 domains/materials/image/cli.py --material "Stainless Steel" --show-prompt
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from domains.materials.image.material_config import MaterialImageConfig
from domains.materials.image.pipeline import GenerationResult, ImageGenerationPipeline

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate material before/after laser cleaning images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 domains/materials/image/cli.py --material "Aluminum"
  python3 domains/materials/image/cli.py --material "Brass" --show-prompt --dry-run
        """
    )
    
    # Required arguments
    parser.add_argument("--material", required=True, 
                       help="Material name (e.g., 'Aluminum', 'Stainless Steel')")
    
    # Output options
    parser.add_argument("--output-dir", type=Path,
                       help="Output directory (default: public/images/materials)")
    parser.add_argument("--filename",
                       help="Output filename (default: {material-slug}-laser-cleaning-hero.png)")
    
    # Control options
    parser.add_argument('--no-validate', action='store_true',
                       help='[NOT RECOMMENDED] Skip mandatory validation')
    parser.add_argument("--show-prompt", action="store_true",
                       help="Show the generated prompt")
    parser.add_argument("--dry-run", action="store_true",
                       help="Generate prompt but don't create image")

    # Shape/object override
    parser.add_argument("--shape", type=str,
                       help="Override the researched shape/object")
    
    # Contamination severity
    parser.add_argument("--severity", type=str, choices=["light", "moderate", "heavy"],
                       default=None,
                       help="Contamination severity (auto-set by context if not specified)")
    
    # Environmental context
    parser.add_argument("--context", type=str, 
                       choices=["indoor", "outdoor", "industrial", "marine", "laboratory"],
                       default="outdoor",
                       help="Environmental context")
    
    # Contamination variety
    parser.add_argument("--uniformity", type=int, choices=[1, 2, 3, 4, 5],
                       default=None,
                       help="Number of contaminant types (1-5)")
    
    # Visual weight adjustments
    parser.add_argument("--aging-weight", type=float, default=None,
                       help="Aging intensity (0.0-2.0)")
    parser.add_argument("--contamination-weight", type=float, default=None,
                       help="Contamination intensity (0.0-2.0)")
    
    # Safety options
    parser.add_argument("--backup", action="store_true",
                       help="Backup existing image before overwriting")
    parser.add_argument("--no-overwrite", action="store_true",
                       help="Don't overwrite existing image")
    
    # Model selection
    parser.add_argument("--use-flash", action="store_true",
                       help="Use Gemini 2.0 Flash instead of Imagen (faster, more available)")
    
    # Validation options
    parser.add_argument("--skip-validation", action="store_true",
                       help="Skip Gemini vision validation (useful for testing)")
    
    return parser.parse_args()


def main():
    """Main CLI entry point."""
    args = parse_args()
    
    # Check API key
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        logger.error("❌ GEMINI_API_KEY environment variable not set")
        sys.exit(1)
    
    # Initialize pipeline (with optional Gemini Flash)
    pipeline = ImageGenerationPipeline(
        gemini_api_key=gemini_api_key,
        use_flash=args.use_flash
    )
    
    # Get category for this material
    category = pipeline.get_material_category(args.material)
    
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
    
    # Set output path
    output_dir = args.output_dir or Path("public/images/materials")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if args.filename:
        output_path = output_dir / args.filename
    else:
        # Generate safe slug: lowercase, replace spaces/slashes with hyphens, strip parentheses
        slug = args.material.lower()
        slug = slug.replace(" ", "-").replace("/", "-")
        slug = slug.replace("(", "").replace(")", "")  # Strip parentheses
        slug = "-".join(part for part in slug.split("-") if part)  # Remove empty parts/double hyphens
        output_path = output_dir / f"{slug}-laser-cleaning-hero.png"
    
    # Handle existing file
    if output_path.exists():
        if args.no_overwrite:
            logger.info(f"⚠️  Image already exists: {output_path}")
            sys.exit(0)
        if args.backup:
            import shutil
            backup_path = output_path.with_suffix('.backup.png')
            shutil.copy2(output_path, backup_path)
            logger.info(f"📦 Backed up existing image to: {backup_path}")
    
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
    if args.shape:
        logger.info(f"   • Shape Override: {args.shape}")
    logger.info("")
    
    # Run pipeline
    result: GenerationResult = pipeline.generate(
        material=args.material,
        config=config,
        output_path=output_path,
        shape_override=args.shape,
        show_prompt=args.show_prompt,
        dry_run=args.dry_run,
        skip_validation=args.skip_validation
    )
    
    # Final summary
    logger.info("\n" + "="*80)
    if result.passed:
        logger.info("✅ GENERATION COMPLETE - PASSED VALIDATION")
    elif result.validation_result:
        logger.info(f"⚠️  GENERATION COMPLETE - Score: {result.validation_result.realism_score:.0f}/100")
    else:
        logger.info("✅ GENERATION COMPLETE")
    logger.info("="*80)
    
    # Exit with appropriate code
    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
