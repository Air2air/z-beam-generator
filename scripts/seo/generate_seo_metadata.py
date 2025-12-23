#!/usr/bin/env python3
"""
Generate SEO metadata (page_title and meta_description) for all domains.

This script:
1. Loads data from Materials.yaml, Contaminants.yaml, Settings.yaml, Compounds.yaml
2. Uses SEOMetadataGenerator to create page_title and meta_description
3. Writes results back to the data files

Usage:
    python3 scripts/seo/generate_seo_metadata.py --domain materials
    python3 scripts/seo/generate_seo_metadata.py --domain all
    python3 scripts/seo/generate_seo_metadata.py --material aluminum-laser-cleaning
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, Any, List
import argparse

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from export.generation.seo_metadata_generator import SEOMetadataGenerator


class SEOMetadataPopulator:
    """Populate SEO metadata in data files."""
    
    def __init__(self):
        self.materials_path = project_root / "data" / "materials" / "Materials.yaml"
        self.contaminants_path = project_root / "data" / "contaminants" / "Contaminants.yaml"
        self.settings_path = project_root / "data" / "settings" / "Settings.yaml"
        self.compounds_path = project_root / "data" / "compounds" / "Compounds.yaml"
        
    def load_yaml(self, path: Path) -> Dict[str, Any]:
        """Load YAML file."""
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def save_yaml(self, path: Path, data: Dict[str, Any]) -> None:
        """Save YAML file."""
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    def generate_materials_seo(self, material_name: str = None) -> int:
        """Generate SEO metadata for materials."""
        print("\n📝 Generating SEO metadata for materials...")
        
        data = self.load_yaml(self.materials_path)
        materials = data.get('materials', {})
        
        generator = SEOMetadataGenerator({'page_type': 'material'})
        count = 0
        
        for slug, material_data in materials.items():
            # Skip if specific material requested and this isn't it
            if material_name and slug != material_name:
                continue
            
            name = material_data.get('name', slug)
            print(f"\n  Processing: {name} ({slug})")
            
            try:
                # Generate SEO metadata
                frontmatter = {
                    'name': name,
                    'category': material_data.get('category'),
                    'subcategory': material_data.get('subcategory'),
                    'properties': material_data.get('properties', {}),
                    'machine_settings': material_data.get('machine_settings', {}),
                }
                
                result = generator.generate(frontmatter)
                
                # Add to material data
                if 'page_title' in result and 'meta_description' in result:
                    material_data['page_title'] = result['page_title']
                    material_data['meta_description'] = result['meta_description']
                    
                    print(f"    ✅ Title: {result['page_title']} ({len(result['page_title'])} chars)")
                    print(f"    ✅ Description: {result['meta_description']} ({len(result['meta_description'])} chars)")
                else:
                    print(f"    ⚠️  SEO metadata not generated")
                    continue
                
                count += 1
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
                continue
        
        # Save updated data
        if count > 0:
            self.save_yaml(self.materials_path, data)
            print(f"\n✅ Generated SEO metadata for {count} materials")
        
        return count
    
    def generate_contaminants_seo(self, contaminant_name: str = None) -> int:
        """Generate SEO metadata for contaminants."""
        print("\n📝 Generating SEO metadata for contaminants...")
        
        data = self.load_yaml(self.contaminants_path)
        contaminants = data.get('contaminants', {})
        
        generator = SEOMetadataGenerator({'page_type': 'contaminant'})
        count = 0
        
        for slug, contaminant_data in contaminants.items():
            if contaminant_name and slug != contaminant_name:
                continue
            
            name = contaminant_data.get('name', slug)
            print(f"\n  Processing: {name} ({slug})")
            
            try:
                frontmatter = {
                    'name': name,
                    'type': contaminant_data.get('type'),
                    'category': contaminant_data.get('category'),
                    'removal_characteristics': contaminant_data.get('removal_characteristics', {}),
                }
                
                result = generator.generate(frontmatter)
                
                if 'page_title' in result and 'meta_description' in result:
                    contaminant_data['page_title'] = result['page_title']
                    contaminant_data['meta_description'] = result['meta_description']
                    
                    print(f"    ✅ Title: {result['page_title']} ({len(result['page_title'])} chars)")
                    print(f"    ✅ Description: {result['meta_description']} ({len(result['meta_description'])} chars)")
                else:
                    print(f"    ⚠️  SEO metadata not generated")
                    continue
                
                count += 1
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
                continue
        
        if count > 0:
            self.save_yaml(self.contaminants_path, data)
            print(f"\n✅ Generated SEO metadata for {count} contaminants")
        
        return count
    
    def generate_settings_seo(self, setting_name: str = None) -> int:
        """Generate SEO metadata for settings."""
        print("\n📝 Generating SEO metadata for settings...")
        
        data = self.load_yaml(self.settings_path)
        settings = data.get('settings', {})
        
        generator = SEOMetadataGenerator({'page_type': 'settings'})
        count = 0
        
        for slug, setting_data in settings.items():
            if setting_name and slug != setting_name:
                continue
            
            name = setting_data.get('name', slug)
            print(f"\n  Processing: {name} ({slug})")
            
            try:
                frontmatter = {
                    'name': name,
                    'material_name': name,  # Settings use material name
                    'machine_settings': setting_data.get('machine_settings', {}),
                    'relationships': setting_data.get('relationships', {}),
                }
                
                result = generator.generate(frontmatter)
                
                if 'page_title' in result and 'meta_description' in result:
                    setting_data['page_title'] = result['page_title']
                    setting_data['meta_description'] = result['meta_description']
                    
                    print(f"    ✅ Title: {result['page_title']} ({len(result['page_title'])} chars)")
                    print(f"    ✅ Description: {result['meta_description']} ({len(result['meta_description'])} chars)")
                else:
                    print(f"    ⚠️  SEO metadata not generated")
                    continue
                
                count += 1
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
                continue
        
        if count > 0:
            self.save_yaml(self.settings_path, data)
            print(f"\n✅ Generated SEO metadata for {count} settings")
        
        return count
    
    def generate_compounds_seo(self, compound_name: str = None) -> int:
        """Generate SEO metadata for compounds."""
        print("\n📝 Generating SEO metadata for compounds...")
        
        data = self.load_yaml(self.compounds_path)
        compounds = data.get('compounds', {})
        
        generator = SEOMetadataGenerator({'page_type': 'compound'})
        count = 0
        
        for slug, compound_data in compounds.items():
            if compound_name and slug != compound_name:
                continue
            
            name = compound_data.get('name', slug)
            print(f"\n  Processing: {name} ({slug})")
            
            try:
                frontmatter = {
                    'name': name,
                    'hazard_class': compound_data.get('hazard_class'),
                    'cas_number': compound_data.get('cas_number'),
                }
                
                result = generator.generate(frontmatter)
                
                if 'page_title' in result and 'meta_description' in result:
                    compound_data['page_title'] = result['page_title']
                    compound_data['meta_description'] = result['meta_description']
                    
                    print(f"    ✅ Title: {result['page_title']} ({len(result['page_title'])} chars)")
                    print(f"    ✅ Description: {result['meta_description']} ({len(result['meta_description'])} chars)")
                else:
                    print(f"    ⚠️  SEO metadata not generated")
                    continue
                
                count += 1
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
                continue
        
        if count > 0:
            self.save_yaml(self.compounds_path, data)
            print(f"\n✅ Generated SEO metadata for {count} compounds")
        
        return count


def main():
    parser = argparse.ArgumentParser(description='Generate SEO metadata for domains')
    parser.add_argument('--domain', choices=['materials', 'contaminants', 'settings', 'compounds', 'all'],
                        default='all', help='Domain to generate SEO for')
    parser.add_argument('--material', help='Specific material slug to process')
    parser.add_argument('--contaminant', help='Specific contaminant slug to process')
    parser.add_argument('--setting', help='Specific setting slug to process')
    parser.add_argument('--compound', help='Specific compound slug to process')
    
    args = parser.parse_args()
    
    populator = SEOMetadataPopulator()
    total = 0
    
    print("\n" + "="*80)
    print("📊 SEO METADATA GENERATION")
    print("="*80)
    
    if args.domain in ['materials', 'all']:
        total += populator.generate_materials_seo(args.material)
    
    if args.domain in ['contaminants', 'all']:
        total += populator.generate_contaminants_seo(args.contaminant)
    
    if args.domain in ['settings', 'all']:
        total += populator.generate_settings_seo(args.setting)
    
    if args.domain in ['compounds', 'all']:
        total += populator.generate_compounds_seo(args.compound)
    
    print("\n" + "="*80)
    print(f"✅ COMPLETE: Generated SEO metadata for {total} items")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
