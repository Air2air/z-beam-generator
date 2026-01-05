#!/usr/bin/env python3
"""
Regenerate all frontmatter files from Materials.yaml.

This script uses the TrivialFrontmatterExporter to regenerate all 132 material
frontmatter files with the latest data from Materials.yaml, including new date fields.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# pylint: disable=wrong-import-position
from domains.materials.materials_cache import load_materials_cached
from export.core.trivial_exporter import TrivialFrontmatterExporter

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def main():
    """Regenerate all frontmatter files."""
    print("\n" + "="*80)
    print("REGENERATE ALL FRONTMATTER FROM MATERIALS.YAML")
    print("="*80 + "\n")
    
    # Load Materials.yaml
    logger.info("📂 Loading Materials.yaml...")
    materials_data = load_materials_cached()
    materials_section = materials_data.get('materials', {})
    
    if not materials_section:
        logger.error("❌ No materials found in Materials.yaml")
        return 1
    
    logger.info(f"✅ Loaded {len(materials_section)} materials\n")
    
    # Initialize exporter
    logger.info("🔧 Initializing TrivialFrontmatterExporter...")
    exporter = TrivialFrontmatterExporter()
    logger.info("✅ Exporter initialized\n")
    
    # Export all materials
    logger.info(f"📝 Exporting {len(materials_section)} materials...\n")
    
    success_count = 0
    error_count = 0
    
    for i, (material_name, material_data) in enumerate(materials_section.items(), 1):
        try:
            logger.info(f"[{i}/{len(materials_section)}] {material_name}...")
            exporter.export_single(material_name, material_data)
            success_count += 1
        except Exception as e:
            logger.error(f"❌ Error exporting {material_name}: {e}")
            error_count += 1
    
    # Summary
    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    print(f"   ✅ Successfully exported: {success_count}")
    print(f"   ❌ Errors: {error_count}")
    print("   📁 Output directory: frontmatter/materials/")
    print("="*80 + "\n")
    
    return 0 if error_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
