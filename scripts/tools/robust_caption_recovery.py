#!/usr/bin/env python3
"""
Robust Caption Recovery Tool

Recovers caption text from git history files that have line-wrapping issues
and formats them properly for frontmatter integration.
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

@dataclass 
class CaptionData:
    """Structure for caption data"""
    description: str
    before_text: str
    after_text: str
    material: str

class RobustCaptionRecovery:
    """Recovers caption data with robust text parsing"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.frontmatter_dir = self.project_root / "content" / "frontmatter"
        self.target_commit = "bc616274"
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
        self.logger = logging.getLogger(__name__)
    
    def get_available_materials(self) -> List[str]:
        """Get materials with caption data in git history"""
        try:
            cmd = [
                "git", "ls-tree", "-r", "--name-only", 
                self.target_commit, "content/components/caption/"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode != 0:
                return []
            
            materials = []
            for line in result.stdout.strip().split('\n'):
                if line and line.endswith('.yaml'):
                    filename = Path(line).name
                    material_name = filename.replace('-laser-cleaning.yaml', '')
                    materials.append(material_name)
            
            return sorted(materials)
        except Exception:
            return []
    
    def extract_text_blocks(self, raw_content: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract before_text and after_text from raw content using robust parsing"""
        
        # Remove BOM if present
        if raw_content.startswith('\ufeff'):
            raw_content = raw_content[1:]
        
        try:
            # Method 1: Try to find text blocks between before_text and after_text markers
            before_match = re.search(r'before_text:\s*\|\s*\n(.*?)(?=\n\s*after_text:|\n\s*#|\nafter_text:)', 
                                   raw_content, re.DOTALL)
            after_match = re.search(r'after_text:\s*\|\s*\n(.*?)(?=\n\s*#|\Z)', 
                                  raw_content, re.DOTALL)
            
            before_text = None
            after_text = None
            
            if before_match:
                before_text = before_match.group(1).strip()
                # Clean up the text - remove excessive whitespace and normalize
                before_text = re.sub(r'\s+', ' ', before_text)
                before_text = before_text.strip()
            
            if after_match:
                after_text = after_match.group(1).strip()
                # Clean up the text - remove excessive whitespace and normalize
                after_text = re.sub(r'\s+', ' ', after_text)
                after_text = after_text.strip()
            
            return before_text, after_text
            
        except Exception as e:
            self.logger.error(f"Error extracting text blocks: {e}")
            return None, None
    
    def recover_caption_robust(self, material: str) -> Optional[CaptionData]:
        """Recover caption data using robust parsing"""
        try:
            caption_file = f"content/components/caption/{material}-laser-cleaning.yaml"
            cmd = ["git", "show", f"{self.target_commit}:{caption_file}"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode != 0:
                return None
            
            # Extract text blocks robustly
            before_text, after_text = self.extract_text_blocks(result.stdout)
            
            if not before_text or not after_text:
                return None
            
            # Create description
            material_display = material.replace('-', ' ').title()
            description = f"Microscopic analysis of {material_display} surface before and after laser cleaning treatment"
            
            return CaptionData(
                description=description,
                before_text=before_text,
                after_text=after_text,
                material=material
            )
            
        except Exception as e:
            self.logger.error(f"Error recovering caption for {material}: {e}")
            return None
    
    def has_existing_caption(self, material: str) -> bool:
        """Check if material already has caption in frontmatter"""
        frontmatter_file = self.frontmatter_dir / f"{material}-laser-cleaning.yaml"
        
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
        frontmatter_file = self.frontmatter_dir / f"{material}-laser-cleaning.yaml"
        
        if not frontmatter_file.exists():
            return False
        
        try:
            # Read existing frontmatter
            with open(frontmatter_file, 'r', encoding='utf-8') as f:
                content = f.read()
            data = yaml.safe_load(content)
            
            # Add caption data
            data['caption'] = {
                'description': caption_data.description,
                'beforeText': caption_data.before_text,
                'afterText': caption_data.after_text
            }
            
            # Write back to file
            with open(frontmatter_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, 
                         allow_unicode=True, width=float('inf'))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating frontmatter for {material}: {e}")
            return False
    
    def run_recovery(self, dry_run: bool = False, limit: int = None) -> Dict[str, Any]:
        """Run caption recovery with robust parsing"""
        
        print("🔍 ROBUST CAPTION RECOVERY")
        print("=" * 50)
        print(f"📁 Source: Git history commit {self.target_commit}")
        print(f"📁 Target: {self.frontmatter_dir}")
        print(f"📋 Mode: {'DRY RUN' if dry_run else 'LIVE RECOVERY'}")
        if limit:
            print(f"📊 Limit: First {limit} materials")
        print("-" * 80)
        
        # Get available materials
        available_materials = self.get_available_materials()
        if limit:
            available_materials = available_materials[:limit]
        
        print(f"🔍 Processing {len(available_materials)} materials...")
        print()
        
        results = {
            'total_available': len(available_materials),
            'processed': 0,
            'recovered': 0,
            'skipped_existing': 0,
            'errors': 0,
            'recovered_materials': [],
            'error_materials': []
        }
        
        for i, material in enumerate(available_materials, 1):
            print(f"[{i}/{len(available_materials)}] ", end="")
            results['processed'] += 1
            
            # Check if already has caption
            if self.has_existing_caption(material):
                print(f"  ➖ Caption exists: {material}")
                results['skipped_existing'] += 1
                continue
            
            # Recover caption data
            caption_data = self.recover_caption_robust(material)
            if not caption_data:
                print(f"  ❌ Failed: {material}")
                results['errors'] += 1
                results['error_materials'].append(material)
                continue
            
            # Update frontmatter (if not dry run)
            if not dry_run:
                if self.update_frontmatter_with_caption(material, caption_data):
                    print(f"  ✅ Recovered: {material}")
                    results['recovered'] += 1
                    results['recovered_materials'].append(material)
                else:
                    print(f"  ❌ Update failed: {material}")
                    results['errors'] += 1
                    results['error_materials'].append(material)
            else:
                print(f"  🔄 Would recover: {material}")
                results['recovered'] += 1
                results['recovered_materials'].append(material)
        
        print("-" * 80)
        print("📊 RECOVERY SUMMARY")
        print(f"  📁 Materials processed: {results['processed']}")
        print(f"  ✅ Captions recovered: {results['recovered']}")
        print(f"  ➖ Already had captions: {results['skipped_existing']}")
        print(f"  ❌ Errors: {results['errors']}")
        
        if not dry_run and results['recovered'] > 0:
            print("🎉 Caption recovery completed successfully!")
        elif dry_run:
            print("🔍 Dry run completed")
        
        return results

def main():
    """Main execution function"""
    
    # Get project root
    project_root = Path(__file__).resolve().parent.parent.parent
    
    # Parse arguments
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv
    
    # Check for limit
    limit = None
    for arg in sys.argv:
        if arg.startswith('--limit='):
            try:
                limit = int(arg.split('=')[1])
            except ValueError:
                pass
    
    # Create recovery tool
    recovery = RobustCaptionRecovery(str(project_root))
    
    # Run recovery
    results = recovery.run_recovery(dry_run=dry_run, limit=limit)
    
    # Exit with appropriate code
    sys.exit(0 if results['errors'] == 0 else 1)

if __name__ == "__main__":
    main()