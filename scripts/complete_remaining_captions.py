#!/usr/bin/env python3
"""
Complete Remaining Caption Generation
=====================================

Specifically targets the 8 remaining files that need caption generation.
"""

import sys
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from components.caption.generators.frontmatter_generator import FrontmatterCaptionGenerator
from api.client_factory import create_api_client

# Direct mapping of remaining files
REMAINING_FILES = [
    {
        'file': 'ceramic-matrix-composites-cmcs-laser-cleaning.yaml',
        'material_name': 'CMCs'
    },
    {
        'file': 'fiber-reinforced-polyurethane-frpu-laser-cleaning.yaml', 
        'material_name': 'FRPU'
    },
    {
        'file': 'glass-fiber-reinforced-polymers-gfrp-laser-cleaning.yaml',
        'material_name': 'GFRP'
    },
    {
        'file': 'metal-matrix-composites-mmcs-laser-cleaning.yaml',
        'material_name': 'MMCs'
    },
    {
        'file': 'polytetrafluoroethylene-laser-cleaning.yaml',
        'material_name': 'PTFE'
    },
    {
        'file': 'polyvinyl-chloride-laser-cleaning.yaml',
        'material_name': 'PVC'
    }
]

class RemainingCaptionProcessor:
    """Process the remaining files for caption generation."""
    
    def __init__(self):
        self.caption_generator = FrontmatterCaptionGenerator()
        self.api_client = None
        self.stats = {
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'files_processed': []
        }
        
    def initialize_api_client(self) -> bool:
        """Initialize API client for caption generation."""
        try:
            self.api_client = create_api_client()
            if self.api_client:
                print("✅ API client initialized")
                return True
            else:
                print("❌ Failed to initialize API client")
                return False
        except Exception as e:
            print(f"❌ Error initializing API client: {e}")
            return False
    
    def load_frontmatter(self, frontmatter_path: Path) -> Optional[Dict[str, Any]]:
        """Load existing frontmatter data."""
        try:
            with open(frontmatter_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Handle both pure YAML and --- separated YAML
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 2:
                    yaml_content = parts[1].strip()
                else:
                    yaml_content = content
            else:
                yaml_content = content
            
            return yaml.safe_load(yaml_content)
            
        except Exception as e:
            print(f"❌ Error loading frontmatter from {frontmatter_path}: {e}")
            return None
    
    def save_frontmatter(self, frontmatter_path: Path, data: Dict[str, Any]) -> bool:
        """Save updated frontmatter data."""
        try:
            # Update metadata
            if 'metadata' not in data:
                data['metadata'] = {}
            data['metadata']['lastUpdated'] = datetime.now().isoformat()
            data['metadata']['captionIntegrated'] = True
            
            # Write YAML with safe formatting to prevent quote escaping issues
            with open(frontmatter_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, 
                         sort_keys=False, width=1000, default_style='"')
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving frontmatter: {e}")
            return False
    
    def process_file(self, file_info: Dict[str, str]) -> bool:
        """Process a single file for caption generation."""
        filename = file_info['file']
        material_name = file_info['material_name']
        
        print(f"\n🎯 Processing: {material_name} ({filename})")
        
        # Build file path
        frontmatter_path = Path(f"content/components/frontmatter/{filename}")
        
        if not frontmatter_path.exists():
            print(f"❌ File not found: {frontmatter_path}")
            return False
        
        # Load existing frontmatter
        frontmatter_data = self.load_frontmatter(frontmatter_path)
        if frontmatter_data is None:
            print("❌ Failed to load frontmatter")
            return False
        
        # Check if caption already exists
        if 'caption' in frontmatter_data:
            print("⚠️  Caption already exists, skipping")
            return True
        
        # Generate caption
        try:
            print(f"🔄 Generating caption content for {material_name}...")
            
            # Get material name from frontmatter
            material_name_from_data = frontmatter_data.get('name', material_name)
            
            # Generate caption using the correct method
            result = self.caption_generator.generate_for_frontmatter(
                material_name=material_name_from_data,
                material_data=frontmatter_data,
                api_client=self.api_client,
                frontmatter_data=frontmatter_data
            )
            
            if not result.success or not result.content:
                print("❌ Failed to generate caption")
                return False
            
            caption_data = result.content
            print(f"✅ Caption data generated: {len(str(caption_data))} chars")
            
        except Exception as e:
            print(f"❌ Error generating caption: {e}")
            return False
        
        # Remove micro image from images section if it exists
        if 'images' in frontmatter_data and 'micro' in frontmatter_data['images']:
            print("🔄 Removing micro image from images section...")
            del frontmatter_data['images']['micro']
            
            # Remove images section if it's empty
            if not frontmatter_data['images']:
                del frontmatter_data['images']
        
        # Integrate caption
        frontmatter_data['caption'] = caption_data
        
        # Save updated frontmatter
        if self.save_frontmatter(frontmatter_path, frontmatter_data):
            print(f"✅ Updated frontmatter saved to: {frontmatter_path}")
            print("🎉 Caption integration completed for {}")
            print("   📝 Caption added under 'caption' key")
            print("   🖼️ Micro image moved from images.micro to caption.imageUrl")
            print("   🔄 Frontmatter metadata updated")
            return True
        else:
            print("❌ Failed to save frontmatter")
            return False
    
    def run(self):
        """Process all remaining files."""
        print("🚀 Processing Remaining Caption Generation")
        print("=" * 50)
        
        if not self.initialize_api_client():
            print("❌ Failed to initialize API client")
            return
        
        print(f"📋 Processing {len(REMAINING_FILES)} remaining files...")
        
        for file_info in REMAINING_FILES:
            self.stats['processed'] += 1
            
            if self.process_file(file_info):
                self.stats['successful'] += 1
                self.stats['files_processed'].append({
                    'file': file_info['file'],
                    'material': file_info['material_name'],
                    'status': 'success'
                })
            else:
                self.stats['failed'] += 1
                self.stats['files_processed'].append({
                    'file': file_info['file'],
                    'material': file_info['material_name'],
                    'status': 'failed'
                })
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 PROCESSING COMPLETE")
        print("=" * 50)
        print(f"📈 Total Files: {self.stats['processed']}")
        print(f"✅ Successful: {self.stats['successful']}")
        print(f"❌ Failed: {self.stats['failed']}")
        
        if self.stats['failed'] > 0:
            print("\n❌ Failed Files:")
            for result in self.stats['files_processed']:
                if result['status'] == 'failed':
                    print(f"   • {result['material']}: {result['file']}")
        
        success_rate = (self.stats['successful'] / self.stats['processed']) * 100
        print(f"\n🎯 Success Rate: {success_rate:.1f}%")


def main():
    processor = RemainingCaptionProcessor()
    processor.run()


if __name__ == '__main__':
    main()