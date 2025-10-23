#!/usr/bin/env python3
"""
Caption Data Restoration Script

Extracts caption data from Materials.yaml and adds it to frontmatter files
in the correct format as specified by the example.

Expected caption format per example:
caption:
  description: Microscopic analysis of [material] surface before and after laser cleaning treatment
  beforeText: [before_text from Materials.yaml]
  afterText: [after_text from Materials.yaml]

Usage:
    python3 scripts/tools/restore_caption_data.py
    python3 scripts/tools/restore_caption_data.py --material Slate
    python3 scripts/tools/restore_caption_data.py --dry-run
"""

import os
import sys
import yaml
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

class CaptionDataRestorer:
    """Restores caption data from Materials.yaml to frontmatter files"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.project_root = Path(__file__).parent.parent.parent
        self.materials_file = self.project_root / "data" / "materials.yaml"
        self.frontmatter_dir = self.project_root / "content" / "frontmatter"
        
        self.restore_stats = {
            'processed': 0,
            'restored': 0,
            'captions_found': 0,
            'captions_added': 0,
            'errors': 0
        }
        
        # Load materials data with captions
        self.materials_data = self.load_materials_data()
    
    def load_materials_data(self) -> Dict[str, Any]:
        """Load materials.yaml data"""
        try:
            with open(self.materials_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Error loading materials.yaml: {e}")
            sys.exit(1)
    
    def extract_caption_data(self, material_name: str) -> Optional[Dict[str, Any]]:
        """Extract caption data for a specific material from Materials.yaml"""
        
        if 'materials' not in self.materials_data:
            return None
        
        if material_name not in self.materials_data['materials']:
            return None
        
        material_data = self.materials_data['materials'][material_name]
        
        # Build caption structure per example format
        caption = {
            'description': f"Microscopic analysis of {material_name} surface before and after laser cleaning treatment"
        }
        
        before_text = None
        after_text = None
        
        # Method 1: Check traditional captions structure
        if 'captions' in material_data:
            captions_data = material_data['captions']
            if 'before_text' in captions_data:
                before_text = captions_data['before_text']
            if 'after_text' in captions_data:
                after_text = captions_data['after_text']
        
        # Method 2: Check ai_text_fields structure
        if 'ai_text_fields' in material_data:
            ai_fields = material_data['ai_text_fields']
            
            # Extract from caption_beforeText field
            if 'caption_beforeText' in ai_fields and 'content' in ai_fields['caption_beforeText']:
                content = ai_fields['caption_beforeText']['content']
                # Handle JSON-like content
                if isinstance(content, str) and ('beforeText' in content or 'content' in content):
                    import json
                    try:
                        parsed = json.loads(content)
                        if 'beforeText' in parsed:
                            before_text = parsed['beforeText']
                        elif 'content' in parsed:
                            before_text = parsed['content']
                    except:
                        # If not JSON, use as is
                        before_text = content
                elif isinstance(content, str):
                    before_text = content
            
            # Extract from caption_afterText field
            if 'caption_afterText' in ai_fields and 'content' in ai_fields['caption_afterText']:
                content = ai_fields['caption_afterText']['content']
                # Handle JSON-like content
                if isinstance(content, str) and ('afterText' in content or 'content' in content):
                    import json
                    try:
                        parsed = json.loads(content)
                        if 'afterText' in parsed:
                            after_text = parsed['afterText']
                        elif 'content' in parsed:
                            after_text = parsed['content']
                    except:
                        # If not JSON, use as is
                        after_text = content
                elif isinstance(content, str):
                    after_text = content
        
        # Add texts to caption if found
        if before_text:
            caption['beforeText'] = before_text
        if after_text:
            caption['afterText'] = after_text
        
        # Only return if we have at least before or after text
        if 'beforeText' in caption or 'afterText' in caption:
            return caption
        
        return None
    
    def restore_caption_to_frontmatter(self, file_path: Path, material_name: str) -> bool:
        """Restore caption data to a frontmatter file"""
        
        try:
            # Load frontmatter
            with open(file_path, 'r', encoding='utf-8') as f:
                frontmatter_data = yaml.safe_load(f)
            
            if not frontmatter_data:
                print(f"  ⚠️  Empty file: {file_path.name}")
                return False
            
            # Check if caption already exists
            if 'caption' in frontmatter_data:
                print(f"  ➖ Caption already exists: {file_path.name}")
                return False
            
            # Extract caption data from Materials.yaml
            caption_data = self.extract_caption_data(material_name)
            
            if not caption_data:
                print(f"  ➖ No caption data found: {file_path.name}")
                return False
            
            # Add caption to frontmatter in correct position (after images)
            if not self.dry_run:
                # Find the right position to insert caption (after images, before regulatoryStandards)
                ordered_frontmatter = {}
                
                # Copy fields in correct order
                field_order = [
                    'name', 'category', 'subcategory', 'title', 'subtitle', 'description',
                    'author', 'images', 'caption', 'regulatoryStandards', 'applications'
                ]
                
                # Add fields in order if they exist
                for field in field_order:
                    if field == 'caption':
                        ordered_frontmatter[field] = caption_data
                    elif field in frontmatter_data:
                        ordered_frontmatter[field] = frontmatter_data[field]
                
                # Add any remaining fields not in the order list
                for field, value in frontmatter_data.items():
                    if field not in ordered_frontmatter:
                        ordered_frontmatter[field] = value
                
                # Write enhanced file
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(ordered_frontmatter, f, default_flow_style=False,
                             allow_unicode=True, sort_keys=False, indent=2)
            
            print(f"  ✅ Caption restored: {file_path.name}")
            self.restore_stats['captions_added'] += 1
            return True
            
        except Exception as e:
            print(f"  ❌ Error processing {file_path.name}: {e}")
            self.restore_stats['errors'] += 1
            return False
    
    def restore_material(self, material_name: str) -> bool:
        """Restore caption for specific material"""
        
        file_path = self.frontmatter_dir / f"{material_name.lower().replace(' ', '-')}-laser-cleaning.yaml"
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return False
        
        print(f"🔄 Restoring caption for {material_name}...")
        restored = self.restore_caption_to_frontmatter(file_path, material_name)
        
        self.restore_stats['processed'] += 1
        if restored:
            self.restore_stats['restored'] += 1
        
        return restored
    
    def identify_materials_with_captions(self) -> list[str]:
        """Identify all materials that have caption data in Materials.yaml"""
        
        materials_with_captions = []
        
        if 'materials' in self.materials_data:
            for material_name, material_data in self.materials_data['materials'].items():
                has_captions = False
                
                # Check traditional captions structure
                if 'captions' in material_data:
                    captions_data = material_data['captions']
                    if 'before_text' in captions_data or 'after_text' in captions_data:
                        has_captions = True
                
                # Check ai_text_fields structure
                if 'ai_text_fields' in material_data:
                    ai_fields = material_data['ai_text_fields']
                    if ('caption_beforeText' in ai_fields and 'content' in ai_fields['caption_beforeText']) or \
                       ('caption_afterText' in ai_fields and 'content' in ai_fields['caption_afterText']):
                        has_captions = True
                
                if has_captions:
                    materials_with_captions.append(material_name)
        
        return materials_with_captions
    
    def restore_all_captions(self) -> None:
        """Restore captions for all materials that have caption data"""
        
        # Identify materials with caption data
        materials_with_captions = self.identify_materials_with_captions()
        self.restore_stats['captions_found'] = len(materials_with_captions)
        
        print(f"🔍 Found {len(materials_with_captions)} materials with caption data:")
        for material in materials_with_captions:
            print(f"   - {material}")
        print()
        
        print(f"🚀 Starting caption restoration...")
        print(f"📁 Source: Materials.yaml captions data")
        print(f"📁 Target: {self.frontmatter_dir}")
        print(f"📋 Mode: {'DRY RUN' if self.dry_run else 'LIVE RESTORATION'}")
        print("-" * 80)
        
        for i, material_name in enumerate(materials_with_captions, 1):
            print(f"[{i}/{len(materials_with_captions)}] ", end="")
            restored = self.restore_caption_to_frontmatter(
                self.frontmatter_dir / f"{material_name.lower().replace(' ', '-')}-laser-cleaning.yaml",
                material_name
            )
            
            self.restore_stats['processed'] += 1
            if restored:
                self.restore_stats['restored'] += 1
        
        print("-" * 80)
        print("📊 CAPTION RESTORATION SUMMARY")
        print(f"  🔍 Materials with captions found: {self.restore_stats['captions_found']}")
        print(f"  📁 Files processed: {self.restore_stats['processed']}")
        print(f"  ✅ Captions restored: {self.restore_stats['restored']}")
        print(f"  📝 Caption blocks added: {self.restore_stats['captions_added']}")
        print(f"  ❌ Errors: {self.restore_stats['errors']}")
        
        if self.restore_stats['errors'] == 0:
            print("🎉 Caption restoration completed successfully!")
        else:
            print(f"⚠️  Caption restoration completed with {self.restore_stats['errors']} errors")

def main():
    parser = argparse.ArgumentParser(description='Restore caption data to frontmatter files')
    parser.add_argument('--material', help='Restore caption for specific material only')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without writing files')
    
    args = parser.parse_args()
    
    # Initialize restorer
    restorer = CaptionDataRestorer(dry_run=args.dry_run)
    
    # Restore captions
    if args.material:
        restorer.restore_material(args.material)
    else:
        restorer.restore_all_captions()

if __name__ == '__main__':
    main()