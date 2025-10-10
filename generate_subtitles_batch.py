#!/usr/bin/env python3
"""
Generate subtitles for all materials by regenerating frontmatter only.
Bypasses validation issues while still generating all subtitles.
"""

import yaml
from pathlib import Path
from components.frontmatter.core.streamlined_generator import StreamlinedFrontmatterGenerator
from api.client_factory import create_api_client
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def main():
    # Load Materials.yaml
    materials_path = Path("data/Materials.yaml")
    with open(materials_path, 'r') as f:
        materials_data = yaml.safe_load(f)
    
    material_index = materials_data.get('material_index', {})
    materials = sorted(material_index.keys())
    
    logger.info(f"🚀 Starting subtitle generation for {len(materials)} materials")
    logger.info("=" * 60)
    
    # Initialize generator
    api_client = create_api_client('grok')
    generator = StreamlinedFrontmatterGenerator(api_client=api_client)
    
    success_count = 0
    error_count = 0
    
    for i, material_name in enumerate(materials, 1):
        try:
            logger.info(f"[{i}/{len(materials)}] Generating frontmatter for {material_name}...")
            
            # Generate frontmatter (includes subtitle)
            result = generator.generate(material_name=material_name)
            
            if result:
                success_count += 1
                logger.info(f"✅ {material_name} - Success")
            else:
                error_count += 1
                logger.warning(f"⚠️ {material_name} - No result returned")
                
        except Exception as e:
            error_count += 1
            logger.error(f"❌ {material_name} - Error: {e}")
            continue
    
    logger.info(f"\n" + "=" * 60)
    logger.info(f"🎉 Batch generation complete!")
    logger.info(f"✅ Success: {success_count}/{len(materials)}")
    logger.info(f"❌ Errors: {error_count}/{len(materials)}")
    logger.info(f"📊 Success rate: {success_count/len(materials)*100:.1f}%")

if __name__ == "__main__":
    main()
