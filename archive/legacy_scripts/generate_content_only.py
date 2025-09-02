#!/usr/bin/env python3
"""
Generate ONLY content component files for 24 materials
Targeted fix following CLAUDE_INSTRUCTIONS.md mi        # Summary
        logger.info("\n🎯 CONTENT GENERATION COMPLETE")
        logger.info(f"✅ Successfully generated: {total_materials}/24 content files")
        logger.info(f"⏱️  Total time: {total_time:.1f}s")
        logger.info(f"📈 Average time per content: {total_time/max(total_materials, 1):.1f}s")
        
        if total_materials < 24:
            logger.warning(f"⚠️  {24 - total_materials} content files failed generation")
            return 1
        else:
            logger.info("🎉 All content files generated successfully!")
            return 0
            
    except Exception as e:
        logger.error(f"💥 CRITICAL FAILURE: {str(e)}")
        return 1 principle
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
    """Generate content components for the first 24 materials."""
    
    # Use actual material names from the system (first 24)
    target_materials = [
        "Alabaster", "Alumina", "Aluminum", "Ash", "Bamboo", "Basalt",
        "Beech", "Beryllium", "Birch", "Bluestone", "Borosilicate Glass", "Brass",
        "Breccia", "Brick", "Bronze", "Calcite", "Carbon Fiber Reinforced Polymer", "Cedar",
        "Cement", "Ceramic Matrix Composites CMCs", "Cherry", "Cobalt", "Concrete", "Copper"
    ]
    
    # Author information with full structure
    authors = {
        1: {
            "id": 1,
            "name": "Yi-Chun Lin",
            "sex": "f",
            "title": "Ph.D.",
            "country": "Taiwan",
            "expertise": "Laser Materials Processing",
            "image": "/images/author/yi-chun-lin.jpg"
        },
        2: {
            "id": 2,
            "name": "Alessandro Moretti",
            "sex": "m", 
            "title": "Ph.D.",
            "country": "Italy",
            "expertise": "Industrial Laser Applications",
            "image": "/images/author/alessandro-moretti.jpg"
        },
        3: {
            "id": 3,
            "name": "Ikmanda Roswati",
            "sex": "f",
            "title": "Ph.D.", 
            "country": "Indonesia",
            "expertise": "Material Science",
            "image": "/images/author/ikmanda-roswati.jpg"
        },
        4: {
            "id": 4,
            "name": "Todd Dunning",
            "sex": "m",
            "title": "Ph.D.",
            "country": "USA",
            "expertise": "Laser Technology", 
            "image": "/images/author/todd-dunning.jpg"
        }
    }
    
    logger.info("🚀 Generating CONTENT components only for 24 materials")
    
    try:
        # Initialize generator with Grok API client (content uses grok per config)
        from generators.dynamic_generator import DynamicGenerator
        from cli.api_config import create_api_client
        
        generator = DynamicGenerator()
        
        # Create Grok API client for content generation
        api_client = create_api_client("grok")
        generator.set_api_client(api_client)
        
        total_materials = 0
        total_time = 0
        
        for material_name in target_materials:
            start_time = time.time()
            
            try:
                logger.info(f"� Generating content: {material_name}")
                
                # Get material data to extract author_id
                material = generator.material_loader.get_material(material_name)
                if not material:
                    logger.error(f"    ❌ FAILED: {material_name} - Material not found")
                    continue
                
                # Get author_id from material data (it's in the 'data' field)
                material_data = material.get('data', {})
                author_id = material_data.get('author_id')
                if not author_id:
                    logger.error(f"    ❌ FAILED: {material_name} - No author_id in material data")
                    continue
                
                # Get author info
                author_info = authors.get(author_id)
                if not author_info:
                    logger.error(f"    ❌ FAILED: {material_name} - Invalid author_id: {author_id}")
                    continue
                
                # Set author on generator
                generator.set_author(author_info)
                
                # Generate ONLY content component
                result = generator.generate_component(
                    material_name=material_name,
                    component_type="content",
                    schema_fields={}
                )
                
                if result and result.success:
                    generation_time = time.time() - start_time
                    total_time += generation_time
                    total_materials += 1
                    
                    # Save to correct directory
                    output_dir = Path("content/components/content")
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Create filename
                    from generators.dynamic_generator import create_filename_slug
                    filename = create_filename_slug(material_name) + ".md"
                    filepath = output_dir / filename
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(result.content)
                    
                    logger.info(f"    ✅ SUCCESS: {material_name} (Author {author_id}: {author_info['name']}) ({generation_time:.1f}s)")
                    logger.info(f"    📁 Saved to: {filepath}")
                    
                else:
                    logger.error(f"    ❌ FAILED: {material_name} - {result.error_message if result else 'No result'}")
                    
            except Exception as e:
                logger.error(f"    💥 FAILED: {material_name} - {str(e)}")
                continue
        
        # Summary
        logger.info("\n🎯 CONTENT GENERATION COMPLETE")
        logger.info(f"✅ Successfully generated: {total_materials}/24 content files")
        logger.info(f"⏱️  Total time: {total_time:.1f}s")
        logger.info(f"📈 Average time per content: {total_time/max(total_materials, 1):.1f}s")
        
        if total_materials < 24:
            logger.warning(f"⚠️  {24 - total_materials} content files failed generation")
            return 1
        else:
            logger.info("🎉 All content files generated successfully!")
            return 0
            
    except Exception as e:
        logger.error(f"💥 CRITICAL FAILURE: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
