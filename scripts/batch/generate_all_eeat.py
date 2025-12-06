#!/usr/bin/env python3
"""
Batch EEAT Generator - Generate EEAT for all materials

Generates EEAT (Experience, Expertise, Authoritativeness, Trustworthiness) 
metadata for all materials from their regulatoryStandards.

EEAT Structure:
- reviewedBy: "Z-Beam Quality Assurance Team"
- citations: 1-3 random regulatoryStandards descriptions
- isBasedOn: 1 random regulatoryStandard with name and url

Usage:
    python3 scripts/batch/generate_all_eeat.py [--dry-run] [--material MATERIAL_NAME]
    
    --dry-run: Preview what would be generated without saving
    --material: Generate for specific material only
"""

import sys
import yaml
import logging
from pathlib import Path
from typing import Dict, List

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from domains.materials.coordinator import UnifiedMaterialsGenerator
from shared.api.client_factory import create_api_client

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


def load_materials() -> Dict:
    """Load Materials.yaml"""
    materials_path = PROJECT_ROOT / "materials" / "data" / "Materials.yaml"
    
    with open(materials_path, 'r') as f:
        return yaml.safe_load(f)


def check_existing_eeat(materials_data: Dict) -> tuple:
    """
    Check which materials already have EEAT.
    
    Returns:
        (materials_with_eeat, materials_without_eeat)
    """
    with_eeat = []
    without_eeat = []
    
    for material_name, material_data in materials_data['materials'].items():
        if 'eeat' in material_data and material_data['eeat']:
            with_eeat.append(material_name)
        else:
            without_eeat.append(material_name)
    
    return with_eeat, without_eeat


def generate_all_eeat(dry_run: bool = False, specific_material: str = None):
    """
    Generate EEAT for all materials (or specific material).
    
    Args:
        dry_run: If True, preview without saving
        specific_material: If provided, only generate for this material
    """
    logger.info("=" * 70)
    logger.info("BATCH EEAT GENERATION")
    logger.info("=" * 70)
    
    # Load materials
    logger.info("\n📖 Loading Materials.yaml...")
    materials_data = load_materials()
    total_materials = len(materials_data['materials'])
    logger.info(f"✅ Loaded {total_materials} materials")
    
    # Check existing EEAT
    logger.info("\n🔍 Checking existing EEAT...")
    with_eeat, without_eeat = check_existing_eeat(materials_data)
    logger.info(f"   ✅ Already have EEAT: {len(with_eeat)}")
    logger.info(f"   ⏳ Missing EEAT: {len(without_eeat)}")
    
    # Filter to specific material if requested
    if specific_material:
        if specific_material not in materials_data['materials']:
            logger.error(f"❌ Material not found: {specific_material}")
            return False
        
        if specific_material in with_eeat:
            logger.warning(f"⚠️  {specific_material} already has EEAT")
            response = input("Regenerate? (y/N): ").strip().lower()
            if response != 'y':
                logger.info("Cancelled")
                return True
        
        materials_to_process = [specific_material]
        logger.info(f"\n🎯 Processing single material: {specific_material}")
    else:
        materials_to_process = without_eeat
        logger.info(f"\n🚀 Processing {len(materials_to_process)} materials")
    
    if dry_run:
        logger.info("\n🔍 DRY-RUN MODE: No EEAT will be saved")
    
    if not materials_to_process:
        logger.info("\n✨ All materials already have EEAT!")
        return True
    
    # Create generator (need API client even though EEAT doesn't use it)
    logger.info("\n🔧 Initializing generator...")
    try:
        api_client = create_api_client('winston')
        generator = UnifiedMaterialsGenerator(api_client)
    except Exception as e:
        logger.error(f"❌ Failed to initialize generator: {e}")
        return False
    
    # Generate EEAT for each material
    logger.info("\n" + "=" * 70)
    logger.info("GENERATING EEAT")
    logger.info("=" * 70)
    
    success_count = 0
    skip_count = 0
    error_count = 0
    errors = []
    
    for i, material_name in enumerate(materials_to_process, 1):
        logger.info(f"\n[{i}/{len(materials_to_process)}] {material_name}")
        
        try:
            material_data = materials_data['materials'][material_name]
            
            # Check if material has regulatoryStandards
            reg_standards = material_data.get('regulatoryStandards', [])
            dict_standards = [s for s in reg_standards if isinstance(s, dict)]
            
            if not dict_standards:
                logger.warning(f"   ⏭️  Skipped: No valid regulatoryStandards")
                skip_count += 1
                continue
            
            if dry_run:
                # Just preview what would be generated
                logger.info(f"   📊 Would generate EEAT from {len(dict_standards)} standards")
                success_count += 1
            else:
                # Actually generate and save
                eeat_data = generator.generate(material_name, 'eeat')
                logger.info(f"   ✅ Generated: {len(eeat_data['citations'])} citations")
                success_count += 1
                
        except Exception as e:
            logger.error(f"   ❌ Failed: {e}")
            errors.append(f"{material_name}: {e}")
            error_count += 1
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("GENERATION COMPLETE")
    logger.info("=" * 70)
    logger.info(f"\n📊 Summary:")
    logger.info(f"   Total processed: {len(materials_to_process)}")
    logger.info(f"   ✅ Success: {success_count}")
    logger.info(f"   ⏭️  Skipped: {skip_count}")
    logger.info(f"   ❌ Errors: {error_count}")
    
    if errors:
        logger.info(f"\n❌ Errors encountered:")
        for error in errors:
            logger.info(f"   • {error}")
    
    if dry_run:
        logger.info(f"\n🔍 DRY-RUN: No changes were saved")
        logger.info(f"   Run without --dry-run to actually generate EEAT")
    else:
        logger.info(f"\n✅ EEAT saved to Materials.yaml")
        logger.info(f"\n📋 Next steps:")
        logger.info(f"   1. Deploy to frontmatter: python3 run.py --deploy")
        logger.info(f"   2. Verify: Check frontmatter/materials/*.yaml files")
    
    return error_count == 0


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate EEAT for all materials',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Generate for all materials missing EEAT
    python3 scripts/batch/generate_all_eeat.py
    
    # Preview without saving
    python3 scripts/batch/generate_all_eeat.py --dry-run
    
    # Generate for specific material
    python3 scripts/batch/generate_all_eeat.py --material Aluminum
        """
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview what would be generated without saving'
    )
    
    parser.add_argument(
        '--material',
        type=str,
        help='Generate EEAT for specific material only'
    )
    
    args = parser.parse_args()
    
    try:
        success = generate_all_eeat(
            dry_run=args.dry_run,
            specific_material=args.material
        )
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
