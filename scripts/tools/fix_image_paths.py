#!/usr/bin/env python3
"""
Fix Image Paths in Frontmatter Files
=====================================
Ensures all image URLs use the /images/material/{slug} format.

Usage:
    python3 scripts/tools/fix_image_paths.py [--dry-run]
"""

import os
import re
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Tuple


class ImagePathFixer:
    """Fix image paths in frontmatter YAML files"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.frontmatter_dir = Path("content/components/frontmatter")
        self.fixed_count = 0
        self.error_count = 0
        self.skipped_count = 0
        
    def fix_all_frontmatter(self) -> Dict:
        """Fix image paths in all frontmatter files"""
        print("🔧 Fixing Image Paths in Frontmatter Files")
        print("=" * 60)
        
        if self.dry_run:
            print("🔍 DRY RUN MODE - No files will be modified")
            print()
        
        if not self.frontmatter_dir.exists():
            print(f"❌ Frontmatter directory not found: {self.frontmatter_dir}")
            return {"success": False, "error": "Directory not found"}
        
        yaml_files = list(self.frontmatter_dir.glob("*.yaml"))
        print(f"📋 Found {len(yaml_files)} frontmatter files to check")
        print()
        
        for yaml_file in sorted(yaml_files):
            self._fix_file(yaml_file)
        
        # Print summary
        print()
        print("=" * 60)
        print("📊 Summary:")
        print(f"  ✅ Fixed: {self.fixed_count} files")
        print(f"  ⏭️  Skipped: {self.skipped_count} files (already correct)")
        print(f"  ❌ Errors: {self.error_count} files")
        
        if self.dry_run:
            print()
            print("🔍 DRY RUN COMPLETE - No files were modified")
        
        return {
            "success": self.error_count == 0,
            "fixed": self.fixed_count,
            "skipped": self.skipped_count,
            "errors": self.error_count,
            "dry_run": self.dry_run
        }
    
    def _fix_file(self, file_path: Path) -> bool:
        """Fix image paths in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if file needs fixing
            if not self._needs_fixing(content):
                print(f"✅ {file_path.name} - Already correct")
                self.skipped_count += 1
                return True
            
            # Parse YAML
            data = yaml.safe_load(content)
            
            if not data or 'images' not in data:
                print(f"⏭️  {file_path.name} - No images section")
                self.skipped_count += 1
                return True
            
            # Fix paths
            modified = self._fix_image_paths(data, file_path.stem)
            
            if not modified:
                print(f"✅ {file_path.name} - Already correct")
                self.skipped_count += 1
                return True
            
            if self.dry_run:
                print(f"🔍 {file_path.name} - Would fix paths")
                self.fixed_count += 1
                return True
            
            # Save fixed file
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            
            print(f"✅ {file_path.name} - Fixed")
            self.fixed_count += 1
            return True
            
        except Exception as e:
            print(f"❌ {file_path.name} - Error: {e}")
            self.error_count += 1
            return False
    
    def _needs_fixing(self, content: str) -> bool:
        """Check if content has incorrect image paths"""
        # Look for paths like /images/{something} but not /images/material/
        # Also check for /images/author/ which is correct
        pattern = r'url:\s*/images/(?!material/|author/)'
        return bool(re.search(pattern, content))
    
    def _fix_image_paths(self, data: Dict, file_stem: str) -> bool:
        """Fix image paths in the data dictionary"""
        modified = False
        
        # Extract material slug from filename (remove -laser-cleaning suffix)
        material_slug = file_stem.replace('-laser-cleaning', '')
        
        images = data.get('images', {})
        
        # Fix hero image
        if 'hero' in images and isinstance(images['hero'], dict):
            if 'url' in images['hero']:
                old_url = images['hero']['url']
                if not old_url.startswith('/images/material/'):
                    # Extract filename from old URL
                    filename = old_url.split('/')[-1]
                    new_url = f'/images/material/{filename}'
                    images['hero']['url'] = new_url
                    modified = True
                    print(f"    🔧 Hero: {old_url} → {new_url}")
        
        # Fix micro image (in caption section)
        if 'caption' in data and isinstance(data['caption'], dict):
            if 'imageUrl' in data['caption'] and isinstance(data['caption']['imageUrl'], dict):
                if 'url' in data['caption']['imageUrl']:
                    old_url = data['caption']['imageUrl']['url']
                    if not old_url.startswith('/images/material/'):
                        filename = old_url.split('/')[-1]
                        new_url = f'/images/material/{filename}'
                        data['caption']['imageUrl']['url'] = new_url
                        modified = True
                        print(f"    🔧 Micro: {old_url} → {new_url}")
        
        return modified


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Fix image paths in frontmatter files to use /images/material/ format"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be fixed without modifying files'
    )
    
    args = parser.parse_args()
    
    fixer = ImagePathFixer(dry_run=args.dry_run)
    result = fixer.fix_all_frontmatter()
    
    exit_code = 0 if result['success'] else 1
    exit(exit_code)


if __name__ == "__main__":
    main()
