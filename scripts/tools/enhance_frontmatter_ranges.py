#!/usr/bin/env python3
"""
Frontmatter Range Enhancement Script

Adds missing min/max range values to frontmatter properties based on category ranges
from Categories.yaml. This addresses the issue where the migration preserved property
values but didn't include the appropriate min/max ranges.

Usage:
    python3 scripts/tools/enhance_frontmatter_ranges.py
    python3 scripts/tools/enhance_frontmatter_ranges.py --material Zinc
    python3 scripts/tools/enhance_frontmatter_ranges.py --dry-run
"""

import os
import sys
import yaml
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

class FrontmatterRangeEnhancer:
    """Enhances frontmatter files with missing min/max ranges from Categories.yaml"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.project_root = Path(__file__).parent.parent.parent
        self.categories_file = self.project_root / "data" / "Categories.yaml"
        self.frontmatter_dir = self.project_root / "content" / "frontmatter"
        
        self.enhancement_stats = {
            'processed': 0,
            'enhanced': 0,
            'ranges_added': 0,
            'errors': 0
        }
        
        # Load category ranges
        self.category_ranges = self.load_category_ranges()
    
    def load_category_ranges(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Load category range data from Categories.yaml"""
        try:
            with open(self.categories_file, 'r', encoding='utf-8') as f:
                categories_data = yaml.safe_load(f)
            
            # Extract category ranges
            category_ranges = {}
            for category, category_info in categories_data['categories'].items():
                if 'category_ranges' in category_info:
                    category_ranges[category] = category_info['category_ranges']
            
            print(f"✅ Loaded ranges for {len(category_ranges)} categories")
            return category_ranges
            
        except Exception as e:
            print(f"❌ Error loading Categories.yaml: {e}")
            sys.exit(1)
    
    def get_property_ranges(self, category: str, property_name: str) -> Optional[Dict[str, Any]]:
        """Get min/max ranges for a property based on category"""
        category_lower = category.lower()
        
        if category_lower in self.category_ranges:
            category_data = self.category_ranges[category_lower]
            if property_name in category_data:
                prop_data = category_data[property_name]
                
                # Extract min/max if available
                ranges = {}
                if 'min' in prop_data:
                    ranges['min'] = prop_data['min']
                if 'max' in prop_data:
                    ranges['max'] = prop_data['max']
                
                return ranges if ranges else None
        
        return None
    
    def enhance_property(self, property_name: str, property_data: Dict[str, Any], 
                        category: str) -> tuple[Dict[str, Any], bool]:
        """Enhance a single property with ranges if missing"""
        
        if not isinstance(property_data, dict):
            return property_data, False
        
        # Skip if already has min/max
        if 'min' in property_data and 'max' in property_data:
            return property_data, False
        
        # Get ranges from category
        ranges = self.get_property_ranges(category, property_name)
        if not ranges:
            return property_data, False
        
        # Add missing ranges
        enhanced_property = property_data.copy()
        ranges_added = 0
        
        if 'min' not in enhanced_property and 'min' in ranges:
            enhanced_property['min'] = ranges['min']
            ranges_added += 1
        
        if 'max' not in enhanced_property and 'max' in ranges:
            enhanced_property['max'] = ranges['max']
            ranges_added += 1
        
        return enhanced_property, ranges_added > 0
    
    def enhance_material_properties(self, material_properties: Dict[str, Any], 
                                   category: str) -> tuple[Dict[str, Any], int]:
        """Enhance all properties in materialProperties section"""
        
        enhanced_props = material_properties.copy()
        total_ranges_added = 0
        
        # Process both material_characteristics and laser_material_interaction
        for section_name in ['material_characteristics', 'laser_material_interaction']:
            if section_name in enhanced_props:
                section = enhanced_props[section_name]
                
                # Process each property in the section
                for prop_name, prop_data in section.items():
                    if prop_name in ['label', 'description']:
                        continue  # Skip section metadata
                    
                    enhanced_prop, was_enhanced = self.enhance_property(
                        prop_name, prop_data, category
                    )
                    
                    if was_enhanced:
                        enhanced_props[section_name][prop_name] = enhanced_prop
                        total_ranges_added += 1
        
        return enhanced_props, total_ranges_added
    
    def enhance_frontmatter_file(self, file_path: Path) -> bool:
        """Enhance a single frontmatter file with missing ranges"""
        
        try:
            # Load frontmatter
            with open(file_path, 'r', encoding='utf-8') as f:
                frontmatter_data = yaml.safe_load(f)
            
            if not frontmatter_data:
                print(f"  ⚠️  Empty file: {file_path.name}")
                return False
            
            # Get material category
            category = frontmatter_data.get('category', '').lower()
            if not category:
                print(f"  ⚠️  No category found: {file_path.name}")
                return False
            
            # Enhance materialProperties
            if 'materialProperties' in frontmatter_data:
                enhanced_props, ranges_added = self.enhance_material_properties(
                    frontmatter_data['materialProperties'], category
                )
                
                if ranges_added > 0:
                    if not self.dry_run:
                        frontmatter_data['materialProperties'] = enhanced_props
                        
                        # Write enhanced file
                        with open(file_path, 'w', encoding='utf-8') as f:
                            yaml.dump(frontmatter_data, f, default_flow_style=False,
                                     allow_unicode=True, sort_keys=False, indent=2)
                    
                    print(f"  ✅ Enhanced: {file_path.name} (+{ranges_added} ranges)")
                    self.enhancement_stats['ranges_added'] += ranges_added
                    return True
                else:
                    print(f"  ➖ No enhancement needed: {file_path.name}")
            else:
                print(f"  ⚠️  No materialProperties found: {file_path.name}")
            
            return False
            
        except Exception as e:
            print(f"  ❌ Error processing {file_path.name}: {e}")
            self.enhancement_stats['errors'] += 1
            return False
    
    def enhance_material(self, material_name: str) -> bool:
        """Enhance specific material frontmatter file"""
        
        file_path = self.frontmatter_dir / f"{material_name.lower().replace(' ', '-')}-laser-cleaning.yaml"
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return False
        
        print(f"🔄 Enhancing {material_name}...")
        enhanced = self.enhance_frontmatter_file(file_path)
        
        self.enhancement_stats['processed'] += 1
        if enhanced:
            self.enhancement_stats['enhanced'] += 1
        
        return enhanced
    
    def enhance_all_materials(self) -> None:
        """Enhance all frontmatter files"""
        
        frontmatter_files = list(self.frontmatter_dir.glob("*-laser-cleaning.yaml"))
        total_files = len(frontmatter_files)
        
        print(f"🚀 Starting range enhancement for {total_files} frontmatter files...")
        print(f"📁 Source directory: {self.frontmatter_dir}")
        print(f"📋 Mode: {'DRY RUN' if self.dry_run else 'LIVE ENHANCEMENT'}")
        print("-" * 80)
        
        for i, file_path in enumerate(frontmatter_files, 1):
            print(f"[{i}/{total_files}] ", end="")
            enhanced = self.enhance_frontmatter_file(file_path)
            
            self.enhancement_stats['processed'] += 1
            if enhanced:
                self.enhancement_stats['enhanced'] += 1
        
        print("-" * 80)
        print("📊 ENHANCEMENT SUMMARY")
        print(f"  📁 Processed: {self.enhancement_stats['processed']}")
        print(f"  ✅ Enhanced: {self.enhancement_stats['enhanced']}")
        print(f"  🔢 Ranges Added: {self.enhancement_stats['ranges_added']}")
        print(f"  ❌ Errors: {self.enhancement_stats['errors']}")
        
        if self.enhancement_stats['errors'] == 0:
            print("🎉 Enhancement completed successfully!")
        else:
            print(f"⚠️  Enhancement completed with {self.enhancement_stats['errors']} errors")

def main():
    parser = argparse.ArgumentParser(description='Enhance frontmatter files with missing ranges')
    parser.add_argument('--material', help='Enhance specific material only')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without writing files')
    
    args = parser.parse_args()
    
    # Initialize enhancer
    enhancer = FrontmatterRangeEnhancer(dry_run=args.dry_run)
    
    # Enhance materials
    if args.material:
        enhancer.enhance_material(args.material)
    else:
        enhancer.enhance_all_materials()

if __name__ == '__main__':
    main()