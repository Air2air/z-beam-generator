#!/usr/bin/env python3
"""
Regenerate the 3 materials with improved validation (enhanced author info)
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

def regenerate_with_improved_validation():
    """Regenerate the 3 materials with enhanced validation"""
    logger.info("🔄 Regenerating materials with improved validation system")
    
    try:
        from components.content.generator import ContentComponentGenerator
        from api.client_manager import create_api_client
        import yaml
        
        # Load material data
        with open("data/materials.yaml", 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        materials_data = data['materials']
        
        # Get first 3 materials
        first_three = []
        for category_name, category_data in materials_data.items():
            if 'items' in category_data:
                for material in category_data['items']:
                    if len(first_three) < 3:
                        material_with_category = material.copy()
                        material_with_category['category'] = category_name
                        first_three.append(material_with_category)
                    else:
                        break
            if len(first_three) >= 3:
                break
        
        # Create API client
        api_client = create_api_client('deepseek')
        logger.info("✅ API client created")
        
        # Create content generator (now with enhanced author info)
        content_generator = ContentComponentGenerator()
        
        results = []
        
        for i, material in enumerate(first_three, 1):
            material_name = material['name']
            author_id = material.get('author_id', 1)
            
            logger.info(f"\n{'='*60}")
            logger.info(f"REGENERATING {i}/3: {material_name}")
            logger.info(f"Author ID: {author_id}")
            logger.info(f"{'='*60}")
            
            # Prepare material data
            material_data = {
                'name': material_name,
                'data': {
                    'formula': material.get('formula', ''),
                    'author_id': author_id,
                    'category': material.get('category', 'unknown'),
                    **material
                },
                'article_type': 'material'
            }
            
            # Use minimal author info - will be auto-enhanced
            author_info = {'id': author_id}
            
            # Frontmatter data
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
            
            # Generate content with enhanced validation
            result = content_generator.generate(
                material_name=material_name,
                material_data=material_data,
                api_client=api_client,
                author_info=author_info,  # Auto-enhanced with complete info
                frontmatter_data=frontmatter_data
            )
            
            if result.success:
                # Extract quality metrics
                import re
                overall_match = re.search(r'overall_score:\s*([\d.]+)', result.content)
                authenticity_match = re.search(r'author_authenticity:\s*([\d.]+)', result.content)
                
                if overall_match and authenticity_match:
                    overall_score = float(overall_match.group(1))
                    authenticity = float(authenticity_match.group(1))
                    
                    logger.info(f"📊 Quality: Overall={overall_score:.1f}, Authenticity={authenticity:.1f}")
                else:
                    overall_score = 0
                    authenticity = 0
                
                # Save to file
                filename = material_name.lower().replace(' ', '-').replace('(', '').replace(')', '') + "-laser-cleaning.md"
                filepath = Path("content") / filename
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(result.content)
                
                logger.info(f"💾 Saved to: {filepath}")
                logger.info(f"✅ {material_name} regenerated successfully")
                
                results.append({
                    'material': material_name,
                    'author_id': author_id,
                    'overall_score': overall_score,
                    'authenticity': authenticity,
                    'success': True
                })
            else:
                logger.error(f"❌ Failed to regenerate {material_name}: {result.error_message}")
                results.append({
                    'material': material_name,
                    'author_id': author_id,
                    'success': False,
                    'error': result.error_message
                })
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Regeneration failed: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    """Main regeneration with validation improvements"""
    logger.info("🚀 Regenerating Materials with Improved Validation")
    logger.info("="*60)
    
    logger.info("🔍 Previous Results (incomplete author info):")
    logger.info("   Alumina: Overall=51.9, Authenticity=16.0")
    logger.info("   Porcelain: Overall=48.2, Authenticity=0.0")
    logger.info("   Silicon Nitride: Overall=50.6, Authenticity=8.0")
    logger.info("")
    logger.info("🎯 Now regenerating with enhanced author info loading...")
    
    results = regenerate_with_improved_validation()
    
    logger.info("\n" + "="*60)
    logger.info("📊 REGENERATION RESULTS")
    logger.info("="*60)
    
    successful = 0
    failed = 0
    total_improvement_overall = 0
    total_improvement_auth = 0
    
    previous_scores = {
        'Alumina': {'overall': 51.9, 'authenticity': 16.0},
        'Porcelain': {'overall': 48.2, 'authenticity': 0.0},
        'Silicon Nitride': {'overall': 50.6, 'authenticity': 8.0}
    }
    
    for result in results:
        if result['success']:
            successful += 1
            material = result['material']
            overall = result['overall_score']
            auth = result['authenticity']
            
            prev = previous_scores.get(material, {'overall': 50, 'authenticity': 10})
            improve_overall = overall - prev['overall']
            improve_auth = auth - prev['authenticity']
            
            total_improvement_overall += improve_overall
            total_improvement_auth += improve_auth
            
            logger.info(f"✅ {material}:")
            logger.info(f"   Overall: {prev['overall']:.1f} → {overall:.1f} ({improve_overall:+.1f})")
            logger.info(f"   Authenticity: {prev['authenticity']:.1f} → {auth:.1f} ({improve_auth:+.1f})")
        else:
            failed += 1
            logger.error(f"❌ {result['material']}: {result.get('error', 'Unknown error')}")
    
    logger.info(f"\n📊 Summary: {successful}/3 successful, {failed}/3 failed")
    
    if successful > 0:
        avg_improvement_overall = total_improvement_overall / successful
        avg_improvement_auth = total_improvement_auth / successful
        
        logger.info(f"📈 Average Improvements:")
        logger.info(f"   Overall Quality: {avg_improvement_overall:+.1f} points")
        logger.info(f"   Author Authenticity: {avg_improvement_auth:+.1f} points")
        
        if avg_improvement_auth > 50:
            logger.info("\n🎉 EXCELLENT: Major authenticity improvements achieved!")
        elif avg_improvement_auth > 20:
            logger.info("\n✅ GOOD: Significant authenticity improvements")
        else:
            logger.info("\n📈 PROGRESS: Some improvement, but more tuning needed")
    
    logger.info("\n💡 KEY IMPROVEMENT: ContentComponentGenerator now auto-loads complete author info")
    logger.info("💡 This enables proper persona and formatting validation scoring")
    
    logger.info("\n" + "="*60)
    logger.info("🎯 IMPROVED VALIDATION REGENERATION COMPLETE")

if __name__ == "__main__":
    main()
