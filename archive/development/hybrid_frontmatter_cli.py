#!/usr/bin/env python3
"""
Command-line interface for hybrid frontmatter generation

Provides easy access to different generation modes:
- --mode data-only: Refresh non-text data from Materials.yaml (no AI cost)
- --mode text-only: Update text fields with Grok AI (medium cost)
- --mode hybrid: Data + AI text generation (recommended)
- --mode full: Complete AI generation with DeepSeek (highest cost)

Examples:
    python3 hybrid_frontmatter_cli.py --material Aluminum --mode hybrid
    python3 hybrid_frontmatter_cli.py --material Steel --mode data-only
    python3 hybrid_frontmatter_cli.py --all --mode text-only --force-refresh
"""

import argparse
import sys
import logging
from pathlib import Path
import yaml


# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from components.frontmatter.core.hybrid_generation_manager import HybridFrontmatterManager, GenerationMode
from api.client_factory import get_api_client_for_component
from data.materials import load_materials_cached

def setup_logging(verbose: bool = False) -> logging.Logger:
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def get_api_clients(mode: GenerationMode):
    """Get appropriate API clients for the generation mode"""
    text_client = None
    full_client = None
    
    if mode in [GenerationMode.TEXT_ONLY, GenerationMode.HYBRID]:
        # Need Grok for text generation
        try:
            text_client = get_api_client_for_component("caption")  # Caption uses Grok
        except Exception as e:
            print(f"❌ Failed to initialize Grok API client: {e}")
            print("   Text generation will be skipped")
    
    if mode == GenerationMode.FULL:
        # Need DeepSeek for full generation
        try:
            full_client = get_api_client_for_component("frontmatter")  # Frontmatter uses DeepSeek
        except Exception as e:
            print(f"❌ Failed to initialize DeepSeek API client: {e}")
            return None, None
    
    return text_client, full_client

def generate_single_material(
    material_name: str,
    mode: GenerationMode,
    manager: HybridFrontmatterManager,
    text_client,
    full_client,
    force_refresh: bool = False,
    dry_run: bool = False
) -> bool:
    """Generate frontmatter for a single material"""
    
    logger = logging.getLogger(__name__)
    logger.info(f"🔄 Generating frontmatter for {material_name} in {mode.value} mode")
    
    try:
        # Get existing frontmatter if it exists
        existing_frontmatter = None
        frontmatter_path = Path(f"content/frontmatter/{material_name.lower().replace(' ', '-')}-laser-cleaning.yaml")
        
        if frontmatter_path.exists():
            try:
                with open(frontmatter_path) as f:
                    existing_frontmatter = yaml.safe_load(f)
                logger.debug(f"Loaded existing frontmatter with {len(existing_frontmatter)} fields")
            except Exception as e:
                logger.warning(f"Could not load existing frontmatter: {e}")
        
        # Generate frontmatter
        result = manager.generate_frontmatter(
            material_name=material_name,
            mode=mode,
            text_api_client=text_client,
            full_api_client=full_client,
            existing_frontmatter=existing_frontmatter,
            force_refresh=force_refresh
        )
        
        if dry_run:
            logger.info("🔍 Dry run - would generate:")
            logger.info(f"   Fields: {len(result)}")
            return True
        
        # Save result
        frontmatter_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save frontmatter without metadata
        
        with open(frontmatter_path, 'w') as f:
            yaml.dump(result, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"✅ Successfully generated frontmatter for {material_name}")
        logger.info(f"   Saved to: {frontmatter_path}")
        logger.info(f"   Fields: {len(result)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to generate frontmatter for {material_name}: {e}")
        return False

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Hybrid Frontmatter Generation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Generation Modes:
  data-only  : Refresh non-text data from Materials.yaml (fast, no AI cost)
  text-only  : Update text fields with Grok AI (medium speed/cost)
  hybrid     : Data from Materials.yaml + Grok text generation (recommended)
  full       : Complete AI generation with DeepSeek (slow, high cost)

Examples:
  %(prog)s --material Aluminum --mode hybrid
  %(prog)s --material Steel --mode data-only
  %(prog)s --all --mode text-only --force-refresh
  %(prog)s --material Titanium --mode hybrid --dry-run
        """
    )
    
    # Material selection
    material_group = parser.add_mutually_exclusive_group(required=True)
    material_group.add_argument(
        "--material", "-m",
        type=str,
        help="Generate frontmatter for specific material"
    )
    material_group.add_argument(
        "--all", "-a",
        action="store_true",
        help="Generate frontmatter for all materials"
    )
    
    # Generation mode
    parser.add_argument(
        "--mode",
        type=str,
        choices=["data-only", "text-only", "hybrid", "full"],
        default="hybrid",
        help="Generation mode (default: hybrid)"
    )
    
    # Options
    parser.add_argument(
        "--force-refresh", "-f",
        action="store_true",
        help="Force regeneration of existing fields"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be generated without actually generating"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--recommendations", "-r",
        action="store_true",
        help="Show generation mode recommendations for materials"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.verbose)
    
    # Convert mode string to enum
    mode_map = {
        "data-only": GenerationMode.DATA_ONLY,
        "text-only": GenerationMode.TEXT_ONLY,
        "hybrid": GenerationMode.HYBRID,
        "full": GenerationMode.FULL
    }
    mode = mode_map[args.mode]
    
    # Create manager
    manager = HybridFrontmatterManager(logger)
    
    # Get materials list
    if args.all:
        try:
            materials_data = load_materials_cached()
            # Get actual materials from the 'materials' section
            if 'materials' in materials_data:
                materials = list(materials_data['materials'].keys())
            else:
                materials = list(materials_data.keys())
            logger.info(f"Found {len(materials)} materials for batch generation")
        except Exception as e:
            logger.error(f"Failed to load materials list: {e}")
            return 1
    else:
        materials = [args.material]
    
    # Show recommendations if requested
    if args.recommendations:
        logger.info("🎯 Generation Mode Recommendations:")
        logger.info("=" * 50)
        
        for material in materials[:10]:  # Limit to first 10 for readability
            try:
                recommendations = manager.get_generation_recommendations(material)
                logger.info(f"{material:15s}: {recommendations['recommended']:10s} - {recommendations['reason']}")
            except Exception as e:
                logger.warning(f"{material:15s}: Error getting recommendations - {e}")
        
        if len(materials) > 10:
            logger.info(f"... and {len(materials) - 10} more materials")
        
        if not args.dry_run:
            return 0  # Exit after showing recommendations unless dry-run
    
    # Get API clients
    text_client, full_client = get_api_clients(mode)
    
    if mode == GenerationMode.FULL and not full_client:
        logger.error("Cannot proceed with full mode - DeepSeek client required")
        return 1
    
    if mode in [GenerationMode.TEXT_ONLY, GenerationMode.HYBRID] and not text_client:
        logger.warning("Text generation will be skipped - Grok client not available")
    
    # Process materials
    logger.info(f"🚀 Starting {mode.value} generation for {len(materials)} materials")
    
    success_count = 0
    total_count = len(materials)
    
    for i, material in enumerate(materials, 1):
        logger.info(f"[{i}/{total_count}] Processing {material}")
        
        try:
            success = generate_single_material(
                material_name=material,
                mode=mode,
                manager=manager,
                text_client=text_client,
                full_client=full_client,
                force_refresh=args.force_refresh,
                dry_run=args.dry_run
            )
            
            if success:
                success_count += 1
            
        except KeyboardInterrupt:
            logger.info("⚠️  Generation interrupted by user")
            break
        except Exception as e:
            logger.error(f"❌ Unexpected error processing {material}: {e}")
    
    # Summary
    logger.info("=" * 50)
    logger.info("📊 Generation Summary:")
    logger.info(f"   Mode: {mode.value}")
    logger.info(f"   Total materials: {total_count}")
    logger.info(f"   Successful: {success_count}")
    logger.info(f"   Failed: {total_count - success_count}")
    
    if args.dry_run:
        logger.info("   (Dry run - no files were modified)")
    
    return 0 if success_count == total_count else 1

if __name__ == "__main__":
    sys.exit(main())