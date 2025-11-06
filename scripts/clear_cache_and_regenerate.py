#!/usr/bin/env python3
"""
Clear Materials.yaml cache and regenerate all frontmatter files.

This ensures the frontmatter exporter uses fresh data from Materials.yaml,
not cached data from before the author migration.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from materials.data.materials import clear_materials_cache, load_materials_cached
from components.frontmatter.core.trivial_exporter import TrivialFrontmatterExporter
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def main():
    """Clear cache and regenerate all frontmatter."""
    
    # Step 1: Clear the cache
    logger.info("🧹 Clearing Materials.yaml cache...")
    clear_materials_cache()
    logger.info("✅ Cache cleared")
    
    # Step 2: Verify fresh load shows slim author format
    logger.info("🔍 Verifying Materials.yaml has slim author format...")
    materials_data = load_materials_cached()
    
    # Check first material (Aluminum) - materials are nested under 'materials' key
    materials_dict = materials_data.get('materials', {})
    aluminum = materials_dict.get('Aluminum', {})
    author_field = aluminum.get('author', {})
    
    if isinstance(author_field, dict) and len(author_field) == 1 and 'id' in author_field:
        logger.info(f"✅ Verified: Materials.yaml has slim format (author: {{id: {author_field['id']}}})")
    else:
        logger.error(f"❌ ERROR: Materials.yaml still has full author format: {author_field}")
        return 1
    
    # Step 3: Regenerate all frontmatter
    logger.info("🔄 Regenerating all 132 frontmatter files...")
    exporter = TrivialFrontmatterExporter()
    
    success_count = 0
    error_count = 0
    
    for material_name, material_data in materials_dict.items():
        try:
            exporter.export_single(material_name, material_data)
            success_count += 1
        except Exception as e:
            error_count += 1
            logger.error(f"❌ Error exporting {material_name}: {e}")
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info(f"🏁 Regeneration Complete")
    logger.info(f"✅ Success: {success_count} files")
    logger.info(f"❌ Errors: {error_count} files")
    logger.info(f"{'='*60}")
    
    return 0 if error_count == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
