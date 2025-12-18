#!/usr/bin/env python3
"""
Split Categories.yaml into subcategory-based files for reusability

This script extracts logical data groupings from the master Categories.yaml file
and creates focused subcategory files for independent component usage.

Author: Z-Beam Generator
Date: October 30, 2025
"""

import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class CategorySplitter:
    """Splits Categories.yaml into logical subcategory files"""
    
    def __init__(self, source_file: Path, output_dir: Path):
        self.source_file = source_file
        self.output_dir = output_dir
        self.timestamp = datetime.now().isoformat()
        
    def load_source(self) -> Dict[str, Any]:
        """Load the master Categories.yaml file"""
        logger.info(f"📖 Loading {self.source_file}")
        with open(self.source_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def save_file(self, filename: str, data: Dict[str, Any], description: str):
        """Save a subcategory file with metadata header"""
        filepath = self.output_dir / filename
        
        # Add generation metadata
        output = {
            '_metadata': {
                'source': 'Categories.yaml',
                'generated': self.timestamp,
                'description': description,
                'version': '1.0.0'
            },
            **data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(output, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        logger.info(f"✅ Created: {filename}")
        return filepath
    
    def split_all(self):
        """Execute the complete split operation"""
        logger.info("\n🔧 Starting Categories.yaml split operation...\n")
        
        # Load source data
        data = self.load_source()
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Material Index & Category Metadata
        logger.info("📦 1/8: Extracting Material Index...")
        # Note: material_index is actually in Materials.yaml, not Categories.yaml
        # This file will just have category_metadata
        self.save_file('material_index.yaml', {
            'category_metadata': {
                cat: {
                    'article_type': info.get('article_type'),
                    'description': info.get('description')
                }
                for cat, info in data.get('category_metadata', {}).items()
            } if 'category_metadata' in data else {}
        }, 'Category metadata for quick lookups (material_index is in Materials.yaml)')
        
        # 2. Property Taxonomy
        logger.info("📦 2/8: Extracting Property Taxonomy...")
        self.save_file('property_taxonomy.yaml', {
            'propertyCategories': data.get('propertyCategories', {})
        }, 'Property classification system including laser-material interaction and material characteristics')
        
        # 3. Machine Settings
        logger.info("📦 3/8: Extracting Machine Settings...")
        self.save_file('machine_settings.yaml', {
            'machine_settingsRanges': data.get('machine_settingsRanges', {}),
            'machine_settingsDescriptions': data.get('machine_settingsDescriptions', {})
        }, 'Laser machine parameter ranges and detailed guidance for optimal material processing')
        
        # 4. Material Properties (from categories)
        logger.info("📦 4/8: Extracting Material Properties...")
        material_props = {
            'materialPropertyDescriptions': data.get('materialPropertyDescriptions', {}),
            'categories': {}
        }
        
        # Extract category_ranges and properties from each category
        for cat_name, cat_data in data.get('categories', {}).items():
            material_props['categories'][cat_name] = {
                'name': cat_data.get('name'),
                'description': cat_data.get('description'),
                'category_ranges': cat_data.get('category_ranges', {}),
                'subcategories': cat_data.get('subcategories', {}),
                'properties': cat_data.get('properties', {})
            }
            
            # Include specialized property sections if they exist
            for prop_section in ['electricalProperties', 'chemicalProperties', 'processingParameters', 
                               'structuralProperties', 'mechanicalProperties']:
                if prop_section in cat_data:
                    material_props['categories'][cat_name][prop_section] = cat_data[prop_section]
        
        self.save_file('material_properties.yaml', material_props, 
                      'Physical, thermal, optical, mechanical, and electrical property ranges by category')
        
        # 5. Safety & Regulatory
        logger.info("📦 5/8: Extracting Safety & Regulatory...")
        safety_reg = {
            'universal_regulatory_standards': data.get('universal_regulatory_standards', []),
            'safetyTemplates': data.get('safetyTemplates', {}),
            'regulatoryTemplates': data.get('regulatoryTemplates', {})
        }
        
        # Extract per-category regulatory standards
        safety_reg['category_regulatory_standards'] = {}
        for cat_name, cat_data in data.get('categories', {}).items():
            if 'regulatory_standards' in cat_data:
                safety_reg['category_regulatory_standards'][cat_name] = cat_data['regulatory_standards']
        
        self.save_file('safety_regulatory.yaml', safety_reg,
                      'Safety templates, regulatory standards, and compliance requirements')
        
        # 6. Industry & Applications
        logger.info("📦 6/8: Extracting Industry & Applications...")
        industry_apps = {
            'industryGuidance': data.get('industryGuidance', {}),
            'applicationTypeDefinitions': data.get('applicationTypeDefinitions', {}),
            'standardOutcomeMetrics': data.get('standardOutcomeMetrics', {})
        }
        
        # Extract per-category common applications and industry tags
        industry_apps['category_applications'] = {}
        industry_apps['category_industry_tags'] = {}
        for cat_name, cat_data in data.get('categories', {}).items():
            if 'common_applications' in cat_data:
                industry_apps['category_applications'][cat_name] = cat_data['common_applications']
            if 'industryTags' in cat_data:
                industry_apps['category_industry_tags'][cat_name] = cat_data['industryTags']
        
        self.save_file('industry_applications.yaml', industry_apps,
                      'Industry-specific guidance, application types, and outcome metrics')
        
        # 7. Environmental Impact
        logger.info("📦 7/8: Extracting Environmental Impact...")
        self.save_file('environmental_impact.yaml', {
            'environmentalImpactTemplates': data.get('environmentalImpactTemplates', {})
        }, 'Environmental sustainability benefits and impact templates')
        
        # 8. Category Metadata (comprehensive)
        logger.info("📦 8/8: Extracting Category Metadata...")
        category_meta = {
            'metadata': data.get('metadata', {}),
            'categories': {}
        }
        
        # Extract high-level category info
        for cat_name, cat_data in data.get('categories', {}).items():
            category_meta['categories'][cat_name] = {
                'name': cat_data.get('name'),
                'description': cat_data.get('description'),
                'subcategories': cat_data.get('subcategories', {}),
                'common_applications': cat_data.get('common_applications', [])
            }
        
        self.save_file('category_metadata.yaml', category_meta,
                      'High-level category definitions, structure, and metadata')
        
        logger.info(f"\n✨ Split complete! Created 8 files in {self.output_dir}")
        logger.info(f"📊 Source file size: {self.source_file.stat().st_size:,} bytes")
        
        # Calculate total size of split files
        total_size = sum(f.stat().st_size for f in self.output_dir.glob('*.yaml'))
        logger.info(f"📦 Split files total: {total_size:,} bytes")
        logger.info(f"💾 Size difference: {total_size - self.source_file.stat().st_size:+,} bytes (includes metadata)")


def main():
    """Main execution"""
    project_root = Path(__file__).parent.parent.parent
    source_file = project_root / 'data' / 'Categories.yaml'
    output_dir = project_root / 'data' / 'categories'
    
    if not source_file.exists():
        logger.error(f"❌ Source file not found: {source_file}")
        return 1
    
    splitter = CategorySplitter(source_file, output_dir)
    splitter.split_all()
    
    logger.info("\n🎯 Next steps:")
    logger.info("   1. Review generated files in data/categories/")
    logger.info("   2. Test the new CategoryDataLoader")
    logger.info("   3. Update components to use new loader")
    logger.info("   4. Keep Categories.yaml as backup (optional)")
    
    return 0


if __name__ == '__main__':
    exit(main())
