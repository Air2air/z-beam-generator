#!/usr/bin/env python3
"""
Comprehensive Frontmatter Structure Fix

Addresses three main issues:
1. Adds missing micro images to images section where needed
2. Moves caption positioning to correct location (after images)
3. Ensures proper image structure consistency
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

class FrontmatterStructureFixer:
    """Fixes frontmatter structure issues comprehensively"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.frontmatter_dir = self.project_root / "content" / "frontmatter"
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
        self.logger = logging.getLogger(__name__)
    
    def get_material_slug(self, material_name: str) -> str:
        """Convert material name to URL-safe slug"""
        import re
        material_slug = material_name.lower()
        material_slug = re.sub(r'[^a-z0-9\s-]', '', material_slug)
        material_slug = re.sub(r'\s+', '-', material_slug)
        material_slug = re.sub(r'-+', '-', material_slug)
        return material_slug.strip('-')
    
    def add_missing_micro_image(self, data: Dict[str, Any], material_name: str) -> bool:
        """Add missing micro image to images section if not present"""
        modified = False
        
        if 'images' not in data:
            data['images'] = {}
        
        images = data['images']
        
        # Add micro image if missing
        if 'micro' not in images:
            material_slug = self.get_material_slug(material_name)
            material_title = material_name.title()
            
            images['micro'] = {
                'alt': f'Microscopic view of {material_title} surface after laser cleaning showing detailed surface structure',
                'url': f'/images/material/{material_slug}-laser-cleaning-micro.jpg'
            }
            modified = True
        
        return modified
    
    def move_caption_to_correct_position(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Move caption to correct position after images section"""
        
        # Define the correct order
        correct_order = [
            'name', 'category', 'subcategory', 'title', 'subtitle', 'description',
            'author', 'images', 'caption', 'regulatoryStandards', 'applications',
            'materialProperties', 'machineSettings', 'environmentalImpact',
            'outcomeMetrics', 'preservedData'
        ]
        
        # Create new ordered dictionary
        ordered_data = {}
        
        # Add fields in correct order if they exist
        for key in correct_order:
            if key in data:
                ordered_data[key] = data[key]
        
        # Add any remaining fields that weren't in the correct_order list
        for key, value in data.items():
            if key not in ordered_data:
                ordered_data[key] = value
        
        return ordered_data
    
    def process_file(self, file_path: Path) -> bool:
        """Process a single frontmatter file"""
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            data = yaml.safe_load(content)
            if not data:
                return False
            
            # Extract material name
            material_name = data.get('name', file_path.stem.replace('-laser-cleaning', ''))
            
            modified = False
            
            # 1. Add missing micro image
            if self.add_missing_micro_image(data, material_name):
                modified = True
            
            # 2. Move caption to correct position
            original_keys = list(data.keys())
            data = self.move_caption_to_correct_position(data)
            new_keys = list(data.keys())
            
            if original_keys != new_keys:
                modified = True
            
            # Write back if modified
            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False, 
                             allow_unicode=True, width=float('inf'))
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error processing {file_path}: {e}")
            return False
    
    def run_comprehensive_fix(self) -> Dict[str, Any]:
        """Run comprehensive frontmatter structure fixes"""
        
        print("🔧 COMPREHENSIVE FRONTMATTER STRUCTURE FIX")
        print("=" * 50)
        print(f"📁 Target: {self.frontmatter_dir}")
        print("🎯 Fixes:")
        print("   1. Add missing micro images")
        print("   2. Move caption to correct position (after images)")
        print("   3. Ensure consistent structure")
        print("-" * 80)
        
        results = {
            'total_files': 0,
            'modified_files': 0,
            'micro_images_added': 0,
            'captions_repositioned': 0,
            'errors': 0,
            'modified_materials': [],
            'error_materials': []
        }
        
        # Process all frontmatter files
        frontmatter_files = list(self.frontmatter_dir.glob("*.yaml"))
        results['total_files'] = len(frontmatter_files)
        
        print(f"🔍 Processing {len(frontmatter_files)} frontmatter files...")
        print()
        
        for i, file_path in enumerate(frontmatter_files, 1):
            material_name = file_path.stem.replace('-laser-cleaning', '')
            print(f"[{i}/{len(frontmatter_files)}] ", end="")
            
            try:
                # Check what needs fixing before processing
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f.read())
                
                needs_micro = 'images' not in data or 'micro' not in data.get('images', {})
                has_caption = 'caption' in data
                
                # Determine caption position
                keys_list = list(data.keys())
                caption_index = keys_list.index('caption') if 'caption' in keys_list else -1
                images_index = keys_list.index('images') if 'images' in keys_list else -1
                needs_reposition = (has_caption and images_index >= 0 and 
                                  (caption_index < 0 or caption_index <= images_index))
                
                if self.process_file(file_path):
                    fixes = []
                    if needs_micro:
                        fixes.append("micro image")
                        results['micro_images_added'] += 1
                    if needs_reposition:
                        fixes.append("caption position")
                        results['captions_repositioned'] += 1
                    
                    print(f"  ✅ Fixed: {material_name} ({', '.join(fixes)})")
                    results['modified_files'] += 1
                    results['modified_materials'].append(material_name)
                else:
                    print(f"  ➖ No changes: {material_name}")
                    
            except Exception as e:
                print(f"  ❌ Error: {material_name} - {e}")
                results['errors'] += 1
                results['error_materials'].append(material_name)
        
        print("-" * 80)
        print("📊 COMPREHENSIVE FIX SUMMARY")
        print(f"  📁 Files processed: {results['total_files']}")
        print(f"  ✅ Files modified: {results['modified_files']}")
        print(f"  🖼️ Micro images added: {results['micro_images_added']}")
        print(f"  📝 Captions repositioned: {results['captions_repositioned']}")
        print(f"  ❌ Errors: {results['errors']}")
        
        if results['modified_files'] > 0:
            print("🎉 Frontmatter structure fixes completed successfully!")
        
        return results

def main():
    """Main execution function"""
    
    # Get project root
    project_root = Path(__file__).resolve().parent.parent.parent
    
    # Create fixer
    fixer = FrontmatterStructureFixer(str(project_root))
    
    # Run comprehensive fix
    results = fixer.run_comprehensive_fix()
    
    # Exit with appropriate code
    sys.exit(0 if results['errors'] == 0 else 1)

if __name__ == "__main__":
    main()