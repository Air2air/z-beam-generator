#!/usr/bin/env python3
"""
Batch Caption Generator - Generate captions for all materials missing them

This script generates microscopy captions for all materials in Materials.yaml
that are missing beforeText or afterText caption fields.

Usage:
    # Generate all missing captions
    python3 scripts/batch/generate_all_captions.py
    
    # Dry run (show what would be generated)
    python3 scripts/batch/generate_all_captions.py --dry-run
    
    # Generate for specific materials only
    python3 scripts/batch/generate_all_captions.py --materials "Bronze,Steel,Aluminum"
"""

import argparse
import logging
import sys
import yaml
from pathlib import Path
from typing import List

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from materials.caption.generators.generator import CaptionComponentGenerator
from shared.api.client_factory import create_api_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

MATERIALS_FILE = project_root / "materials" / "data" / "Materials.yaml"


def load_materials() -> dict:
    """Load Materials.yaml"""
    with open(MATERIALS_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def find_missing_captions(materials_data: dict) -> List[str]:
    """Find all materials missing caption data"""
    missing = []
    for name, mat in materials_data['materials'].items():
        caption = mat.get('caption', {})
        if not caption or not caption.get('beforeText') or not caption.get('afterText'):
            missing.append(name)
    return sorted(missing)


def main():
    parser = argparse.ArgumentParser(
        description='Batch generate captions for materials missing them'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be generated without actually generating'
    )
    parser.add_argument(
        '--materials',
        type=str,
        help='Comma-separated list of specific materials to generate (e.g., "Bronze,Steel")'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Maximum number of materials to process (for testing)'
    )
    
    args = parser.parse_args()
    
    # Load materials
    logger.info("📖 Loading Materials.yaml...")
    materials_data = load_materials()
    
    # Determine which materials to process
    if args.materials:
        material_names = [m.strip() for m in args.materials.split(',')]
        logger.info(f"Processing specified materials: {material_names}")
    else:
        material_names = find_missing_captions(materials_data)
        logger.info(f"Found {len(material_names)} materials missing captions")
    
    # Apply limit if specified
    if args.limit:
        material_names = material_names[:args.limit]
        logger.info(f"Limited to {args.limit} materials")
    
    if args.dry_run:
        logger.info("🔍 DRY-RUN MODE: No captions will be generated")
        logger.info(f"\nWould generate captions for {len(material_names)} materials:")
        for name in material_names[:20]:
            logger.info(f"  - {name}")
        if len(material_names) > 20:
            logger.info(f"  ... and {len(material_names)-20} more")
        return 0
    
    # Initialize generator and API client
    logger.info("🎨 Initializing caption generator...")
    generator = CaptionComponentGenerator()
    api_client = create_api_client()
    
    # Process each material
    logger.info(f"\n🚀 Generating captions for {len(material_names)} materials...")
    logger.info("=" * 60)
    
    success_count = 0
    error_count = 0
    
    for idx, material_name in enumerate(material_names, 1):
        try:
            logger.info(f"\n[{idx}/{len(material_names)}] Generating {material_name}...")
            
            material_data = materials_data['materials'][material_name]
            
            result = generator.generate(
                material_name=material_name,
                material_data=material_data,
                api_client=api_client
            )
            
            if result.success:
                logger.info(f"✅ {material_name} caption generated")
                success_count += 1
            else:
                logger.error(f"❌ {material_name} failed: {result.error}")
                error_count += 1
                
        except Exception as e:
            logger.error(f"❌ {material_name} error: {e}")
            error_count += 1
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 BATCH GENERATION COMPLETE")
    logger.info(f"   Total processed: {len(material_names)}")
    logger.info(f"   ✅ Successful: {success_count}")
    logger.info(f"   ❌ Failed: {error_count}")
    logger.info("=" * 60)
    
    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
