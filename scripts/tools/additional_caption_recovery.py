#!/usr/bin/env python3
"""
Additional Caption Recovery Tool

Recovers remaining caption data from various git commits and sources
for materials that were missed in the initial comprehensive recovery.
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
    author: Optional[str] = None

class AdditionalCaptionRecovery:
    """Recovers additional caption data from various git sources"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.frontmatter_dir = self.project_root / "content" / "frontmatter"
        
        # Different commits with caption data
        self.caption_sources = {
            'bc616274': 'content/components/caption/',  # Main comprehensive source
            'ff38ad5b': 'content/components/caption/',  # Rare earth materials
            'd833e97c': 'content/components/caption/',  # Hickory and others
        }
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
        self.logger = logging.getLogger(__name__)
    
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
    
    def get_available_materials_from_commit(self, commit: str, path: str) -> List[str]:
        """Get materials with caption data in specific git commit"""
        try:
            cmd = ["git", "ls-tree", "-r", "--name-only", commit, path]
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
    
    def recover_caption_from_commit(self, material: str, commit: str, path: str) -> Optional[CaptionData]:
        """Recover caption data for a specific material from specific git commit"""
        try:
            caption_file = f"{path}{material}-laser-cleaning.yaml"
            cmd = ["git", "show", f"{commit}:{caption_file}"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode != 0:
                return None
            
            # Extract text blocks robustly
            before_text, after_text = self.extract_text_blocks(result.stdout)
            
            if not before_text or not after_text:
                return None
            
            # Extract author if available
            author_match = re.search(r'author:\s*"([^"]+)"', result.stdout)
            author = author_match.group(1) if author_match else None
            
            # Create description
            material_display = material.replace('-', ' ').title()
            description = f"Microscopic analysis of {material_display} surface before and after laser cleaning treatment"
            
            return CaptionData(
                description=description,
                before_text=before_text,
                after_text=after_text,
                material=material,
                author=author
            )
            
        except Exception as e:
            self.logger.error(f"Error recovering caption for {material} from {commit}: {e}")
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
    
    def run_additional_recovery(self, target_materials: List[str] = None) -> Dict[str, Any]:
        """Run additional caption recovery for specific materials"""
        
        print("🔍 ADDITIONAL CAPTION RECOVERY")
        print("=" * 50)
        print(f"📁 Target: {self.frontmatter_dir}")
        print(f"📋 Sources: {len(self.caption_sources)} git commits")
        if target_materials:
            print(f"📊 Target materials: {len(target_materials)}")
        print("-" * 80)
        
        results = {
            'total_processed': 0,
            'recovered': 0,
            'skipped_existing': 0,
            'errors': 0,
            'recovered_materials': [],
            'error_materials': []
        }
        
        # If no target materials specified, get all missing materials
        if not target_materials:
            # Get materials without captions
            all_materials = []
            for frontmatter_file in self.frontmatter_dir.glob("*.yaml"):
                material = frontmatter_file.stem.replace('-laser-cleaning', '')
                if not self.has_existing_caption(material):
                    all_materials.append(material)
            target_materials = sorted(all_materials)
        
        print(f"🎯 Processing {len(target_materials)} materials...")
        print()
        
        for i, material in enumerate(target_materials, 1):
            print(f"[{i}/{len(target_materials)}] ", end="")
            results['total_processed'] += 1
            
            # Check if already has caption
            if self.has_existing_caption(material):
                print(f"  ➖ Caption exists: {material}")
                results['skipped_existing'] += 1
                continue
            
            # Try to recover from different commits
            caption_data = None
            for commit, path in self.caption_sources.items():
                caption_data = self.recover_caption_from_commit(material, commit, path)
                if caption_data:
                    break
            
            if not caption_data:
                print(f"  ❌ Not found: {material}")
                results['errors'] += 1
                results['error_materials'].append(material)
                continue
            
            # Update frontmatter
            if self.update_frontmatter_with_caption(material, caption_data):
                print(f"  ✅ Recovered: {material}")
                results['recovered'] += 1
                results['recovered_materials'].append(material)
            else:
                print(f"  ❌ Update failed: {material}")
                results['errors'] += 1
                results['error_materials'].append(material)
        
        print("-" * 80)
        print("📊 ADDITIONAL RECOVERY SUMMARY")
        print(f"  📁 Materials processed: {results['total_processed']}")
        print(f"  ✅ Captions recovered: {results['recovered']}")
        print(f"  ➖ Already had captions: {results['skipped_existing']}")
        print(f"  ❌ Errors: {results['errors']}")
        
        if results['recovered'] > 0:
            print("🎉 Additional caption recovery completed!")
        
        return results

def main():
    """Main execution function"""
    
    # Get project root
    project_root = Path(__file__).resolve().parent.parent.parent
    
    # Create recovery tool
    recovery = AdditionalCaptionRecovery(str(project_root))
    
    # Define specific materials we know have caption data in git history
    target_materials = [
        'hickory', 'cerium', 'lanthanum', 'dysprosium', 'europium', 
        'neodymium', 'praseodymium', 'terbium', 'yttrium',
        'cast-iron', 'tool-steel'
    ]
    
    # Run recovery
    results = recovery.run_additional_recovery(target_materials)
    
    # Exit with appropriate code
    sys.exit(0 if results['errors'] == 0 else results['errors'])

if __name__ == "__main__":
    main()