#!/usr/bin/env python3
"""
Generate Content for First 3 Materials
Uses the production content component system following CLAUDE_INSTRUCTIONS.md
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

def generate_content_for_material(material, api_client):
    """Generate content for a single material using the content component"""
    from components.content.generator import ContentComponentGenerator
    
    material_name = material['name']
    logger.info(f"🎯 Generating content for: {material_name}")
    
    # Create content generator
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
    
    # Prepare author info - Load full author data from authors.json
    author_id = material.get('author_id', 1)
    
    # Load full author information
    import json
    try:
        with open('components/author/authors.json', 'r') as f:
            authors_data = json.load(f)
        
        # Find the author by ID
        author_info = None
        for author in authors_data.get('authors', []):
            if author.get('id') == author_id:
                author_info = author
                break
        
        if not author_info:
            # Fallback to basic info if author not found
            author_info = {'id': author_id}
            logger.warning(f"Author ID {author_id} not found in authors.json, using basic info")
        else:
            logger.debug(f"Loaded full author data for {author_info.get('name', 'Unknown')}")
            
    except Exception as e:
        logger.warning(f"Failed to load authors.json: {e}, using basic author info")
        author_info = {'id': author_id}
    
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
        # Generate content
        result = content_generator.generate(
            material_name=material_name,
            material_data=material_data,
            api_client=api_client,
            author_info=author_info,
            frontmatter_data=frontmatter_data
        )
        
        if result.success:
            logger.info(f"✅ Content generated successfully for {material_name}")
            logger.info(f"📄 Content length: {len(result.content)} characters")
            return result.content
        else:
            logger.error(f"❌ Content generation failed for {material_name}: {result.error_message}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Exception during content generation for {material_name}: {e}")
        return None

def save_content_file(material_name, content):
    """Save generated content to file"""
    # Create content directory if it doesn't exist
    content_dir = Path("content/components/content")
    content_dir.mkdir(parents=True, exist_ok=True)
    
    # Create filename (lowercase, hyphenated)
    filename = material_name.lower().replace(' ', '-').replace('(', '').replace(')', '') + "-laser-cleaning.md"
    filepath = content_dir / filename
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"💾 Content saved to: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"❌ Failed to save content for {material_name}: {e}")
        return None

def main():
    """Main execution function"""
    logger.info("🚀 Starting content generation for first 3 materials")
    
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
        
        # Generate content for each material
        successful_generations = 0
        failed_generations = 0
        
        for i, material in enumerate(first_three, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"MATERIAL {i}/3: {material['name']}")
            logger.info(f"Author ID: {material.get('author_id', 'Unknown')}")
            logger.info(f"Category: {material.get('category', 'Unknown')}")
            logger.info(f"Formula: {material.get('formula', 'N/A')}")
            logger.info(f"{'='*60}")
            
            # Generate content
            content = generate_content_for_material(material, api_client)
            
            if content:
                # Save to file
                filepath = save_content_file(material['name'], content)
                if filepath:
                    successful_generations += 1
                    logger.info(f"✅ Successfully completed {material['name']}")
                else:
                    failed_generations += 1
            else:
                failed_generations += 1
                logger.error(f"❌ Failed to generate content for {material['name']}")
        
        # Final summary
        logger.info(f"\n{'='*60}")
        logger.info("📊 GENERATION SUMMARY")
        logger.info(f"✅ Successful: {successful_generations}/3")
        logger.info(f"❌ Failed: {failed_generations}/3")
        logger.info(f"{'='*60}")
        
        if successful_generations > 0:
            logger.info("🎉 Content generation completed successfully!")
            logger.info("📁 Check the 'content/' directory for generated files")
        else:
            logger.error("💥 All content generation attempts failed")
            return 1
            
        return 0
        
    except Exception as e:
        logger.error(f"💥 Critical error in main execution: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
