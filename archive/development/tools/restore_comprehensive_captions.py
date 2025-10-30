#!/usr/bin/env python3
"""
Comprehensive Caption Restoration Tool

Recovers high-quality caption data from git history (content/components/caption/)
and converts it to proper frontmatter format for integration into frontmatter files.

This tool addresses the loss of comprehensive caption data that was generated 
in October 2025 but was stored in separate component files that were later removed.
"""

import os
import sys
import subprocess
import yaml
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

@dataclass 
class CaptionData:
    """Structure for caption data"""
    description: str
    before_text: str
    after_text: str
    material: str
    generation_date: Optional[str] = None
    author: Optional[str] = None

class ComprehensiveCaptionRestorer:
    """Restores comprehensive caption data from git history"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.materials_file = self.project_root / "data" / "Materials.yaml"
        self.frontmatter_dir = self.project_root / "content" / "frontmatter"
        
        # Target git commit with comprehensive caption data
        self.target_commit = "bc616274"
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
        self.logger = logging.getLogger(__name__)
    
    def get_available_caption_materials(self) -> List[str]:
        """Get list of materials that have caption data in git history"""
        try:
            # Get list of caption files from git history
            cmd = [
                "git", "ls-tree", "-r", "--name-only", 
                self.target_commit, "content/components/caption/"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode != 0:
                self.logger.error(f"Git command failed: {result.stderr}")
                return []
            
            materials = []
            for line in result.stdout.strip().split('\n'):
                if line and line.endswith('.yaml'):
                    # Extract material name: content/components/caption/aluminum-laser-cleaning.yaml -> aluminum
                    filename = Path(line).name
                    material_name = filename.replace('-laser-cleaning.yaml', '')
                    materials.append(material_name)
            
            return sorted(materials)
            
        except Exception as e:
            self.logger.error(f"Error getting caption materials: {e}")
            return []
    
    def recover_caption_from_git(self, material: str) -> Optional[CaptionData]:
        """Recover caption data for a specific material from git history"""
        try:
            caption_file = f"content/components/caption/{material}-laser-cleaning.yaml"
            cmd = ["git", "show", f"{self.target_commit}:{caption_file}"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode != 0:
                self.logger.warning(f"Could not recover caption for {material}: {result.stderr}")
                return None
            
            # Parse the YAML content
            yaml_content = result.stdout
            try:
                data = yaml.safe_load(yaml_content)
                
                # Extract caption data
                before_text = data.get('before_text', '').strip()
                after_text = data.get('after_text', '').strip()
                
                # Create description from material name
                material_display = material.replace('-', ' ').title()
                description = f"Microscopic analysis of {material_display} surface before and after laser cleaning treatment"
                
                # Get generation info
                generation_date = None
                author = None
                if 'generation' in data:
                    generation_date = data['generation'].get('generated')
                if 'author' in data:
                    author = data['author']
                
                return CaptionData(
                    description=description,
                    before_text=before_text,
                    after_text=after_text,
                    material=material,
                    generation_date=generation_date,
                    author=author
                )
                
            except yaml.YAMLError as e:
                self.logger.error(f"YAML parsing error for {material}: {e}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error recovering caption for {material}: {e}")
            return None
    
    def convert_to_frontmatter_format(self, caption_data: CaptionData) -> Dict[str, Any]:
        """Convert comprehensive caption data to frontmatter format"""
        return {
            'description': caption_data.description,
            'beforeText': caption_data.before_text,
            'afterText': caption_data.after_text
        }
    
    def get_frontmatter_filename(self, material: str) -> Path:
        """Get the frontmatter filename for a material"""
        return self.frontmatter_dir / f"{material}-laser-cleaning.yaml"
    
    def has_existing_caption(self, material: str) -> bool:
        """Check if material already has caption in frontmatter"""
        frontmatter_file = self.get_frontmatter_filename(material)
        
        if not frontmatter_file.exists():
            return False
        
        try:
            with open(frontmatter_file, 'r', encoding='utf-8') as f:
                content = f.read()
            data = yaml.safe_load(content)
            return 'caption' in data and data['caption']
        except Exception:
            return False
    
    def update_frontmatter_with_caption(self, material: str, caption_data: CaptionData) -> bool:
        """Update frontmatter file with caption data"""
        frontmatter_file = self.get_frontmatter_filename(material)
        
        if not frontmatter_file.exists():
            self.logger.warning(f"Frontmatter file not found: {frontmatter_file}")
            return False
        
        try:
            # Read existing frontmatter
            with open(frontmatter_file, 'r', encoding='utf-8') as f:
                content = f.read()
            data = yaml.safe_load(content)
            
            # Add caption data
            data['caption'] = self.convert_to_frontmatter_format(caption_data)
            
            # Write back to file
            with open(frontmatter_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, 
                         allow_unicode=True, width=float('inf'))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating frontmatter for {material}: {e}")
            return False
    
    def run_comprehensive_restoration(self, dry_run: bool = False) -> Dict[str, Any]:
        """Run comprehensive caption restoration from git history"""
        
        print("🔍 COMPREHENSIVE CAPTION RESTORATION")
        print("=" * 50)
        print(f"📁 Source: Git history commit {self.target_commit}")
        print(f"📁 Target: {self.frontmatter_dir}")
        print(f"📋 Mode: {'DRY RUN' if dry_run else 'LIVE RESTORATION'}")
        print("-" * 80)
        
        # Get available materials
        available_materials = self.get_available_caption_materials()
        print(f"🔍 Found {len(available_materials)} materials with comprehensive caption data:")
        
        # Group materials for display
        for i, material in enumerate(available_materials, 1):
            if i <= 10:  # Show first 10
                print(f"   - {material.replace('-', ' ').title()}")
            elif i == 11:
                print(f"   ... and {len(available_materials) - 10} more")
                break
        
        print()
        print("🚀 Starting comprehensive caption restoration...")
        print("-" * 80)
        
        results = {
            'total_available': len(available_materials),
            'processed': 0,
            'restored': 0,
            'skipped_existing': 0,
            'errors': 0,
            'restored_materials': [],
            'error_materials': []
        }
        
        for i, material in enumerate(available_materials, 1):
            print(f"[{i}/{len(available_materials)}] ", end="")
            results['processed'] += 1
            
            # Check if already has caption
            if self.has_existing_caption(material):
                print(f"  ➖ Caption already exists: {material}-laser-cleaning.yaml")
                results['skipped_existing'] += 1
                continue
            
            # Recover caption data
            caption_data = self.recover_caption_from_git(material)
            if not caption_data:
                print(f"  ❌ Failed to recover: {material}-laser-cleaning.yaml")
                results['errors'] += 1
                results['error_materials'].append(material)
                continue
            
            # Update frontmatter (if not dry run)
            if not dry_run:
                if self.update_frontmatter_with_caption(material, caption_data):
                    print(f"  ✅ Caption restored: {material}-laser-cleaning.yaml")
                    results['restored'] += 1
                    results['restored_materials'].append(material)
                else:
                    print(f"  ❌ Failed to update: {material}-laser-cleaning.yaml")
                    results['errors'] += 1
                    results['error_materials'].append(material)
            else:
                print(f"  🔄 Would restore: {material}-laser-cleaning.yaml")
                results['restored'] += 1  # Count as would-be restored for dry run
                results['restored_materials'].append(material)
        
        print("-" * 80)
        print("📊 COMPREHENSIVE CAPTION RESTORATION SUMMARY")
        print(f"  🔍 Materials with comprehensive captions available: {results['total_available']}")
        print(f"  📁 Files processed: {results['processed']}")
        print(f"  ✅ Captions restored: {results['restored']}")
        print(f"  ➖ Already had captions: {results['skipped_existing']}")
        print(f"  ❌ Errors: {results['errors']}")
        
        if results['error_materials']:
            print(f"  📋 Error materials: {', '.join(results['error_materials'])}")
        
        if not dry_run and results['restored'] > 0:
            print("🎉 Comprehensive caption restoration completed successfully!")
        elif dry_run:
            print("🔍 Dry run completed - no files were modified")
        
        return results

def main():
    """Main execution function"""
    
    # Get project root
    project_root = Path(__file__).resolve().parent.parent.parent
    
    # Check for dry run mode
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv
    
    # Create restorer
    restorer = ComprehensiveCaptionRestorer(str(project_root))
    
    # Run restoration
    results = restorer.run_comprehensive_restoration(dry_run=dry_run)
    
    # Exit with appropriate code
    sys.exit(0 if results['errors'] == 0 else 1)

if __name__ == "__main__":
    main()