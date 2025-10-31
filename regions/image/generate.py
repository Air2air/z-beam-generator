#!/usr/bin/env python3
"""
City Image Generator CLI

Generate historical city images with population research and configurable aging.

Usage:
    python3 regions/image/generate.py --city "Belmont" --county "San Mateo County"
    python3 regions/image/generate.py --city "Oakland" --county "Alameda County" --preset "aged_1930s"
    python3 regions/image/generate.py --city "San Jose" --year 1945 --photo-condition 3 --scenery-condition 4
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from regions.image.city_generator import CityImageGenerator
from regions.image.presets import get_config, PRESET_CONFIGS
from shared.api.gemini_image_client import GeminiImageClient

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Generate historical city images with population research",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use preset configuration
  python3 regions/image/generate.py --city "Belmont" --county "San Mateo County" --preset "aged_1930s"
  
  # Custom configuration
  python3 regions/image/generate.py --city "Oakland" --county "Alameda County" --year 1935 --photo-condition 4 --scenery-condition 3
  
  # Focus on specific subject
  python3 regions/image/generate.py --city "San Francisco" --county "San Francisco County" --preset "aged_1930s" --subject "harbor"
  python3 regions/image/generate.py --city "Oakland" --county "Alameda County" --year 1925 --photo-condition 2 --subject "barber shop"
  
  # Quick generation with defaults
  python3 regions/image/generate.py --city "San Jose" --county "Santa Clara County"

Available presets:
  pristine_1920s, light_1930s, moderate_1930s, aged_1930s, heavily_aged_1930s, moderate_1940s, aged_1950s
  
Subject examples:
  harbor, barber shop, train station, factory, pharmacy, bakery, hotel, saloon, bank, post office
        """
    )
    
    # Required arguments
    parser.add_argument("--city", required=True, help="City name (e.g., 'Belmont')")
    parser.add_argument("--county", required=True, help="County name (e.g., 'San Mateo County')")
    
    # Configuration options
    config_group = parser.add_mutually_exclusive_group()
    config_group.add_argument("--preset", choices=list(PRESET_CONFIGS.keys()),
                            help="Use preset configuration")
    
    # Custom configuration
    parser.add_argument("--year", type=int, help="Year (e.g., 1935)")
    parser.add_argument("--photo-condition", type=int, choices=[1,2,3,4,5],
                       help="Photo aging level 1-5 (1=heavily aged, 5=pristine)")
    parser.add_argument("--scenery-condition", type=int, choices=[1,2,3,4,5],
                       help="Scenery wear level 1-5 (1=heavily worn, 5=pristine)")
    
    # Subject focus
    parser.add_argument("--subject", type=str,
                       help="Optional subject to focus on (e.g., 'harbor', 'barber shop', 'train station')")
    
    # Output options
    parser.add_argument("--output-dir", type=Path,
                       help="Output directory (default: public/images/regions/{city})")
    parser.add_argument("--filename", help="Output filename (default: {city}_historical.png)")
    
    # Display options
    parser.add_argument("--show-prompt", action="store_true",
                       help="Display the generated prompt")
    parser.add_argument("--dry-run", action="store_true",
                       help="Generate prompt but don't create image")
    
    args = parser.parse_args()
    
    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("❌ GEMINI_API_KEY not set in environment")
        logger.info("\nSet it with:")
        logger.info("  export GEMINI_API_KEY='your-key-here'")
        return 1
    
    # Display header
    print("=" * 70)
    print(f"🎨 City Image Generation: {args.city}, {args.county}")
    print("=" * 70)
    
    # Get configuration
    if args.preset:
        config = get_config(city=args.city, preset_name=args.preset)
    elif args.year or args.photo_condition or args.scenery_condition:
        config = get_config(
            city=args.city,
            year=args.year,
            photo_condition=args.photo_condition,
            scenery_condition=args.scenery_condition
        )
    else:
        # Default to aged_1930s
        config = get_config(city=args.city, preset_name="aged_1930s")
    
    # Display configuration
    print(f"\n🏙️  City: {config.city}")
    print(f"📅 Era: {config.year} ({config.get_decade()})")
    print(f"📸 Photo Condition: {config.photo_condition}/5")
    print(f"🏢 Scenery Condition: {config.scenery_condition}/5")
    if args.subject:
        print(f"🎯 Subject: {args.subject}")
    
    # Initialize generator
    print("\n🚀 Initializing city image generator...")
    try:
        city_gen = CityImageGenerator(gemini_api_key=api_key)
        if not args.dry_run:
            image_client = GeminiImageClient(api_key=api_key)
    except Exception as e:
        logger.error(f"❌ Error initializing: {e}")
        return 1
    
    # Generate prompt
    print("\n📝 Generating prompt with population research...")
    try:
        package = city_gen.generate_complete(
            city_name=config.city,
            county_name=args.county,
            decade=config.get_decade(),
            config=config,
            subject=args.subject
        )
    except Exception as e:
        logger.error(f"❌ Error generating prompt: {e}")
        return 1
    
    # Display prompt if requested
    if args.show_prompt or args.dry_run:
        print("\n" + "=" * 70)
        print("📸 GENERATED PROMPT:")
        print("=" * 70)
        print(package["prompt"])
        print("\n" + "=" * 70)
        print("🚫 NEGATIVE PROMPT:")
        print("=" * 70)
        print(package["negative_prompt"])
        print("\n" + "=" * 70)
        print("⚙️  GENERATION PARAMETERS:")
        print("=" * 70)
        print(f"Aspect Ratio: {package['aspect_ratio']}")
        print(f"Guidance Scale: {package['guidance_scale']}")
        print(f"Safety Filter: {package['safety_filter_level']}")
    
    if args.dry_run:
        print("\n🔍 Dry run complete - no image generated")
        return 0
    
    # Set output directory and filename
    if args.output_dir:
        output_dir = args.output_dir
    else:
        safe_name = config.city.lower().replace(" ", "_").replace(",", "")
        output_dir = Path(f"public/images/regions/{safe_name}")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if args.filename:
        output_path = output_dir / args.filename
    else:
        safe_name = config.city.lower().replace(" ", "_").replace(",", "")
        output_path = output_dir / f"{safe_name}_historical.png"
    
    # Generate image
    print("\n🎨 Generating image...")
    print("⏳ This may take 5-10 seconds...")
    
    try:
        image_client.generate_image(
            package["prompt"],
            output_path=output_path,
            negative_prompt=package["negative_prompt"],
            aspect_ratio=package["aspect_ratio"],
            guidance_scale=package["guidance_scale"],
            safety_filter_level=package["safety_filter_level"]
        )
        print(f"✅ Image saved: {output_path}")
        print("\n💰 Cost: $0.04")
    except Exception as e:
        logger.error(f"❌ Error generating image: {e}")
        return 1
    
    print("\n" + "=" * 70)
    print("✅ COMPLETE!")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
