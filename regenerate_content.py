#!/usr/bin/env python3
"""
Regenerate the first 3 materials with validation enabled
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def load_material_data():
    """Load material data from materials.yaml"""
    import yaml
    
    materials_file = "data/materials.yaml"
    try:
        with open(materials_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data['materials']
    except Exception as e:
        logger.error(f"Failed to load materials data: {e}")
        raise

def get_first_three_materials(materials_data):
    """Extract the first 3 materials from the materials data"""
    first_three = []
    
    # Navigate through the materials structure
    for category_name, category_data in materials_data.items():
        if 'items' in category_data:
            for material in category_data['items']:
                if len(first_three) < 3:
                    # Add category info to material
                    material_with_category = material.copy()
                    material_with_category['category'] = category_name
                    first_three.append(material_with_category)
                else:
                    break
        if len(first_three) >= 3:
            break
    
    return first_three

def create_api_client():
    """Create API client using the established patterns"""
    from api.client_manager import create_api_client as create_client
    
    # Use DeepSeek as primary provider
    try:
        api_client = create_client('deepseek')
        logger.info("✅ DeepSeek API client created successfully")
        return api_client
    except Exception as e:
        logger.error(f"Failed to create DeepSeek client: {e}")
        # Fallback to Grok if DeepSeek fails
        try:
            api_client = create_client('grok')
            logger.info("✅ Grok API client created successfully (fallback)")
            return api_client
        except Exception as e2:
            logger.error(f"Failed to create Grok client: {e2}")
            raise RuntimeError("No API clients available")

def regenerate_content_for_material(material, api_client):
    """Regenerate content for a single material with validation enabled"""
    from components.content.generator import ContentComponentGenerator
    
    material_name = material['name']
    logger.info(f"🎯 Regenerating content for: {material_name}")
    
    # Create content generator (now with validation enabled)
    content_generator = ContentComponentGenerator()
    
    # Prepare material data in the expected format
    material_data = {
        'name': material_name,
        'data': {
            'formula': material.get('formula', ''),
            'author_id': material.get('author_id', 1),
            'category': material.get('category', 'unknown'),
            **material  # Include all other material properties
        },
        'article_type': 'material'
    }
    
    # Prepare author info
    author_info = {
        'id': material.get('author_id', 1)
    }
    
    # Generate frontmatter data (simplified)
    frontmatter_data = {
        'chemicalProperties': {
            'formula': material.get('formula', ''),
            'materialType': material.get('category', 'unknown').title()
        },
        'properties': {},
        'category': material.get('category', 'unknown'),
        'technicalSpecifications': {}
    }
    
    # Add laser parameters if available
    if 'laser_parameters' in material:
        laser_params = material['laser_parameters']
        frontmatter_data['properties'].update({
            'fluenceThreshold': laser_params.get('fluence_threshold', ''),
            'pulseDuration': laser_params.get('pulse_duration', ''),
            'wavelengthOptimal': laser_params.get('wavelength_optimal', ''),
            'powerRange': laser_params.get('power_range', '')
        })
    
    try:
        # Generate content with validation enabled
        result = content_generator.generate(
            material_name=material_name,
            material_data=material_data,
            api_client=api_client,
            author_info=author_info,
            frontmatter_data=frontmatter_data
        )
        
        if result.success:
            logger.info(f"✅ Content regenerated successfully for {material_name}")
            logger.info(f"📄 Content length: {len(result.content)} characters")
            
            # Check if validation is enabled
            if "quality_scoring_enabled: true" in result.content:
                logger.info("🎯 Quality validation: ENABLED")
            else:
                logger.warning("⚠️  Quality validation status unclear")
                
            return result.content
        else:
            logger.error(f"❌ Content generation failed for {material_name}: {result.error_message}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Exception during content generation for {material_name}: {e}")
        return None

def save_content_file(material_name, content):
    """Save regenerated content to file (overwriting existing)"""
    # Create content directory if it doesn't exist
    content_dir = Path("content")
    content_dir.mkdir(exist_ok=True)
    
    # Create filename (lowercase, hyphenated)
    filename = material_name.lower().replace(' ', '-').replace('(', '').replace(')', '') + "-laser-cleaning.md"
    filepath = content_dir / filename
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"💾 Content regenerated and saved to: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"❌ Failed to save content for {material_name}: {e}")
        return None

def main():
    """Main execution function"""
    logger.info("🔄 Regenerating first 3 materials with validation enabled")
    
    try:
        # Load materials data
        logger.info("📁 Loading materials data...")
        materials_data = load_material_data()
        
        # Get first 3 materials
        first_three = get_first_three_materials(materials_data)
        logger.info(f"📋 Found first 3 materials: {[m['name'] for m in first_three]}")
        
        # Create API client
        logger.info("🔌 Setting up API client...")
        api_client = create_api_client()
        
        # Regenerate content for each material
        successful_regenerations = 0
        failed_regenerations = 0
        
        for i, material in enumerate(first_three, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"REGENERATING MATERIAL {i}/3: {material['name']}")
            logger.info(f"Author ID: {material.get('author_id', 'Unknown')}")
            logger.info(f"Category: {material.get('category', 'Unknown')}")
            logger.info(f"Formula: {material.get('formula', 'N/A')}")
            logger.info(f"{'='*60}")
            
            # Regenerate content
            content = regenerate_content_for_material(material, api_client)
            
            if content:
                # Save to file (overwriting existing)
                filepath = save_content_file(material['name'], content)
                if filepath:
                    successful_regenerations += 1
                    logger.info(f"✅ Successfully regenerated {material['name']}")
                else:
                    failed_regenerations += 1
            else:
                failed_regenerations += 1
                logger.error(f"❌ Failed to regenerate content for {material['name']}")
        
        # Final summary
        logger.info(f"\n{'='*60}")
        logger.info("📊 REGENERATION SUMMARY")
        logger.info(f"✅ Successful: {successful_regenerations}/3")
        logger.info(f"❌ Failed: {failed_regenerations}/3")
        logger.info(f"🎯 Validation: ENABLED (quality scoring active)")
        logger.info(f"{'='*60}")
        
        if successful_regenerations > 0:
            logger.info("🎉 Content regeneration completed successfully!")
            logger.info("📁 Check the 'content/' directory for regenerated files")
            logger.info("🔍 Files now include quality metrics and validation data")
        else:
            logger.error("💥 All content regeneration attempts failed")
            return 1
            
        return 0
        
    except Exception as e:
        logger.error(f"💥 Critical error in main execution: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
