#!/usr/bin/env python3
"""
Z-Beam Generator: Clean Batch Generation of 24 Materials
No fallbacks, fail-fast approach as specified in CLAUDE_INSTRUCTIONS.md
"""

import sys
import os
from pathlib import Path
import time
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Generate 24 materials with clean fail-fast approach"""
    from generators.dynamic_generator import DynamicGenerator
    
    # Material assignments (6 per author)
    materials_by_author = {
        1: ["Alumina", "Zirconia", "Silicon-Carbide", "Tungsten-Carbide", "Titanium-Nitride", "Aluminum-Nitride"],
        2: ["Stainless-Steel-316L", "Carbon-Steel", "Tool-Steel", "Inconel-625", "Hastelloy-C276", "Monel-400"],
        3: ["Aluminum-6061", "Titanium-Grade-2", "Copper-C101", "Brass-360", "Bronze-C932", "Magnesium-AZ31"],
        4: ["PTFE", "PEEK", "Polycarbonate", "ABS", "HDPE", "PVC"]
    }
    
    logger.info("🚀 Starting clean batch generation of 24 materials")
    logger.info("✅ No fallbacks - fail-fast approach")
    
    try:
        # Initialize generator with no mock support
        generator = DynamicGenerator()
        
        # Set up API client
        from api.client import APIClient
        api_client = APIClient()
        generator.set_api_client(api_client)
        
        total_materials = 0
        total_time = 0
        
        for author_id, materials in materials_by_author.items():
            logger.info(f"\n👤 Author {author_id}: Generating {len(materials)} materials")
            
            for material_name in materials:
                start_time = time.time()
                
                try:
                    logger.info(f"  🔄 Generating: {material_name}")
                    
                    # Create generation request for all components
                    from generators.dynamic_generator import GenerationRequest
                    
                    request = GenerationRequest(
                        material=material_name,
                        components=["frontmatter", "content", "author", "badgesymbol", 
                                  "propertiestable", "metatags", "jsonld", "tags", 
                                  "bullets", "table", "caption"],
                        output_dir="content"
                    )
                    
                    # Set author on generator (if supported)
                    if hasattr(generator, 'set_author_id'):
                        generator.set_author_id(author_id)
                    
                    # Generate with strict requirements
                    result = generator.generate_multiple(request)
                    
                    if result and result.success:
                        generation_time = time.time() - start_time
                        total_time += generation_time
                        total_materials += 1
                        
                        logger.info(f"    ✅ SUCCESS: {material_name} ({generation_time:.1f}s)")
                        logger.info(f"    📊 Components: {result.successful_components}/{result.total_components}")
                        
                    else:
                        logger.error(f"    ❌ FAILED: {material_name} - Generation failed")
                        
                except Exception as e:
                    logger.error(f"    💥 FAILED: {material_name} - {str(e)}")
                    # Continue with next material (fail-fast per material, not per batch)
                    continue
        
        # Summary
        logger.info(f"\n🎯 GENERATION COMPLETE")
        logger.info(f"✅ Successfully generated: {total_materials}/24 materials")
        logger.info(f"⏱️  Total time: {total_time:.1f}s")
        logger.info(f"📈 Average time per material: {total_time/max(total_materials, 1):.1f}s")
        
        if total_materials < 24:
            logger.warning(f"⚠️  {24 - total_materials} materials failed generation")
            return 1
        else:
            logger.info("🎉 All materials generated successfully!")
            return 0
            
    except Exception as e:
        logger.error(f"💥 CRITICAL FAILURE: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
